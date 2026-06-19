"""Headless EN14825 SCOP batch matrix specification and row handler."""

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
from apps.calculator.ui.en14825.scop_adapter import ScopAdapter
from apps.calculator.ui.en14825.scop_models import ScopPointInput
from apps.calculator.ui.table_grid_model import parse_numeric_cell

__all__ = [
    "En14825ScopBatchCommonInputs",
    "En14825ScopBatchHandler",
    "En14825ScopBatchResult",
    "build_en14825_scop_batch_spec",
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


def _format_point_label(point_key: str, temperature: object) -> str:
    value = float(temperature)
    temperature_text = f"{value:g}"
    return f"{point_key} ({temperature_text}°C)"


def build_en14825_scop_batch_spec(
    climate: str,
    tbiv_temp_c: float | None = None,
    tol_temp_c: float | None = None,
    *,
    adapter: ScopAdapter | None = None,
) -> BatchMatrixSpec:
    """Build the matrix from adapter-owned SCOP point availability."""
    resolved_adapter = adapter if adapter is not None else ScopAdapter()
    availability = resolved_adapter.resolve_point_availability(
        climate,
        tbiv_temp_c,
        tol_temp_c,
    )
    temperatures = availability["resolved_temperatures"]
    points = [_measurement_point("p_design_h", "Pdesignh", "p_design_h", None)]
    for point_key in availability["required_independent_points"]:
        field_key = point_key.lower()
        points.append(
            _measurement_point(
                point_key,
                _format_point_label(point_key, temperatures[point_key]),
                f"{field_key}_capacity",
                f"{field_key}_power",
            )
        )

    return BatchMatrixSpec(
        profile_key="en14825_scop",
        title="EN14825 SCOP Batch Matrix",
        physical_rows=_PHYSICAL_ROWS,
        row_type_labels=_ROW_TYPE_LABELS,
        measurement_points=tuple(points),
        result_metrics=(
            ("scop", "SCOP", 9),
            ("qh_kwh", "QH [kWh]", 11),
        ),
    )


@dataclass(frozen=True)
class En14825ScopBatchCommonInputs:
    climate: str
    tbiv_temp_c: float | None = None
    tol_temp_c: float | None = None
    cd: float | None = None
    appliance_type: str | None = None
    p_to_w: float = 0.0
    p_sb_w: float = 0.0
    p_ck_w: float = 0.0
    p_off_w: float = 0.0


@dataclass(frozen=True)
class En14825ScopBatchResult:
    values: dict[str, str]
    state: BatchRowState


class En14825ScopBatchHandler:
    """Calculate one tested-only EN14825 SCOP batch case."""

    def __init__(
        self,
        common_inputs: En14825ScopBatchCommonInputs,
        *,
        adapter: ScopAdapter | None = None,
    ) -> None:
        self._common_inputs = common_inputs
        self._adapter = adapter if adapter is not None else ScopAdapter()
        self.spec = build_en14825_scop_batch_spec(
            common_inputs.climate,
            common_inputs.tbiv_temp_c,
            common_inputs.tol_temp_c,
            adapter=self._adapter,
        )
        self._point_keys = tuple(
            point.key for point in self.spec.measurement_points[1:]
        )
        self._required_keys = self.spec.input_keys

    def calculate_row(self, row: Mapping[str, str]) -> En14825ScopBatchResult:
        text_values = {
            key: str(row.get(key, "")).strip() for key in self._required_keys
        }
        if not any(text_values.values()) or not all(text_values.values()):
            return self._blank_result(BatchRowState.PENDING)

        try:
            numeric = {
                key: parse_numeric_cell(value) for key, value in text_values.items()
            }
            points = {
                point_key: ScopPointInput(
                    tested_capacity=numeric[f"{point_key.lower()}_capacity"],
                    tested_power=numeric[f"{point_key.lower()}_power"],
                )
                for point_key in self._point_keys
            }
            common = self._common_inputs
            summary = self._adapter.calculate(
                inputs=points,
                p_design_h_w=numeric["p_design_h"],
                climate=common.climate,
                p_to_w=common.p_to_w,
                p_sb_w=common.p_sb_w,
                p_ck_w=common.p_ck_w,
                p_off_w=common.p_off_w,
                cd=common.cd,
                appliance_type=common.appliance_type,
                tbiv_temp_c=common.tbiv_temp_c,
                tol_temp_c=common.tol_temp_c,
            )
            if (
                summary.status_code != "complete"
                or summary.tested_scop is None
                or summary.tested_qh_kwh is None
            ):
                return self._blank_result(BatchRowState.ERROR)
            return En14825ScopBatchResult(
                values={
                    "scop": f"{summary.tested_scop:.2f}",
                    "qh_kwh": f"{summary.tested_qh_kwh:.1f}",
                },
                state=BatchRowState.OK,
            )
        except Exception:
            return self._blank_result(BatchRowState.ERROR)

    @staticmethod
    def _blank_result(state: BatchRowState) -> En14825ScopBatchResult:
        return En14825ScopBatchResult(
            values={"scop": "", "qh_kwh": ""},
            state=state,
        )
