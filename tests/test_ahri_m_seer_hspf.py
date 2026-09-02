"""Focused Appendix M SEER/HSPF formula and integration regressions."""

from pathlib import Path

import pytest

from core.calculators.capability import (
    AhriHspfRequest, AhriHspf2Request, AhriSeerRequest, AhriSeer2Request,
    CapabilityRequestTypeError, execute_standard_calculation,
)
from core.calculators.dispatcher import create_calculator_for_profile
from core.calculators.standards.ahri_hspf import AHRIHspfCalculator
from core.calculators.standards.ahri_seer import AHRISeerCalculator
from core.calculators.standards._ahri_m.numeric import round_nearest_005

SEER_POINTS = {"A2": (15000, 1200), "B2": (16000, 1100), "EV": (6800, 350), "B1": (3500, 120), "F1": (3400, 80)}
HSPF_POINTS = {"H01": (3300, 130), "H11": (2200, 140), "H1N": (14000, 1100), "H2V": (4900, 360), "H32": (8200, 890), "H12": (14000, 1100)}


def test_appendix_m_seer_golden_and_intermediate_contract():
    result = create_calculator_for_profile(profile_id="ahri_usa_m_seer").calculate_seer(SEER_POINTS)
    assert result["seasonal_cooling_numerator"] == pytest.approx(5349.664335664335)
    assert result["seasonal_energy_denominator"] == pytest.approx(296.4020649760093)
    assert result["raw_seer"] == pytest.approx(18.048674310340367)
    assert result["published_seer"] == result["SEER"] == 18.05
    assert [row["tj"] for row in result["bin_details"]] == [67, 72, 77, 82, 87, 92, 97, 102]
    assert [row["hours"] for row in result["bin_details"]] == pytest.approx([.214, .231, .216, .161, .104, .052, .018, .004])
    assert [row["operating_case"] for row in result["bin_details"]] == ["Case I", "Case I", "Case II", "Case II", "Case II", "Case II", "Case II", "Case III"]
    assert result["t1"] == pytest.approx(72.5615696887686)
    assert result["tv"] == pytest.approx(80.19842466214054)
    assert result["t2"] == pytest.approx(97.5657894736842)


def test_appendix_m_hspf_2017_golden_and_bin_inputs():
    result = create_calculator_for_profile(profile_id="ahri_usa_m_hspf").calculate_hspf(
        HSPF_POINTS, c_d_heating=.25, t_off=0, t_on=5
    )
    assert result["dhr_min_raw"] == 14000
    assert result["dhr_min_standardized"] == 15000
    assert result["dhr_max_raw"] == 28000
    assert result["dhr_max_standardized"] == 30000
    assert result["seasonal_heating_load_numerator"] == pytest.approx(4605.5625)
    assert result["seasonal_compressor_energy_denominator"] == pytest.approx(359.4864442524207)
    assert result["seasonal_resistance_energy_denominator"] == pytest.approx(80.69562457271222)
    assert result["raw_hspf"] == pytest.approx(10.462858044836917)
    assert result["published_hspf"] == result["HSPF"] == 10.45
    rows = {row["tj"]: row for row in result["bin_details"]}
    expected_case_ii = {47: 20.2933714789, 42: 30.6776015001, 37: 42.3396358265, 32: 66.1206585080, 27: 59.4719991538, 22: 46.8867802395}
    for temp, expected in expected_case_ii.items():
        assert rows[temp]["operating_case"] == "Case II"
        assert rows[temp]["e_comp"] == pytest.approx(expected)
    assert rows[2]["cutout_delta"] == .5 and rows[2]["e_comp"] == pytest.approx(2.355)
    assert rows[-3]["cutout_delta"] == 0 and rows[-3]["e_comp"] == 0
    assert rows[-8]["cutout_delta"] == 0 and rows[-8]["e_comp"] == 0


