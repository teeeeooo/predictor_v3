"""Position-only Configure notifications must not rebuild plot items."""
import tkinter as tk
import pytest

from apps.calculator.ui.sections.bin_detail_panel import BinDetailGraph
from tests.helpers.tk import destroy_tk_root


def test_graph_keeps_items_on_move_and_updates_on_size_data_and_series():
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(str(exc))
    try:
        root.geometry("600x300")
        graph = BinDetailGraph(root, graph_series=(("Hours", "hours"), ("Power", "power")))
        graph.canvas.pack(fill="both", expand=True)
        graph.set_data(({"tj": 20, "hours": 2, "power": 8}, {"tj": 30, "hours": 4, "power": 10}))
        root.update()
        items = graph.canvas.find_all()
        for x in range(5):
            graph.canvas.event_generate("<Configure>", x=x, y=x,
                                        width=graph.canvas.winfo_width(), height=graph.canvas.winfo_height())
        root.update()
        assert graph.canvas.find_all() == items
        root.geometry("700x350")
        root.update()
        resized = graph.canvas.find_all()
        assert resized != items
        graph.set_series_key("power")
        assert graph.canvas.find_all() != resized
        graph.set_data(())
        texts = [graph.canvas.itemcget(item, "text") for item in graph.canvas.find_all() if graph.canvas.type(item) == "text"]
        assert texts == ["상세 데이터 없음"]
    finally:
        destroy_tk_root(root)
