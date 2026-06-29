from pathlib import Path

from apps.calculator.application.hong_kong_cspf import HongKongCspfUseCase
from tests.calculator_ui_sample_values import HONG_KONG_CSPF_SAMPLE_VALUES


def test_hong_kong_cspf_usecase_empty_input():
    result = HongKongCspfUseCase().calculate(
        {
            "declared_capacity": "",
            "full_capacity": "",
            "full_power": "",
            "half_capacity": "",
            "half_power": "",
        }
    )

    assert result.status == "empty"
    assert result.status_text == "입력 대기"
    assert result.summary_fields == ()
    assert result.detail_status == "입력 대기"


def test_hong_kong_cspf_usecase_invalid_input():
    raw_values = dict(HONG_KONG_CSPF_SAMPLE_VALUES)
    raw_values["full_power"] = "bad"

    result = HongKongCspfUseCase().calculate(raw_values)

    assert result.status == "invalid"
    assert result.status_text == "입력 오류: 숫자 입력을 확인하세요."
    assert result.summary_fields == ()
    assert result.invalid_fields == {"full_power": "숫자 입력 필요"}


def test_hong_kong_cspf_usecase_valid_sample_outputs():
    result = HongKongCspfUseCase().calculate(HONG_KONG_CSPF_SAMPLE_VALUES)

    assert result.status == "ok"
    assert result.status_text == "계산 완료"
    assert result.summary_fields == (
        ("CSPF", "4.939"),
        ("CSTL [kWh]", "1769.6"),
        ("CSEC [kWh]", "358.3"),
    )
    assert result.detail_summary == result.summary_fields
    assert result.detail_rows


def test_hong_kong_cspf_section_no_longer_imports_core_dispatcher():
    source = Path("apps/calculator/ui/sections/hong_kong_cspf_section.py").read_text(
        encoding="utf-8"
    )

    assert "core.calculators.dispatcher" not in source
    assert "create_calculator_for_profile" not in source
    assert "calculate_cspf" not in source
