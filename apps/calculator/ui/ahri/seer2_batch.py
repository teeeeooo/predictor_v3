"""Headless AHRI SEER2 batch matrix specification and row handler."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from apps.calculator.application.ahri import (
    AHRI_SEER2_POINT_ORDER,
    AhriSeer2Adapter,
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


AHRI_SEER2_BATCH_SPEC = BatchMatrixSpec(
    profile_key="ahri_seer2",
    title="AHRI 210/240 SEER2 Batch Matrix",
    physical_rows=_PHYSICAL_ROWS,
    row_type_labels=_ROW_TYPE_LABELS,
    measurement_points=tuple(
        _measurement_point(point) for point in AHRI_SEER2_POINT_ORDER
    ),
    result_metrics=(
        ("seer2", "SEER2", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
    ),
)


@dataclass(frozen=True)
class AhriSeer2BatchCommonInputs:
    system_type: str


@dataclass(frozen=True)
class AhriSeer2BatchResult:
    values: dict[str, str]
    state: BatchRowState


class AhriSeer2BatchHandler:
    """Calculate one AHRI SEER2 batch case through the main UI adapter."""

    spec = AHRI_SEER2_BATCH_SPEC

    def __init__(
        self,
        common_inputs: AhriSeer2BatchCommonInputs,
        *,
        adapter: AhriSeer2Adapter | None = None,
    ) -> None:
        self._common_inputs = common_inputs
        self._adapter = adapter or AhriSeer2Adapter()

    def calculate_row(self, row: Mapping[str, str]) -> AhriSeer2BatchResult:
        text_values = {
            key: str(row.get(key, "")).strip() for key in self.spec.input_keys
        }
        if not all(text_values.values()):
            return self._blank_result(BatchRowState.PENDING)
        try:
            summary = self._adapter.calculate(
                text_values,
                system_type=self._common_inputs.system_type,
            )
            if summary is None:
                return self._blank_result(BatchRowState.PENDING)
            return AhriSeer2BatchResult(
                values={"seer2": f"{summary.seer2:.3f}"},
                state=BatchRowState.OK,
            )
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            return self._blank_result(BatchRowState.ERROR)

    @staticmethod
    def _blank_result(state: BatchRowState) -> AhriSeer2BatchResult:
        return AhriSeer2BatchResult(values={"seer2": ""}, state=state)