def test_appendix_m_hspf_optional_sources_and_fallbacks():
    calculator = create_calculator_for_profile(profile_id="ahri_usa_m_hspf")
    tested = calculator.calculate_hspf({**HSPF_POINTS, "H22": (10000, 990)}, t_off=None, t_on=None)
    assert tested["summary"]["metadata"]["h12_source"] == "tested"
    assert tested["summary"]["metadata"]["h22_source"] == "tested"
    same_speed_points = {key: value for key, value in HSPF_POINTS.items() if key != "H12"}
    same_speed = calculator.calculate_hspf(same_speed_points, h1n_same_speed_as_h32=True)
    assert same_speed["summary"]["metadata"]["h12_source"] == "h1n_same_speed_as_h32"
    calculated = calculator.calculate_hspf(same_speed_points, h1n_same_speed_as_h32=False)
    assert calculated["summary"]["metadata"]["h12_source"] == "calculated_from_h32"
    assert calculated["summary"]["metadata"]["h22_source"] == "appendix_m_fallback"


def test_appendix_m_seer_rejects_nonphysical_intermediate_envelope():
    points = dict(SEER_POINTS)
    points["EV"] = (50000, 350)
    with pytest.raises(ValueError, match="NQ"):
        create_calculator_for_profile(profile_id="ahri_usa_m_seer").calculate_seer(points)


def test_appendix_m_hspf_standardized_dhr_midpoint_tie_selects_upper_value():
    points = dict(HSPF_POINTS)
    points["H1N"] = (12500, 1100)
    result = create_calculator_for_profile(profile_id="ahri_usa_m_hspf").calculate_hspf(points)
    assert result["dhr_min_raw"] == 12500
    assert result["dhr_min_standardized"] == 15000


def test_appendix_m_hspf_no_cutout_keeps_compressor_available_all_bins():
    result = create_calculator_for_profile(profile_id="ahri_usa_m_hspf").calculate_hspf(
        HSPF_POINTS,
        t_off=None,
        t_on=None,
    )
    assert all(row["cutout_delta"] == 1.0 for row in result["bin_details"])


def test_appendix_m_hspf_demand_defrost_credit_uses_2017_equation():
    calculator = create_calculator_for_profile(profile_id="ahri_usa_m_hspf")
    baseline = calculator.calculate_hspf(HSPF_POINTS)
    credited = calculator.calculate_hspf(
        HSPF_POINTS,
        demand_defrost=True,
        defrost_test_minutes=180,
        defrost_max_minutes=720,
    )
    expected_factor = 1.0 + 0.03 * (1.0 - (180.0 - 90.0) / (720.0 - 90.0))
    assert baseline["f_def"] == 1.0
    assert credited["f_def"] == pytest.approx(expected_factor)
    assert credited["raw_hspf"] == pytest.approx(baseline["raw_hspf"] * expected_factor)


def test_appendix_m_hspf_rejects_nonphysical_intermediate_envelope():
    points = dict(HSPF_POINTS)
    points["H2V"] = (50000, 360)
    with pytest.raises(ValueError, match="NQ"):
        create_calculator_for_profile(profile_id="ahri_usa_m_hspf").calculate_hspf(points)


def test_appendix_m_rounding_is_decimal_half_up():
    assert round_nearest_005(10.462858) == 10.45
    assert round_nearest_005(18.048674) == 18.05
    assert round_nearest_005(10.475) == 10.50


def test_appendix_m_profiles_dispatch_to_distinct_facades():
    assert isinstance(create_calculator_for_profile(profile_id="ahri_usa_m_seer"), AHRISeerCalculator)
    assert isinstance(create_calculator_for_profile(profile_id="ahri_usa_m_hspf"), AHRIHspfCalculator)
    assert Path("data/region_configs/usa_m_seer.json").exists()
    assert Path("data/region_configs/usa_m_hspf.json").exists()


def test_appendix_m_and_m1_capabilities_reject_cross_request_types():
    with pytest.raises(CapabilityRequestTypeError):
        execute_standard_calculation("ahri210240.seer2", AhriSeerRequest(SEER_POINTS))
    with pytest.raises(CapabilityRequestTypeError):
        execute_standard_calculation("ahri210240.seer", AhriSeer2Request(SEER_POINTS))
    with pytest.raises(CapabilityRequestTypeError):
        execute_standard_calculation("ahri210240.hspf2", AhriHspfRequest(HSPF_POINTS))
    with pytest.raises(CapabilityRequestTypeError):
        execute_standard_calculation("ahri210240.hspf", AhriHspf2Request(HSPF_POINTS))


def test_appendix_m_core_does_not_import_m1_engines():
    for path in Path("core/calculators/standards/_ahri_m").glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "standards._ahri" not in source
        assert ".._ahri" not in source
