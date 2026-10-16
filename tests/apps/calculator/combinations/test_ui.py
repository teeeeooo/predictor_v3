"""Actual CalculatorTkApp → section action → shared dialog integration."""
import csv
from dataclasses import replace
import time
import tkinter as tk
from tkinter import ttk
import pytest

from apps.calculator.ui.calculator_app import CalculatorTkApp
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.theme import apply_calculator_theme
from apps.calculator.application.combinations.models import Candidate
from apps.calculator.ui.combinations.sources import collect
from .seeds import contexts


def pump(root, condition, timeout=30):
    end=time.monotonic()+timeout
    while not condition() and time.monotonic()<end:
        root.update()
    assert condition(), "Tk operation timed out"


def tables(widget):
    if isinstance(widget,MetricInputTable):
        yield widget
    for child in widget.winfo_children():
        yield from tables(child)


def populate(section, context):
    values=dict(context.values)
    for table in tables(section._frame):
        known=table.get_text_values()
        table.set_values_batch({k:v for k,v in values.items() if k in known})
    if context.kind=="en_seer":
        section._p_design_var.set(values["p_design_c_w"])
        section._t_design_var.set(values["t_design_c"])
    if context.kind=="en_scop":
        section.p_design_h_vars[context.climate].set(values["p_design_h_w"])
        section.tbiv_vars[context.climate].set(values["tbiv_temp_c"])
        section.tol_vars[context.climate].set(values["tol_temp_c"])


@pytest.fixture(scope="module")
def root():
    # One Tcl interpreter per module avoids macOS Tk's destroyed-root event loop.
    root = tk.Tk()
    root.withdraw()
    # Standalone tests use the same chrome metrics as the actual app entrypoint.
    apply_calculator_theme(root)
    yield root
    try:
        root.destroy()
    except tk.TclError:
        pass


