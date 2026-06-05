"""Hong Kong CSPF row-per-case batch calculation spec."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from core.calculator_dispatcher import create_calculator_for_profile
from ui_tk.batch_models import (
    BatchColumnRole,
    BatchColumnSpec,
    BatchProfileSpec,
    BatchRowState,
)
from ui_tk.profile_resolver import resolve_profile_id
from ui_tk.sections.iso16358_helpers import build_cspf_input
from ui_tk.sections.result_formatting import summarize_cspf_result
from ui_tk.table_grid_model import parse_numeric_cell


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

    def calculate_row(self, row: Mapping[str, str]) -> BatchCalculationResult:
        if not _has_complete_required_inputs(row):
            return _blank_result()
        try:
            measured, declared = build_cspf_input(
                full_capacity=_required_number(row, FULL_CAPACITY, "35 Full Cap"),
                full_power=_required_number(row, FULL_POWER, "35 Full Power"),
                half_capacity=_required_number(row, HALF_CAPACITY, "35 Half Cap"),
                half_power=_required_number(row, HALF_POWER, "35 Half Power"),
                declared_capacity=_required_number(row, DECLARED, "Declared"),
            )
            profile_id = resolve_profile_id(self._region_label, "CSPF")
            calc = create_calculator_for_profile(profile_id=profile_id)
            result = calc.calculate_cspf(measured, declared_capacity=declared)
            fields = dict(summarize_cspf_result(result).fields)
            return BatchCalculationResult(
                values={
                    CSPF: fields.get("CSPF", "-"),
                    CSEC: fields.get("CSEC [kWh]", "-"),
                },
                state=BatchRowState.OK,
            )
        except Exception:
            return _blank_result(BatchRowState.ERROR)


def _required_number(row: Mapping[str, str], key: str, label: str) -> float:
    try:
        return parse_numeric_cell(str(row.get(key, "")))
    except ValueError as exc:
        raise ValueError(f"{label}: {exc}") from exc


def _has_complete_required_inputs(row: Mapping[str, str]) -> bool:
    return all(str(row.get(key, "")).strip() for key in _REQUIRED_INPUT_KEYS)


def _blank_result(state: BatchRowState = BatchRowState.PENDING) -> BatchCalculationResult:
    return BatchCalculationResult(values={CSPF: "", CSEC: ""}, state=state)
