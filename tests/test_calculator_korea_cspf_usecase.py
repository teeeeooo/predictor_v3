"""Focused tests for KOREA KS C 9306 CSPF application boundary."""

from __future__ import annotations

from apps.calculator.application.korea import KoreaCspfUseCase
from apps.calculator.application.korea.midpoint_guide import (
    calculate_cspf_midpoint_guide,
)


KOREA_CSPF_SAMPLE_VALUES = {
    "declared_capacity": "3500",
    "full_capacity": "3600",
    "full_power": "900",
    "half_capacity": "1700",
    "half_power": "380",
    "min_capacity": "900",
    "min_power": "250",
}


def test_korea_cspf_usecase_empty_input():
    result = KoreaCspfUseCase().calculate({key: "" for key in KOREA_CSPF_SAMPLE_VALUES})

    assert result.status == "empty"
    assert result.status_text == "입력 대기"
    assert result.detail_status == "입력 대기"
    assert result.guide_status == "입력 대기"


def test_korea_cspf_usecase_invalid_input():
    raw_values = dict(KOREA_CSPF_SAMPLE_VALUES)
    raw_values["min_power"] = "bad"

    result = KoreaCspfUseCase().calculate(raw_values)

    assert result.status == "invalid"
    assert result.status_text == "입력 오류: 숫자 입력을 확인하세요."
    assert result.invalid_fields == {"min_power": "숫자 입력 필요"}
    assert result.guide_status == "입력 오류: 숫자 입력을 확인하세요."


def test_korea_cspf_usecase_valid_sample_outputs_and_guide():
    result = KoreaCspfUseCase().calculate(KOREA_CSPF_SAMPLE_VALUES)

    assert result.status == "ok"
    assert result.status_text == "계산 완료"
    assert result.summary_fields == (
        ("CSPF", "4.559"),
        ("CSTL [kWh]", "1134.1"),
        ("CSEC [kWh]", "248.8"),
    )
    assert result.guide_fields == (
        ("current_tc", "29.3 °C"),
        ("recommended_tc", "30.7 °C"),
        ("recommended_mid_capacity", "2258 W"),
    )
    assert result.detail_summary == result.summary_fields
    assert result.detail_rows


def test_cspf_midpoint_guide_uses_input_load_line_without_core_result_keys():
    guide = calculate_cspf_midpoint_guide(
        declared_capacity=3500.0,
        full_capacity=3600.0,
        half_capacity=1700.0,
        min_capacity=900.0,
    )

    assert round(guide.current_tc, 1) == 29.3
    assert round(guide.recommended_tc, 1) == 30.7
    assert round(guide.recommended_mid_capacity) == 2258
