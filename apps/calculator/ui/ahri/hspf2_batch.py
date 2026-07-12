"""Product-aware AHRI HSPF2 dynamic batch specification and row handler."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from apps.calculator.application.ahri import (
    AHRI_HSPF2_DUAL_POINT_ORDER,
    AHRI_HSPF2_TRIPLE_POINT_ORDER,
    AhriHspf2Adapter,
    AhriHspf2Options,
)
from apps.calculator.ui.ahri.hspf2_points import (
    AHRI_HSPF2_UI_POINT_ORDER,
    ahri_hspf2_ui_point_label,
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


@dataclass(frozen=True)
class AhriHspf2BatchActiveOptions:
    region: str = "IV"
    h42_enabled: bool = True
    h12_enabled: bool = False
    h22_enabled: bool = False
    product_classification: str = "variable_capacity"
    h4_full_enabled: bool = False
    h2_low_enabled: bool = True
    h2_boost_enabled: bool = True
    h3_low_enabled: bool = True


@dataclass(frozen=True)
class AhriHspf2BatchCommonInputs:
    active: AhriHspf2BatchActiveOptions
    h1n_h32_same_hz: bool
    min_spd: bool
    numeric_values: Mapping[str, str]
    low_stage_lockout_enabled: bool = False
    defrost_mode: str = "explicit_override"


@dataclass(frozen=True)
class AhriHspf2BatchResult:
    values: dict[str, str]
    state: BatchRowState


def _point_spec(point: str, *, enabled: bool = True, label: str | None = None) -> MatrixMeasurementPointSpec:
    return MatrixMeasurementPointSpec(
        key=point,
        label=label or point,
        input_keys_by_row_type=MappingProxyType(
            {
                MatrixPhysicalRowType.CAPACITY: f"capacity_{point}" if enabled else None,
                MatrixPhysicalRowType.POWER: f"power_{point}" if enabled else None,
            }
        ),
        width_chars=BATCH_MATRIX_POINT_WIDTH_CHARS,
    )


def build_ahri_hspf2_batch_spec(active: AhriHspf2BatchActiveOptions) -> BatchMatrixSpec:
    product = active.product_classification
    points: list[MatrixMeasurementPointSpec] = [
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
    if product == "variable_capacity":
        enabled = {
            "H42": active.h42_enabled,
            "H12": active.h12_enabled,
            "H22": active.h22_enabled,
        }
        points.extend(
            _point_spec(
                point,
                enabled=enabled.get(point, True),
                label=ahri_hspf2_ui_point_label(point),
            )
            for point in AHRI_HSPF2_UI_POINT_ORDER
        )
        result_metrics = (("hspf2", "HSPF2", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),)
    elif product == "dual_stage":
        enabled = {"H2Low": active.h2_low_enabled, "H4Full": active.h4_full_enabled}
        points.extend(
            _point_spec(point, enabled=enabled.get(point, True))
            for point in AHRI_HSPF2_DUAL_POINT_ORDER
        )
        result_metrics = _multi_result_metrics()
    elif product == "triple_capacity_northern":
        enabled = {
            "H2Boost": active.h2_boost_enabled,
            "H3Low": active.h3_low_enabled,
        }
        points.extend(
            _point_spec(point, enabled=enabled.get(point, True))
            for point in AHRI_HSPF2_TRIPLE_POINT_ORDER
        )
        result_metrics = _multi_result_metrics()
    else:
        raise ValueError(f"Unsupported AHRI HSPF2 batch product: {product!r}")
    return BatchMatrixSpec(
        profile_key=f"ahri_hspf2_{product}",
        title="AHRI 210/240 HSPF2 Batch Matrix",
        physical_rows=_PHYSICAL_ROWS,
        row_type_labels=_ROW_LABELS,
        measurement_points=tuple(points),
        result_metrics=result_metrics,
    )


def _multi_result_metrics() -> tuple[tuple[str, str, int], ...]:
    return (
        ("raw_hspf2", "Raw HSPF2", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        ("published_hspf2", "Published HSPF2", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        ("total_heating", "Total Heating [kBtu]", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        ("compressor_energy", "Compressor [kWh]", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        ("resistance_energy", "Resistance [kWh]", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        ("total_energy", "Total Energy [kWh]", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
    )


class AhriHspf2BatchHandler:
    """Calculate one visible HSPF2 batch case through the product-aware adapter."""

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
        active = self.common.active
        options = AhriHspf2Options(
            region=active.region,
            measured_h42=active.h42_enabled,
            measured_h12=active.h12_enabled,
            measured_h22=active.h22_enabled,
            h1n_same_speed_as_h32=self.common.h1n_h32_same_hz,
            minimum_speed_limited=self.common.min_spd,
            product_classification=active.product_classification,
            measured_h4_full=active.h4_full_enabled,
            measured_h2_low=active.h2_low_enabled,
            measured_h2_boost=active.h2_boost_enabled,
            measured_h3_low=active.h3_low_enabled,
            low_stage_lockout_enabled=self.common.low_stage_lockout_enabled,
            defrost_mode=self.common.defrost_mode,
        )
        try:
            summary = self.adapter.calculate(values, options=options)
            if summary is None:
                return self._blank(BatchRowState.PENDING)
            if active.product_classification == "variable_capacity":
                result_values = {"hspf2": f"{summary.hspf2:.3f}"}
            else:
                result_values = {
                    "raw_hspf2": f"{summary.raw_hspf2:.6f}",
                    "published_hspf2": f"{summary.published_hspf2:.2f}",
                    "total_heating": f"{summary.total_heating_kbtu:.3f}",
                    "compressor_energy": f"{summary.compressor_energy_kwh:.3f}",
                    "resistance_energy": f"{summary.resistance_energy_kwh:.3f}",
                    "total_energy": f"{summary.total_energy_kwh:.3f}",
                }
            return AhriHspf2BatchResult(result_values, BatchRowState.OK)
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            return self._blank(BatchRowState.ERROR)

    def _blank(self, state: BatchRowState) -> AhriHspf2BatchResult:
        return AhriHspf2BatchResult(
            values={key: "" for key, _label, _width in self.spec.result_metrics},
            state=state,
        )
