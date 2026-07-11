"""Focused Brazil application and batch mapping tests."""

from __future__ import annotations

import json
from pathlib import Path

from apps.calculator.application.brazil_cspf import BrazilCspfUseCase
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.batch_dialogs.profiles.brazil_cspf import (
    BRAZIL_CSPF_MATRIX_SPEC,
    BrazilCspfBatchHandler,
    CALCULATED_29_BIN_EER,
    FINAL,
    MEASURED_29_HALF_EER,
    ROW_STATUS,
    RULE_1,
    RULE_2,
    THREE_POINT_CSPF,
    THREE_POINT_CSEC,
    THREE_POINT_CSTL,
    TWO_POINT_CSPF,
    TWO_POINT_CSEC,
    TWO_POINT_CSTL,
)
from core.calculators.capability import execute_standard_calculation
from core.calculators.capability.results import (
    BrazilCspfComplianceResult,
    BrazilRuleEvaluation,
)


FIXTURE_PATH = Path("tests/fixtures/brazil_cspf_compliance_golden.json")


def _raw_values() -> dict[str, str]:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    measured = fixture["measured_points"]
    return {
        "full_capacity": str(measured["35_full"]["capacity"]),
        "full_power": str(measured["35_full"]["power"]),
        "half_capacity": str(measured["35_half"]["capacity"]),
        "half_power": str(measured["35_half"]["power"]),
        "half_29_capacity": str(measured["29_half"]["capacity"]),
        "half_29_power": str(measured["29_half"]["power"]),
    }


def test_brazil_usecase_calls_one_composite_capability_and_formats_golden():
    calls = []

    def executor(capability_id, request):
        calls.append((capability_id, request))
        return execute_standard_calculation(capability_id, request)

    result = BrazilCspfUseCase(capability_executor=executor).calculate(_raw_values())

    assert result.status == "ok"
    assert result.rows == (
        ("3-point", "6.02", "2461", "409"),
        ("2-point", "4.55", "2461", "541"),
    )
    assert [rule.status_text for rule in result.rules] == ["OK", "NG"]
    assert result.rules[0].comparison == (
        "3-point CSPF 6.02 ≤ 2-point CSPF 4.55 × 1.4 = 6.37"
    )
    assert result.rules[1].comparison == (
        "29°C Half 실측 EER 5.56 > 29°C bin 계산 EER 5.75"
    )
    assert result.final_status == "OK"
    assert result.final_status_text == "최종 판정: OK"
    assert len(calls) == 1
    assert calls[0][0] == "brazil.cspf_compliance"
    assert set(calls[0][1].measured_points) == {"35_full", "35_half", "29_half"}


def test_brazil_usecase_clears_result_for_empty_partial_and_invalid_input():
    usecase = BrazilCspfUseCase()

    empty = usecase.calculate({})
    assert empty.status == "empty"
    assert empty.rows == ()

    partial = usecase.calculate({"full_capacity": "2978"})
    assert partial.status == "invalid"
    assert partial.rows == ()

    invalid = _raw_values()
    invalid["half_29_power"] = "nan"
    result = usecase.calculate(invalid)
    assert result.status == "invalid"
    assert result.rows == ()


def test_brazil_display_rounding_does_not_recompute_core_rule_decision():
    raw_result = {
        "annual_cooling_kwh": 1.0,
        "annual_power_kwh": 1.0,
        "bin_details": (),
    }
    operation_result = BrazilCspfComplianceResult(
        three_point_result=raw_result,
        two_point_result=raw_result,
        three_point_exact_cspf=6.024,
        two_point_exact_cspf=4.3,
        rule_1_multiplier=1.4,
        rule_1=BrazilRuleEvaluation(6.024, 6.02, False),
        rule_2=BrazilRuleEvaluation(5.0, 5.0, False),
        final_passed=False,
    )

    result = BrazilCspfUseCase(
        capability_executor=lambda _capability_id, _request: operation_result
    ).calculate(_raw_values())

    assert result.rows[0][1] == "6.02"
    assert result.rules[0].comparison.endswith("= 6.02")
    assert result.rules[0].status_text == "NG"
    assert result.final_status == "NG"


def test_brazil_batch_row_matches_single_result_and_contains_rule_outputs():
    handler = BrazilCspfBatchHandler()
    result = handler.calculate_row(_raw_values())

    assert result.state is BatchRowState.OK
    assert result.values[THREE_POINT_CSPF] == "6.02"
    assert result.values[THREE_POINT_CSTL] == "2461"
    assert result.values[THREE_POINT_CSEC] == "409"
    assert result.values[TWO_POINT_CSPF] == "4.55"
    assert result.values[TWO_POINT_CSTL] == "2461"
    assert result.values[TWO_POINT_CSEC] == "541"
    assert result.values[RULE_1] == "OK"
    assert result.values[MEASURED_29_HALF_EER] == "5.56"
    assert result.values[CALCULATED_29_BIN_EER] == "5.75"
    assert result.values[RULE_2] == "NG"
    assert result.values[FINAL] == "OK"
    assert result.values[ROW_STATUS] == "OK"


def test_brazil_batch_keeps_partial_and_invalid_rows_independent():
    handler = BrazilCspfBatchHandler()
    partial = handler.calculate_row({"full_capacity": "2978"})
    invalid_values = _raw_values()
    invalid_values["half_power"] = "bad"
    invalid = handler.calculate_row(invalid_values)

    assert partial.state is BatchRowState.PENDING
    assert partial.values[THREE_POINT_CSPF] == ""
    assert partial.values[ROW_STATUS] == "PENDING"
    assert invalid.state is BatchRowState.ERROR
    assert invalid.values[TWO_POINT_CSPF] == ""
    assert invalid.values[ROW_STATUS] == "ERROR"


def test_brazil_batch_matrix_has_six_inputs_and_required_outputs():
    assert BRAZIL_CSPF_MATRIX_SPEC.input_keys == (
        "full_capacity",
        "full_power",
        "half_capacity",
        "half_power",
        "half_29_capacity",
        "half_29_power",
    )
    assert len(BRAZIL_CSPF_MATRIX_SPEC.result_keys) == 12
    assert BRAZIL_CSPF_MATRIX_SPEC.result_keys[-1] == ROW_STATUS
