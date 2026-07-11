"""Hong Kong HSPF single-calculation application usecase."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from core.calculators.capability import Iso16358HspfRequest, execute_standard_calculation
from apps.calculator.application.hong_kong_hspf.models import HongKongHspfUseCaseResult
from apps.calculator.application.profile_resolver import resolve_profile_id


CapabilityExecutor = Callable[[str, object], object]

_INPUT_WAITING_STATUS = "입력 대기"
_INPUT_ERROR_STATUS = "입력 오류: 숫자 입력을 확인하세요."
_CALCULATION_ERROR_STATUS = "계산 오류"
_FIELDS = ("full_capacity", "full_power", "half_capacity", "half_power")


class HongKongHspfUseCase:
    """Calculate Hong Kong HSPF from raw section inputs."""

    def __init__(self, capability_executor: CapabilityExecutor = execute_standard_calculation):
        self._capability_executor = capability_executor

    def calculate(
        self,
        raw_values: Mapping[str, str],
        *,
        region_label: str = "Hong Kong",
    ) -> HongKongHspfUseCaseResult:
        """Calculate a Hong Kong HSPF summary/detail DTO."""
        if not any(str(raw_values.get(field, "")).strip() for field in _FIELDS):
            return HongKongHspfUseCaseResult(
                status="empty",
                status_text=_INPUT_WAITING_STATUS,
                detail_status=_INPUT_WAITING_STATUS,
            )

        numeric, invalid = _parse_numeric_fields(raw_values)
        if invalid:
            return HongKongHspfUseCaseResult(
                status="invalid",
                status_text=_INPUT_ERROR_STATUS,
                detail_status=_INPUT_ERROR_STATUS,
                invalid_fields=invalid,
            )

        measured = {
            "7_full": {
                "capacity": numeric["full_capacity"],
                "power": numeric["full_power"],
            },
            "7_half": {
                "capacity": numeric["half_capacity"],
                "power": numeric["half_power"],
            },
        }
        try:
            profile_id = resolve_profile_id(region_label, "HSPF")
            result = self._capability_executor(
                "iso16358.hspf", Iso16358HspfRequest(profile_id, measured)
            )
        except Exception as exc:
            status_text = f"오류: {type(exc).__name__}: {exc}"
            return HongKongHspfUseCaseResult(
                status="error",
                status_text=status_text,
                detail_status=_CALCULATION_ERROR_STATUS,
            )

        summary_fields = _summary_fields(result)
        return HongKongHspfUseCaseResult(
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
        ("HSPF", _metric_value(result, "hspf")),
        (
            "HSTL [kWh]",
            _kwh_value(result, kwh_aliases=("hstl_kwh", "hstl"), wh_aliases=("hstl_wh",)),
        ),
        (
            "HSEC [kWh]",
            _kwh_value(result, kwh_aliases=("hsec_kwh", "hsec"), wh_aliases=("hsec_wh",)),
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
