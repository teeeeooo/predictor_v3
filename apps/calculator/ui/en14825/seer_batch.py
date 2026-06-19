"""Headless EN14825 SEER batch matrix specification and row handler."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from apps.calculator.ui.batch.matrix_models import (
    BatchMatrixSpec,
    MatrixMeasurementPointSpec,
    MatrixPhysicalRowType,
)
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.en14825.seer_adapter import SeerAdapter
from apps.calculator.ui.en14825.seer_models import SeerPointInput
from apps.calculator.ui.table_grid_model import parse_numeric_cell

__all__ = [
    "EN14825_SEER_BATCH_SPEC",
    "En14825SeerBatchCommonInputs",
    "En14825SeerBatchHandler",
    "En14825SeerBatchResult",
]


_PHYSICAL_ROWS = (
    MatrixPhysicalRowType.CAPACITY,
    MatrixPhysicalRowType.POWER,
)
_ROW_TYPE_LABELS = MappingProxyType(
    {
        MatrixPhysicalRowType.CAPACITY: "Capacity",
        MatrixPhysicalRowType.POWER: "Power",
    }
)


def _measurement_point(
    key: str,
    label: str,
    capacity_key: str,
    power_key: str | None,
) -> MatrixMeasurementPointSpec:
    return MatrixMeasurementPointSpec(
        key=key,
        label=label,
        input_keys_by_row_type=MappingProxyType(
            {
                MatrixPhysicalRowType.CAPACITY: capacity_key,
                MatrixPhysicalRowType.POWER: power_key,
            }
        ),
    )


EN14825_SEER_BATCH_SPEC = BatchMatrixSpec(
    profile_key="en14825_seer",
    title="EN14825 SEER Batch Matrix",
    physical_rows=_PHYSICAL_ROWS,
    row_type_labels=_ROW_TYPE_LABELS,
    measurement_points=(
        _measurement_point("p_design_c", "Pdesignc", "p_design_c", None),
        _measurement_point("a", "A (35°C)", "a_capacity", "a_power"),
        _measurement_point("b", "B (30°C)", "b_capacity", "b_power"),
        _measurement_point("c", "C (25°C)", "c_capacity", "c_power"),
        _measurement_point("d", "D (20°C)", "d_capacity", "d_power"),
    ),
    result_metrics=(
        ("seer", "SEER", 9),
        ("qc_kwh", "QC [kWh]", 11),
    ),
)


@dataclass(frozen=True)
class En14825SeerBatchCommonInputs:
    t_design_c: float
    cd: float
    appliance_type: str
    p_to_w: float = 0.0
    p_sb_w: float = 0.0
    p_ck_w: float = 0.0
    p_off_w: float = 0.0


@dataclass(frozen=True)
class En14825SeerBatchResult:
    values: dict[str, str]
    state: BatchRowState


class En14825SeerBatchHandler:
    """Calculate one tested-only EN14825 SEER batch case."""

    spec = EN14825_SEER_BATCH_SPEC
    _POINT_KEYS = ("a", "b", "c", "d")
    _REQUIRED_KEYS = (
        "p_design_c",
        "a_capacity",
        "a_power",
        "b_capacity",
        "b_power",
        "c_capacity",
        "c_power",
        "d_capacity",
        "d_power",
    )

    def __init__(
        self,
        common_inputs: En14825SeerBatchCommonInputs,
        *,
        adapter: SeerAdapter | None = None,
    ) -> None:
        self._common_inputs = common_inputs
        self._adapter = adapter if adapter is not None else SeerAdapter()

    def calculate_row(self, row: Mapping[str, str]) -> En14825SeerBatchResult:
        text_values = {
            key: str(row.get(key, "")).strip() for key in self._REQUIRED_KEYS
        }
        if not any(text_values.values()):
            return self._blank_result(BatchRowState.PENDING)
        if not all(text_values.values()):
            return self._blank_result(BatchRowState.PENDING)

        try:
            numeric = {
                key: parse_numeric_cell(value) for key, value in text_values.items()
            }
            points = {
                key.upper(): SeerPointInput(
                    tested_capacity=numeric[f"{key}_capacity"],
                    tested_power=numeric[f"{key}_power"],
                )
                for key in self._POINT_KEYS
            }
            common = self._common_inputs
            summary = self._adapter.calculate(
                inputs=points,
                p_design_c_w=numeric["p_design_c"],
                p_to_w=common.p_to_w,
                p_sb_w=common.p_sb_w,
                p_ck_w=common.p_ck_w,
                p_off_w=common.p_off_w,
                t_design_c=common.t_design_c,
                cd=common.cd,
                appliance_type=common.appliance_type,
            )
            if (
                summary.status_code != "complete"
                or summary.tested_seer is None
                or summary.tested_qc_kwh is None
            ):
                return self._blank_result(BatchRowState.ERROR)
            return En14825SeerBatchResult(
                values={
                    "seer": f"{summary.tested_seer:.2f}",
                    "qc_kwh": f"{summary.tested_qc_kwh:.1f}",
                },
                state=BatchRowState.OK,
            )
        except Exception:
            return self._blank_result(BatchRowState.ERROR)

    @staticmethod
    def _blank_result(state: BatchRowState) -> En14825SeerBatchResult:
        return En14825SeerBatchResult(
            values={"seer": "", "qc_kwh": ""},
            state=state,
        )
