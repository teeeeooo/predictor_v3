"""Native Tk regressions for bounded drawing and combination resize targets."""
import tkinter as tk

import pytest

from apps.calculator.application.combinations.adapters import seed_session
from apps.calculator.application.combinations.models import Candidate
from apps.calculator.ui.combinations.manager import CombinationManager
from apps.calculator.ui.combinations.result_table import ResultPageTable
from .seeds import contexts


@pytest.fixture(scope="module")
def root():
    root = tk.Tk()
    root.withdraw()
    errors = []
    root.report_callback_exception = lambda *args: errors.append(args)
    yield root
    root.destroy()
    assert not errors


def open_iso(root, count=1):
    context = contexts()[0]
    manager = CombinationManager(root, lambda: [context])
    session = seed_session(context, manager.adapter)
    session.pools["35_full"] = [Candidate(capacity="3600", power="900") for _ in range(count)]
    manager.sessions[context.identity] = session
    manager.open()
    return manager


def test_result_scroll_resize_and_short_page_preserve_extent_and_data(root):
    window = tk.Toplevel(root)
    window.geometry("650x430")
    try:
        table = ResultPageTable(window)
        table.pack(fill="both", expand=True)
        headers = tuple(f"시험점 {column}" for column in range(15))
        rows = tuple(tuple(f"{row}:{column}" for column in range(15)) for row in range(100))
        table.set_page(headers, rows, tuple(range(100)), "run")
        root.update()
        grid = table.renderer.frame
        natural_size = (grid.winfo_reqwidth(), grid.winfo_reqheight())
        first, last = (0, 0), (99, 14)
        assert first in table.renderer.painted_positions and last not in table.renderer.painted_positions
        assert len(table.renderer.painted_positions) < 200
        assert grid.winfo_children() == []
        canvas = table.viewport.canvas
        canvas.xview_moveto(1)
        canvas.yview_moveto(1)
        root.update()
        assert last in table.renderer.painted_positions and first not in table.renderer.painted_positions
        assert canvas.xview()[1] == canvas.yview()[1] == 1
        for size in ("800x550", "650x430", "900x600"):
            window.geometry(size)
            root.update()
            assert (grid.winfo_reqwidth(), grid.winfo_reqheight()) == natural_size
            canvas.xview_moveto(1)
            canvas.yview_moveto(1)
            root.update()
            assert last in table.renderer.painted_positions
            assert table.snapshot() == rows
        # Keyboard navigation reveals a logical result and focuses the Canvas.
        table.interaction_controller.select((0, 1))
        table.interaction_controller._arrow("left")
        root.update()
        assert first in table.renderer.painted_positions
        x1, y1, x2, y2 = table.renderer.cell_bbox(first, root=True)
        assert x1 >= canvas.winfo_rootx()
        assert y1 >= canvas.winfo_rooty()
        assert x2 <= canvas.winfo_rootx() + canvas.winfo_width()
        assert y2 <= canvas.winfo_rooty() + canvas.winfo_height()
        table.set_page(headers, rows[:1], (100,), "run")
        root.update()
        assert grid.winfo_reqheight() < natural_size[1] / 10
        assert canvas.yview() == (0, 1)
        assert table.snapshot() == rows[:1]
        # Closing with a queued visibility update must cancel the owned callback.
        table.renderer.schedule()
    finally:
        window.destroy()
        root.update()


def test_candidate_scrolling_keeps_edit_and_keyboard_reveals_hidden_column(root):
    manager = open_iso(root, 100)
    try:
        window = manager.handle.dialog.window
        window.geometry("640x590")
        root.update()
        content = manager.handle.dialog._adapter
        table = content.candidates.blocks["35_full"].table
        controller = table.interaction_controller
        entry = table.focus_widget((0, 0))
        controller.select((0, 0))
        entry.focus_force()
        root.update()
        controller._enter_edit_mode((0, 0))
        entry.insert("end", "7")
        snapshot, revision = table.snapshot(), content.session.revision
        canvas = content.candidates.viewport.canvas
        canvas.xview_moveto(1)
        window.geometry("760x650")
        root.update()
        assert entry.winfo_manager() == "place"
        assert root.focus_get() is entry
        assert controller._mode == "edit"
        assert table.snapshot() == snapshot and content.session.revision == revision
        controller._escape()
        controller.select((1, 98))
        controller._arrow("right")
        root.update()
        target = table.focus_widget((1, 99))
        assert target is entry
        assert controller.active == (1, 99)
        assert root.focus_get() is target and target.winfo_ismapped()
        assert target.winfo_rootx() >= canvas.winfo_rootx()
        assert target.winfo_rootx() + target.winfo_width() <= canvas.winfo_rootx() + canvas.winfo_width()
        assert content.session.pools["35_full"][0].capacity == "3600"
    finally:
        manager.handle.dispose()
        root.update()


def test_combination_edge_hit_areas_drag_axes_and_minimum_size(root):
    manager = open_iso(root)
    try:
        shell = manager.handle.dialog
        window = shell.window
        window.geometry("800x650+90+90")
        root.update()
        origin = (window.winfo_x(), window.winfo_y())
        for name, cursor, dx, dy in (
            ("bottom", "sb_v_double_arrow", 0, 40),
            ("right", "sb_h_double_arrow", 40, 0),
            ("corner", "bottom_right_corner", 20, 20),
        ):
            edge = shell.resize_edges.edges[name]
            assert str(edge.cget("cursor")) == cursor
            x, y = edge.winfo_rootx() + edge.winfo_width() // 2, edge.winfo_rooty() + edge.winfo_height() // 2
            assert window.winfo_containing(x, y) is edge
            before = (window.winfo_width(), window.winfo_height())
            edge.event_generate("<Button-1>", rootx=x, rooty=y)
            edge.event_generate("<B1-Motion>", rootx=x+dx, rooty=y+dy)
            edge.event_generate("<ButtonRelease-1>", rootx=x+dx, rooty=y+dy)
            root.update()
            assert (window.winfo_width(), window.winfo_height()) == (before[0]+dx, before[1]+dy)
            assert (window.winfo_x(), window.winfo_y()) == origin
        corner = shell.resize_edges.edges["corner"]
        x, y = corner.winfo_rootx(), corner.winfo_rooty()
        corner.event_generate("<Button-1>", rootx=x, rooty=y)
        corner.event_generate("<B1-Motion>", rootx=x-1000, rooty=y-1000)
        corner.event_generate("<ButtonRelease-1>", rootx=x-1000, rooty=y-1000)
        root.update()
        assert (window.winfo_width(), window.winfo_height()) == window.minsize()
    finally:
        manager.handle.dispose()
        root.update()