def test_actual_app_all_section_contexts_detail_export_and_reopen(root, tmp_path, monkeypatch):
    errors=[]
    root.report_callback_exception=lambda *args: errors.append(args)
    app=CalculatorTkApp(root)
    try:
        sections={"iso":app.iso_tab._two_point_section,
                  "en_seer":app.en14825_tab.seer_section,"en_scop":app.en14825_tab.scop_section,
                  "m_seer":app.ahri210240_m_tab.seer_section,"m_hspf":app.ahri210240_m_tab.hspf_section,
                  "seer2":app.ahri210240_tab.seer2_section,"hspf2":app.ahri210240_tab.hspf2_section,
                  "korea_cspf":app.korea_tab.cspf_section,"korea_hspf":app.korea_tab.hspf_section}
        for mode,key,attribute in (("SASO T3","saso","_saso_t3_section"),("Brazil CSPF","brazil","_brazil_section")):
            app.iso_tab._mode_combo.set(mode);app.iso_tab._on_mode_changed()
            sections[key]=getattr(app.iso_tab,attribute)
        app.iso_tab._mode_combo.set("Hong Kong");app.iso_tab._on_mode_changed()
        sections.update(hong_kong_cspf=app.iso_tab.sections["CSPF"],hong_kong_hspf=app.iso_tab.sections["HSPF"])
        filename=tmp_path/"조합.csv"
        monkeypatch.setattr("apps.calculator.ui.table_csv_export.filedialog.asksaveasfilename",lambda **kw:str(filename))
        checked=[]
        for context in contexts():
            section=sections[context.kind]
            if context.product:
                section.product_var.set({"variable_capacity":"Variable Capacity","dual_stage":"Dual Stage","triple_capacity_northern":"Triple Stage Northern"}[context.product])
            if context.system_type:
                section.type_var.set(context.system_type)
            populate(section,context)
            section.combination_button.invoke()
            manager=section.combinations
            index=next(i for i,c in enumerate(manager.contexts) if c.kind==context.kind and c.profile==context.profile and c.climate==context.climate and c.mode==context.mode and c.product==context.product and c.system_type==context.system_type)
            manager.select(index)
            manager.reload()
            content=manager.handle.dialog._adapter
            assert list(content.candidates.blocks) == [p.key for p in content.points]
            for point in content.points:
                block=content.candidates.blocks[point.key]
                assert (block.table is not None) == point.independent
                if block.table is not None:
                    assert block.table.row_count()==2
            common_keys = set(content.settings.field_tables) | set(content.settings.options.selectors).intersection({"appliance_type"})
            assert common_keys == set(dict(content.session.context.values))
            assert all(table.row_count() == 1 for table in content.settings.tables)
            main_tables = list(tables(section._frame))
            if context.kind.startswith("en_"):
                main_tables += app.en14825_tab._common_input_tables
            aliases = {"p_design_c_w": "p_design_c", "p_design_h_w": "p_design_h",
                       "tbiv_temp_c": "tbiv", "tol_temp_c": "tol",
                       **{key + "_w": key for key in ("p_to", "p_sb", "p_ck", "p_off")}}
            for key, table in content.settings.field_tables.items():
                main_key = aliases.get(key, key)
                source = next(t for t in main_tables if main_key in t.field_order)
                column = next(c for (_r, c), field in source.editable_cells.items() if field == main_key)
                assert dict(table.columns)[key] == dict(source.columns)[column]
                assert table.data_column_chars == source.data_column_chars
            if context.kind.startswith("en_"):
                assert all(not key.startswith("declared_") for key in common_keys)
            assert content.calculate_button.instate(["!disabled"]), (context,content.status.cget("text"))
            content.calculate_button.invoke()
            run=content.session.run
            assert run.status=="running" and run.processed==0
            pump(root,lambda:run.status!="running")
            assert run.succeeded==1, (context,run.results)
            assert "기준" not in content.results.table.headers
            assert content.adapter.project(run.snapshot.context,run.detail(run.results[0]))==run.results[0].score
            if context.product == "triple_capacity_northern":
                # A real common-setting edit changes the active point policy.
                block=content.candidates.blocks["H3Low"]
                assert block.table is None
                retained=tuple(content.session.pools["H3Low"])
                settings_table=content.settings.field_tables["low_min_c"]
                original=settings_table.get_text_values()["low_min_c"]
                settings_table.set_address_values_batch({("value", "low_min_c"): "0"})
                assert block.table is not None
                assert tuple(content.session.pools["H3Low"])==retained
                settings_table.set_address_values_batch({("value", "low_min_c"): original})
                assert block.table is None
                assert tuple(content.session.pools["H3Low"])==retained
                root.update()
                viewport=content.candidates.viewport
                assert viewport.vertical_overflow_delta()>0
                viewport.canvas.yview_moveto(1.0)
                root.update()
                assert viewport.canvas.yview()[1]==1.0
            content.results.table.interaction_controller.select((0, 0))
            # Detail is the real action, and the subdialog contains pinned input text.
            before=set(manager.handle.dialog.window.winfo_children())
            content.results.detail()
            opened=[w for w in manager.handle.dialog.window.winfo_children() if w not in before]
            assert opened
            for window in opened:
                window.destroy()
            content.results.export()
            assert filename.read_bytes().startswith(b'\xef\xbb\xbf')
            with filename.open(encoding="utf-8-sig",newline="") as handle:
                rows=list(csv.DictReader(handle))
            assert len(rows)==1 and rows[0]["값"]==str(run.results[0].score.value)
            assert "run_id" not in rows[0]
            manager.handle.dispose()
            section.combination_button.invoke()
            assert manager.current.run is run
            manager.handle.dispose()
            checked.append(context)
        # Editable options stay in the same session; old results keep their snapshot.
        manager=sections["hspf2"].combinations
        manager.open()
        original=manager.current
        content=manager.handle.dialog._adapter
        run=original.run
        tabs=content.context_tabs.tabs()
        button=content.settings.options.flag_controls["measured_h2_boost"]
        button.invoke()
        assert manager.current is original and original.run is run
        assert original.stale
        assert content.context_tabs.tabs()==tabs
        assert sum(p.independent for p in manager.adapter.points(manager.current.context))==7
        assert dict(run.snapshot.context.options)["measured_h2_boost"] is True
        manager.handle.dispose()
        assert len(checked)==22
        assert not errors, errors
    finally:
        for widget in root.winfo_children():
            widget.destroy()


