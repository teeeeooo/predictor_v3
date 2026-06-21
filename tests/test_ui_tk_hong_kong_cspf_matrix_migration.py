"""Focused tests for Hong Kong CSPF matrix migration adapter and controller."""

from __future__ import annotations

from apps.calculator.ui.batch.matrix_models import (
    CSEC,
    CSPF,
    DECLARED_CAPACITY,
    FULL_CAPACITY,
    FULL_POWER,
    HALF_CAPACITY,
    HALF_POWER,
    HONG_KONG_CSPF_MATRIX_SPEC,
)
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.sections.hong_kong_cspf_batch_spec import (
    HONG_KONG_CSPF_BATCH_SPEC,
    HongKongCspfBatchHandler,
)
from apps.calculator.ui.batch_dialogs.profiles.hong_kong_cspf import (
    HongKongCspfMatrixController,
)
from tests.calculator_ui_sample_values import HONG_KONG_CSPF_SAMPLE_VALUES


class _HeadlessMatrixTable:
    """Headless stand-in for BatchMatrixTable (no Tk required)."""

    def __init__(self, cases: list[dict[str, str]] | None = None) -> None:
        self.spec = HONG_KONG_CSPF_MATRIX_SPEC
        self.cases: list[dict[str, str]] = (
            [dict(c) for c in cases]
            if cases is not None
            else [dict(c) for c in self.spec.default_cases]
        )
        self._results: dict[int, dict[str, str]] = {}

    def set_result(self, logical_index: int, values: dict[str, str]) -> None:
        self._results[logical_index] = dict(values)
        if logical_index < len(self.cases):
            self.cases[logical_index].update(values)


def _sample_cases() -> list[dict[str, str]]:
    return [dict(HONG_KONG_CSPF_SAMPLE_VALUES), {}, {}, {}, {}]


def test_matrix_adapter_input_keys_match_existing_batch_contract():
    assert HONG_KONG_CSPF_MATRIX_SPEC.input_keys == HONG_KONG_CSPF_BATCH_SPEC.input_keys


def test_matrix_adapter_result_keys_match_existing_batch_contract():
    assert HONG_KONG_CSPF_MATRIX_SPEC.result_keys == HONG_KONG_CSPF_BATCH_SPEC.result_keys


def test_matrix_controller_calculates_each_logical_case():
    table = _HeadlessMatrixTable(_sample_cases())
    handler = HongKongCspfBatchHandler("Hong Kong")
    controller = HongKongCspfMatrixController(table, handler)

    summary = controller.recalculate()

    assert summary.valid_rows == 1
    assert summary.blank_rows == 4
    assert summary.error_rows == 0


def test_matrix_controller_result_matches_handler_direct_call():
    table = _HeadlessMatrixTable(_sample_cases())
    handler = HongKongCspfBatchHandler("Hong Kong")
    controller = HongKongCspfMatrixController(table, handler)

    controller.recalculate()

    direct_result = handler.calculate_row(table.cases[0])
    assert table._results[0][CSPF] == direct_result.values[CSPF]
    assert table._results[0][CSEC] == direct_result.values[CSEC]
    assert direct_result.values[CSPF] == "4.939"


def test_matrix_default_cases_are_empty():
    table = _HeadlessMatrixTable()
    assert len(table.cases) == 5
    assert all(not case for case in table.cases)


def test_matrix_controller_blank_cases_produce_blank_results():
    table = _HeadlessMatrixTable([{}, {}, {}])
    handler = HongKongCspfBatchHandler("Hong Kong")
    controller = HongKongCspfMatrixController(table, handler)

    summary = controller.recalculate()

    assert summary.valid_rows == 0
    assert summary.blank_rows == 3
    for index in range(3):
        assert table._results[index][CSPF] == ""
        assert table._results[index][CSEC] == ""


