"""Headless AHRI HSPF2 dynamic batch specification and row handler."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from apps.calculator.application.ahri import (
    AhriHspf2Adapter,
    AhriHspf2Options,
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

_PHYSICAL_ROWS = (MatrixPhysicalRowType.CAPACITY, MatrixPhysicalRowType.POWER)
_ROW_LABELS = MappingProxyType(
    {
        MatrixPhysicalRowType.CAPACITY: "Capacity",
        MatrixPhysicalRowType.POWER: "Power",
    }
)
AHRI_HSPF2_UI_POINT_ORDER = (
    "H01",
    "H11",
    "H2Int",
    "H32",
    "H42",
    "H1N",
    "H12",
    "H22",
)
AHRI_HSPF2_UI_POINT_LABELS = MappingProxyType(
    {
        "H2Int": "H2v",
        "H1N": "H1N(STD)",
    }
)


def ahri_hspf2_ui_point_label(point: str) -> str:
    return AHRI_HSPF2_UI_POINT_LABELS.get(point, point)


@dataclass(frozen=True)
class AhriHspf2BatchActiveOptions:
    region: str = "IV"
    h42_enabled: bool = True
    h12_enabled: bool = False
    h22_enabled: bool = False


@dataclass(frozen=True)
class AhriHspf2BatchCommonInputs:
    active: AhriHspf2BatchActiveOptions
    h1n_h32_same_hz: bool
    min_spd: bool
    numeric_values: Mapping[str, str]


@dataclass(frozen=True)
class AhriHspf2BatchResult:
    values: dict[str, str]
    state: BatchRowState


def build_ahri_hspf2_batch_spec(
    active: AhriHspf2BatchActiveOptions,
) -> BatchMatrixSpec:
    enabled = {
        "H42": active.h42_enabled,
        "H12": active.h12_enabled,
        "H22": active.h22_enabled,
    }
    points = [
        MatrixMeasurementPointSpec(
            key="A2",
            label="A2",
            input_keys_by_row_type=MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: "a2_capacity",
                    MatrixPhysicalRowType.POWER: None,
                }
            ),
            width_chars=BATCH_MATRIX_POINT_WIDTH_CHARS,
        )
    ]
    for point in AHRI_HSPF2_UI_POINT_ORDER:
        is_enabled = enabled.get(point, True)
        points.append(
            MatrixMeasurementPointSpec(
                key=point,
                label=ahri_hspf2_ui_point_label(point),
                input_keys_by_row_type=MappingProxyType(
                    {
                        MatrixPhysicalRowType.CAPACITY: (
                            f"capacity_{point}" if is_enabled else None
                        ),
                        MatrixPhysicalRowType.POWER: (
                            f"power_{point}" if is_enabled else None
                        ),
                    }
                ),
                width_chars=BATCH_MATRIX_POINT_WIDTH_CHARS,
            )
        )
    return BatchMatrixSpec(
        profile_key="ahri_hspf2",
        title="AHRI 210/240 HSPF2 Batch Matrix",
        physical_rows=_PHYSICAL_ROWS,
        row_type_labels=_ROW_LABELS,
        measurement_points=tuple(points),
        result_metrics=(
            ("hspf2", "HSPF2", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        ),
    )


class AhriHspf2BatchHandler:
    """Calculate one visible HSPF2 batch case through the main adapter."""

    def __init__(
        self,
        common: AhriHspf2BatchCommonInputs,
        *,
        adapter: AhriHspf2Adapter | None = None,
    ) -> None:
        self.common = common
        self.adapter = adapter or AhriHspf2Adapter()
        self.spec = build_ahri_hspf2_batch_spec(common.active)

    def calculate_row(self, row: Mapping[str, str]) -> AhriHspf2BatchResult:
        visible = {key: str(row.get(key, "")).strip() for key in self.spec.input_keys}
        if not all(visible.values()):
            return self._blank(BatchRowState.PENDING)
        values = dict(self.common.numeric_values)
        values.update(visible)
        options = AhriHspf2Options(
            region=self.common.active.region,
            measured_h42=self.common.active.h42_enabled,
            measured_h12=self.common.active.h12_enabled,
            measured_h22=self.common.active.h22_enabled,
            h1n_same_speed_as_h32=self.common.h1n_h32_same_hz,
            minimum_speed_limited=self.common.min_spd,
        )
        try:
            summary = self.adapter.calculate(values, options=options)
            if summary is None:
                return self._blank(BatchRowState.PENDING)
            return AhriHspf2BatchResult(
                values={"hspf2": f"{summary.hspf2:.3f}"},
                state=BatchRowState.OK,
            )
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            return self._blank(BatchRowState.ERROR)

    @staticmethod
    def _blank(state: BatchRowState) -> AhriHspf2BatchResult:
        return AhriHspf2BatchResult(values={"hspf2": ""}, state=state)