def test_point_blocks_share_viewport_and_resize(root):
    from apps.calculator.ui.sections.iso_iseer_2point_section import IsoIseer2PointSection
    section = IsoIseer2PointSection(root)
    populate(section, contexts()[0])
    section.combination_button.invoke()
    manager = section.combinations
    try:
        content = manager.handle.dialog._adapter
        window = manager.handle.dialog.window
        blocks = content.candidates.blocks
        assert list(blocks) == ["35_full", "35_half"]
        for block in blocks.values():
            assert block.table.row_count() == 2
        first, second = blocks.values()
        first.table.set_positions_batch({(row, col): value for col in range(12)
                                        for row, value in ((0, "3600"), (1, "900"))})
        content.calculate_button.invoke()
        pump(root, lambda: content.session.run.status != "running")
        for size in ("640x590", "800x720", "640x480"):
            window.geometry(size)
            root.update()
            viewport = content.candidates.viewport
            assert viewport.horizontal_overflow_delta() > 0
            assert first.winfo_y() < second.winfo_y()
            assert first.table.grid_table.canvas_view.layout.row_height > 1
            # Both rows fit inside each block; only the outer viewport scrolls.
            for block in blocks.values():
                view = block.table.grid_table.canvas_view
                bottom = view.cell_bbox((1, 0), root=True)[3]
                assert bottom <= block.winfo_rooty()+block.winfo_height()
                assert view.corner == {"35_full":"STD", "35_half":"HALF"}[block.point.key]
                assert "유효" in block.caption.cget("text") and "/" in block.caption.cget("text")
                assert "붙여넣기" not in block.caption.cget("text")
                assert not hasattr(block, "names_button")
                assert block.page_caption.cget("text") == "1/1"
                assert block.buttons[3].instate(["disabled"]) and block.buttons[4].instate(["disabled"])
                assert bottom <= block.caption.winfo_rooty()
                assert block.caption.master is block.buttons[0].master is block.toolbar
                assert abs(block.caption.winfo_rooty()-block.buttons[0].winfo_rooty()) < block.caption.winfo_height()
                assert block.buttons[-1].winfo_rootx()+block.buttons[-1].winfo_width() <= viewport.canvas.winfo_rootx()+viewport.canvas.winfo_width()
                regular = ttk.Button(window, text="+ 열 추가")
                root.update_idletasks()
                assert block.buttons[0].winfo_reqwidth() < regular.winfo_reqwidth()*0.75
                assert block.buttons[0].winfo_reqheight() < regular.winfo_reqheight()
                regular.destroy()
            table = content.results.table
            # Shared cell padding fits one full result value at the minimum height,
            # and two at normal sizes; remaining rows stay scrollable.
            position = (0 if size == "640x480" else 1, 0)
            renderer = table.renderer
            text_box = renderer.frame.bbox(renderer._painted[position].text)
            canvas = table.viewport.canvas
            assert renderer.frame.winfo_rooty()+text_box[3] <= canvas.winfo_rooty()+canvas.winfo_height(), size
            for button in (content.calculate_button, *content.results.actions.values()):
                assert button.winfo_rooty()+button.winfo_height() <= window.winfo_rooty()+window.winfo_height()
        # A horizontal page stays wide, but never forces the window off-screen.
        assert window.winfo_width() == 640
        assert content.session.run.succeeded == 12
    finally:
        manager.handle.dispose()
        section._frame.destroy()


def test_pair_rectangles_number_only_and_column_identity(root):
    from apps.calculator.ui.sections.iso_iseer_2point_section import IsoIseer2PointSection
    section = IsoIseer2PointSection(root)
    populate(section, contexts()[0])
    section.combination_button.invoke()
    manager = section.combinations
    try:
        content = manager.handle.dialog._adapter
        blocks = content.candidates.blocks
        for key, capacities, powers in (
            ("35_full", "3600\t3700\t3800", "900\t920\t950"),
            ("35_half", "1800\t1850\t1900\t1950\t2000", "400\t410\t420\t430\t440"),
        ):
            table = blocks[key].table
            table.interaction_controller.select((0, 0))
            table.clipboard_clear(); table.clipboard_append(capacities+"\n"+powers)
            table.interaction_controller._paste()
        assert [len(content.session.pools[k]) for k in blocks] == [3, 5]
        # A retained old label is never offered for editing or shown in rankings.
        table = blocks["35_full"].table
        table.restore_snapshot([replace(table.candidates[0], label="이전 이름"), *table.candidates[1:]])
        assert table.row_count() == 2
        assert not table.set_positions_batch({(2, 0): "새 이름"})
        content.calculate_button.invoke()
        pump(root, lambda: content.session.run.status != "running")
        run = content.session.run
        assert run.succeeded == 15
        assert len({result.selections for result in run.results}) == 15
        for result in run.results:
            for key, index in zip(blocks, result.selections):
                table = content.results.table
                assert table.rows[table.identities.index(result.ordinal)][table.headers.index(key)] == f"#{index+1}"
        pinned = run.detail(run.results[0])
        block = blocks["35_full"]
        table = block.table
        ids = [c.id for c in table.candidates]
        half = blocks["35_half"].table.snapshot()
        # A third pasted row cannot create a name row or overwrite other points.
        table.interaction_controller.select((0, 0))
        table.clipboard_clear(); table.clipboard_append("3601\n901\n덮어쓰면 안 됨")
        table.interaction_controller._paste()
        assert table.candidates[0].label == "이전 이름"
        assert table.candidates[0].power == "901"
        assert blocks["35_half"].table.snapshot() == half
        table.interaction_controller._undo_last()
        assert table.candidates[0].capacity == "3600"
        assert [c.id for c in table.candidates] == ids
        # Include/exclude operates on whole columns and retains invalid drafts.
        root.update()
        view = table.grid_table.canvas_view
        x, y, _, _ = view.cell_bbox((-1, 1))
        view.frame.event_generate("<Button-1>", x=x+3, y=y+3)
        assert set(table.interaction_controller.selected_positions()) == {(0, 1), (1, 1)}
        block.toggle()
        table.set_positions_batch({(0, 1): "bad"})
        assert content.calculate_button.instate(["!disabled"])
        assert not content.session.pools["35_full"][1].included
        block.toggle()
        assert content.calculate_button.instate(["disabled"])
        assert "후보 #2" in content.status.cget("text")
        block.remove()
        assert [c.id for c in content.session.pools["35_full"]] == [ids[0], ids[2]]
        assert content.session.stale and run.detail(run.results[0]) == pinned
        # Editing a value does not rebuild the table or reset viewport position.
        root.update()
        canvas = content.candidates.viewport.canvas
        canvas.xview_moveto(0.2); root.update()
        position = canvas.xview()
        table = block.table
        widget = table.grid_table
        table.interaction_controller.select((1, 0))
        table.set_positions_batch({(1, 0): "902"})
        root.update()
        assert table.grid_table is widget
        assert table.interaction_controller.active == (1, 0)
        assert canvas.xview() == position
        saved = dict((key, tuple(pool)) for key, pool in content.session.pools.items())
        manager.handle.dispose(); section.combination_button.invoke()
        assert manager.current.run is run
        assert {k: tuple(v) for k, v in manager.current.pools.items()} == saved
    finally:
        manager.handle.dispose()
        section._frame.destroy()


