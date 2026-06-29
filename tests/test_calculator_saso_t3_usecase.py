from pathlib import Path

from apps.calculator.application.saso_t3 import SasoT3UseCase


SASO_T3_SAMPLE_VALUES = {
    "full_46_capacity": "5000",
    "full_46_power": "1500",
    "full_35_capacity": "6000",
    "full_35_power": "1500",
    "half_35_capacity": "3000",
    "half_35_power": "680",
    "min_35_capacity": "1200",
    "min_35_power": "300",
}


def test_saso_t3_usecase_empty_input():
    result = SasoT3UseCase().calculate(
        {
            "full_46_capacity": "",
            "full_46_power": "",
            "full_35_capacity": "",
            "full_35_power": "",
            "half_35_capacity": "",
            "half_35_power": "",
            "min_35_capacity": "",
            "min_35_power": "",
        }
    )

    assert result.status == "empty"
    assert result.status_text == "입력 대기"
    assert result.rows == ()
    assert result.detail_status == "입력 대기"


def test_saso_t3_usecase_invalid_required_input():
    raw_values = dict(SASO_T3_SAMPLE_VALUES)
    raw_values["full_46_capacity"] = "bad"

    result = SasoT3UseCase().calculate(raw_values)

    assert result.status == "invalid"
    assert result.status_text == "입력 오류: 숫자 입력을 확인하세요."
    assert result.rows == ()
    assert result.invalid_fields == {"full_46_capacity": "숫자 입력 필요"}


def test_saso_t3_usecase_invalid_optional_input_keeps_required_row():
    raw_values = dict(SASO_T3_SAMPLE_VALUES)
    raw_values["min_35_power"] = "-300"

    result = SasoT3UseCase().calculate(raw_values)

    assert result.status == "partial"
    assert result.status_text == "4-point 입력 오류: 35 Min 숫자 입력을 확인하세요."
    assert result.rows[0] == (
        "With 35 Min (4-point)",
        "-",
        "-",
        "-",
        "입력 오류",
        "-",
        "-",
        "-",
    )
    assert result.rows[1][0] == "Required only (3-point)"
    assert result.rows[1][5] == "4.166"
    assert result.invalid_fields == {"min_35_power": "양수 입력 필요"}


def test_saso_t3_usecase_valid_sample_outputs():
    result = SasoT3UseCase().calculate(SASO_T3_SAMPLE_VALUES)

    assert result.status == "ok"
    assert result.status_text == "자동 계산 완료"
    assert result.rows == (
        (
            "With 35 Min (4-point)",
            "3.33",
            "4.00",
            "4.41",
            "4.00",
            "4.230",
            "19885.0",
            "4700.9",
        ),
        (
            "Required only (3-point)",
            "3.33",
            "4.00",
            "4.41",
            "-",
            "4.166",
            "19885.0",
            "4773.5",
        ),
    )
    assert set(result.detail_sources or {}) == {
        "Required only (3-point)",
        "With 35 Min (4-point)",
    }
    assert all(rows for rows in (result.detail_sources or {}).values())


def test_saso_t3_section_no_longer_imports_core_dispatcher_or_mutates_config():
    source = Path("apps/calculator/ui/sections/iso_saso_t3_section.py").read_text(
        encoding="utf-8"
    )

    assert "core.calculators.dispatcher" not in source
    assert "create_calculator_for_profile" not in source
    assert "calculate_cspf" not in source
    assert ".config[" not in source
