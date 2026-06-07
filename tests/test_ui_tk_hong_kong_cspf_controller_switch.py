"""Focused pilot tests for HongKongCspfSection controller switch.

Verifies that HongKongCspfSection instantiates and behaves correctly
with TkTableController after the pilot switch from ExcelLikeTableController.
"""

from __future__ import annotations

import pytest

from ui_tk.table.controller import TkTableController


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
    from ui_tk.sections.hong_kong_cspf_section import HongKongCspfSection

    sec = HongKongCspfSection(tk_root, region_label="Hong Kong")
    sec.pack()
    tk_root.update_idletasks()
    return sec


class TestControllerSwitch:
    """Controllers are TkTableController after switch."""

    def test_rated_controller_is_tk_table_controller(self, section) -> None:
        assert isinstance(section.rated_controller, TkTableController)

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
    """recalculate_now works after valid values via new controller."""

    def test_recalculate_now_after_valid_values(self, section) -> None:
        # Set known valid values
        section.input_table.set_values({
            "full_capacity": "3600",
            "full_power": "900",
            "half_capacity": "1700",
            "half_power": "380",
        })
        section.rated_table.set_values({"declared_capacity": "3500"})
        section.recalculate_now()
        # Result panel should have rendered summary tables (not empty/error state)
        assert section.result_panel.summary_tables
        # Copy text should not contain an error message
        copy_text = section.result_panel._text.get("1.0", "end-1c")
        assert "오류" not in copy_text
        assert "error" not in copy_text.lower()
