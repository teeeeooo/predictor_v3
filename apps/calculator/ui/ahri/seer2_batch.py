"""Product-aware AHRI SEER2 batch matrix specification and row handler."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from apps.calculator.application.ahri import (
    AHRI_SEER2_PRODUCT_POINT_ORDER,
    AhriSeer2Adapter,
    AhriSeer2Options,
)
from apps.calculator.ui.batch.matrix_models import (
    BatchMatrixSpec,
    MatrixMeasurementPointSpec,
    MatrixPhysicalRowType,
)
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.layout_constants import (
    BATCH_MATRIX_POINT_WIDTH_CHARS,
    BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS,
)

__all__ = [
    "AHRI_SEER2_BATCH_SPEC",
    "AhriSeer2BatchCommonInputs",
    "AhriSeer2BatchHandler",
    "AhriSeer2BatchResult",
    "build_ahri_seer2_batch_spec",
]

_PHYSICAL_ROWS = (MatrixPhysicalRowType.CAPACITY, MatrixPhysicalRowType.POWER)
_ROW_TYPE_LABELS = MappingProxyType(
    {
        MatrixPhysicalRowType.CAPACITY: "Capacity",
        MatrixPhysicalRowType.POWER: "Power",
    }
)


def _measurement_point(point: str) -> MatrixMeasurementPointSpec:
    return MatrixMeasurementPointSpec(
        key=point,
        label=point,
        input_keys_by_row_type=MappingProxyType(
            {
                MatrixPhysicalRowType.CAPACITY: f"capacity_{point}",
                MatrixPhysicalRowType.POWER: f"power_{point}",
            }
        ),
        width_chars=BATCH_MATRIX_POINT_WIDTH_CHARS,
    )


def build_ahri_seer2_batch_spec(product_classification: str) -> BatchMatrixSpec:
    try:
        points = AHRI_SEER2_PRODUCT_POINT_ORDER[product_classification]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported AHRI SEER2 batch product: {product_classification!r}"
        ) from exc
    if product_classification == "variable_capacity":
        profile_key = "ahri_seer2"
        result_metrics = (
            ("seer2", "SEER2", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        )
    else:
        profile_key = f"ahri_seer2_{product_classification}"
        result_metrics = (
            ("raw_seer2", "Raw SEER2", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
            (
                "published_seer2",
                "Published SEER2",
                BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS,
            ),
            (
                "total_cooling",
                "Total Cooling [kBtu]",
                BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS,
            ),
            (
                "total_energy",
                "Total Energy [kWh]",
                BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS,
            ),
        )
    return BatchMatrixSpec(
        profile_key=profile_key,
        title="AHRI 210/240 SEER2 Batch Matrix",
        physical_rows=_PHYSICAL_ROWS,
        row_type_labels=_ROW_TYPE_LABELS,
        measurement_points=tuple(_measurement_point(point) for point in points),
        result_metrics=result_metrics,
    )


AHRI_SEER2_BATCH_SPEC = build_ahri_seer2_batch_spec("variable_capacity")


@dataclass(frozen=True)
class AhriSeer2BatchCommonInputs:
    system_type: str
    product_classification: str = "variable_capacity"
    options: AhriSeer2Options | None = None


@dataclass(frozen=True)
class AhriSeer2BatchResult:
    values: dict[str, str]
    state: BatchRowState


class AhriSeer2BatchHandler:
    """Calculate one active-product SEER2 batch case through the UI adapter."""

    def __init__(
        self,
        common_inputs: AhriSeer2BatchCommonInputs,
        *,
        adapter: AhriSeer2Adapter | None = None,
    ) -> None:
        self._common_inputs = common_inputs
        self._adapter = adapter or AhriSeer2Adapter()
        self.spec = build_ahri_seer2_batch_spec(
            common_inputs.product_classification
        )

    def calculate_row(self, row: Mapping[str, str]) -> AhriSeer2BatchResult:
        text_values = {
            key: str(row.get(key, "")).strip() for key in self.spec.input_keys
        }
        if not all(text_values.values()):
            return self._blank_result(BatchRowState.PENDING)
        try:
            if self._common_inputs.product_classification == "variable_capacity":
                summary = self._adapter.calculate(
                    text_values,
                    system_type=self._common_inputs.system_type,
                )
            else:
                summary = self._adapter.calculate(
                    text_values,
                    system_type=self._common_inputs.system_type,
                    product_classification=self._common_inputs.product_classification,
                    options=self._common_inputs.options,
                )
            if summary is None:
                return self._blank_result(BatchRowState.PENDING)
            if self._common_inputs.product_classification == "variable_capacity":
                values = {"seer2": f"{summary.seer2:.3f}"}
            else:
                values = {
                    "raw_seer2": f"{summary.raw_seer2:.6f}",
                    "published_seer2": f"{summary.published_seer2:.2f}",
                    "total_cooling": f"{summary.total_cooling_kbtu:.3f}",
                    "total_energy": f"{summary.total_energy_kwh:.3f}",
                }
            return AhriSeer2BatchResult(
                values=values, state=BatchRowState.OK
            )
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            return self._blank_result(BatchRowState.ERROR)

    def _blank_result(self, state: BatchRowState) -> AhriSeer2BatchResult:
        return AhriSeer2BatchResult(
            values={key: "" for key, _label, _width in self.spec.result_metrics},
            state=state,
        )
