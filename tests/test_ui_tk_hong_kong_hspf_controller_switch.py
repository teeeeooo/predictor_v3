"""Focused tests for HongKongHspfSection controller switch.

Verifies that HongKongHspfSection instantiates and behaves correctly
with TkTableController after the switch from ExcelLikeTableController.
"""

from __future__ import annotations

import pytest

from apps.calculator.ui.table.controller import TkTableController


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
def section(tk_root):
    from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection

    sec = HongKongHspfSection(tk_root, region_label="Hong Kong")
    sec.pack()
    tk_root.update_idletasks()
    return sec


class TestControllerSwitch:
    """Controllers are TkTableController after switch."""

    def test_input_controller_is_tk_table_controller(self, section) -> None:
        assert isinstance(section.input_controller, TkTableController)


class TestPasteBehavior:
    """Paste into input table works through TkTableController."""

    def test_paste_updates_input_editable_cell(self, section) -> None:
        ctrl = section.input_controller
        ctrl.select((0, 0))
        ctrl.table.clipboard_clear()
        ctrl.table.clipboard_append("9999")
        ctrl._paste()
        assert ctrl.table.text_at_position((0, 0)) == "9999"

    def test_paste_does_not_reject_invalid_text(self, section) -> None:
        ctrl = section.input_controller
        ctrl.select((0, 0))
        ctrl.table.clipboard_clear()
        ctrl.table.clipboard_append("not_a_number")
        ctrl._paste()
        assert ctrl.table.text_at_position((0, 0)) == "not_a_number"


class TestRecalculate:
    """recalculate_now works after valid values and blocks on invalid."""

    def test_recalculate_now_after_valid_values(self, section) -> None:
        section.input_table.set_values({
            "full_capacity": "6300",
            "full_power": "1500",
            "half_capacity": "3200",
            "half_power": "800",
        })
        section.recalculate_now()
        # Result panel should have rendered summary tables (not empty/error state)
        assert section.result_panel.summary_tables
        copy_text = section.result_panel._text.get("1.0", "end-1c")
        assert "오류" not in copy_text
        assert "error" not in copy_text.lower()

    def test_recalculate_blocks_on_invalid_value(self, section) -> None:
        # Inject invalid text directly
        section.input_table.set_values({
            "full_capacity": "not_a_number",
            "full_power": "1500",
            "half_capacity": "3200",
            "half_power": "800",
        })
        section.recalculate_now()
        # Copy text should contain an error message
        copy_text = section.result_panel._text.get("1.0", "end-1c")
        assert "오류" in copy_text or "error" in copy_text.lower()


class TestUndoBehavior:
    """Undo restores original value after invalid text input."""

    def test_undo_restores_original_value(self, section) -> None:
        ctrl = section.input_controller
        section.input_table.set_values({"full_capacity": "6300"})
        # Focus and enter edit mode on cell (0, 0)
        ctrl.select((0, 0))
        ctrl._enter_edit_mode((0, 0))
        section.input_table.update_idletasks()
        
        # Simulate invalid edit
        # First check the current value.
        assert ctrl.table.text_at_position((0, 0)) == "6300"
        
        # Mutate value by triggering entry edit and focus out
        entry = section.input_table.editable_entries["full_capacity"]
        entry.delete(0, "end")
        entry.insert(0, "invalid_val")
        ctrl._focus_out(None)
        
        assert ctrl.table.text_at_position((0, 0)) == "invalid_val"
        
        # Trigger undo
        ctrl._undo_last()
        assert ctrl.table.text_at_position((0, 0)) == "6300"
