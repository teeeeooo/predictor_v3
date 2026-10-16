"""Batch adapters retain transactions and one editor as the logical grid grows."""
import tkinter as tk

import pytest

from apps.calculator.ui.batch.case_table import BatchCaseTable
from apps.calculator.ui.batch.matrix_table import BatchMatrixTable
from apps.calculator.ui.batch.matrix_models import HONG_KONG_CSPF_MATRIX_SPEC, FULL_CAPACITY
from apps.calculator.ui.batch.models import BatchColumnRole, BatchColumnSpec, BatchProfileSpec
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.theme import apply_calculator_theme
from tests.helpers.tk import destroy_tk_root


@pytest.fixture
def root():
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(str(exc))
    apply_calculator_theme(root)
    root.geometry("480x260")
    yield root
    destroy_tk_root(root)


def test_case_paste_growth_undo_and_readonly_results_keep_editor(root):
    spec = BatchProfileSpec(profile_key="canvas", title="Cases", columns=(
        BatchColumnSpec("input", "Input", BatchColumnRole.INPUT),
        BatchColumnSpec("result", "Result", BatchColumnRole.RESULT),
    ), default_rows=({},))
    changed = []
    table = BatchCaseTable(root, spec, values_changed_callback=lambda: changed.append(True))
    table.pack(fill="both", expand=True)
    ctrl, view = table.interaction_controller, table.canvas_view
    root.update()
    ctrl.select((0, 0))
    editor = table.focus_widget((0, 0))
    table.clipboard_clear()
    table.clipboard_append("10\t999\n20\t888\n30\t777")
    ctrl._paste()
    root.update()
    assert len(changed) == 1
    assert table.input_rows() == [{"input": "10"}, {"input": "20"}, {"input": "30"}]
    assert all(row["result"] == "" for row in table.model.rows)
    assert view.editor.entry is editor
    table.set_row_results(1, {"result": "40"})
    assert table.text_at_position((1, 1)) == "40"
    assert table.focus_widget((1, 1)) is view.frame
    assert editor.winfo_manager() == ""
    ctrl._undo_last()
    root.update()
    assert table.row_count() == 1
    assert table.text_at_position((0, 0)) == ""
    assert view.editor.entry is editor
    assert len(changed) == 2


def test_matrix_scroll_resize_and_shape_changes_keep_draft_and_bounded_items(root):
    table = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    ctrl = TkTableController(table)
    table.interaction_controller = ctrl
    table.pack(fill="both", expand=True)
    table.restore_snapshot([{FULL_CAPACITY: str(1000+i)} for i in range(200)])
    root.update()
    view = table.canvas_view
    editor = view.editor.entry
    assert table.row_count() == 400
    assert len(view.painted_positions) < 150
    assert int(view.frame.cget("height")) == view.layout.height(400)
    ctrl.select((398, 3))
    ctrl._enter_edit_mode((398, 3))
    editor.focus_force()
    root.update()
    assert editor.get() == "1199"
    editor.delete(0, "end")
    editor.insert(0, "draft")
    root.geometry("550x300")
    root.update()
    assert root.focus_get() is editor
    assert editor.get() == "draft"
    assert table.cases[-1][FULL_CAPACITY] == "draft"
    assert (398, 3) in view.painted_positions
    assert len(view.frame.find_all()) < 400
    editor.event_generate("<Escape>")
    root.update()
    assert table.cases[-1][FULL_CAPACITY] == "1199"
    table.restore_snapshot([{}])
    root.update()
    assert table.row_count() == 2
    assert view.editor.entry is editor
    assert ctrl.active is None
    assert int(view.frame.cget("height")) == view.layout.height(2)
    viewport = table.viewport_frame
    table.destroy()
    root.update()
    assert view._pending is None
    assert not viewport._view_observers