def test_context_tabs_preserve_window_and_sessions_and_reload_selected_only(root):
    from apps.calculator.ui.sections.iso_iseer_2point_section import IsoIseer2PointSection
    section = IsoIseer2PointSection(root)
    populate(section, contexts()[0])
    section.combination_button.invoke()
    manager = section.combinations
    try:
        shell = manager.handle.dialog
        window = shell.window
        window.geometry("800x720+30+40")
        root.update()
        geometry = window.geometry()
        original = manager.current
        content = shell._adapter
        labels = [content.context_tabs.tab(i, "text") for i in range(2)]
        assert labels == [ctx.profile for ctx in manager.contexts]
        content.candidates.blocks["35_full"].table.set_positions_batch({(0, 1): "3700", (1, 1): "950"})
        content.calculate_button.invoke()
        assert str(content.context_tabs.tab(1, "state")) == "disabled"
        pump(root, lambda: original.run.status != "running")
        run = original.run
        content.context_tabs.select(1)
        root.update()
        assert content.disposed
        assert manager.handle.dialog is shell and shell.window is window
        assert window.geometry() == geometry
        second = manager.current
        assert second is not original and second.run is None
        shell._adapter.candidates.blocks["35_full"].table.set_positions_batch({(0, 0): "4100"})
        second_input = tuple(second.pools["35_full"])
        shell._adapter.context_tabs.select(0)
        root.update()
        assert manager.current is original and original.run is run
        assert len(original.pools["35_full"]) == 2
        assert window.geometry() == geometry
        # Explicit reload consumes current main inputs and resets this tab only.
        section.input_table.set_values_batch({"full_capacity": "3900"})
        shell._adapter.reload_button.invoke()
        root.update()
        assert manager.current.run is None
        assert len(manager.current.pools["35_full"]) == 1
        assert manager.current.pools["35_full"][0].capacity == "3900"
        assert tuple(second.pools["35_full"]) == second_input
        assert manager.sessions[second.context.identity] is second
    finally:
        manager.handle.dispose()
        section._frame.destroy()


