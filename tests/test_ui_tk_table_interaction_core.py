import subprocess
import sys

from ui_tk.table.interaction_core import (
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
from ui_tk.table.roles import CellRole


def test_interaction_core_import_does_not_load_tkinter():
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            "import ui_tk.table.interaction_core, sys; "
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
