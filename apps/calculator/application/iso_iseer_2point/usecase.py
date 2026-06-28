"""ISO/ISEER 2-point single-calculation application usecase."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from apps.calculator.adapters.core_calculator_dispatcher import (
    create_calculator_for_profile,
)
from apps.calculator.application.iso_iseer_2point.models import (
    IsoIseer2PointUseCaseResult,
    MeasuredPoints,
    ResultRow,
)
from apps.calculator.application.profile_resolver import (
    resolve_two_point_profile_id,
    two_point_profile_labels,
)


CalculatorFactory = Callable[..., object]

_INPUT_WAITING_STATUS = "입력 대기"
_INPUT_ERROR_STATUS = "입력 오류: 숫자 입력을 확인하세요."
_CALCULATION_ERROR_STATUS = "계산 오류"
_AUTO_CALC_DONE_STATUS = "자동 계산 완료"


class IsoIseer2PointUseCase:
    """Calculate ISO 16358-1 and India ISEER comparison rows."""

    def __init__(self, calculator_factory: CalculatorFactory = create_calculator_for_profile):
        self._calculator_factory = calculator_factory

    def calculate(self, raw_values: Mapping[str, str]) -> IsoIseer2PointUseCaseResult:
        """Calculate both ISO/ISEER profiles from raw input-table text values."""
        if not any(value.strip() for value in raw_values.values()):
            return IsoIseer2PointUseCaseResult(
                status="empty",
                status_text=_INPUT_WAITING_STATUS,
                detail_status=_INPUT_WAITING_STATUS,
            )

        try:
            measured = _parse_measured_points(raw_values)
        except ValueError:
            return IsoIseer2PointUseCaseResult(
                status="invalid",
                status_text=_INPUT_ERROR_STATUS,
                detail_status=_INPUT_ERROR_STATUS,
            )

        rows: list[ResultRow] = []
        detail_sources: dict[str, tuple[dict, ...]] = {}
        detail_summaries: dict[str, tuple[tuple[str, str], ...]] = {}
        errors: list[str] = []
        for profile_label in two_point_profile_labels():
            try:
                profile_id = resolve_two_point_profile_id(profile_label)
                calculator = self._calculator_factory(profile_id=profile_id)
                result = calculator.calculate_cspf(measured)
                row = _two_point_result_row(profile_label, measured, result)
                rows.append(row)
                detail_sources[profile_label] = _bin_details(result)
                detail_summaries[profile_label] = _summary_from_row(row)
            except Exception as exc:
                errors.append(f"{profile_label}: {type(exc).__name__}: {exc}")

        if errors:
            return IsoIseer2PointUseCaseResult(
                status="error",
                status_text="오류: " + " / ".join(errors),
                detail_status=_CALCULATION_ERROR_STATUS,
            )

        return IsoIseer2PointUseCaseResult(
            status="ok",
            status_text=_AUTO_CALC_DONE_STATUS,
            rows=tuple(rows),
            detail_sources=detail_sources,
            detail_summaries=detail_summaries,
            detail_status=None,
        )


def _parse_measured_points(raw_values: Mapping[str, str]) -> MeasuredPoints:
    values = {
        key: float(raw_values[key])
        for key in ("full_capacity", "full_power", "half_capacity", "half_power")
    }
    return {
        "35_full": {
            "capacity": values["full_capacity"],
            "power": values["full_power"],
        },
        "35_half": {
            "capacity": values["half_capacity"],
            "power": values["half_power"],
        },
    }


def _two_point_result_row(
    title: str,
    measured: MeasuredPoints,
    result: Mapping[str, object],
) -> ResultRow:
    return (
        title,
        _eer_value(measured, "35_full"),
        _eer_value(measured, "35_half"),
        _metric_value(result, "cspf"),
        _kwh_value(result, ("annual_cooling_kwh", "cstl_kwh", "cstl")),
        _kwh_value(result, ("annual_power_kwh", "csec_kwh", "csec")),
    )


def _summary_from_row(row: ResultRow) -> tuple[tuple[str, str], ...]:
    return (
        ("CSPF/ISEER", row[3]),
        ("CSTL [kWh]", row[4]),
        ("CSEC [kWh]", row[5]),
    )


def _eer_value(measured: MeasuredPoints, point_key: str) -> str:
    point = measured.get(point_key, {})
    capacity = point.get("capacity")
    power = point.get("power")
    if capacity is None or power is None or power <= 0:
        return "-"
    return f"{capacity / power:.2f}"


def _bin_details(result: Mapping[str, object]) -> tuple[dict, ...]:
    raw = result.get("bin_details")
    if not isinstance(raw, list):
        return ()
    return tuple(dict(item) for item in raw if isinstance(item, Mapping))


def _metric_value(result: Mapping[str, object], key: str) -> str:
    value = _value(result, (key,))
    return "-" if value is None else f"{value:.3f}"


def _kwh_value(result: Mapping[str, object], aliases: tuple[str, ...]) -> str:
    value = _value(result, aliases)
    return "-" if value is None else f"{value:.1f}"


def _value(result: Mapping[str, object], aliases: tuple[str, ...]) -> float | None:
    for key in aliases:
        raw_value = result.get(key)
        if raw_value is not None:
            return float(raw_value)
    return None
