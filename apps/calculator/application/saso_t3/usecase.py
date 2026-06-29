"""SASO T3 single-calculation application usecase."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from apps.calculator.adapters.saso_t3_calculator import (
    calculate_saso_t3_cspf,
)
from apps.calculator.application.profile_resolver import (
    MODE_SASO_T3,
    resolve_calculation_mode_profile_id,
)
from apps.calculator.application.saso_t3.models import (
    MeasuredPoints,
    ResultRow,
    SasoT3BatchUseCaseResult,
    SasoT3UseCaseResult,
)


SasoT3CalculatorGateway = Callable[..., Mapping[str, object]]

REQUIRED_TRACE_LABEL = "Required only (3-point)"
OPTIONAL_TRACE_LABEL = "With 35 Min (4-point)"

_REQUIRED_FIELDS = (
    "full_46_capacity",
    "full_46_power",
    "full_35_capacity",
    "full_35_power",
    "half_35_capacity",
    "half_35_power",
)
_OPTIONAL_FIELDS = (
    "min_35_capacity",
    "min_35_power",
)
_INPUT_WAITING_STATUS = "입력 대기"
_INPUT_ERROR_STATUS = "입력 오류: 숫자 입력을 확인하세요."
_CALCULATION_ERROR_STATUS = "계산 오류"
_AUTO_CALC_DONE_STATUS = "자동 계산 완료"


class SasoT3UseCase:
    """Calculate SASO T3 required-only and optional-test comparison rows."""

    def __init__(
        self,
        calculator_gateway: SasoT3CalculatorGateway = calculate_saso_t3_cspf,
    ):
        self._calculator_gateway = calculator_gateway

    def calculate(self, raw_values: Mapping[str, str]) -> SasoT3UseCaseResult:
        """Calculate SASO T3 rows from raw input-table text values."""
        if not any(str(raw_values.get(field, "")).strip() for field in _REQUIRED_FIELDS):
            return SasoT3UseCaseResult(
                status="empty",
                status_text=_INPUT_WAITING_STATUS,
                detail_status=_INPUT_WAITING_STATUS,
            )

        required_measured, required_invalid = _parse_required_inputs(raw_values)
        if required_invalid:
            return SasoT3UseCaseResult(
                status="invalid",
                status_text=_INPUT_ERROR_STATUS,
                detail_status=_INPUT_ERROR_STATUS,
                invalid_fields=required_invalid,
            )

        required_row, required_trace, required_error = self._calculate_required_row(
            required_measured
        )
        if required_error is not None:
            return SasoT3UseCaseResult(
                status="error",
                status_text=required_error,
                detail_status=required_error,
            )

        trace_results = {REQUIRED_TRACE_LABEL: required_trace}
        detail_summaries = {REQUIRED_TRACE_LABEL: _summary_from_row(required_row)}
        detail_statuses: dict[str, str] = {}
        status = _AUTO_CALC_DONE_STATUS

        optional_measured, optional_invalid = _parse_optional_inputs(
            raw_values,
            required_measured,
        )
        if optional_invalid:
            optional_row: ResultRow = _optional_error_row("입력 오류")
            detail_statuses[OPTIONAL_TRACE_LABEL] = (
                "상세 데이터 없음: 35 Min 숫자 입력을 확인하세요."
            )
            status = "4-point 입력 오류: 35 Min 숫자 입력을 확인하세요."
            invalid_fields = optional_invalid
        else:
            optional_row, optional_trace, optional_error = self._calculate_optional_row(
                optional_measured
            )
            if optional_error is not None:
                optional_row = _optional_error_row(optional_error)
                detail_statuses[OPTIONAL_TRACE_LABEL] = (
                    "상세 데이터 없음: 35 Min 숫자 입력을 확인하세요."
                )
                status = "4-point 입력 오류: 35 Min 숫자 입력을 확인하세요."
                invalid_fields = None
            else:
                trace_results[OPTIONAL_TRACE_LABEL] = optional_trace
                detail_summaries[OPTIONAL_TRACE_LABEL] = _summary_from_row(optional_row)
                invalid_fields = None

        return SasoT3UseCaseResult(
            status="ok" if not detail_statuses else "partial",
            status_text=status,
            rows=(optional_row, required_row),
            detail_sources=trace_results,
            detail_summaries=detail_summaries,
            detail_statuses=detail_statuses,
            detail_status=None,
            invalid_fields=invalid_fields,
        )

    def calculate_batch_row(self, raw_values: Mapping[str, str]) -> SasoT3BatchUseCaseResult:
        """Calculate SASO T3 batch values with batch-specific optional semantics."""
        required_measured, required_invalid = _parse_required_inputs(raw_values)
        if required_invalid:
            return _blank_batch_result("error")

        required_row, _required_trace, required_error = self._calculate_required_row(
            required_measured
        )
        if required_error is not None:
            return _blank_batch_result("error")

        values = {
            "req_cspf": required_row[5],
            "req_cstl": required_row[6],
            "req_csec": required_row[7],
            "opt_cspf": "",
            "opt_cstl": "",
            "opt_csec": "",
        }
        opt_cap = str(raw_values.get("min_35_capacity", "")).strip()
        opt_power = str(raw_values.get("min_35_power", "")).strip()
        if not opt_cap and not opt_power:
            return SasoT3BatchUseCaseResult(values=values, status="ok")
        if not opt_cap or not opt_power:
            return SasoT3BatchUseCaseResult(values=values, status="error")

        optional_measured, optional_invalid = _parse_optional_inputs(
            raw_values,
            required_measured,
        )
        if optional_invalid:
            return SasoT3BatchUseCaseResult(values=values, status="error")
        optional_row, _optional_trace, optional_error = self._calculate_optional_row(
            optional_measured
        )
        if optional_error is not None:
            return SasoT3BatchUseCaseResult(values=values, status="error")
        values.update(
            {
                "opt_cspf": optional_row[5],
                "opt_cstl": optional_row[6],
                "opt_csec": optional_row[7],
            }
        )
        return SasoT3BatchUseCaseResult(values=values, status="ok")

    def _calculate_required_row(
        self, measured: MeasuredPoints
    ) -> tuple[ResultRow, tuple[dict, ...], str | None]:
        try:
            result = self._calculate_with_selection(measured, "required_only")
            return (
                _saso_result_row(REQUIRED_TRACE_LABEL, measured, result, include_min=False),
                _bin_details(result),
                None,
            )
        except Exception:
            return (), (), "계산 오류: SASO T3 required-only 결과를 계산할 수 없습니다."

    def _calculate_optional_row(
        self, measured: MeasuredPoints
    ) -> tuple[ResultRow, tuple[dict, ...], str | None]:
        try:
            result = self._calculate_with_selection(measured, "with_optional_test")
            return (
                _saso_result_row(OPTIONAL_TRACE_LABEL, measured, result, include_min=True),
                _bin_details(result),
                None,
            )
        except Exception:
            return (), (), "계산 오류"

    def _calculate_with_selection(
        self,
        measured: MeasuredPoints,
        test_selection: str,
    ) -> Mapping[str, object]:
        return self._calculator_gateway(
            measured,
            profile_id=resolve_calculation_mode_profile_id(MODE_SASO_T3),
            test_selection=test_selection,
        )


def _parse_required_inputs(
    raw_values: Mapping[str, str]
) -> tuple[dict[str, dict[str, float]], dict[str, str]]:
    numeric, invalid = _parse_positive_fields(raw_values, _REQUIRED_FIELDS)
    if invalid:
        return {}, invalid
    return {
        "46_full": {
            "capacity": numeric["full_46_capacity"],
            "power": numeric["full_46_power"],
        },
        "35_full": {
            "capacity": numeric["full_35_capacity"],
            "power": numeric["full_35_power"],
        },
        "35_half": {
            "capacity": numeric["half_35_capacity"],
            "power": numeric["half_35_power"],
        },
    }, {}


def _parse_optional_inputs(
    raw_values: Mapping[str, str],
    required_measured: MeasuredPoints,
) -> tuple[dict[str, dict[str, float]], dict[str, str]]:
    numeric, invalid = _parse_positive_fields(raw_values, _OPTIONAL_FIELDS)
    if invalid:
        return {}, invalid
    measured = {key: dict(value) for key, value in required_measured.items()}
    measured["35_min"] = {
        "capacity": numeric["min_35_capacity"],
        "power": numeric["min_35_power"],
    }
    return measured, {}


def _parse_positive_fields(
    raw_values: Mapping[str, str],
    fields: tuple[str, ...],
) -> tuple[dict[str, float], dict[str, str]]:
    numeric: dict[str, float] = {}
    invalid: dict[str, str] = {}
    for field in fields:
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


def _saso_result_row(
    title: str,
    measured: MeasuredPoints,
    result: Mapping[str, object],
    *,
    include_min: bool,
) -> ResultRow:
    return (
        title,
        _eer_value(measured, "46_full"),
        _eer_value(measured, "35_full"),
        _eer_value(measured, "35_half"),
        _eer_value(measured, "35_min") if include_min else "-",
        _metric_value(result, "cspf"),
        _kwh_value(result, ("annual_cooling_kwh", "cstl_kwh", "cstl")),
        _kwh_value(result, ("annual_power_kwh", "csec_kwh", "csec")),
    )


def _optional_error_row(message: str) -> ResultRow:
    return (OPTIONAL_TRACE_LABEL, "-", "-", "-", message, "-", "-", "-")


def _summary_from_row(row: ResultRow) -> tuple[tuple[str, str], ...]:
    return (
        ("CSPF", row[5]),
        ("CSTL [kWh]", row[6]),
        ("CSEC [kWh]", row[7]),
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


def _blank_batch_result(status: str) -> SasoT3BatchUseCaseResult:
    return SasoT3BatchUseCaseResult(
        values={
            "req_cspf": "",
            "req_cstl": "",
            "req_csec": "",
            "opt_cspf": "",
            "opt_cstl": "",
            "opt_csec": "",
        },
        status=status,
    )
