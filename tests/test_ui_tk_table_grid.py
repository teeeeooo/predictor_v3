"""Minimal widget-adapter tests for the Tkinter Entry-grid foundation."""

import sys

import pytest

from ui_tk.table_grid_model import GridColumn, GridRow


@pytest.fixture
def tk_root():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")
    root.withdraw()
    try:
        yield root
    finally:
        root.destroy()


def _grid(root, callback=None):
    from ui_tk.table_grid import TableGrid

    return TableGrid(
        root,
        rows=(GridRow("full", "Full"), GridRow("half", "Half")),
        columns=(GridColumn("capacity", "Capacity"), GridColumn("power", "Power")),
        values_changed_callback=callback,
    )


def test_adapter_import_does_not_import_pyqt5():
    for name in list(sys.modules):
        if name.startswith("PyQt5"):
            del sys.modules[name]

    import ui_tk.table_grid  # noqa: F401

    assert not any(name.startswith("PyQt5") for name in sys.modules)


def test_widget_tree_and_text_table_round_trip(tk_root):
    grid = _grid(tk_root)
    grid.pack()
    grid.set_cell("full", "capacity", "3600")

    assert grid.get_text_table()["full"]["capacity"] == "3600"
    assert len(grid.winfo_children()) > 0


def test_callback_only_runs_for_actual_value_change(tk_root):
    calls = []
    grid = _grid(tk_root, callback=lambda: calls.append("changed"))

    assert grid.set_cell("full", "capacity", "3600") is True
    assert grid.set_cell("full", "capacity", "3600") is False

    assert calls == ["changed"]


def test_invalid_numeric_state_is_exposed_without_calculator_call(tk_root):
    grid = _grid(tk_root)
    grid.set_cell("full", "capacity", "not-a-number")

    assert ("full", "capacity") in grid.invalid_cells()
    with pytest.raises(ValueError, match="invalid cells"):
        grid.get_numeric_table()
