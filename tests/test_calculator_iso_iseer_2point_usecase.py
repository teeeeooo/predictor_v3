from pathlib import Path

from apps.calculator.application.iso_iseer_2point.usecase import IsoIseer2PointUseCase
from tests.calculator_ui_sample_values import ISO_TWO_POINT_SAMPLE_VALUES


def test_iso_iseer_2point_usecase_empty_input():
    result = IsoIseer2PointUseCase().calculate(
        {
            "full_capacity": "",
            "full_power": "",
            "half_capacity": "",
            "half_power": "",
        }
    )

    assert result.status == "empty"
    assert result.status_text == "입력 대기"
    assert result.rows == ()
    assert result.detail_status == "입력 대기"


def test_iso_iseer_2point_usecase_invalid_input():
    raw_values = dict(ISO_TWO_POINT_SAMPLE_VALUES)
    raw_values["full_power"] = "bad"

    result = IsoIseer2PointUseCase().calculate(raw_values)

    assert result.status == "invalid"
    assert result.status_text == "입력 오류: 숫자 입력을 확인하세요."
    assert result.rows == ()
    assert result.detail_status == "입력 오류: 숫자 입력을 확인하세요."


def test_iso_iseer_2point_usecase_valid_sample_outputs():
    result = IsoIseer2PointUseCase().calculate(ISO_TWO_POINT_SAMPLE_VALUES)

    assert result.status == "ok"
    assert result.status_text == "자동 계산 완료"
    assert result.rows == (
        ("ISO 16358-1", "4.00", "4.47", "5.188", "2639.3", "508.7"),
        ("India ISEER", "4.00", "4.47", "4.560", "2786.7", "611.1"),
    )
    assert set(result.detail_sources or {}) == {"ISO 16358-1", "India ISEER"}
    assert all(rows for rows in (result.detail_sources or {}).values())
    assert result.detail_summaries == {
        "ISO 16358-1": (
            ("CSPF/ISEER", "5.188"),
            ("CSTL [kWh]", "2639.3"),
            ("CSEC [kWh]", "508.7"),
        ),
        "India ISEER": (
            ("CSPF/ISEER", "4.560"),
            ("CSTL [kWh]", "2786.7"),
            ("CSEC [kWh]", "611.1"),
        ),
    }


def test_iso_iseer_2point_section_no_longer_imports_core_dispatcher():
    source = Path("apps/calculator/ui/sections/iso_iseer_2point_section.py").read_text(
        encoding="utf-8"
    )

    assert "core.calculators.dispatcher" not in source
    assert "create_calculator_for_profile" not in source
    assert "calculate_cspf" not in source
