"""Brazil CSPF batch row calculation adapter."""

from __future__ import annotations

from collections.abc import Mapping

from apps.calculator.application.brazil_cspf import BrazilCspfUseCase
from apps.calculator.ui.batch.models import BatchRowState

from .schema import (
    BRAZIL_CSPF_MATRIX_SPEC,
    CALCULATED_29_BIN_EER,
    BrazilCspfBatchCalculationResult,
    FINAL,
    FULL_CAPACITY,
    FULL_POWER,
    HALF_29_CAPACITY,
    HALF_29_POWER,
    HALF_CAPACITY,
    HALF_POWER,
    MEASURED_29_HALF_EER,
    ROW_STATUS,
    RULE_1,
    RULE_2,
    THREE_POINT_CSEC,
    THREE_POINT_CSPF,
    THREE_POINT_CSTL,
    TWO_POINT_CSPF,
)


_REQUIRED_INPUT_KEYS = (
    FULL_CAPACITY,
    FULL_POWER,
    HALF_CAPACITY,
    HALF_POWER,
    HALF_29_CAPACITY,
    HALF_29_POWER,
)


class BrazilCspfBatchHandler:
    """Adapt one matrix row to the Brazil application usecase."""

    spec = BRAZIL_CSPF_MATRIX_SPEC

    def __init__(self, usecase: BrazilCspfUseCase | None = None) -> None:
        self._usecase = usecase or BrazilCspfUseCase()

    def calculate_row(
        self, row: Mapping[str, str]
    ) -> BrazilCspfBatchCalculationResult:
        if not _has_complete_inputs(row):
            return _blank_result(BatchRowState.PENDING, "PENDING")
        result = self._usecase.calculate(
            {key: str(row.get(key, "")) for key in _REQUIRED_INPUT_KEYS}
        )
        if not result.is_ok or len(result.rows) != 2 or len(result.rules) != 2:
            return _blank_result(BatchRowState.ERROR, "ERROR")
        three_point, two_point = result.rows
        rule_1, rule_2 = result.rules
        return BrazilCspfBatchCalculationResult(
            values={
                THREE_POINT_CSPF: three_point[1],
                THREE_POINT_CSTL: three_point[2],
                THREE_POINT_CSEC: three_point[3],
                TWO_POINT_CSPF: two_point[1],
                RULE_1: rule_1.status_text,
                MEASURED_29_HALF_EER: rule_2.left_value_text,
                CALCULATED_29_BIN_EER: rule_2.right_value_text,
                RULE_2: rule_2.status_text,
                FINAL: result.final_status or "",
                ROW_STATUS: "OK",
            },
            state=BatchRowState.OK,
        )


def _has_complete_inputs(row: Mapping[str, str]) -> bool:
    return all(str(row.get(key, "")).strip() for key in _REQUIRED_INPUT_KEYS)


def _blank_result(
    state: BatchRowState,
    row_status: str,
) -> BrazilCspfBatchCalculationResult:
    return BrazilCspfBatchCalculationResult(
        values={key: "" for key in BRAZIL_CSPF_MATRIX_SPEC.result_keys[:-1]}
        | {ROW_STATUS: row_status},
        state=state,
    )


__all__ = ["BrazilCspfBatchHandler"]
