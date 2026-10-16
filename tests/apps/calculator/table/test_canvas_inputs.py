"""Editable Canvas parity: real Entry editing, logical transactions and lifetime."""
import tkinter as tk

import pytest

from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.theme import apply_calculator_theme


@pytest.fixture(scope="module")
def root():
    root = tk.Tk()
    root.withdraw()
    apply_calculator_theme(root)
    errors = []
    root.report_callback_exception = lambda *args: errors.append(args)
    yield root
    root.destroy()
    assert not errors


def make_table(parent, **kwargs):
    return MetricInputTable(parent, columns=(("full", "Full"), ("half", "Half")),
        rows=(("capacity", "Capacity"), ("power", "Power"), ("cop", "COP")),
        editable_cells={(row, col): f"{row}_{col}" for row in ("capacity", "power") for col in ("full", "half")},
        section_break_before_rows={"cop"}, **kwargs)


def test_native_and_drawn_natural_geometry_and_responsive_editor(root):
    window = tk.Toplevel(root)
    try:
        native = make_table(window, rendering="native")
        table = make_table(window, rendering="canvas", layout_policy="responsive")
        native.pack()
        table.pack(fill="x")
        controller = TkTableController(table)
        root.update()
        assert (table.winfo_reqwidth(), table.winfo_reqheight()) == (native.winfo_reqwidth(), native.winfo_reqheight())
        controller.select((0, 0))
        entry = table.focus_widget((0, 0))
        entry.focus_force()
        controller._enter_edit_mode((0, 0))
        entry.insert("end", "한글 draft")
        root.update()
        before = entry.winfo_width()
        window.geometry(f"{window.winfo_width()+200}x{window.winfo_height()}")
        root.update()
        assert entry.winfo_width() > before
        assert entry.get() == "한글 draft" and controller._mode == "edit"
        assert root.focus_get() is entry
        controller._escape()
        assert table.get_text_values()["capacity_full"] == ""
        assert len(table.table_frame.winfo_children()) == 1
    finally:
        window.destroy()
        root.update()


def test_replace_partial_edit_cancel_focus_commit_and_undo(root):
    window = tk.Toplevel(root)
    try:
        table = make_table(window, rendering="canvas")
        table.pack()
        table.set_value("capacity_full", "1234")
        controller = TkTableController(table)
        controller.select((0, 0))
        entry = table.focus_widget((0, 0))
        root.update()
        entry.focus_force()
        root.update()
        entry.event_generate("<KeyPress-a>")
        entry.event_generate("<KeyPress-b>")
        assert table.get_text_values()["capacity_full"] == "ab"
        entry.event_generate("<Escape>")
        assert entry.get() == "1234"
        entry.event_generate("<F2>")
        entry.icursor(2)
        entry.insert("insert", "X")
        entry.event_generate("<Return>")
        root.update()
        assert controller.active == (1, 0)
        assert table.focus_widget((1, 0)) is entry
        assert table.get_text_values()["capacity_full"] == "12X34"
        controller._undo_last()
        assert table.get_text_values()["capacity_full"] == "1234"
        controller._edit_f2()
        entry.insert("end", "900")
        table.canvas_view.frame.focus_force()
        root.update()
        controller._undo_last()
        assert table.get_text_values()["power_full"] == ""
    finally:
        window.destroy()
        root.update()


def test_paste_clear_undo_readonly_and_model_updates_do_not_rebuild_editor(root):
    window = tk.Toplevel(root)
    try:
        changes = []
        table = make_table(window, rendering="canvas", values_changed_callback=lambda: changes.append(table.snapshot()))
        table.pack()
        controller = TkTableController(table)
        table.set_readonly_addresses({("power", "half")}, display_values={("power", "half"): "AUTO"})
        controller.select((0, 0))
        entry = table.focus_widget((0, 0))
        table.clipboard_clear()
        table.clipboard_append("3600\tbad\n900\t888\nnot an input\t999")
        controller._paste()
        root.update()
        assert len(changes) == 1
        assert table.snapshot() == {"capacity_full": "3600", "capacity_half": "bad", "power_full": "900", "power_half": ""}
        assert table.display_text_at_position((1, 1)) == "AUTO"
        view = table.canvas_view
        x, y, _, _ = view.cell_bbox((0, 0))
        view.frame.event_generate("<Button-1>", x=x+3, y=y+3)
        x, y, _, _ = view.cell_bbox((1, 1), root=True)
        entry.event_generate("<B1-Motion>", rootx=x+3, rooty=y+3)
        assert controller.selection_bounds == (0, 1, 0, 1)
        controller._clear()
        assert len(changes) == 2
        controller._undo_last()
        assert table.snapshot()["capacity_half"] == "bad"
        controller._undo_last()
        assert all(value == "" for value in table.snapshot().values())
        assert table.focus_widget((0, 1)) is entry
        table.set_value("capacity_half", "edited externally")
        assert entry.get() == "edited externally"
        table.set_readonly_addresses({("capacity", "half")})
        assert not entry.winfo_manager()
        assert table.focus_widget((0, 1)) is table.canvas_view.frame
        names = set(entry._tclCommands or ())
        table.canvas_view.schedule()
        window.destroy()
        root.update()
        assert names.isdisjoint(root.tk.call("info", "commands"))
    finally:
        if window.winfo_exists():
            window.destroy()
