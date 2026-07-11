"""Focused tests for IsoIseer2PointSection controller switch.

Verifies that IsoIseer2PointSection instantiates and behaves correctly
with TkTableController after the switch from ExcelLikeTableController.
"""

from __future__ import annotations

import pytest

from apps.calculator.ui.table.controller import TkTableController
from tests.calculator_ui_sample_values import ISO_TWO_POINT_SAMPLE_VALUES


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
    from apps.calculator.ui.sections.iso_iseer_2point_section import IsoIseer2PointSection

    sec = IsoIseer2PointSection(tk_root)
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
            "full_capacity": "3600",
            "full_power": "900",
            "half_capacity": "1700",
            "half_power": "380",
        })
        section.recalculate_now()
        # Compact result grid should have rows populated.
        assert section.result_table.rows
        # Copy text should contain "자동 계산 완료" and not "오류"
        copy_text = section.result_table.status_label.cget("text")
        assert "완료" in copy_text
        assert "오류" not in copy_text

    def test_recalculate_blocks_on_invalid_value(self, section) -> None:
        # Inject invalid text directly
        section.input_table.set_values({
            "full_capacity": "not_a_number",
            "full_power": "900",
            "half_capacity": "1700",
            "half_power": "380",
        })
        section.recalculate_now()
        # Copy text should contain an error message
        copy_text = section.result_table.status_label.cget("text")
        assert "오류" in copy_text or "error" in copy_text.lower()


class TestUndoBehavior:
    """Undo restores original value after invalid text input."""

    def test_undo_restores_original_value(self, section) -> None:
        ctrl = section.input_controller
        section.input_table.set_values(ISO_TWO_POINT_SAMPLE_VALUES)
        # Focus and enter edit mode on cell (0, 0)
        ctrl.select((0, 0))
        ctrl._enter_edit_mode((0, 0))
        section.input_table.update_idletasks()

        # First check the current value (default full_capacity: "3600")
        assert ctrl.table.text_at_position((0, 0)) == "3600"

        # Mutate value by triggering entry edit and focus out
        entry = section.input_table.editable_entries["full_capacity"]
        entry.delete(0, "end")
        entry.insert(0, "invalid_val")
        ctrl._focus_out(None)

        assert ctrl.table.text_at_position((0, 0)) == "invalid_val"

        # Trigger undo
        ctrl._undo_last()
        assert ctrl.table.text_at_position((0, 0)) == "3600"


class TestSharedTableVisualFoundation:
    def test_iso_input_uses_flat_shared_grid_surface(self, section) -> None:
        table = section.input_table
        assert table.visual_style == "shared"
        assert table.table_frame.outer_edge_policy == "flat_low_contrast"
        assert int(table.table_frame.cget("borderwidth")) == 0
        assert table.header_cells["full"].surface_role == "header_cell"

    def test_result_uses_compact_grid_and_preserves_logical_data(self, section) -> None:
        section.input_table.set_values(ISO_TWO_POINT_SAMPLE_VALUES)
        section.recalculate_now()
        grid = section.result_table.table
        assert grid.surface_role == "two_point_comparison_table"
        assert grid.frame.winfo_class() == "Frame"
        assert grid.frame.focus_policy == "visible"
        assert int(grid.frame.cget("takefocus")) == 1
        assert grid.logical_data() == (
            section.result_table.column_labels,
            section.result_table.rows,
        )
        assert grid.header_labels[0].alignment_role == "header_identity"
        assert grid.header_labels[1].alignment_role == "header_value"
        assert grid.value_labels[(0, 0)].alignment_role == "identity_text"
        assert grid.value_labels[(0, 1)].alignment_role == "numeric_result"

    def test_result_whole_table_copy_matches_export_contract(self, section) -> None:
        section.input_table.set_values(ISO_TWO_POINT_SAMPLE_VALUES)
        section.recalculate_now()
        headers, rows = section.result_table.table_export_data()
        section.result_table.table.copy()
        assert section.result_table.table.frame.clipboard_get() == "\n".join(
            ["\t".join(headers), *("\t".join(row) for row in rows)]
        )
