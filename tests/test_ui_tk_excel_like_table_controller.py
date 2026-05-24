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
from ui_tk.layout_constants import TABLE_ACTIVE_BG, TABLE_EDITABLE_BG, TABLE_SELECTED_BG
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


@pytest.fixture
def two_controlled_tables(tk_root):
    table1 = MetricInputTable(
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
    table1.pack()
    table1.set_values({"a": "1", "b": "2", "c": "3", "d": "4"})
    controller1 = ExcelLikeTableController(table1)

    table2 = MetricInputTable(
        tk_root,
        columns=(("x", "X"), ("y", "Y")),
        rows=(("u", "U"), ("v", "V")),
        editable_cells={
            ("u", "x"): "e",
            ("u", "y"): "f",
            ("v", "x"): "g",
            ("v", "y"): "h",
        },
    )
    table2.pack()
    table2.set_values({"e": "5", "f": "6", "g": "7", "h": "8"})
    controller2 = ExcelLikeTableController(table2)

    tk_root.update_idletasks()
    return table1, controller1, table2, controller2


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
    assert table.editable_entries["b"].cget("insertontime") == 0
    assert controller._navigate("enter") == "break"
    assert controller.active == (1, 1)
    assert table.editable_entries["d"].cget("insertontime") == 0

    controller._click(SimpleNamespace(state=0), (0, 0))
    assert table.editable_entries["a"].cget("insertontime") == 0
    assert controller._type_replace(SimpleNamespace(char="9", state=0), (0, 0)) == "break"
    assert table.get_text_values()["a"] == "9"
    assert len(calls) == 1
    assert table.editable_entries["a"].cget("insertontime") == 600
    controller._undo_last()
    assert table.get_text_values()["a"] == "1"


def test_click_does_not_show_typing_caret_until_first_key(controlled_table):
    table, controller, _calls = controlled_table
    controller._click(SimpleNamespace(state=0), (0, 0))
    entry = table.editable_entries["a"]
    assert entry.cget("insertontime") == 0
    controller._type_replace(SimpleNamespace(char="9", state=0), (0, 0))
    assert table.get_text_values()["a"] == "9"
    assert entry.cget("insertontime") == 600


def test_arrow_keys_move_active_cell_when_in_selection_mode(controlled_table):
    table, controller, _calls = controlled_table
    controller.select((0, 0))
    assert controller.active == (0, 0)
    assert controller._arrow("right") == "break"
    assert controller.active == (0, 1)
    assert controller._arrow("down") == "break"
    assert controller.active == (1, 1)
    assert controller._arrow("left") == "break"
    assert controller.active == (1, 0)
    assert controller._arrow("up") == "break"
    assert controller.active == (0, 0)
    # out of bounds stays at edge
    assert controller._arrow("left") == "break"
    assert controller.active == (0, 0)
    assert controller._arrow("up") == "break"
    assert controller.active == (0, 0)
    # once replace is no longer pending, arrows fall through to default entry behavior
    controller._type_replace(SimpleNamespace(char="9", state=0), (0, 0))
    assert controller._arrow("right") == ""


def test_kp_enter_bindings_exist_and_navigate_like_return(controlled_table):
    table, controller, _calls = controlled_table
    entry = table.editable_entries["a"]
    binds = entry.bind()
    assert any("KP_Enter" in b for b in binds)
    assert any("Shift" in b and "KP_Enter" in b for b in binds)
    controller.select((0, 0))
    assert controller._navigate("enter") == "break"
    assert controller.active == (1, 0)
    assert controller._navigate("shift-enter") == "break"
    assert controller.active == (0, 0)


def test_escape_clears_selection_and_restores_default_background(controlled_table):
    table, controller, _calls = controlled_table
    controller.select((0, 0))
    controller.select((1, 1), extend=True)
    assert controller.selection_bounds is not None
    assert controller._clear_selection() == "break"
    assert controller.anchor is None
    assert controller.active is None
    assert controller.selection_bounds is None
    for field_key in table.editable_entries:
        assert table.editable_entries[field_key].cget("background") == TABLE_EDITABLE_BG


def test_focus_out_clears_selection_when_not_internal_move(controlled_table):
    table, controller, _calls = controlled_table
    controller.select((0, 0))
    assert controller.active == (0, 0)
    controller._internal_focus_move = False
    controller._on_focus_out(SimpleNamespace())
    assert controller.active is None
    assert table.editable_entries["a"].cget("background") == TABLE_EDITABLE_BG


def test_focus_out_ignored_during_internal_navigation(controlled_table):
    table, controller, _calls = controlled_table
    controller.select((0, 0))
    controller._internal_focus_move = True
    controller._on_focus_out(SimpleNamespace())
    assert controller.active == (0, 0)


def test_table_frame_click_on_blank_area_clears_selection(controlled_table):
    table, controller, _calls = controlled_table
    controller.select((0, 0))
    # Binding exists on table_frame
    assert "<Button-1>" in table.table_frame.bind()
    # Simulate a click directly on the table_frame widget (blank gap area)
    event = SimpleNamespace(widget=table.table_frame)
    assert controller._on_table_frame_click(event) == "break"
    assert controller.active is None
    assert table.editable_entries["a"].cget("background") == TABLE_EDITABLE_BG


def test_header_label_click_clears_selection_via_recursive_binding(controlled_table):
    table, controller, _calls = controlled_table
    controller.select((0, 0))
    # Pick the first header cell (corner or column header)
    header_cell = list(table.header_cells.values())[0]
    # Find the Label inside it
    labels = [c for c in header_cell.winfo_children() if c.winfo_class() == "Label"]
    assert labels, "header cell must contain a Label"
    label = labels[0]
    # The recursive binding should exist on the Label
    assert "<Button-1>" in label.bind()
    # Simulate the bound callback path
    controller._clear_selection()
    assert controller.active is None
    assert table.editable_entries["a"].cget("background") == TABLE_EDITABLE_BG


def test_click_on_other_table_clears_previous_selection(two_controlled_tables):
    t1, c1, t2, c2 = two_controlled_tables
    c1.select((0, 0))
    assert c1.active == (0, 0)
    assert t1.editable_entries["a"].cget("background") == TABLE_ACTIVE_BG
    # Click on a cell in the second table
    c2._click(SimpleNamespace(state=0), (0, 0))
    # Previous controller should have been cleared
    assert c1.active is None
    assert t1.editable_entries["a"].cget("background") == TABLE_EDITABLE_BG
    # New controller should be active
    assert c2.active == (0, 0)
    assert t2.editable_entries["e"].cget("background") == TABLE_ACTIVE_BG


def test_internal_focus_move_resets_via_after_idle(controlled_table, tk_root):
    table, controller, _calls = controlled_table
    controller.select((0, 0))
    controller._navigate("tab")
    assert controller._internal_focus_move is True
    # Process after_idle callbacks
    tk_root.update_idletasks()
    assert controller._internal_focus_move is False


def test_external_focus_out_after_internal_move_clears(controlled_table, tk_root):
    table, controller, _calls = controlled_table
    controller.select((0, 0))
    controller._navigate("tab")
    tk_root.update_idletasks()
    assert controller._internal_focus_move is False
    controller._on_focus_out(SimpleNamespace())
    assert controller.active is None
    assert table.editable_entries["b"].cget("background") == TABLE_EDITABLE_BG


def test_focus_out_during_internal_move_is_suppressed_then_clears_after_idle(
    controlled_table, tk_root
):
    table, controller, _calls = controlled_table
    controller.select((0, 0))
    controller._navigate("tab")
    assert controller._internal_focus_move is True
    # Simulate focus-out arriving before after_idle resets the flag
    controller._on_focus_out(SimpleNamespace())
    assert controller.active == (0, 1)  # Should NOT be cleared yet
    tk_root.update_idletasks()
    assert controller._internal_focus_move is False
    # Now simulate an external focus-out
    controller._on_focus_out(SimpleNamespace())
    assert controller.active is None
    assert table.editable_entries["b"].cget("background") == TABLE_EDITABLE_BG


def test_command_and_control_shortcuts_bound_on_entry_and_frame(controlled_table):
    import sys

    table, controller, _calls = controlled_table
    entry = table.editable_entries["a"]
    binds = entry.bind()
    assert "<Control-Key-c>" in binds
    assert "<Control-Key-v>" in binds
    assert "<Control-Key-z>" in binds
    if sys.platform == "darwin":
        assert any("Mod1-Key-c" in b for b in binds)
        assert any("Mod1-Key-C" in b for b in binds)
        assert any("Mod1-Key-v" in b for b in binds)
        assert any("Mod1-Key-V" in b for b in binds)
        assert any("Mod1-Key-z" in b for b in binds)
        assert any("Mod1-Key-Z" in b for b in binds)
    frame_binds = table.table_frame.bind()
    if sys.platform == "darwin":
        assert any("Mod1-Key-c" in b for b in frame_binds)


def test_paste_atomic_reject_on_invalid_value(controlled_table):
    table, controller, calls = controlled_table
    controller.select((0, 0))
    controller.select((0, 1), extend=True)
    table.clipboard_clear()
    table.clipboard_append("10\tbad")
    controller._paste()
    assert table.get_text_values() == {"a": "1", "b": "2", "c": "3", "d": "4"}
    assert calls == []
