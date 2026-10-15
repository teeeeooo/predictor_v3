"""Actual CalculatorTkApp → section action → shared dialog integration."""
import csv
from dataclasses import replace
import time
import tkinter as tk
import pytest

from apps.calculator.ui.calculator_app import CalculatorTkApp
from apps.calculator.ui.metric_input_table import MetricInputTable
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
            if content.common is not None:
                count=content.common.row_count()
                content.common.ensure_row_count(count+1)
                assert content.common.row_count()==count
            else:
                assert not content.common_keys
            assert content.calculate_button.instate(["!disabled"]), (context,content.status.cget("text"))
            content.calculate_button.invoke()
            run=content.session.run
            assert run.status=="running" and run.processed==0
            pump(root,lambda:run.status!="running")
            assert run.succeeded==1, (context,run.results)
            assert content.adapter.project(run.snapshot.context,run.detail(run.results[0]))==run.results[0].score
            if context.product == "triple_capacity_northern":
                # A real common-setting edit changes the active point policy.
                block=content.candidates.blocks["H3Low"]
                assert block.table is None
                retained=tuple(content.session.pools["H3Low"])
                row=content.common_keys.index("low_min_c")
                original=content.common.text_at_position((row,1))
                content.common.set_positions_batch({(row,1): "0"})
                assert block.table is not None
                assert tuple(content.session.pools["H3Low"])==retained
                content.common.set_positions_batch({(row,1): original})
                assert block.table is None
                assert tuple(content.session.pools["H3Low"])==retained
                root.update()
                viewport=content.candidates.viewport
                assert viewport.vertical_overflow_delta()>0
                viewport.canvas.yview_moveto(1.0)
                root.update()
                assert viewport.canvas.yview()[1]==1.0
            content.results.tree.selection_set("1")
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
            assert len(rows)==1 and rows[0]["run_id"]==run.snapshot.id
            manager.handle.dispose()
            section.combination_button.invoke()
            assert manager.current.run is run
            manager.handle.dispose()
            checked.append(context)
        # Measurement mode changes use separate sessions and never relabel old results.
        manager=sections["hspf2"].combinations
        manager.open()
        original=manager.current
        content=manager.handle.dialog._adapter
        button=next(w for w in content.options_panel.controls if w.cget("text")=="H2 BOOST 실측")
        button.invoke()
        assert manager.current is not original
        assert manager.current.run is None
        assert sum(p.independent for p in manager.adapter.points(manager.current.context))==7
        manager.select(next(i for i,c in enumerate(manager.contexts) if c.identity==original.context.identity))
        assert manager.current is original and manager.current.run is not None
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
            assert first.table.cell_frame((1, 0)).winfo_height() > 1
            # Both rows fit inside each block; only the outer viewport scrolls.
            for block in blocks.values():
                bottom = block.table.cell_frame((1, 0))
                assert bottom.winfo_rooty()+bottom.winfo_height() <= block.winfo_rooty()+block.winfo_height()
            tree = content.results.tree
            assert tree.bbox(tree.get_children()[1]), size
            for button in (content.calculate_button, *content.results.actions.values()):
                assert button.winfo_rooty()+button.winfo_height() <= window.winfo_rooty()+window.winfo_height()
        # A horizontal page stays wide, but never forces the window off-screen.
        assert window.winfo_width() == 640
        assert content.session.run.succeeded == 12
    finally:
        manager.handle.dispose()
        section._frame.destroy()


def test_pair_rectangles_metadata_and_column_identity(root):
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
        content.calculate_button.invoke()
        pump(root, lambda: content.session.run.status != "running")
        run = content.session.run
        assert run.succeeded == 15
        assert len({result.selections for result in run.results}) == 15
        for result in run.results:
            for key, index in zip(blocks, result.selections):
                assert content.results.tree.set(str(result.ordinal), key) == f"#{index+1}"
        pinned = run.detail(run.results[0])
        block = blocks["35_full"]
        table = block.table
        ids = [c.id for c in table.candidates]
        half = blocks["35_half"].table.snapshot()
        # Metadata remains optional and numeric overflow cannot overwrite it.
        block.names_var.set(True); block.show_names()
        table.set_positions_batch({(2, 0): "원본 시험"})
        table.interaction_controller.select((0, 0))
        table.clipboard_clear(); table.clipboard_append("3601\n901\n덮어쓰면 안 됨")
        table.interaction_controller._paste()
        assert table.candidates[0].label == "원본 시험"
        assert table.candidates[0].power == "901"
        assert blocks["35_half"].table.snapshot() == half
        table.interaction_controller._undo_last()
        assert table.candidates[0].capacity == "3600"
        assert [c.id for c in table.candidates] == ids
        # Include/exclude operates on whole columns and retains invalid drafts.
        table.select_column(1)
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
        other=content.candidates.blocks["35_half"]
        other_snapshot=other.table.snapshot()
        panel.move(1)
        assert panel.page==1 and panel.table.interaction_controller._undo.pop() is None
        assert other.table.snapshot()==other_snapshot and other.page==0
        content.calculate_button.invoke();run=session.run
        heartbeats=[]
        root.after(5,lambda:heartbeats.append(run.processed))
        root.after(30,content.cancel_button.invoke)
        pump(root,lambda:run.status!="running")
        assert heartbeats and 0<run.processed<10000 and run.status=="cancelled"
        assert len(content.results.tree.get_children())<=100
        content.results.tree.selection_set(content.results.tree.get_children()[0])
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
        monkeypatch.setattr("apps.calculator.ui.table_csv_export.filedialog.asksaveasfilename",lambda **kw:str(filename))
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
        assert len(rows)==run.processed and all(row["partial"]=="True" for row in rows)
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