def test_result_drag_copy_readonly_selection_and_paging(root):
    from apps.calculator.ui.sections.iso_iseer_2point_section import IsoIseer2PointSection
    section = IsoIseer2PointSection(root)
    populate(section, contexts()[0])
    section.combination_button.invoke()
    manager = section.combinations
    try:
        content = manager.handle.dialog._adapter
        content.session.pools["35_full"] = [Candidate(capacity="3500", power=str(900+i)) for i in range(101)]
        content.calculate()
        pump(root, lambda: content.session.run.status != "running")
        window = manager.handle.dialog.window
        window.geometry("900x800+30+30")
        window.lift()
        root.update()
        table = content.results.table
        controller = table.interaction_controller
        canvas = table.renderer.frame
        def pointer(sequence, position):
            x, y, _, _ = table.renderer.cell_bbox(position)
            canvas.event_generate(sequence, x=x+3, y=y+3,
                                  rootx=canvas.winfo_rootx()+x+3, rooty=canvas.winfo_rooty()+y+3)
        pointer("<Button-1>", (0, 1))
        pointer("<B1-Motion>", (1, 2))
        root.update()
        assert controller.selection_bounds == (0, 1, 1, 2)
        expected = "\n".join("\t".join(row[1:3]) for row in table.rows[:2])
        canvas.focus_force()
        canvas.event_generate("<Control-c>")
        root.update()
        assert table.clipboard_get() == expected
        # Reversed drag and the visible copy action use the same rectangle.
        pointer("<Button-1>", (1, 2))
        pointer("<B1-Motion>", (0, 1))
        content.results.actions["선택 범위 복사"].invoke()
        assert table.clipboard_get() == expected
        before = table.snapshot()
        controller._clear()
        table.clipboard_clear(); table.clipboard_append("9999")
        controller._paste()
        controller._undo_last()
        assert table.snapshot() == before
        table.viewport.canvas.yview_moveto(0.3)
        root.update()
        scroll = table.viewport.canvas.yview()
        content.session.changed()
        content.results.refresh()
        root.update()
        assert controller.selection_bounds == (0, 1, 1, 2)
        assert table.viewport.canvas.yview() == scroll
        assert "재계산 필요" in content.results.caption.cget("text")
        assert table.row_count() == 100
        content.results.move(1)
        root.update()
        assert table.row_count() == 1 and controller.active is None
        assert table.viewport.canvas.yview()[0] == 0
        controller.select((0, 0))
        assert table.selected_ordinal() == content.session.run.ranked()[100][1].ordinal
        content.results.move(-1)
        assert table.row_count() == 100 and controller.active is None
    finally:
        manager.handle.dispose()
        section._frame.destroy()


def test_ten_thousand_wide_results_keep_widgets_and_callbacks_bounded(root):
    from apps.calculator.application.combinations.adapters import StandardAdapter, seed_session
    from apps.calculator.application.combinations.service import start
    from apps.calculator.ui.combinations.results import ResultsPanel
    from .test_service import finish

    adapter = StandardAdapter()
    context = next(ctx for ctx in contexts() if ctx.product == "triple_capacity_northern")
    context = replace(context, values=tuple({**dict(context.values), "low_min_c": "0"}.items()),
                      options=tuple({**dict(context.options), "measured_h2_boost": True}.items()))
    assert sum(p.independent for p in adapter.points(context)) == 9
    session = seed_session(context, adapter)
    key = next(p.key for p in adapter.points(context) if p.independent)
    candidate = session.pools[key][0]
    session.pools[key] = [Candidate(capacity=candidate.capacity, power=candidate.power) for _ in range(10000)]
    run = finish(start(session, adapter))
    assert run.succeeded == 10000
    window = tk.Toplevel(root)
    window.geometry("900x650")
    try:
        panel = ResultsPanel(window, session)
        panel.pack(fill="both", expand=True)
        root.update()
        table = panel.table
        canvas = table.renderer.frame
        first_items = canvas.find_all()
        assert len(first_items) < 600  # Visible area, not all 1,500 result cells.
        assert canvas.winfo_children() == []
        commands = len(root.tk.call("info", "commands"))
        for page in range(1, 100):
            panel.move(1)
            root.update()
            assert table.row_count() == 100
            assert table.renderer.frame is canvas
            assert canvas.find_all() == first_items
            # Check each page, so a regression fails before commands can pile up.
            assert len(root.tk.call("info", "commands")) == commands
            assert table.identities == tuple(range(page*100+1, page*100+101))
        controller = table.interaction_controller
        controller.select((0, 0)); controller.select((1, 2), extend=True)
        panel.copy()
        assert table.clipboard_get() == "\n".join("\t".join(row[:3]) for row in table.rows[:2])
        root.update_idletasks()
        callback_names = set(canvas._tclCommands or ())
        window.destroy()
        root.update()
        assert callback_names.isdisjoint(root.tk.call("info", "commands"))
    finally:
        if window.winfo_exists():
            window.destroy()


