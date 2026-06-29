"""Focused tests for IsoSasoT3Section controller switch.

Verifies that IsoSasoT3Section instantiates and behaves correctly
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
    from apps.calculator.ui.sections.iso_saso_t3_section import IsoSasoT3Section

    sec = IsoSasoT3Section(tk_root)
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
        # Select first editable cell (row 0, col 0 which is full_46 capacity)
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
    """recalculate_now works after valid values and handles invalid cases."""

    def test_recalculate_now_after_valid_values(self, section) -> None:
        section.input_table.set_values({
            "full_46_capacity": "5000",
            "full_46_power": "1500",
            "full_35_capacity": "6000",
            "full_35_power": "1500",
            "half_35_capacity": "3000",
            "half_35_power": "680",
            "min_35_capacity": "1200",
            "min_35_power": "300",
        })
        section.recalculate_now()
        assert section.result_table.rows
        copy_text = section.result_table.status_label.cget("text")
        assert "완료" in copy_text
        assert "오류" not in copy_text

    def test_recalculate_blocks_on_invalid_required_value(self, section) -> None:
        # Inject invalid required point capacity
        section.input_table.set_values({
            "full_46_capacity": "not_a_number",
            "full_46_power": "1500",
            "full_35_capacity": "6000",
            "full_35_power": "1500",
            "half_35_capacity": "3000",
            "half_35_power": "680",
            "min_35_capacity": "1200",
            "min_35_power": "300",
        })
        section.recalculate_now()
        copy_text = section.result_table.status_label.cget("text")
        assert "오류" in copy_text or "error" in copy_text.lower()
        # Status should report calculation failure/error tone matched to CSPF/HSPF
        assert "숫자 입력을 확인하세요" in copy_text

        # Verify invalid field is visually marked
        assert section.input_table.is_field_invalid("full_46_capacity") is True
        from apps.calculator.ui.layout_constants import TABLE_INVALID_BG
        assert section.input_table.editable_entries["full_46_capacity"].cget("background") == TABLE_INVALID_BG

    def test_recalculate_blocks_on_required_non_positive_value(self, section) -> None:
        # Inject non-positive value
        section.input_table.set_values({
            "full_46_capacity": "0",  # Invalid positivity
            "full_46_power": "1500",
            "full_35_capacity": "6000",
            "full_35_power": "1500",
            "half_35_capacity": "3000",
            "half_35_power": "680",
            "min_35_capacity": "1200",
            "min_35_power": "300",
        })
        section.recalculate_now()
        copy_text = section.result_table.status_label.cget("text")
        assert "오류" in copy_text or "error" in copy_text.lower()
        assert "숫자 입력을 확인하세요" in copy_text

        # Verify invalid field is visually marked due to positivity check
        assert section.input_table.is_field_invalid("full_46_capacity") is True

    def test_recalculate_blocks_on_invalid_optional_value(self, section) -> None:
        # Inject invalid optional point (35 Min capacity)
        section.input_table.set_values({
            "full_46_capacity": "5000",
            "full_46_power": "1500",
            "full_35_capacity": "6000",
            "full_35_power": "1500",
            "half_35_capacity": "3000",
            "half_35_power": "680",
            "min_35_capacity": "invalid_val",
            "min_35_power": "300",
        })
        section.recalculate_now()
        copy_text = section.result_table.status_label.cget("text")
        assert "오류" in copy_text or "error" in copy_text.lower()
        assert "35 Min" in copy_text
        # Optional row is error row, but required row is still calculated (partial behavior preserved)
        rows = section.result_table.rows
        assert len(rows) == 2
        assert rows[0][0] == "With 35 Min (4-point)"
        assert "입력" in rows[0][4] or "error" in rows[0][4].lower() or "수정" in rows[0][4] or "확인" in rows[0][4]
        assert rows[1][0] == "Required only (3-point)"
        assert rows[1][5] != "-"

        # Verify only optional field is marked invalid
        assert section.input_table.is_field_invalid("min_35_capacity") is True
        assert section.input_table.is_field_invalid("full_46_capacity") is False

    def test_recalculate_blocks_on_optional_non_positive_value(self, section) -> None:
        # Inject non-positive optional point
        section.input_table.set_values({
            "full_46_capacity": "5000",
            "full_46_power": "1500",
            "full_35_capacity": "6000",
            "full_35_power": "1500",
            "half_35_capacity": "3000",
            "half_35_power": "680",
            "min_35_capacity": "-500",  # Invalid positivity
            "min_35_power": "300",
        })
        section.recalculate_now()
        copy_text = section.result_table.status_label.cget("text")
        assert "오류" in copy_text or "error" in copy_text.lower()
        assert "35 Min" in copy_text
        # Required row is still available
        rows = section.result_table.rows
        assert len(rows) == 2
        assert rows[1][0] == "Required only (3-point)"
        assert rows[1][5] != "-"

        # Verify only optional field is marked invalid
        assert section.input_table.is_field_invalid("min_35_capacity") is True
        assert section.input_table.is_field_invalid("full_46_capacity") is False

    def test_optional_becomes_valid_after_correction(self, section) -> None:
        # 1. Start with invalid optional input
        section.input_table.set_values({
            "full_46_capacity": "5000",
            "full_46_power": "1500",
            "full_35_capacity": "6000",
            "full_35_power": "1500",
            "half_35_capacity": "3000",
            "half_35_power": "680",
            "min_35_capacity": "invalid_val",
            "min_35_power": "300",
        })
        section.recalculate_now()
        assert section.input_table.is_field_invalid("min_35_capacity") is True

        # 2. Correct the optional input to a valid positive value
        section.input_table.set_values({
            "min_35_capacity": "1200",
        })
        section.recalculate_now()

        # 3. Verify invalid state is cleared and calculation completes successfully
        assert section.input_table.is_field_invalid("min_35_capacity") is False
        copy_text = section.result_table.status_label.cget("text")
        assert "완료" in copy_text
        assert "오류" not in copy_text
        rows = section.result_table.rows
        assert len(rows) == 2
        assert rows[0][5] != "-"  # 4-point CSPF calculated
        assert rows[1][5] != "-"  # 3-point CSPF calculated


class TestUndoBehavior:
    """Undo restores original value after invalid text input."""

    def test_undo_restores_original_value(self, section) -> None:
        ctrl = section.input_controller
        section.input_table.set_values({"full_46_capacity": "5000"})
        # Select cell (0, 0) - full_46 capacity.
        ctrl.select((0, 0))
        ctrl._enter_edit_mode((0, 0))
        section.input_table.update_idletasks()

        assert ctrl.table.text_at_position((0, 0)) == "5000"

        # Mutate value
        entry = section.input_table.editable_entries["full_46_capacity"]
        entry.delete(0, "end")
        entry.insert(0, "invalid_val")
        ctrl._focus_out(None)

        assert ctrl.table.text_at_position((0, 0)) == "invalid_val"

        # Trigger undo
        ctrl._undo_last()
        assert ctrl.table.text_at_position((0, 0)) == "5000"
