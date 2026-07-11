"""Focused tests for IsoIseer2PointSection controller switch.

Verifies that IsoIseer2PointSection instantiates and behaves correctly
with TkTableController after the switch from ExcelLikeTableController.
"""

from __future__ import annotations

import pytest

from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table.compact_result_grid import CompactResultGrid
from apps.calculator.ui.table.visual_policy import SemanticTone, TkTableVisualPolicy
from apps.calculator.ui.table_clipboard import encode_table_tsv
from apps.calculator.ui.layout_constants import (
    RESULT_VALUE_BG,
    TABLE_ERROR_BG,
    TABLE_INVALID_BG,
    TABLE_PASS_BG,
)
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
    def test_calculated_and_pass_keep_distinct_meaning_with_same_background(
        self,
    ) -> None:
        policy = TkTableVisualPolicy()
        assert SemanticTone.CALCULATED is not SemanticTone.PASS
        assert policy.background(SemanticTone.CALCULATED) == TABLE_PASS_BG
        assert policy.background(SemanticTone.PASS) == TABLE_PASS_BG
        assert policy.background(SemanticTone.FAIL) == TABLE_ERROR_BG
        assert policy.background(SemanticTone.DEFAULT) == RESULT_VALUE_BG
        assert policy.background(SemanticTone.INVALID) == TABLE_INVALID_BG

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
        assert grid.frame.bind("<Control-c>")
        assert grid.frame.bind("<Command-c>")
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
        assert grid.value_labels[(0, 0)].semantic_tone == "default"
        for row in range(len(grid.rows)):
            for column in range(1, len(grid.headers)):
                label = grid.value_labels[(row, column)]
                assert label.semantic_tone == "calculated"
                assert label.cget("background") == TABLE_PASS_BG

    def test_result_whole_table_copy_matches_export_contract(self, section) -> None:
        section.input_table.set_values(ISO_TWO_POINT_SAMPLE_VALUES)
        section.recalculate_now()
        headers, rows = section.result_table.table_export_data()
        section.result_table.table.copy()
        assert section.result_table.table.frame.clipboard_get() == "\n".join(
            ["\t".join(headers), *("\t".join(row) for row in rows)]
        )

    @pytest.mark.parametrize("target_kind", ("header", "body"))
    def test_visible_cell_click_focuses_grid_and_keyboard_copy(
        self, section, tk_root, target_kind: str
    ) -> None:
        section.input_table.set_values(ISO_TWO_POINT_SAMPLE_VALUES)
        section.recalculate_now()
        tk_root.deiconify()
        tk_root.update_idletasks()
        grid = section.result_table.table
        target = (
            grid.header_labels[0]
            if target_kind == "header"
            else grid.value_labels[(0, 0)]
        )

        target.event_generate("<Button-1>")
        assert tk_root.focus_get() == grid.frame

        grid.frame.event_generate("<Control-c>")
        assert grid.frame.clipboard_get() == encode_table_tsv(grid.headers, grid.rows)

    def test_multiple_grids_under_one_parent_are_independent(self, tk_root) -> None:
        first = CompactResultGrid(tk_root, headers=("First", "Value"))
        second = CompactResultGrid(tk_root, headers=("Second", "Value"))
        first.pack()
        second.pack()
        first.set_rows((("A", "1"),))
        second.set_rows((("B", "2"),))
        tk_root.deiconify()
        tk_root.update_idletasks()

        assert str(first.frame) != str(second.frame)
        assert first.headers == ("First", "Value")
        assert second.headers == ("Second", "Value")
        assert first.rows == (("A", "1"),)
        assert second.rows == (("B", "2"),)
        assert first.value_cells[(0, 0)] is not second.value_cells[(0, 0)]

        first.header_labels[0].event_generate("<Button-1>")
        assert tk_root.focus_get() == first.frame
        second.value_labels[(0, 0)].event_generate("<Button-1>")
        assert tk_root.focus_get() == second.frame

        first.set_rows((("A2", "3"),))
        assert second.rows == (("B", "2"),)
        first.clear()
        assert first.value_cells == {}
        assert second.value_cells

    def test_tsv_and_copy_delegate_to_shared_clipboard_encoding(self, tk_root) -> None:
        grid = CompactResultGrid(tk_root, headers=("Name", "Value"))
        grid.set_rows((("None-safe", None),))  # type: ignore[arg-type]
        expected = encode_table_tsv(grid.headers, grid.rows)

        assert grid.as_tsv() == expected == "Name\tValue\nNone-safe\t"
        grid.copy()
        assert grid.frame.clipboard_get() == expected