def test_inline_en_settings_edit_lock_reopen_and_content_fit(root):
    from apps.calculator.ui.combinations.manager import CombinationManager
    from apps.calculator.ui.table.roles import CellRole
    context = next(c for c in contexts() if c.kind == "en_seer")
    manager = CombinationManager(root, lambda: [context])
    manager.open()
    try:
        shell = manager.handle.dialog
        content = shell._adapter
        root.update()
        # Settings share the candidate viewport; only calculation-context tabs remain.
        assert content.settings.master is content.candidates.viewport.content
        assert content.settings.winfo_ismapped()
        assert not any(isinstance(child, ttk.Notebook) and child is not content.context_tabs
                       for child in content.frame.winfo_children())
        from apps.calculator.ui.window_geometry import capped_window_size
        from apps.calculator.ui.window_measurement import content_size_with_margins
        natural = (content.frame.winfo_reqwidth(), content.frame.winfo_reqheight())
        padded = content_size_with_margins(*natural)
        assert shell._initial_preferred_size == tuple(
            requested - body + fitted
            for requested, body, fitted in zip(shell._initial_requested_size, natural, padded))
        assert (shell.window.winfo_width(), shell.window.winfo_height()) == capped_window_size(
            *shell._initial_preferred_size, root.winfo_screenwidth(), root.winfo_screenheight())
        assert shell._initial_preferred_size[0] < 1120
        table = content.settings.field_tables["p_design_c_w"]
        controller = content.settings.controllers[content.settings.tables.index(table)]
        assert [key for key, _ in table.columns] == ["p_design_c_w", "t_design_c", "cd"]
        controller.select((0, 0))
        table.clipboard_clear(); table.clipboard_append("3600\t35\t0.2")
        controller._paste()
        assert dict(manager.current.context.values)["p_design_c_w"] == "3600"
        assert dict(context.values)["p_design_c_w"] == "3500"
        selector = content.settings.options.selectors["appliance_type"]
        selector.set("cooling_only")
        selector.event_generate("<<ComboboxSelected>>")
        root.update()
        assert dict(manager.current.context.values)["appliance_type"] == "cooling_only"
        content.calculate()
        assert table.cell_role((0, 0)) == CellRole.READONLY
        assert selector.instate(["disabled"])
        controller._undo_last()
        assert table.get_text_values()["p_design_c_w"] == "3600"
        run = content.session.run
        pump(root, lambda: run.status != "running")
        assert run.succeeded == 1
        assert table.cell_role((0, 0)) == CellRole.EDITABLE
        assert selector.instate(["readonly", "!disabled"])
        shell.window.geometry("640x480")
        root.update()
        viewport = content.candidates.viewport
        viewport.canvas.yview_moveto(1)
        root.update()
        assert viewport.canvas.yview()[1] == 1
        assert content.calculate_button.winfo_rooty() < content.results.winfo_rooty()
        assert content.results.winfo_rooty()+content.results.winfo_height() <= shell.window.winfo_rooty()+shell.window.winfo_height()
        manager.handle.dispose()
        manager.open()
        content = manager.handle.dialog._adapter
        assert content.session.run is run
        assert content.settings.field_tables["p_design_c_w"].get_text_values()["p_design_c_w"] == "3600"
        assert content.settings.options.selectors["appliance_type"].get() == "cooling_only"
    finally:
        manager.handle.dispose()


def test_inline_product_controls_preserve_geometry_and_requiredness(root):
    from apps.calculator.ui.combinations.manager import CombinationManager
    from apps.calculator.ui.table.roles import CellRole
    context = next(c for c in contexts() if c.product == "triple_capacity_northern")
    manager = CombinationManager(root, lambda: [context])
    manager.open()
    try:
        shell = manager.handle.dialog
        shell.window.geometry("900x650+50+50")
        root.update()
        geometry = shell.window.geometry()
        content = shell._adapter
        flags = content.settings.options.flag_controls
        assert set(flags) == {"measured_h2_low", "measured_h2_boost", "measured_h3_low"}
        assert flags["measured_h2_low"].instate(["disabled"])
        assert flags["measured_h3_low"].instate(["disabled"])
        table = content.settings.field_tables["low_min_c"]
        table.set_address_values_batch({("value", "low_min_c"): "0"})
        assert content.settings.options.variables["measured_h3_low"].get()
        assert content.candidates.blocks["H3Low"].table is not None
        retained = tuple(content.session.pools["H3Low"])
        selector = content.settings.options.selectors["defrost_mode"]
        selector.set("calculated_from_timing")
        selector.event_generate("<<ComboboxSelected>>")
        root.update()
        assert manager.handle.dialog is shell
        assert shell.window.geometry() == geometry
        content = shell._adapter
        assert dict(content.session.context.options)["defrost_mode"] == "calculated_from_timing"
        assert tuple(content.session.pools["H3Low"]) == retained
        for key, role in (("defrost_factor", CellRole.READONLY), ("defrost_t_test_minutes", CellRole.EDITABLE)):
            table = content.settings.field_tables[key]
            column = [name for name, _ in table.columns].index(key)
            assert table.cell_role((0, column)) == role
        content.settings.options.flag_controls["measured_h2_boost"].invoke()
        root.update()
        assert manager.handle.dialog is shell and shell.window.geometry() == geometry
        assert shell._adapter.candidates.blocks["H2Boost"].table is None
        assert dict(context.options)["measured_h2_boost"] is True
    finally:
        manager.handle.dispose()


