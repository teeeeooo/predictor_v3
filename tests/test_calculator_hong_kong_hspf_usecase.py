from pathlib import Path

from apps.calculator.application.hong_kong_hspf import HongKongHspfUseCase
from tests.calculator_ui_sample_values import HONG_KONG_HSPF_SAMPLE_VALUES


def test_hong_kong_hspf_usecase_empty_input():
    result = HongKongHspfUseCase().calculate(
        {
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


def test_hong_kong_hspf_usecase_invalid_input():
    raw_values = dict(HONG_KONG_HSPF_SAMPLE_VALUES)
    raw_values["half_power"] = "bad"

    result = HongKongHspfUseCase().calculate(raw_values)

    assert result.status == "invalid"
    assert result.status_text == "입력 오류: 숫자 입력을 확인하세요."
    assert result.summary_fields == ()
    assert result.invalid_fields == {"half_power": "숫자 입력 필요"}


def test_hong_kong_hspf_usecase_valid_sample_outputs():
    result = HongKongHspfUseCase().calculate(HONG_KONG_HSPF_SAMPLE_VALUES)

    assert result.status == "ok"
    assert result.status_text == "계산 완료"
    assert result.summary_fields == (
        ("HSPF", "3.643"),
        ("HSTL [kWh]", "273.2"),
        ("HSEC [kWh]", "75.0"),
    )
    assert result.detail_summary == result.summary_fields
    assert result.detail_rows


def test_hong_kong_hspf_section_no_longer_imports_core_dispatcher():
    source = Path("apps/calculator/ui/sections/hong_kong_hspf_section.py").read_text(
        encoding="utf-8"
    )

    assert "core.calculators.dispatcher" not in source
    assert "create_calculator_for_profile" not in source
    assert "calculate_hspf" not in source
