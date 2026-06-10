import subprocess
import sys

from apps.calculator.ui.table.interaction_core import (
    UndoStack,
    copyable_positions,
    editable_clear_targets,
    editable_paste_targets,
    encode_selection_to_clipboard,
    is_replace_printable,
    parse_clipboard_matrix,
    resolve_adjacent_position,
    resolve_next_position,
    selection_bounds,
)
from apps.calculator.ui.table.roles import CellRole


def test_interaction_core_import_does_not_load_tkinter():
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            "import apps.calculator.ui.table.interaction_core, sys; "
            "assert 'tkinter' not in sys.modules",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_tsv_parse_and_encode_preserve_excel_shapes():
    assert parse_clipboard_matrix("1\t2\r\n3\t4\n") == (("1", "2"), ("3", "4"))
    assert parse_clipboard_matrix("10\n20\n30") == (("10",), ("20",), ("30",))
    assert encode_selection_to_clipboard((("1", "2"), ("3", "4"))) == "1\t2\n3\t4"


def test_paste_targets_support_single_column_multi_row_and_skip_result_cells():
    roles = (CellRole.EDITABLE, CellRole.RESULT, CellRole.EDITABLE)

    targets = editable_paste_targets((("10",), ("20",), ("30",)), (0, 0, 0, 0), roles)

    assert targets == {(0, 0): "10", (1, 0): "20", (2, 0): "30"}
    assert editable_paste_targets((("SHOULD_SKIP",),), (0, 0, 1, 1), roles) == {}


def test_mxn_paste_and_clear_filter_to_editable_roles():
    roles = (CellRole.EDITABLE, CellRole.RESULT, CellRole.EDITABLE)

    assert editable_paste_targets(
        (("a", "b", "c"), ("d", "e", "f")), (0, 0, 0, 0), roles
    ) == {
        (0, 0): "a",
        (0, 2): "c",
        (1, 0): "d",
        (1, 2): "f",
    }
    assert editable_clear_targets(((0, 0), (0, 1), (0, 2)), roles) == {
        (0, 0): "",
        (0, 2): "",
    }


def test_selected_range_one_row_clipboard_fills_each_selected_row():
    roles = (CellRole.EDITABLE, CellRole.EDITABLE, CellRole.RESULT)

    assert editable_paste_targets((("1", "2", "3"),), (0, 3, 0, 2), roles) == {
        (0, 0): "1",
        (0, 1): "2",
        (1, 0): "1",
        (1, 1): "2",
        (2, 0): "1",
        (2, 1): "2",
        (3, 0): "1",
        (3, 1): "2",
    }


def test_selected_range_single_cell_clipboard_fills_every_editable_cell():
    roles = (CellRole.EDITABLE, CellRole.RESULT, CellRole.EDITABLE)

    assert editable_paste_targets((("x",),), (1, 2, 0, 2), roles) == {
        (1, 0): "x",
        (1, 2): "x",
        (2, 0): "x",
        (2, 2): "x",
    }


def test_multi_cell_clipboard_repeats_to_fill_larger_selection():
    roles = (CellRole.EDITABLE, CellRole.EDITABLE, CellRole.EDITABLE)

    # 2x2 clipboard into 4x3 selection: repeats by tiling
    assert editable_paste_targets((("1", "2"), ("3", "4")), (0, 3, 0, 2), roles) == {
        (0, 0): "1", (0, 1): "2", (0, 2): "1",
        (1, 0): "3", (1, 1): "4", (1, 2): "3",
        (2, 0): "1", (2, 1): "2", (2, 2): "1",
        (3, 0): "3", (3, 1): "4", (3, 2): "3",
    }


def test_mx_n_clipboard_repeats_to_fill_selection():
    roles = (CellRole.EDITABLE, CellRole.EDITABLE, CellRole.EDITABLE, CellRole.EDITABLE)

    # 2x2 clipboard into 6x4 selection
    assert editable_paste_targets(
        (("a", "b"), ("c", "d")), (0, 5, 0, 3), roles
    ) == {
        (0, 0): "a", (0, 1): "b", (0, 2): "a", (0, 3): "b",
        (1, 0): "c", (1, 1): "d", (1, 2): "c", (1, 3): "d",
        (2, 0): "a", (2, 1): "b", (2, 2): "a", (2, 3): "b",
        (3, 0): "c", (3, 1): "d", (3, 2): "c", (3, 3): "d",
        (4, 0): "a", (4, 1): "b", (4, 2): "a", (4, 3): "b",
        (5, 0): "c", (5, 1): "d", (5, 2): "c", (5, 3): "d",
    }


def test_3x3_clipboard_repeats_to_fill_larger_selection():
    roles = (CellRole.EDITABLE, CellRole.EDITABLE, CellRole.EDITABLE)

    # 3x3 clipboard into 9x3 selection
    assert editable_paste_targets(
        (("1", "2", "3"), ("4", "5", "6"), ("7", "8", "9")), (0, 8, 0, 2), roles
    ) == {
        (0, 0): "1", (0, 1): "2", (0, 2): "3",
        (1, 0): "4", (1, 1): "5", (1, 2): "6",
        (2, 0): "7", (2, 1): "8", (2, 2): "9",
        (3, 0): "1", (3, 1): "2", (3, 2): "3",
        (4, 0): "4", (4, 1): "5", (4, 2): "6",
        (5, 0): "7", (5, 1): "8", (5, 2): "9",
        (6, 0): "1", (6, 1): "2", (6, 2): "3",
        (7, 0): "4", (7, 1): "5", (7, 2): "6",
        (8, 0): "7", (8, 1): "8", (8, 2): "9",
    }


def test_selection_copy_and_navigation_helpers():
    roles = (CellRole.EDITABLE, CellRole.RESULT, CellRole.DISABLED)

    assert selection_bounds((2, 0), (0, 2)) == (0, 2, 0, 2)
    assert copyable_positions((0, 0, 0, 2), 2, 3, roles) == ((0, 0), (0, 1))
    assert resolve_next_position((0, 2), 2, 3, "tab") == (1, 0)
    assert resolve_next_position((1, 0), 2, 3, "shift-tab") == (0, 2)
    assert resolve_next_position((1, 2), 2, 3, "enter") == (0, 2)
    assert resolve_adjacent_position((0, 0), 2, 3, "left") == (0, 0)
    assert resolve_adjacent_position((0, 0), 2, 3, "down") == (1, 0)


def test_replace_printable_and_undo_stack_policy():
    assert is_replace_printable("a", "a", 0)
    assert not is_replace_printable("Left", "", 0)
    assert not is_replace_printable("v", "v", 0x0004)

    stack = UndoStack(limit=2)
    stack.push({"a": "1"})
    stack.push({"a": "2"})
    stack.push({"a": "3"})

    assert len(stack) == 2
    assert stack.pop() == {"a": "3"}
    assert stack.pop() == {"a": "2"}
    assert stack.pop() is None