def test_m_hspf_demand_defrost_updates_same_tab_and_keeps_snapshot(root):
    from apps.calculator.ui.ahri_m.hspf_section import AhriMHspfSection
    from apps.calculator.ui.table.roles import CellRole
    section = AhriMHspfSection(root)
    populate(section, next(c for c in contexts() if c.kind == "m_hspf"))
    section.combination_button.invoke()
    manager = section.combinations
    try:
        shell = manager.handle.dialog
        content = shell._adapter
        session = content.session
        table = content.settings.field_tables["cd"]
        assert table.columns == section.numeric_table.columns
        assert table.rows == section.numeric_table.rows
        flags = content.settings.options.flag_controls
        assert flags["demand_defrost"].cget("text") == "Demand Defrost"
        assert flags["automatic_cutout"].cget("text") == "Automatic Cutout"
        content.calculate()
        pump(root, lambda: session.run.status != "running")
        original = session.run
        pinned = original.detail(original.results[0])
        pools = {key: tuple(pool) for key, pool in session.pools.items()}
        root.update()
        geometry = shell.window.geometry()
        tab_ids = content.context_tabs.tabs()
        timing_column = [key for key, _ in table.columns].index("defrost_test_minutes")
        for enabled in (True, False, True):
            flags["demand_defrost"].invoke()
            root.update()
            assert manager.current is session and shell._adapter is content
            assert shell.window.geometry() == geometry
            assert content.context_tabs.tabs() == tab_ids and len(tab_ids) == 1
            assert len(manager.sessions) == len(manager.contexts) == 1
            assert dict(session.context.options)["demand_defrost"] is enabled
            assert table.cell_role((0, timing_column)) == (CellRole.EDITABLE if enabled else CellRole.READONLY)
            assert session.run is original and session.stale
            assert original.detail(original.results[0]) == pinned
            assert {key: tuple(pool) for key, pool in session.pools.items()} == pools
        assert "재계산 필요" in content.results.caption.cget("text")
        table.set_address_values_batch({("value", "defrost_test_minutes"): "150"})
        content.calculate()
        pump(root, lambda: session.run.status != "running")
        assert session.run is not original and session.run.succeeded == 1 and not session.stale
        expected = session.run.detail(session.run.results[0])["f_def"]
        assert table.static_text(("value", "defrost_credit")) == f"{expected:.3f}"
        manager.handle.dispose()
        section.combination_button.invoke()
        content = manager.handle.dialog._adapter
        assert manager.current is session and len(content.context_tabs.tabs()) == 1
        assert dict(session.context.options)["demand_defrost"] is True
        assert content.settings.field_tables["cd"].get_text_values()["defrost_test_minutes"] == "150"
        content.reload_button.invoke()
        assert dict(manager.current.context.options)["demand_defrost"] is False
        assert manager.current.run is None and len(manager.contexts) == 1
        assert not section.demand_defrost_var.get()
    finally:
        manager.handle.dispose()
        section._frame.destroy()


