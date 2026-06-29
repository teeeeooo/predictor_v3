"""Hong Kong CSPF single-calculation application usecase."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from apps.calculator.adapters.core_calculator_dispatcher import (
    create_calculator_for_profile,
)
from apps.calculator.application.hong_kong_cspf.models import HongKongCspfUseCaseResult
from apps.calculator.application.profile_resolver import resolve_profile_id


CalculatorFactory = Callable[..., object]

_INPUT_WAITING_STATUS = "입력 대기"
_INPUT_ERROR_STATUS = "입력 오류: 숫자 입력을 확인하세요."
_CALCULATION_ERROR_STATUS = "계산 오류"
_FIELDS = (
    "full_capacity",
    "full_power",
    "half_capacity",
    "half_power",
    "declared_capacity",
)


class HongKongCspfUseCase:
    """Calculate Hong Kong CSPF from raw section inputs."""

    def __init__(self, calculator_factory: CalculatorFactory = create_calculator_for_profile):
        self._calculator_factory = calculator_factory

    def calculate(
        self,
        raw_values: Mapping[str, str],
        *,
        region_label: str = "Hong Kong",
    ) -> HongKongCspfUseCaseResult:
        """Calculate a Hong Kong CSPF summary/detail DTO."""
        if not any(str(raw_values.get(field, "")).strip() for field in _FIELDS):
            return HongKongCspfUseCaseResult(
                status="empty",
                status_text=_INPUT_WAITING_STATUS,
                detail_status=_INPUT_WAITING_STATUS,
            )

        numeric, invalid = _parse_numeric_fields(raw_values)
        if invalid:
            return HongKongCspfUseCaseResult(
                status="invalid",
                status_text=_INPUT_ERROR_STATUS,
                detail_status=_INPUT_ERROR_STATUS,
                invalid_fields=invalid,
            )

        measured = {
            "35_full": {
                "capacity": numeric["full_capacity"],
                "power": numeric["full_power"],
            },
            "35_half": {
                "capacity": numeric["half_capacity"],
                "power": numeric["half_power"],
            },
        }
        try:
            profile_id = resolve_profile_id(region_label, "CSPF")
            calculator = self._calculator_factory(profile_id=profile_id)
            result = calculator.calculate_cspf(
                measured,
                declared_capacity=numeric["declared_capacity"],
            )
        except Exception as exc:
            status_text = f"오류: {type(exc).__name__}: {exc}"
            return HongKongCspfUseCaseResult(
                status="error",
                status_text=status_text,
                detail_status=_CALCULATION_ERROR_STATUS,
            )

        summary_fields = _summary_fields(result)
        return HongKongCspfUseCaseResult(
            status="ok",
            status_text="계산 완료",
            summary_fields=summary_fields,
            detail_rows=_bin_details(result),
            detail_summary=summary_fields,
            detail_status=None,
        )


def _parse_numeric_fields(
    raw_values: Mapping[str, str],
) -> tuple[dict[str, float], dict[str, str]]:
    numeric: dict[str, float] = {}
    invalid: dict[str, str] = {}
    for field in _FIELDS:
        try:
            numeric[field] = float(str(raw_values[field]))
        except (KeyError, TypeError, ValueError):
            invalid[field] = "숫자 입력 필요"
    return numeric, invalid


def _summary_fields(result: Mapping[str, object]) -> tuple[tuple[str, str], ...]:
    return (
        ("CSPF", _metric_value(result, "cspf")),
        ("CSTL [kWh]", _kwh_value(result, ("annual_cooling_kwh", "cstl_kwh", "cstl"))),
        ("CSEC [kWh]", _kwh_value(result, ("annual_power_kwh", "csec_kwh", "csec"))),
    )


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
