"""Focused tests for KOREA KS C 9306 HSPF application boundary."""

from __future__ import annotations

from apps.calculator.application.korea import KoreaHspfUseCase
from apps.calculator.application.korea.midpoint_guide import (
    calculate_hspf_midpoint_guide,
)


KOREA_HSPF_SAMPLE_VALUES = {
    "rated_cooling_capacity": "3500",
    "full_capacity": "4200",
    "full_power": "1200",
    "half_capacity": "2400",
    "half_power": "650",
    "min_capacity": "1200",
    "min_power": "360",
    "defrost_capacity": "3000",
    "defrost_power": "1100",
    "max_capacity": "3600",
    "max_power": "1400",
}


def test_korea_hspf_usecase_empty_input():
    result = KoreaHspfUseCase().calculate({key: "" for key in KOREA_HSPF_SAMPLE_VALUES})

    assert result.status == "empty"
    assert result.status_text == "입력 대기"
    assert result.detail_status == "입력 대기"
    assert result.guide_status == "입력 대기"


def test_korea_hspf_usecase_invalid_input():
    raw_values = dict(KOREA_HSPF_SAMPLE_VALUES)
    raw_values["defrost_power"] = "bad"

    result = KoreaHspfUseCase().calculate(raw_values)

    assert result.status == "invalid"
    assert result.status_text == "입력 오류: 숫자 입력을 확인하세요."
    assert result.invalid_fields == {"defrost_power": "숫자 입력 필요"}
    assert result.guide_status == "입력 오류: 숫자 입력을 확인하세요."


def test_korea_hspf_usecase_valid_sample_outputs_and_guide():
    result = KoreaHspfUseCase().calculate(KOREA_HSPF_SAMPLE_VALUES)

    assert result.status == "ok"
    assert result.status_text == "계산 완료"
    assert result.summary_fields == (
        ("HSPF", "2.882"),
        ("HSTL [kWh]", "6466.5"),
        ("HSEC [kWh]", "2243.5"),
    )
    assert result.guide_fields == (
        ("current_tc", "3.8 °C"),
        ("recommended_tc", "3.6 °C"),
        ("recommended_mid_capacity", "2216 W"),
    )
    assert result.detail_summary == result.summary_fields
    assert result.detail_rows


def test_hspf_midpoint_guide_uses_7c_inputs_only():
    guide = calculate_hspf_midpoint_guide(
        rated_cooling_capacity=3500.0,
        full_capacity=4200.0,
        half_capacity=2400.0,
        min_capacity=1200.0,
    )

    assert round(guide.current_tc, 1) == 3.8
    assert round(guide.recommended_tc, 1) == 3.6
    assert round(guide.recommended_mid_capacity) == 2216
