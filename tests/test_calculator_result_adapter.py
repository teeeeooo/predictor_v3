import pytest

from core.calculators.dispatcher import create_calculator_for_profile
from core.calculator_result_adapter import wrap_calculator_result_envelope


AHRI_SEER2_SAMPLE_POINTS = {
    "A_Full": (36000, 3000),
    "B_Full": (30000, 2200),
    "B_Low": (18000, 1200),
    "E_Int": (24000, 1700),
    "F_Low": (12000, 900),
}


def test_wraps_ahri_seer2_result_without_changing_raw_result():
    calculator = create_calculator_for_profile(profile_id="ahri_usa_seer2")
    raw_result = calculator.calculate_seer2(AHRI_SEER2_SAMPLE_POINTS)

    envelope = wrap_calculator_result_envelope("ahri_usa_seer2", raw_result)

    assert envelope["calculator_profile_id"] == "ahri_usa_seer2"
    assert envelope["calculator_id"] == "ahri_seer2"
    assert envelope["metric"] == "SEER2"
    assert envelope["value"] == raw_result["SEER2"]
    assert envelope["units"] == "Btu/Wh"
    assert envelope["raw_result"] is raw_result
    assert envelope["diagnostics"] == {"bin_details": raw_result["bin_details"]}
    assert envelope["warnings"] == []


def test_wraps_ahri_seer2_result_with_warnings_copy():
    raw_result = {
        "SEER2": 13.5,
        "bin_details": [],
    }

    envelope = wrap_calculator_result_envelope(
        "ahri_usa_seer2",
        raw_result,
        warnings=("manual review",),
    )

    assert envelope["warnings"] == ["manual review"]


def test_wrap_fails_fast_for_unsupported_profile():
    with pytest.raises(ValueError, match="Unsupported calculator result envelope profile"):
        wrap_calculator_result_envelope("ahri_usa_hspf2", {"HSPF2": 8.0})


def test_wrap_fails_fast_when_metric_key_is_missing():
    with pytest.raises(KeyError, match="SEER2"):
        wrap_calculator_result_envelope("ahri_usa_seer2", {"bin_details": []})
