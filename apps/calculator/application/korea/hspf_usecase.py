"""KOREA HSPF single-calculation application usecase."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from apps.calculator.adapters.core_calculator_dispatcher import (
    create_calculator_for_profile,
)
from apps.calculator.application.korea.midpoint_guide import (
    calculate_hspf_midpoint_guide,
)
from apps.calculator.application.korea.models import KoreaHspfUseCaseResult


CalculatorFactory = Callable[..., object]

_INPUT_WAITING_STATUS = "입력 대기"
_INPUT_ERROR_STATUS = "입력 오류: 숫자 입력을 확인하세요."
_CALCULATION_ERROR_STATUS = "계산 오류"
_GUIDE_ERROR_STATUS = "guide 계산 오류"
_FIELDS = (
    "rated_cooling_capacity",
    "full_capacity",
    "full_power",
    "half_capacity",
    "half_power",
    "min_capacity",
    "min_power",
    "defrost_capacity",
    "defrost_power",
    "max_capacity",
    "max_power",
)


class KoreaHspfUseCase:
    """Calculate KOREA KS C 9306 HSPF from raw section inputs."""

    def __init__(self, calculator_factory: CalculatorFactory = create_calculator_for_profile):
        self._calculator_factory = calculator_factory

    def calculate(self, raw_values: Mapping[str, str]) -> KoreaHspfUseCaseResult:
        if not any(str(raw_values.get(field, "")).strip() for field in _FIELDS):
            return KoreaHspfUseCaseResult(
                status="empty",
                status_text=_INPUT_WAITING_STATUS,
                detail_status=_INPUT_WAITING_STATUS,
                guide_status=_INPUT_WAITING_STATUS,
            )

        numeric, invalid = _parse_numeric_fields(raw_values)
        if invalid:
            return KoreaHspfUseCaseResult(
                status="invalid",
                status_text=_INPUT_ERROR_STATUS,
                detail_status=_INPUT_ERROR_STATUS,
                invalid_fields=invalid,
                guide_status=_INPUT_ERROR_STATUS,
            )

        measured = {
            "rated_cooling_capacity": numeric["rated_cooling_capacity"],
            "ks_c_9306_hspf": {
                "capacity": {
                    "rated": {"7": numeric["full_capacity"]},
                    "intermediate": {"7": numeric["half_capacity"]},
                    "min": {"7": numeric["min_capacity"]},
                    "max": {
                        "def": numeric["defrost_capacity"],
                        "-7": numeric["max_capacity"],
                    },
                },
                "power": {
                    "rated": {"7": numeric["full_power"]},
                    "intermediate": {"7": numeric["half_power"]},
                    "min": {"7": numeric["min_power"]},
                    "max": {
                        "def": numeric["defrost_power"],
                        "-7": numeric["max_power"],
                    },
                },
            },
        }
        try:
            calculator = self._calculator_factory(profile_id="ks_c9306_hspf")
            result = calculator.calculate_hspf(measured)
        except Exception as exc:
            status_text = f"오류: {type(exc).__name__}: {exc}"
            return KoreaHspfUseCaseResult(
                status="error",
                status_text=status_text,
                detail_status=_CALCULATION_ERROR_STATUS,
                guide_status=_GUIDE_ERROR_STATUS,
            )

        guide_fields: tuple[tuple[str, str], ...] = ()
        guide_status = None
        try:
            guide = calculate_hspf_midpoint_guide(
                rated_cooling_capacity=numeric["rated_cooling_capacity"],
                full_capacity=numeric["full_capacity"],
                half_capacity=numeric["half_capacity"],
                min_capacity=numeric["min_capacity"],
            )
            guide_fields = (
                ("current_tc", f"{guide.current_tc:.1f} °C"),
                ("recommended_tc", f"{guide.recommended_tc:.1f} °C"),
                ("recommended_mid_capacity", f"{guide.recommended_mid_capacity:.0f} W"),
            )
        except Exception as exc:
            guide_status = f"{_GUIDE_ERROR_STATUS}: {type(exc).__name__}"

        summary_fields = _summary_fields(result)
        return KoreaHspfUseCaseResult(
            status="ok",
            status_text="계산 완료",
            summary_fields=summary_fields,
            detail_rows=_bin_details(result),
            detail_summary=summary_fields,
            detail_status=None,
            guide_fields=guide_fields,
            guide_status=guide_status,
        )


def _parse_numeric_fields(
    raw_values: Mapping[str, str],
) -> tuple[dict[str, float], dict[str, str]]:
    numeric: dict[str, float] = {}
    invalid: dict[str, str] = {}
    for field in _FIELDS:
        try:
            value = float(str(raw_values[field]))
        except (KeyError, TypeError, ValueError):
            invalid[field] = "숫자 입력 필요"
            continue
        if value <= 0:
            invalid[field] = "양수 입력 필요"
            continue
        numeric[field] = value
    return numeric, invalid


def _summary_fields(result: Mapping[str, object]) -> tuple[tuple[str, str], ...]:
    return (
        ("HSPF", _metric_value(result, "hspf")),
        (
            "HSTL [kWh]",
            _kwh_value(
                result,
                kwh_aliases=("hstl_kwh",),
                wh_aliases=("hstl", "HSTL"),
            ),
        ),
        (
            "HSEC [kWh]",
            _kwh_value(
                result,
                kwh_aliases=("hsec_kwh",),
                wh_aliases=("hsec", "HSEC"),
            ),
        ),
    )


def _bin_details(result: Mapping[str, object]) -> tuple[dict, ...]:
    raw = result.get("bin_details")
    if not isinstance(raw, list):
        return ()
    return tuple(dict(item) for item in raw if isinstance(item, Mapping))


def _metric_value(result: Mapping[str, object], key: str) -> str:
    value = _value(result, (key,))
    return "-" if value is None else f"{value:.3f}"


def _kwh_value(
    result: Mapping[str, object],
    *,
    kwh_aliases: tuple[str, ...],
    wh_aliases: tuple[str, ...],
) -> str:
    value = _value(result, kwh_aliases)
    if value is None:
        value = _value(result, wh_aliases)
        if value is not None:
            value /= 1000.0
    return "-" if value is None else f"{value:.1f}"


def _value(result: Mapping[str, object], aliases: tuple[str, ...]) -> float | None:
    for key in aliases:
        raw_value = result.get(key)
        if raw_value is not None:
            return float(raw_value)
    return None
