"""Native checks of geometry, pooled rendering and logical interaction."""
import tkinter as tk

import pytest

from apps.calculator.ui.table.canvas_result_grid import CanvasResultGrid
from apps.calculator.ui.table.compact_result_grid import CompactResultGrid
from apps.calculator.ui.table.visual_policy import SemanticTone
from apps.calculator.ui.combinations.result_table import ResultPageTable


@pytest.fixture(scope="module")
def root():
    root = tk.Tk()
    root.withdraw()
    errors = []
    root.report_callback_exception = lambda *args: errors.append(args)
    yield root
    root.destroy()
    assert not errors


def test_natural_footprint_matches_native_grid_and_clear_is_independent(root):
    window = tk.Toplevel(root)
    try:
        options = dict(headers=("Region/Profile", "EER Full", "CSPF"), column_widths=(18, 12, 12))
        native = CompactResultGrid(window, **options)
        drawn = CanvasResultGrid(window, **options)
        for grid in (native, drawn):
            grid.pack()
            grid.set_rows((("ISO 16358-1", "4.2", "6.12"), ("India ISEER", "4.2", "6.14")))
        root.update()
        assert drawn.logical_data() == native.logical_data()
        assert drawn.as_tsv() == native.as_tsv()
        assert (drawn.frame.winfo_reqwidth(), drawn.frame.winfo_reqheight()) == (
            native.frame.winfo_reqwidth(), native.frame.winfo_reqheight())
        assert len(drawn.painted_positions) == 9
        drawn.set_rows((("Second", None, "2"),))
        drawn.copy()
        assert drawn.frame.clipboard_get() == "Region/Profile\tEER Full\tCSPF\nSecond\t\t2"
        drawn.clear()
        root.update()
        assert drawn.painted_positions == {(-1, col) for col in range(3)}
        assert len(native.rows) == 2
    finally:
        window.destroy()


def test_text_clipping_preserves_full_copy_and_semantic_paint(root):
    window = tk.Toplevel(root)
    try:
        grid = CanvasResultGrid(window, headers=("긴 시험점 이름 / Long name", "결과"), column_widths=(8, 8))
        grid.pack()
        value = "매우 긴 시험점 이름 / measurement 1234567890"
        grid.set_rows(((value, "6.12345678901234567890"),), tones={(0, 1): SemanticTone.CALCULATED})
        root.update()
        for position, painted in grid._painted.items():
            text = grid.frame.itemcget(painted.text, "text")
            x1, _, x2, _ = grid.cell_bbox(position)
            bounds = grid.frame.bbox(painted.text)
            assert x1 <= bounds[0] <= bounds[2] <= x2
            assert grid.frame.itemcget(painted.background, "fill") == grid.cell_background(position)
            if position == (0, 0):
                assert text.endswith("…") and text != value
                assert grid.frame.itemcget(painted.text, "anchor") == "w"
        grid.copy()
        assert value in grid.frame.clipboard_get()
        assert "6.12345678901234567890" in grid.frame.clipboard_get()
    finally:
        window.destroy()


def test_selection_only_repaints_changed_cells_and_coalesces_updates(root, monkeypatch):
    window = tk.Toplevel(root)
    try:
        grid = CanvasResultGrid(window, headers=("Name", "Value"))
        grid.pack()
        grid.set_rows((("A", "1"), ("B", "2")))
        root.update()
        items = grid.frame.find_all()
        changed = []
        configure = grid.frame.itemconfigure
        monkeypatch.setattr(grid.frame, "itemconfigure", lambda *a, **kw: (changed.append(a[0]), configure(*a, **kw))[1])
        grid.set_selection((0, 0, 0, 1), (0, 1))
        pending = grid._pending
        grid.schedule()
        grid.schedule()
        assert grid._pending == pending
        root.update()
        assert len(changed) == 4  # Two cell pairs; headers/unselected row untouched.
        assert grid.frame.find_all() == items
        assert grid.frame.itemcget(grid._painted[(0, 1)].background, "fill") == grid.policy.overlay_background("active")
        changed.clear()
        grid.schedule()
        root.update()
        assert changed == []
        grid.schedule()
    finally:
        window.destroy()
        root.update()  # A pending draw cannot outlive the Canvas.


def test_canvas_keyboard_shift_click_copy_and_readonly_behaviour(root):
    window = tk.Toplevel(root)
    window.geometry("650x430")
    try:
        table = ResultPageTable(window)
        table.pack(fill="both", expand=True)
        rows = tuple(tuple(f"{row}:{col}" for col in range(15)) for row in range(100))
        table.set_page(tuple(f"H{col}" for col in range(15)), rows, tuple(range(100)), "run")
        root.update()
        grid, controller = table.renderer, table.interaction_controller
        canvas = grid.frame
        canvas.focus_force()
        controller.select((0, 0))
        for key, expected in (("Tab", (0, 1)), ("Return", (1, 1)), ("Left", (1, 0)),
                              ("Shift-Return", (0, 0)), ("Right", (0, 1)), ("Shift-Tab", (0, 0))):
            canvas.event_generate(f"<{key}>")
            root.update()
            assert controller.active == expected
            assert root.focus_get() is canvas
        x, y, _, _ = grid.cell_bbox((1, 2))
        canvas.event_generate("<Button-1>", state=1, x=x+3, y=y+3,
                              rootx=canvas.winfo_rootx()+x+3, rooty=canvas.winfo_rooty()+y+3)
        root.update()
        assert controller.selection_bounds == (0, 1, 0, 2)
        canvas.event_generate("<Control-c>")
        assert table.clipboard_get() == "0:0\t0:1\t0:2\n1:0\t1:1\t1:2"
        for key in ("Delete", "BackSpace", "Control-v", "Control-z", "F2", "a", "Escape"):
            canvas.event_generate(f"<{key}>")
        assert table.snapshot() == rows
        # Selection survives scrolling, and copies full offscreen logical data.
        table.viewport.canvas.xview_moveto(1)
        table.viewport.canvas.yview_moveto(1)
        root.update()
        canvas.event_generate("<Command-c>")
        assert table.clipboard_get() == "0:0\t0:1\t0:2\n1:0\t1:1\t1:2"
        # A drag outside the viewport must not select a clipped cell underneath.
        bounds = controller.selection_bounds
        canvas.event_generate("<B1-Motion>", rootx=window.winfo_rootx()-20, rooty=window.winfo_rooty()-20)
        assert controller.selection_bounds == bounds
        # Header schema replacement drops old callbacks and viewport subscribers.
        old_commands = set(canvas._tclCommands or ())
        table.set_page(("X", "Y"), (("A", "B"),), (100,), "next")
        root.update()
        assert controller.active is None
        assert old_commands.isdisjoint(root.tk.call("info", "commands"))
        assert len(table.viewport._view_observers) == 1
    finally:
        window.destroy()
        root.update()