def test_matrix_controller_invalid_input_produces_error_state():
    table = _HeadlessMatrixTable([
        {
            DECLARED_CAPACITY: "3500",
            FULL_CAPACITY: "3600",
            FULL_POWER: "not-a-number",
            HALF_CAPACITY: "1700",
            HALF_POWER: "380",
        }
    ])
    handler = HongKongCspfBatchHandler("Hong Kong")
    controller = HongKongCspfMatrixController(table, handler)

    summary = controller.recalculate()

    assert summary.valid_rows == 0
    assert summary.error_rows == 1
    assert table._results[0][CSPF] == ""


def test_matrix_controller_multiple_cases_with_mixed_states():
    table = _HeadlessMatrixTable([
        {
            DECLARED_CAPACITY: "3500",
            FULL_CAPACITY: "3600",
            FULL_POWER: "900",
            HALF_CAPACITY: "1700",
            HALF_POWER: "380",
        },
        {},
        {
            DECLARED_CAPACITY: "3500",
            FULL_CAPACITY: "bad",
            FULL_POWER: "900",
            HALF_CAPACITY: "1700",
            HALF_POWER: "380",
        },
    ])
    handler = HongKongCspfBatchHandler("Hong Kong")
    controller = HongKongCspfMatrixController(table, handler)

    summary = controller.recalculate()

    assert summary.valid_rows == 1
    assert summary.blank_rows == 1
    assert summary.error_rows == 1


def test_matrix_result_display_text_first_row_only():
    spec = HONG_KONG_CSPF_MATRIX_SPEC
    case_data = {
        DECLARED_CAPACITY: "3500",
        FULL_CAPACITY: "3600",
        FULL_POWER: "900",
        HALF_CAPACITY: "1700",
        HALF_POWER: "380",
        CSPF: "4.939",
        CSEC: "729.0",
    }

    assert spec.display_text((0, 5), case_data, case_data) == "4.939"
    assert spec.display_text((1, 5), case_data, case_data) == ""
    assert spec.display_text((0, 6), case_data, case_data) == "729.0"
    assert spec.display_text((1, 6), case_data, case_data) == ""


def test_matrix_second_row_case_and_result_cells_are_blank_read_only():
    spec = HONG_KONG_CSPF_MATRIX_SPEC

    assert spec.is_blank_read_only((1, 0))
    assert spec.is_blank_read_only((1, 5))
    assert spec.is_blank_read_only((1, 6))
    assert not spec.is_editable((1, 0))
    assert not spec.is_editable((1, 5))
    assert not spec.is_editable((1, 6))


def test_matrix_add_case_produces_two_physical_rows():
    spec = HONG_KONG_CSPF_MATRIX_SPEC
    initial_count = 5
    assert spec.physical_row_count(initial_count) == 10
    assert spec.physical_row_count(initial_count + 1) == 12


def test_matrix_remove_case_preserves_minimum_one():
    spec = HONG_KONG_CSPF_MATRIX_SPEC
    assert spec.physical_row_count(1) == 2
    assert spec.physical_row_count(0) == 0


def test_matrix_editable_cells_are_input_only():
    spec = HONG_KONG_CSPF_MATRIX_SPEC
    for row in range(spec.physical_row_count(1)):
        for col in range(spec.column_count):
            cell = spec.resolve_cell((row, col))
            if cell.kind.value == "input":
                assert spec.is_editable((row, col))
            else:
                assert not spec.is_editable((row, col))


def test_matrix_restore_snapshot_accepts_list():
    spec = HONG_KONG_CSPF_MATRIX_SPEC
    snapshot_list = [
        {DECLARED_CAPACITY: "4200", FULL_CAPACITY: "4300"},
        {},
    ]
    restored = spec.restore_cases(snapshot_list)
    assert len(restored) == 2
    assert restored[0][DECLARED_CAPACITY] == "4200"


def test_matrix_handler_calculate_row_preserves_existing_contract():
    handler = HongKongCspfBatchHandler("Hong Kong")
    row = dict(HONG_KONG_CSPF_BATCH_SPEC.default_rows[0])
    result = handler.calculate_row(row)
    assert result.state is BatchRowState.OK
    assert result.values[CSPF] == "4.939"