def test_candidate_controller_paging_undo_stale_cancel_and_shutdown(root,tmp_path,monkeypatch):
    from apps.calculator.ui.sections.iso_iseer_2point_section import IsoIseer2PointSection
    try:
        section=IsoIseer2PointSection(root)
        populate(section,contexts()[0])
        section.combination_button.invoke()
        manager=section.combinations; content=manager.handle.dialog._adapter
        panel=content.candidates.blocks["35_full"]; table=panel.table;controller=table.interaction_controller
        controller.select((0,0))
        table.clipboard_clear();table.clipboard_append("3600\t3700\n900\t950")
        controller._paste()
        assert len(content.session.pools["35_full"])==2
        first_id=content.session.pools["35_full"][0].id
        controller._undo_last()
        assert len(content.session.pools["35_full"])==1
        controller._paste()
        assert content.session.pools["35_full"][0].id == first_id
        controller.select((0,0));controller.select((1,1),extend=True)
        controller._copy()
        assert table.clipboard_get() == "3600\t3700\n900\t950"
        controller.select((0,0));controller.select((1,1),extend=True)
        controller._clear();controller._undo_last()
        assert content.session.pools["35_full"][1].power=="950"
        content.calculate_button.invoke();run=content.session.run
        frozen=panel.table.snapshot()
        panel.table.interaction_controller._undo_last()
        assert panel.table.snapshot()==frozen
        pump(root,lambda:run.status!="running")
        assert run.succeeded==2
        prior=run.detail(run.results[0])
        panel.table.set_positions_batch({(1,0):"1100"})
        assert content.session.stale and run.detail(run.results[0])==prior
        panel.table.interaction_controller.select((0,0));panel.toggle()
        assert not content.session.pools["35_full"][0].included
        panel.table.select_column(1);panel.remove()
        assert len(content.session.pools["35_full"])==1
        # Large legal pool is retained outside widgets; input projection stays bounded.
        session=content.session
        manager.handle.dispose()
        session.pools["35_full"]=[Candidate(label=f"시험 {i}",capacity="3600",power="900") for i in range(10000)]
        session.changed()
        section.combination_button.invoke();content=manager.handle.dialog._adapter
        panel=content.candidates.blocks["35_full"]
        assert panel.table.column_count()==100 and panel.table.row_count()==2
        manager.handle.dialog.window.geometry("640x590")
        root.update()
        assert panel.page_caption.cget("text") == "1/100"
        assert panel.buttons[3].instate(["disabled"]) and panel.buttons[4].instate(["!disabled"])
        assert panel.toolbar.winfo_reqwidth() <= content.candidates.viewport.canvas.winfo_width()
        assert "붙여넣기" in content.candidates.paste_hint.cget("text")
        other=content.candidates.blocks["35_half"]
        other_snapshot=other.table.snapshot()
        panel.move(1)
        assert panel.page==1 and panel.table.interaction_controller._undo.pop() is None
        assert panel.page_caption.cget("text") == "2/100"
        assert panel.buttons[3].instate(["!disabled"])
        assert other.table.snapshot()==other_snapshot and other.page==0
        content.calculate_button.invoke();run=session.run
        heartbeats=[]
        root.after(5,lambda:heartbeats.append(run.processed))
        root.after(30,content.cancel_button.invoke)
        pump(root,lambda:run.status!="running")
        assert heartbeats and 0<run.processed<10000 and run.status=="cancelled"
        assert content.results.table.row_count()<=100
        content.results.table.interaction_controller.select((0, 0))
        content.results.table.interaction_controller.select((0, 2), extend=True)
        content.results.copy()
        assert "CSPF" in content.results.clipboard_get()
        # Paste overflow never crosses the candidate page or another point.
        table=panel.table
        table.interaction_controller.select((0,99))
        table.clipboard_clear();table.clipboard_append("3601\t9999\n901\t9999")
        table.interaction_controller._paste()
        assert table.column_count()==100
        assert session.pools["35_full"][199].capacity=="3601"
        assert session.pools["35_full"][200].capacity=="3600"
        filename=tmp_path/"partial.csv"
        picker_args=[]
        def choose(**kw):
            picker_args.append(kw)
            return str(filename)
        monkeypatch.setattr("apps.calculator.ui.table_csv_export.filedialog.asksaveasfilename",choose)
        content.results.export()
        original_bytes=filename.read_bytes()
        monkeypatch.setattr("apps.calculator.ui.table_csv_export.filedialog.asksaveasfilename",lambda **kw:"")
        content.results.export()
        assert filename.read_bytes()==original_bytes
        failures=[]
        monkeypatch.setattr("apps.calculator.ui.combinations.results.messagebox.showerror",lambda *args,**kwargs:failures.append(args))
        def denied(*args,**kwargs):
            raise PermissionError("permission denied")
        monkeypatch.setattr("apps.calculator.ui.table_csv_export.export_table_to_csv",denied)
        content.results.export()
        assert failures
        with filename.open(encoding="utf-8-sig",newline="") as handle:
            rows=list(csv.DictReader(handle))
        assert len(rows)==run.processed and "partial" not in rows[0]
        assert picker_args[0]["initialfile"] == "calculator_combinations_partial_stale.csv"
        content.calculate_button.invoke();next_run=session.run
        manager.handle.dispose()
        assert next_run.status=="cancelled"
        section.combination_button.invoke()
        assert manager.current.run is next_run
        manager.handle.dialog._adapter.calculate_button.invoke()
        shutdown_run=session.run
    finally:
        root.destroy()
    assert shutdown_run.status=="cancelled"
