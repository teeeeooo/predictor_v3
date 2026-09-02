"""Appendix M batch matrix specs and row calculation handlers."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from collections.abc import Mapping

from apps.calculator.application.ahri_m import AhriHspfAdapter, AhriHspfOptions, AhriSeerAdapter
from apps.calculator.ui.ahri_m.points import (
    ahri_m_hspf_ui_point_label,
    ahri_m_seer_ui_point_label,
)
from apps.calculator.ui.batch.matrix_models import BatchMatrixSpec, MatrixMeasurementPointSpec, MatrixPhysicalRowType
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.layout_constants import BATCH_MATRIX_POINT_WIDTH_CHARS, BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS, BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS

_ROWS = (MatrixPhysicalRowType.CAPACITY, MatrixPhysicalRowType.POWER)
_ROW_LABELS = MappingProxyType({MatrixPhysicalRowType.CAPACITY: "Capacity", MatrixPhysicalRowType.POWER: "Power"})


def _point(point: str, label: str | None = None) -> MatrixMeasurementPointSpec:
    return MatrixMeasurementPointSpec(
        point, label or point,
        MappingProxyType({MatrixPhysicalRowType.CAPACITY: f"capacity_{point}", MatrixPhysicalRowType.POWER: f"power_{point}"}),
        BATCH_MATRIX_POINT_WIDTH_CHARS,
    )


AHRI_M_SEER_BATCH_SPEC = BatchMatrixSpec(
    profile_key="ahri_m_seer", title="AHRI 210/240 M SEER Batch Matrix",
    physical_rows=_ROWS, row_type_labels=_ROW_LABELS,
    measurement_points=tuple(
        _point(point, ahri_m_seer_ui_point_label(point))
        for point in ("A2", "B2", "EV", "B1", "F1")
    ),
    result_metrics=(("seer", "SEER", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS), ("cstl", "CSTL", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS), ("csec", "CSEC", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS)),
)
AHRI_M_HSPF_BATCH_SPEC = BatchMatrixSpec(
    profile_key="ahri_m_hspf", title="AHRI 210/240 M HSPF Batch Matrix",
    physical_rows=_ROWS, row_type_labels=_ROW_LABELS,
    measurement_points=tuple(
        _point(point, ahri_m_hspf_ui_point_label(point))
        for point in ("H01", "H11", "H1N", "H2V", "H32", "H12", "H22")
    ),
    result_metrics=(
        ("hspf", "HSPF", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        ("dhr", "DHRmin", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
        ("load", "Heating Load [Btu/h]", max(BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS, len("Heating Load [Btu/h]"))),
        ("comp", "Compressor Input [W]", max(BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS, len("Compressor Input [W]"))),
        ("aux", "Auxiliary Input [W]", max(BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS, len("Auxiliary Input [W]"))),
    ),
)


@dataclass(frozen=True)
class BatchRowResult:
    values: dict[str, str]
    state: BatchRowState
    defrost_credit: float | None = None


def _blank(spec: BatchMatrixSpec, state: BatchRowState) -> BatchRowResult:
    return BatchRowResult({key: "" for key in spec.result_keys}, state)
class AhriMSeerBatchHandler:
    def __init__(self, cd: str, *, adapter: AhriSeerAdapter | None = None) -> None:
        self.cd = cd
        self.adapter = adapter or AhriSeerAdapter()

    def calculate_row(self, row: Mapping[str, str]) -> BatchRowResult:
        values = {key: str(row.get(key, "")).strip() for key in AHRI_M_SEER_BATCH_SPEC.input_keys}
        if not all(values.values()):
            return _blank(AHRI_M_SEER_BATCH_SPEC, BatchRowState.PENDING)
        values["cd"] = self.cd
        try:
            summary = self.adapter.calculate(values)
            if summary is None:
                return _blank(AHRI_M_SEER_BATCH_SPEC, BatchRowState.PENDING)
            return BatchRowResult(
                {
                    "seer": f"{summary.published_seer:.2f}",
                    "cstl": f"{summary.seasonal_cooling_numerator:.1f}",
                    "csec": f"{summary.seasonal_energy_denominator:.1f}",
                },
                BatchRowState.OK,
            )
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            return _blank(AHRI_M_SEER_BATCH_SPEC, BatchRowState.ERROR)
@dataclass(frozen=True)
class AhriMHspfBatchCommon:
    cd: str
    defrost_test_minutes: str
    defrost_max_minutes: str
    cut_out_c: str
    cut_in_c: str
    h1n_same_speed_as_h32: bool
    automatic_cutout: bool
    demand_defrost: bool


class AhriMHspfBatchHandler:
    def __init__(self, common: AhriMHspfBatchCommon, *, adapter: AhriHspfAdapter | None = None) -> None:
        self.common = common
        self.adapter = adapter or AhriHspfAdapter()

    def calculate_row(self, row: Mapping[str, str]) -> BatchRowResult:
        values = {key: str(row.get(key, "")).strip() for key in AHRI_M_HSPF_BATCH_SPEC.input_keys}
        required = tuple(f"{kind}_{point}" for point in ("H01", "H11", "H1N", "H2V", "H32") for kind in ("capacity", "power"))
        if not all(values.get(key, "") for key in required):
            return _blank(AHRI_M_HSPF_BATCH_SPEC, BatchRowState.PENDING)
        h12_pair = (values["capacity_H12"], values["power_H12"])
        h22_pair = (values["capacity_H22"], values["power_H22"])
        if (any(h12_pair) and not all(h12_pair)) or (
            any(h22_pair) and not all(h22_pair)
        ):
            return _blank(AHRI_M_HSPF_BATCH_SPEC, BatchRowState.ERROR)
        values.update(
            {
                "cd": self.common.cd,
                "defrost_test_minutes": self.common.defrost_test_minutes,
                "defrost_max_minutes": self.common.defrost_max_minutes,
                "cut_out_c": self.common.cut_out_c,
                "cut_in_c": self.common.cut_in_c,
            }
        )
        options = AhriHspfOptions(
            measured_h12=all(h12_pair),
            measured_h22=all(h22_pair),
            h1n_same_speed_as_h32=self.common.h1n_same_speed_as_h32,
            automatic_cutout=self.common.automatic_cutout,
            demand_defrost=self.common.demand_defrost,
        )
        try:
            summary = self.adapter.calculate(values, options=options)
            if summary is None:
                return _blank(AHRI_M_HSPF_BATCH_SPEC, BatchRowState.PENDING)
            return BatchRowResult(
                {
                    "hspf": f"{summary.published_hspf:.2f}",
                    "dhr": f"{summary.dhr_min_standardized:.0f}",
                    "load": f"{summary.heating_load_aggregate:.1f}",
                    "comp": f"{summary.compressor_energy_aggregate:.1f}",
                    "aux": f"{summary.resistance_energy_aggregate:.1f}",
                },
                BatchRowState.OK,
                defrost_credit=summary.defrost_credit,
            )
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            return _blank(AHRI_M_HSPF_BATCH_SPEC, BatchRowState.ERROR)
