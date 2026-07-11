"""Brazil CSPF compliance application usecase."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping

from apps.calculator.application.brazil_cspf.models import (
    BrazilCspfUseCaseResult,
    BrazilRuleDisplay,
    DetailRows,
    DetailSummaries,
    MeasuredPoints,
    ResultRow,
)
from core.calculators.capability import (
    BrazilCspfComplianceRequest,
    BrazilCspfComplianceResult,
    execute_standard_calculation,
)


CapabilityExecutor = Callable[[str, object], object]

_CAPABILITY_ID = "brazil.cspf_compliance"
_INPUT_FIELDS = (
    "full_capacity",
    "full_power",
    "half_capacity",
    "half_power",
    "half_29_capacity",
    "half_29_power",
)
_INPUT_WAITING_STATUS = "입력 대기"
_INPUT_ERROR_STATUS = "입력 오류: 숫자 입력을 확인하세요."
_CALCULATION_ERROR_STATUS = "계산 오류: Brazil CSPF 결과를 계산할 수 없습니다."
_AUTO_CALC_DONE_STATUS = "자동 계산 완료"


class BrazilCspfUseCase:
    """Parse Brazil single inputs and call the composite capability once."""

    def __init__(
        self,
        capability_executor: CapabilityExecutor = execute_standard_calculation,
    ) -> None:
        self._capability_executor = capability_executor

    def calculate(self, raw_values: Mapping[str, str]) -> BrazilCspfUseCaseResult:
        if not any(str(raw_values.get(field, "")).strip() for field in _INPUT_FIELDS):
            return BrazilCspfUseCaseResult(
                status="empty",
                status_text=_INPUT_WAITING_STATUS,
                detail_status=_INPUT_WAITING_STATUS,
            )
        try:
            measured = _parse_measured_points(raw_values)
        except ValueError:
            return BrazilCspfUseCaseResult(
                status="invalid",
                status_text=_INPUT_ERROR_STATUS,
                detail_status=_INPUT_ERROR_STATUS,
            )

        try:
            operation_result = self._capability_executor(
                _CAPABILITY_ID,
                BrazilCspfComplianceRequest(measured_points=measured),
            )
            if not isinstance(operation_result, BrazilCspfComplianceResult):
                raise TypeError("Brazil capability returned an unexpected result type")
            return _map_operation_result(operation_result)
        except Exception:
            return BrazilCspfUseCaseResult(
                status="error",
                status_text=_CALCULATION_ERROR_STATUS,
                detail_status=_CALCULATION_ERROR_STATUS,
            )


def _parse_measured_points(raw_values: Mapping[str, str]) -> MeasuredPoints:
    values: dict[str, float] = {}
    for field in _INPUT_FIELDS:
        text = str(raw_values.get(field, "")).strip()
        try:
            value = float(text)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid numeric input: {field}") from None
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"Invalid positive finite input: {field}")
        values[field] = value
    return {
        "35_full": {
            "capacity": values["full_capacity"],
            "power": values["full_power"],
        },
        "35_half": {
            "capacity": values["half_capacity"],
            "power": values["half_power"],
        },
        "29_half": {
            "capacity": values["half_29_capacity"],
            "power": values["half_29_power"],
        },
    }


def _map_operation_result(
    result: BrazilCspfComplianceResult,
) -> BrazilCspfUseCaseResult:
    rows = (
        _result_row("3-point", result.three_point_result, result.three_point_exact_cspf),
        _result_row("2-point", result.two_point_result, result.two_point_exact_cspf),
    )
    rules = (
        _rule_1_display(result),
        _rule_2_display(result),
    )
    final_status = "OK" if result.final_passed else "NG"
    return BrazilCspfUseCaseResult(
        status="ok",
        status_text=_AUTO_CALC_DONE_STATUS,
        rows=rows,
        rules=rules,
        final_status=final_status,
        final_status_text=f"최종 판정: {final_status}",
        operation_result=result,
        detail_sources=_detail_sources(result),
        detail_summaries=_detail_summaries(result),
        detail_status=None,
    )


def _detail_sources(result: BrazilCspfComplianceResult) -> DetailRows:
    return {
        "3-point": _bin_details(result.three_point_result),
        "2-point": _bin_details(result.two_point_result),
    }


def _detail_summaries(result: BrazilCspfComplianceResult) -> DetailSummaries:
    return {
        "3-point": _detail_summary(
            result.three_point_result,
            result.three_point_exact_cspf,
        ),
        "2-point": _detail_summary(
            result.two_point_result,
            result.two_point_exact_cspf,
        ),
    }


def _bin_details(raw_result: Mapping[str, object]) -> tuple[dict[str, object], ...]:
    raw = raw_result.get("bin_details")
    if not isinstance(raw, (list, tuple)):
        raise ValueError("Missing Brazil bin detail rows")
    return tuple(dict(item) for item in raw if isinstance(item, Mapping))


def _detail_summary(
    raw_result: Mapping[str, object],
    exact_cspf: float,
) -> tuple[tuple[str, str], ...]:
    return (
        ("CSPF", f"{exact_cspf:.2f}"),
        ("CSTL [kWh]", _rounded_kwh(raw_result, "annual_cooling_kwh")),
        ("CSEC [kWh]", _rounded_kwh(raw_result, "annual_power_kwh")),
    )


def _result_row(
    label: str,
    raw_result: Mapping[str, object],
    exact_cspf: float,
) -> ResultRow:
    return (
        label,
        f"{exact_cspf:.2f}",
        _rounded_kwh(raw_result, "annual_cooling_kwh"),
        _rounded_kwh(raw_result, "annual_power_kwh"),
    )


def _rounded_kwh(raw_result: Mapping[str, object], key: str) -> str:
    try:
        value = float(raw_result[key])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"Missing or invalid Brazil result key: {key}") from None
    if not math.isfinite(value):
        raise ValueError(f"Non-finite Brazil result key: {key}")
    return f"{value:.0f}"


def _rule_1_display(result: BrazilCspfComplianceResult) -> BrazilRuleDisplay:
    rule = result.rule_1
    left = f"{rule.left_value:.2f}"
    right = f"{rule.right_value:.2f}"
    two_point = f"{result.two_point_exact_cspf:.2f}"
    multiplier = f"{result.rule_1_multiplier:.1f}"
    return BrazilRuleDisplay(
        label="Rule 1",
        comparison=(
            f"3-point CSPF {left} ≤ 2-point CSPF {two_point} × "
            f"{multiplier} = {right}"
        ),
        left_value_text=left,
        right_value_text=right,
        status_text="OK" if rule.passed else "NG",
        passed=rule.passed,
        condition_text="CSPF 3pt ≤ CSPF 2pt × 1.4",
    )


def _rule_2_display(result: BrazilCspfComplianceResult) -> BrazilRuleDisplay:
    rule = result.rule_2
    left = f"{rule.left_value:.2f}"
    right = f"{rule.right_value:.2f}"
    return BrazilRuleDisplay(
        label="Rule 2",
        comparison=(
            f"29°C Half 실측 EER {left} > 29°C bin 계산 EER {right}"
        ),
        left_value_text=left,
        right_value_text=right,
        status_text="OK" if rule.passed else "NG",
        passed=rule.passed,
        condition_text="29°C EER 실측 > 계산",
    )
