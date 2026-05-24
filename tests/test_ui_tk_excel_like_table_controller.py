"""Tests for Tkinter Excel-like behavior attached through a controller."""

from __future__ import annotations

import subprocess
import sys
from types import SimpleNamespace

import pytest

from ui_tk.excel_like_table_controller import (
    ExcelLikeTableController,
    clip_paste_targets,
    encode_selection_to_clipboard,
    parse_clipboard_matrix,
    resolve_next_cell,
    resolve_selection_bounds,
    validate_paste_matrix,
)
from ui_tk.layout_constants import TABLE_ACTIVE_BG, TABLE_SELECTED_BG
from ui_tk.metric_input_table import MetricInputTable


def test_pure_helper_module_import_does_not_load_tkinter():
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            "import ui_tk.excel_like_table_controller, sys; "
            "assert 'tkinter' not in sys.modules",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


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


@pytest.fixture
def controlled_table(tk_root):
    table = MetricInputTable(
        tk_root,
        columns=(("left", "Left"), ("right", "Right")),
        rows=(("top", "Top"), ("bottom", "Bottom")),
        editable_cells={
            ("top", "left"): "a",
            ("top", "right"): "b",
            ("bottom", "left"): "c",
            ("bottom", "right"): "d",
        },
    )
    table.pack()
    table.set_values({"a": "1", "b": "2", "c": "3", "d": "4"})
    calls = []
    table.set_values_changed_callback(lambda: calls.append(table.get_text_values()))
    controller = ExcelLikeTableController(table)
    tk_root.update_idletasks()
    return table, controller, calls


def test_clipboard_helpers_parse_encode_clip_and_validate_atomically():
    matrix = parse_clipboard_matrix("1\t2\r\n3\t4\n")
    assert matrix == (("1", "2"), ("3", "4"))
    assert encode_selection_to_clipboard(matrix) == "1\t2\n3\t4"
    assert clip_paste_targets(matrix, (1, 1, 1, 1), 2, 2) == (((1, 1), "1"),)
    assert clip_paste_targets((("7",),), (0, 1, 0, 1), 2, 2) == (
        ((0, 0), "7"),
        ((0, 1), "7"),
        ((1, 0), "7"),
        ((1, 1), "7"),
    )
    with pytest.raises(ValueError):
        validate_paste_matrix((("1", "bad"),))
    with pytest.raises(ValueError):
        parse_clipboard_matrix("1\t2\n3")


def test_selection_bounds_and_navigation_are_grid_based():
    assert resolve_selection_bounds((1, 0), (0, 1)) == (0, 1, 0, 1)
    cells = ((0, 0), (0, 1), (1, 0), (1, 1))
    assert resolve_next_cell((0, 0), cells, "tab") == (0, 1)
    assert resolve_next_cell((0, 1), cells, "tab") == (1, 0)
    assert resolve_next_cell((0, 0), cells, "enter") == (1, 0)
    assert resolve_next_cell((1, 0), cells, "enter") == (0, 1)
    assert resolve_next_cell((0, 0), cells, "shift-tab") == (1, 1)


def test_click_shift_and_drag_make_rectangular_selection(controlled_table, monkeypatch):
    table, controller, _calls = controlled_table
    controller._click(SimpleNamespace(state=0), (0, 0))
    assert controller.selected_positions() == ((0, 0),)
    assert table.editable_entries["a"].cget("background") == TABLE_ACTIVE_BG

    controller._click(SimpleNamespace(state=1), (1, 1))
    assert controller.selected_positions() == ((0, 0), (0, 1), (1, 0), (1, 1))
    assert table.editable_entries["a"].cget("background") == TABLE_SELECTED_BG

    controller.select((0, 0))
    target = table.editable_entries["d"]
    monkeypatch.setattr(table, "winfo_containing", lambda _x, _y: target)
    controller._drag(
        SimpleNamespace(x_root=target.winfo_rootx() + 1, y_root=target.winfo_rooty() + 1)
    )
    assert controller.selection_bounds == (0, 1, 0, 1)


def test_copy_paste_delete_and_undo_use_one_grouped_notification(controlled_table):
    table, controller, calls = controlled_table
    controller.select((0, 0))
    controller.select((1, 1), extend=True)
    controller._copy()
    assert table.clipboard_get() == "1\t2\n3\t4"

    table.clipboard_clear()
    table.clipboard_append("10\t20\n30\t40")
    controller._paste()
    assert table.get_text_values() == {"a": "10", "b": "20", "c": "30", "d": "40"}
    assert len(calls) == 1

    controller._clear()
    assert table.get_text_values() == {"a": "", "b": "", "c": "", "d": ""}
    assert len(calls) == 2
    controller._undo_last()
    assert table.get_text_values() == {"a": "10", "b": "20", "c": "30", "d": "40"}
    assert len(calls) == 3


def test_invalid_paste_is_rejected_without_partial_apply(controlled_table):
    table, controller, calls = controlled_table
    controller.select((0, 0))
    controller.select((0, 1), extend=True)
    table.clipboard_clear()
    table.clipboard_append("10\tbad")

    controller._paste()

    assert table.get_text_values() == {"a": "1", "b": "2", "c": "3", "d": "4"}
    assert calls == []


def test_navigation_and_click_then_type_replace(controlled_table):
    table, controller, calls = controlled_table
    controller.select((0, 0))
    assert controller._navigate("tab") == "break"
    assert controller.active == (0, 1)
    assert controller._navigate("enter") == "break"
    assert controller.active == (1, 1)

    controller._click(SimpleNamespace(state=0), (0, 0))
    assert controller._type_replace(SimpleNamespace(char="9", state=0), (0, 0)) == "break"
    assert table.get_text_values()["a"] == "9"
    assert len(calls) == 1
    controller._undo_last()
    assert table.get_text_values()["a"] == "1"
