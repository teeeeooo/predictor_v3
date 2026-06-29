"""Hong Kong CSPF row-per-case batch calculation spec."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from apps.calculator.application.hong_kong_cspf import HongKongCspfUseCase
from apps.calculator.ui.batch.models import (
    BatchColumnRole,
    BatchColumnSpec,
    BatchProfileSpec,
    BatchRowState,
)


CASE = "case"
DECLARED = "declared_capacity"
FULL_CAPACITY = "full_capacity"
FULL_POWER = "full_power"
HALF_CAPACITY = "half_capacity"
HALF_POWER = "half_power"
CSPF = "cspf"
CSEC = "csec"
STATUS = "status"
_REQUIRED_INPUT_KEYS = (DECLARED, FULL_CAPACITY, FULL_POWER, HALF_CAPACITY, HALF_POWER)


HONG_KONG_CSPF_BATCH_SPEC = BatchProfileSpec(
    profile_key="hong_kong_cspf",
    title="Hong Kong CSPF Batch",
    columns=(
        BatchColumnSpec(DECLARED, "Declared", BatchColumnRole.INPUT, width_chars=12),
        BatchColumnSpec(FULL_CAPACITY, "35 Full Cap", BatchColumnRole.INPUT, width_chars=12),
        BatchColumnSpec(FULL_POWER, "35 Full Power", BatchColumnRole.INPUT, width_chars=13),
        BatchColumnSpec(HALF_CAPACITY, "35 Half Cap", BatchColumnRole.INPUT, width_chars=12),
        BatchColumnSpec(HALF_POWER, "35 Half Power", BatchColumnRole.INPUT, width_chars=13),
        BatchColumnSpec(CSPF, "CSPF", BatchColumnRole.RESULT, width_chars=9),
        BatchColumnSpec(CSEC, "CSEC", BatchColumnRole.RESULT, width_chars=10),
    ),
    default_rows=(
        {
            DECLARED: "3500",
            FULL_CAPACITY: "3600",
            FULL_POWER: "900",
            HALF_CAPACITY: "1700",
            HALF_POWER: "380",
        },
        {},
        {},
        {},
        {},
    ),
)


@dataclass(frozen=True)
class BatchCalculationResult:
    values: dict[str, str]
    state: BatchRowState


class HongKongCspfBatchHandler:
    spec = HONG_KONG_CSPF_BATCH_SPEC

    def __init__(self, region_label: str = "Hong Kong") -> None:
        self._region_label = region_label
        self._usecase = HongKongCspfUseCase()

    def calculate_row(self, row: Mapping[str, str]) -> BatchCalculationResult:
        if not _has_complete_required_inputs(row):
            return _blank_result()
        try:
            result = self._usecase.calculate(
                row,
                region_label=self._region_label,
            )
            if not result.is_ok:
                return _blank_result(BatchRowState.ERROR)
            fields = dict(result.summary_fields)
            return BatchCalculationResult(
                values={
                    CSPF: fields.get("CSPF", "-"),
                    CSEC: fields.get("CSEC [kWh]", "-"),
                },
                state=BatchRowState.OK,
            )
        except Exception:
            return _blank_result(BatchRowState.ERROR)


def _has_complete_required_inputs(row: Mapping[str, str]) -> bool:
    return all(str(row.get(key, "")).strip() for key in _REQUIRED_INPUT_KEYS)


def _blank_result(state: BatchRowState = BatchRowState.PENDING) -> BatchCalculationResult:
    return BatchCalculationResult(values={CSPF: "", CSEC: ""}, state=state)
