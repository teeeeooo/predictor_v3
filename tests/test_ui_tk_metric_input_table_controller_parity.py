"""Parity tests for MetricInputTable + TkTableController before switch.

These tests verify that MetricInputTable and TkTableController interact
safely for the user-facing behaviors that must not regress during a
controller switch.  No production code changes.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from ui_tk.layout_constants import TABLE_INVALID_BG
from ui_tk.metric_input_table import MetricInputTable
from ui_tk.table.controller import TkTableController
from ui_tk.table.interaction_core import CellAddress


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
def sample_table(tk_root):
    table = MetricInputTable(
        tk_root,
        columns=(("c1", "Col1"), ("c2", "Col2")),
        rows=(("r1", "Row1"), ("r2", "Row2")),
        editable_cells={
            ("r1", "c1"): "a",
            ("r1", "c2"): "b",
            ("r2", "c1"): "c",
            ("r2", "c2"): "d",
        },
    )
    table.pack()
    table.set_values({"a": "1", "b": "2", "c": "3", "d": "4"})
    tk_root.update_idletasks()
    return table


@pytest.fixture
def ctrl(sample_table):
    """TkTableController wired to sample MetricInputTable."""
    return TkTableController(sample_table)


@pytest.fixture
def mixed_table(tk_root):
    """2x2 table with left column editable and right column readonly."""
    table = MetricInputTable(
        tk_root,
        columns=(("c1", "Col1"), ("c2", "Col2")),
        rows=(("r1", "Row1"), ("r2", "Row2")),
        editable_cells={
            ("r1", "c1"): "a",
            ("r2", "c1"): "b",
        },
    )
    table.pack()
    table.set_values({"a": "1", "b": "2"})
    # right column cells are readonly; default display is "-"
    tk_root.update_idletasks()
    return table


@pytest.fixture
def mixed_ctrl(mixed_table):
    """TkTableController wired to mixed MetricInputTable."""
    return TkTableController(mixed_table)


class TestAttachAndSelect:
    """Controller attaches, select/active/selected positions work."""

    def test_controller_attaches_without_error(self, ctrl: TkTableController) -> None:
        assert ctrl.table is not None

    def test_select_sets_anchor_and_active(self, ctrl: TkTableController) -> None:
        ctrl.select((0, 0))
        assert ctrl.anchor == (0, 0)
        assert ctrl.active == (0, 0)

    def test_select_extend_keeps_anchor(self, ctrl: TkTableController) -> None:
        ctrl.select((0, 0))
        ctrl.select((1, 1), extend=True)
        assert ctrl.anchor == (0, 0)
        assert ctrl.active == (1, 1)

    def test_selected_positions_single_cell(self, ctrl: TkTableController) -> None:
        ctrl.select((0, 0))
        assert ctrl.selected_positions() == ((0, 0),)

    def test_selected_positions_range(self, ctrl: TkTableController) -> None:
        ctrl.select((0, 0))
        ctrl.select((1, 1), extend=True)
        positions = ctrl.selected_positions()
        assert (0, 0) in positions
        assert (0, 1) in positions
        assert (1, 0) in positions
        assert (1, 1) in positions


class TestCopyPaste:
    """Copy uses clipboard; paste applies raw text to editable cells only."""

    def test_copy_puts_selected_values_on_clipboard(self, ctrl: TkTableController) -> None:
        ctrl.select((0, 0))
        ctrl._copy()
        text = ctrl.table.clipboard_get()
        assert "1" in text  # cell (0,0) has value "1"

    def test_paste_updates_editable_cell(self, ctrl: TkTableController) -> None:
        ctrl.select((0, 0))
        ctrl.table.clipboard_clear()
        ctrl.table.clipboard_append("99")
        ctrl._paste()
        assert ctrl.table.text_at_position((0, 0)) == "99"

    def test_paste_does_not_reject_invalid_text(self, ctrl: TkTableController) -> None:
        # 265 policy: paste layer must not reject for validation reasons.
        ctrl.select((0, 0))
        ctrl.table.clipboard_clear()
        ctrl.table.clipboard_append("not_a_number")
        ctrl._paste()
        assert ctrl.table.text_at_position((0, 0)) == "not_a_number"

    def test_paste_ignores_readonly_target(
        self, mixed_ctrl: TkTableController
    ) -> None:
        # Paste a 2x2 matrix starting at (0,0).
        # Only the left column is editable; right column must stay unchanged.
        mixed_ctrl.select((0, 0))
        mixed_ctrl.table.clipboard_clear()
        mixed_ctrl.table.clipboard_append(
            "10\tREADONLY_SHOULD_NOT_APPLY\n20\tREADONLY_SHOULD_NOT_APPLY"
        )
        mixed_ctrl._paste()

        # Editable cells receive pasted values
        assert mixed_ctrl.table.text_at_position((0, 0)) == "10"
        assert mixed_ctrl.table.text_at_position((1, 0)) == "20"

        # Readonly cells remain unchanged
        assert mixed_ctrl.table.text_at_position((0, 1)) == "-"
        assert mixed_ctrl.table.text_at_position((1, 1)) == "-"

        # Verify underlying snapshot only contains editable fields
        snapshot = mixed_ctrl.table.snapshot()
        assert snapshot.get("a") == "10"
        assert snapshot.get("b") == "20"
        assert len(snapshot) == 2


class TestClearAndUndo:
    """Clear only editable cells; undo restores previous values."""

    def test_clear_clears_selected_editable_cells(self, ctrl: TkTableController) -> None:
        ctrl.select((0, 0))
        ctrl._clear()
        assert ctrl.table.text_at_position((0, 0)) == ""

    def test_undo_restores_value_after_clear(self, ctrl: TkTableController) -> None:
        ctrl.select((0, 0))
        original = ctrl.table.text_at_position((0, 0))
        ctrl._clear()
        ctrl._undo_last()
        assert ctrl.table.text_at_position((0, 0)) == original

    def test_undo_restores_value_after_paste(self, ctrl: TkTableController) -> None:
        ctrl.select((0, 0))
        original = ctrl.table.text_at_position((0, 0))
        ctrl.table.clipboard_clear()
        ctrl.table.clipboard_append("999")
        ctrl._paste()
        assert ctrl.table.text_at_position((0, 0)) == "999"
        ctrl._undo_last()
        assert ctrl.table.text_at_position((0, 0)) == original


class TestInvalidVisualState:
    """Invalid field background is supplied through default_cell_background."""

    def test_invalid_background_supplied_by_surface(self, ctrl: TkTableController) -> None:
        ctrl.table.set_invalid_fields({"a": "bad"})
        color = ctrl.table.default_cell_background((0, 0))
        assert color == TABLE_INVALID_BG

    def test_invalid_cleared_background_returns_editable(self, ctrl: TkTableController) -> None:
        ctrl.table.set_invalid_fields({"a": "bad"})
        ctrl.table.clear_invalid_fields()
        from ui_tk.layout_constants import TABLE_EDITABLE_BG
        color = ctrl.table.default_cell_background((0, 0))
        assert color == TABLE_EDITABLE_BG


class TestReplaceOnType:
    """Replace-on-type writes one typed char and enters edit mode."""

    def test_type_replace_writes_char_and_enters_edit(self, ctrl: TkTableController) -> None:
        ctrl.select((0, 0))
        original = ctrl.table.text_at_position((0, 0))

        # Fake event mimicking a printable keypress
        event = type("Event", (), {"keysym": "a", "char": "x", "state": 0})()
        ctrl._type_replace(event, (0, 0))

        # Value should be the single typed character
        assert ctrl.table.text_at_position((0, 0)) == "x"
        # Controller should be in edit mode
        assert ctrl._mode == "edit"
        # Undo should restore original value
        ctrl._undo_last()
        assert ctrl.table.text_at_position((0, 0)) == original

    def test_type_replace_clears_selection_for_multi_key_append(self, ctrl: TkTableController) -> None:
        ctrl.select((0, 0))
        widget = ctrl.table.focus_widget((0, 0))
        widget.focus_set()
        ctrl._show_selection_caret((0, 0))
        ctrl.table.update_idletasks()

        # 1. Click select (or caret showing) should present selection
        assert widget.selection_present()

        # 2. Fake event mimicking a printable keypress '9' (different from default '1')
        event1 = type("Event", (), {"keysym": "9", "char": "9", "state": 0})()
        ctrl._type_replace(event1, (0, 0))
        ctrl.table.update_idletasks()

        # 3. Value should be '9' and selection should be cleared immediately
        assert ctrl.table.text_at_position((0, 0)) == "9"
        assert not widget.selection_present()
        assert widget.index("insert") == 1

        # 4. Simulate subsequent typing '0' and then another '0' at insert cursor
        cursor_pos = widget.index("insert")
        widget.insert(cursor_pos, "0")
        widget.icursor("end")

        cursor_pos = widget.index("insert")
        widget.insert(cursor_pos, "0")
        widget.icursor("end")

        # Trigger focus out to commit edit
        ctrl._focus_out(None)

        assert ctrl.table.text_at_position((0, 0)) == "900"
