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


def test_candidate_viewport_remains_useful_when_resized(root):
    from apps.calculator.ui.sections.iso_iseer_2point_section import IsoIseer2PointSection
    section = IsoIseer2PointSection(root)
    populate(section, contexts()[0])
    section.combination_button.invoke()
    manager = section.combinations
    try:
        content = manager.handle.dialog._adapter
        window = manager.handle.dialog.window
        table = content.candidates.table
        table.set_text_rows([dict(label=f"시험 {i}", capacity="3600", power="900") for i in range(12)])
        content.calculate_button.invoke()
        pump(root, lambda: content.session.run.status != "running")
        for size, visible_rows in (("640x590", 5), ("800x720", 8), ("640x480", 3)):
            window.geometry(size)
            root.update()
            canvas = table.viewport_frame.canvas
            header_height = table.table_frame.grid_bbox(0, 0, table.column_count(), 0)[3]
            row_height = table.cell_frame((0, 1)).winfo_height()
            assert canvas.winfo_height() >= header_height + visible_rows * row_height
            # The ranking and actions must remain usable alongside input.
            tree = content.results.tree
            assert tree.bbox(tree.get_children()[1]), size
            for button in (content.calculate_button, *content.results.actions.values()):
                assert button.winfo_rooty() + button.winfo_height() <= window.winfo_rooty() + window.winfo_height()
        assert len(content.session.pools["35_full"]) == 12
        assert content.session.run.succeeded == 12
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
        panel=content.candidates; table=panel.table;controller=table.interaction_controller
        controller.select((0,1))
        table.clipboard_clear();table.clipboard_append("시험 A\t3600\t900\n시험 B\t3700\t950")
        controller._paste()
        assert len(content.session.pools["35_full"])==2
        ids=[c.id for c in content.session.pools["35_full"]]
        controller._undo_last()
        assert len(content.session.pools["35_full"])==1
        controller._paste()
        controller.select((0,0));controller._clear()
        assert content.session.pools["35_full"][0].included
        controller.select((0,1));controller.select((1,3),extend=True)
        controller._clear();controller._undo_last()
        assert content.session.pools["35_full"][1].power=="950"
        content.calculate_button.invoke();run=content.session.run
        frozen=panel.table.snapshot()
        panel.table.interaction_controller._undo_last()
        assert panel.table.snapshot()==frozen
        pump(root,lambda:run.status!="running")
        assert run.succeeded==2
        prior=run.detail(run.results[0])
        panel.table.set_positions_batch({(0,3):"1100"})
        assert content.session.stale and run.detail(run.results[0])==prior
        panel.table.interaction_controller.select((0,0));panel.toggle()
        assert not content.session.pools["35_full"][0].included
        panel.table.interaction_controller.select((1,0));panel.remove()
        assert len(content.session.pools["35_full"])==1
        # Large legal pool is retained outside widgets; input projection stays bounded.
        session=content.session
        manager.handle.dispose()
        session.pools["35_full"]=[Candidate(label=f"시험 {i}",capacity="3600",power="900") for i in range(10000)]
        session.changed()
        section.combination_button.invoke();content=manager.handle.dialog._adapter
        assert content.candidates.table.row_count()==100
        content.candidates.move(1)
        assert content.candidates.page==1 and content.candidates.table.interaction_controller._undo.pop() is None
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
        table=content.candidates.table
        table.interaction_controller.select((99,2))
        table.clipboard_clear();table.clipboard_append("3601\t901\n9999\t9999")
        table.interaction_controller._paste()
        assert table.row_count()==100
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
