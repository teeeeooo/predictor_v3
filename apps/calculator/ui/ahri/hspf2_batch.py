"""Headless AHRI HSPF2 dynamic batch specification and row handler."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from apps.calculator.ui.ahri.hspf2_adapter import (
    AHRI_HSPF2_POINT_ORDER,
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
    BATCH_MATRIX_RESULT_SOURCE_WIDTH_CHARS,
)

_PHYSICAL_ROWS = (MatrixPhysicalRowType.CAPACITY, MatrixPhysicalRowType.POWER)
_ROW_LABELS = MappingProxyType(
    {
        MatrixPhysicalRowType.CAPACITY: "Capacity",
        MatrixPhysicalRowType.POWER: "Power",
    }
)
_BATCH_SOURCE_LABELS = MappingProxyType(
    {
        "measured": "meas.",
        "calculated": "calc.",
        "not provided": "n/a",
    }
)


def _compact_source_label(source: str) -> str:
    try:
        return _BATCH_SOURCE_LABELS[source]
    except KeyError as exc:
        raise ValueError(f"Unsupported HSPF2 source label: {source}") from exc


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
    for point in AHRI_HSPF2_POINT_ORDER:
        is_enabled = enabled.get(point, True)
        points.append(
            MatrixMeasurementPointSpec(
                key=point,
                label=point,
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
            ("h12_source", "H12", BATCH_MATRIX_RESULT_SOURCE_WIDTH_CHARS),
            ("h22_source", "H22", BATCH_MATRIX_RESULT_SOURCE_WIDTH_CHARS),
            ("h42_source", "H42", BATCH_MATRIX_RESULT_SOURCE_WIDTH_CHARS),
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
                values={
                    "hspf2": f"{summary.hspf2:.3f}",
                    "h12_source": _compact_source_label(summary.h12_source),
                    "h22_source": _compact_source_label(summary.h22_source),
                    "h42_source": _compact_source_label(summary.h42_source),
                },
                state=BatchRowState.OK,
            )
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            return self._blank(BatchRowState.ERROR)

    @staticmethod
    def _blank(state: BatchRowState) -> AhriHspf2BatchResult:
        return AhriHspf2BatchResult(
            values={key: "" for key in ("hspf2", "h12_source", "h22_source", "h42_source")},
            state=state,
        )
