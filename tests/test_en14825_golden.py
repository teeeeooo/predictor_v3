import json

import pytest

from core.calculator_en14825 import EN14825Calculator


TOLERANCE = 0.005

# Standby power inputs are provided by the source sample in W.
# The calculator API expects kW, so 6.6 W is passed as 0.0066 kW.
STANDBY_POWER_KW = {
    "p_to": 0.0066,
    "p_sb": 0.0012,
    "p_ck": 0.0,
    "p_off": 0.0012,
}

SEER_TEST_POINTS = {
    "A": (3.6233, 0.847),
    "B": (2.4691, 0.389),
    "C": (1.5150, 0.137),
    "D": (1.1277, 0.062),
}


def assert_golden_close(actual, expected, label):
    assert abs(actual - expected) < TOLERANCE, (
        f"{label} golden mismatch: expected={expected:.3f}, actual={actual:.3f}, "
        f"tolerance={TOLERANCE:.3f}"
    )


def scop_points(tbiv_temp_c, tol_temp_c):
    return {
        "A": {"capacity": 2.1598, "power": 0.6062, "temp_c": -7},
        "B": {"capacity": 1.3293, "power": 0.2542, "temp_c": 2},
        "C": {"capacity": 0.9083, "power": 0.1540, "temp_c": 7},
        "D": {"capacity": 0.9299, "power": 0.1231, "temp_c": 12},
        "TOL": {"capacity": 2.3698, "power": 0.8067, "temp_c": tol_temp_c},
        "Tbiv": {"capacity": 2.3669, "power": 0.7820, "temp_c": tbiv_temp_c},
    }


def scop_points_without(*keys, tbiv_temp_c=2, tol_temp_c=-11):
    points = scop_points(tbiv_temp_c=tbiv_temp_c, tol_temp_c=tol_temp_c)
    for key in keys:
        points.pop(key)
    return points


def test_en14825_golden_seer():
    calculator = EN14825Calculator()
    result = calculator.calculate_seer(
        test_points=SEER_TEST_POINTS,
        p_design_c=3.5,
        t_design_c=35,
        **STANDBY_POWER_KW,
    )

    assert_golden_close(result["seer"], 9.104, "SEER")


def test_en14825_unified_config_loads_seer_and_scop_sections():
    calculator = EN14825Calculator("data/region_configs/en14825.json")

    assert calculator.seer_config["design"]["t_design_c"] == 35
    assert calculator.seer_config["operational_hours"]["cooling_only"]["h_off"] == 5088
    assert calculator.scop_config["climates"]["warmer"]["t_design_h_c"] == 2
    assert calculator.scop_config["operational_hours"]["heating_only"]["warmer"]["h_ck"] == 4476


def test_en14825_legacy_scop_config_still_loads_with_seer_fallback():
    calculator = EN14825Calculator("data/region_configs/en14825_scop.json")

    assert calculator.scop_config["climates"]["average"]["heating_bin_hours_total"] == 4910
    assert calculator.seer_config["bin_data"]["temps"][0] == 17
    assert calculator.seer_config["operational_hours"]["reversible"]["h_ck"] == 2672
    result = calculator.calculate_seer(
        test_points=SEER_TEST_POINTS,
        p_design_c=3.5,
        **STANDBY_POWER_KW,
    )
    assert_golden_close(result["seer"], 9.104, "legacy config SEER fallback")


def test_en14825_seer_reads_design_default_and_operational_hours_from_config(tmp_path):
    with open("data/region_configs/en14825.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    config["seer"]["design"]["t_design_c"] = 40
    config["seer"]["operational_hours"]["reversible"]["h_ce"] = 700
    config_path = tmp_path / "en14825_config_driven_seer.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    configured = EN14825Calculator(str(config_path)).calculate_seer(
        test_points=SEER_TEST_POINTS,
        p_design_c=3.5,
        **STANDBY_POWER_KW,
    )
    explicit_legacy = EN14825Calculator(str(config_path)).calculate_seer(
        test_points=SEER_TEST_POINTS,
        p_design_c=3.5,
        t_design_c=35,
        **STANDBY_POWER_KW,
    )

    assert configured["qc_kwh"] == 2450.0
    assert configured["seer_on"] != explicit_legacy["seer_on"]
    assert configured["seer"] != explicit_legacy["seer"]


def test_en14825_seer_reads_default_appliance_type_from_config(tmp_path):
    with open("data/region_configs/en14825.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    config["seer"]["defaults"]["appliance_type"] = "cooling_only"
    config_path = tmp_path / "en14825_config_default_appliance.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    calculator = EN14825Calculator(str(config_path))
    default_result = calculator.calculate_seer(
        test_points=SEER_TEST_POINTS,
        p_design_c=3.5,
        p_to=0.0066,
        p_sb=0.0012,
        p_ck=0.01,
        p_off=0.01,
    )
    explicit_result = calculator.calculate_seer(
        test_points=SEER_TEST_POINTS,
        p_design_c=3.5,
        p_to=0.0066,
        p_sb=0.0012,
        p_ck=0.01,
        p_off=0.01,
        appliance_type="cooling_only",
    )

    assert default_result == explicit_result


def test_en14825_seer_default_matches_reversible():
    calculator = EN14825Calculator()
    kwargs = {
        "test_points": SEER_TEST_POINTS,
        "p_design_c": 3.5,
        "t_design_c": 35,
        **STANDBY_POWER_KW,
    }

    default_result = calculator.calculate_seer(**kwargs)
    reversible_result = calculator.calculate_seer(
        **kwargs, appliance_type="reversible"
    )

    assert default_result["seer"] == reversible_result["seer"]
    assert default_result["seer_on"] == reversible_result["seer_on"]
    assert default_result["qc_kwh"] == reversible_result["qc_kwh"]


def test_en14825_seer_cooling_only_auxiliary_hours_reduce_seer():
    calculator = EN14825Calculator()
    kwargs = {
        "test_points": SEER_TEST_POINTS,
        "p_design_c": 3.5,
        "t_design_c": 35,
        "p_to": 0.0066,
        "p_sb": 0.0012,
        "p_ck": 0.01,
        "p_off": 0.01,
    }

    reversible_result = calculator.calculate_seer(
        **kwargs, appliance_type="reversible"
    )
    cooling_only_result = calculator.calculate_seer(
        **kwargs, appliance_type="cooling_only"
    )

    assert cooling_only_result["seer"] < reversible_result["seer"]


def test_en14825_seer_invalid_appliance_type_raises():
    calculator = EN14825Calculator()

    with pytest.raises(ValueError, match="Unknown SEER appliance_type"):
        calculator.calculate_seer(
            test_points=SEER_TEST_POINTS,
            p_design_c=3.5,
            t_design_c=35,
            appliance_type="heating_only",
            **STANDBY_POWER_KW,
        )


def test_en14825_golden_scop_average():
    calculator = EN14825Calculator()
    result = calculator.calculate_scop(
        test_points=scop_points(tbiv_temp_c=-10, tol_temp_c=-11),
        p_design_h=2.4,
        climate="average",
        tbiv_temp_c=-10,
        tol_temp_c=-11,
        **STANDBY_POWER_KW,
    )

    assert_golden_close(result["scop"], 5.108, "SCOP average")


def test_en14825_scop_warmer_a_tol_tbiv_independent_inputs_not_required():
    calculator = EN14825Calculator()

    result = calculator.calculate_scop(
        test_points=scop_points_without("A", "TOL", "Tbiv", tbiv_temp_c=2, tol_temp_c=-11),
        p_design_h=1.3,
        climate="warmer",
        tbiv_temp_c=2,
        tol_temp_c=-11,
        **STANDBY_POWER_KW,
    )

    assert result["scop"] > 0


def test_en14825_scop_warmer_tbiv_at_2_maps_to_b():
    calculator = EN14825Calculator()
    climate_data = calculator._get_scop_climate_data("warmer")

    resolution = calculator._validate_scop_points(
        test_points=scop_points_without("A", "TOL", "Tbiv", tbiv_temp_c=2, tol_temp_c=-11),
        climate_key="warmer",
        climate_data=climate_data,
        tbiv_temp_c=2,
        tol_temp_c=-11,
    )

    assert resolution["contract"]["mapped_points"]["Tbiv"] == "B"
    assert "Tbiv" not in resolution["contract"]["required_independent_points"]
    assert "Tbiv" not in resolution["contract"]["curve_point_keys"]
    assert resolution["points"]["Tbiv"]["capacity"] == resolution["points"]["B"]["capacity"]
    assert resolution["points"]["Tbiv"]["power"] == resolution["points"]["B"]["power"]


def test_en14825_scop_warmer_tol_below_first_nonzero_bin_not_required():
    calculator = EN14825Calculator()
    climate_data = calculator._get_scop_climate_data("warmer")

    resolution = calculator._validate_scop_points(
        test_points=scop_points_without("A", "TOL", "Tbiv", tbiv_temp_c=2, tol_temp_c=-11),
        climate_key="warmer",
        climate_data=climate_data,
        tbiv_temp_c=2,
        tol_temp_c=-11,
    )

    assert "TOL" not in resolution["contract"]["required_independent_points"]
    assert "TOL" not in resolution["contract"]["curve_point_keys"]
    assert "TOL" in resolution["contract"]["inactive_points"]
    assert resolution["points"]["TOL"]["temp_c"] == -11


@pytest.mark.parametrize(
    "climate,tbiv_temp_c,tol_temp_c",
    [("average", -10, -11), ("colder", -15, -22)],
)
def test_en14825_scop_average_and_colder_keep_a_required(climate, tbiv_temp_c, tol_temp_c):
    calculator = EN14825Calculator()

    with pytest.raises(ValueError, match="Missing SCOP test point: A"):
        calculator.calculate_scop(
            test_points=scop_points_without("A", tbiv_temp_c=tbiv_temp_c, tol_temp_c=tol_temp_c),
            p_design_h=2.4,
            climate=climate,
            tbiv_temp_c=tbiv_temp_c,
            tol_temp_c=tol_temp_c,
            **STANDBY_POWER_KW,
        )


def test_en14825_scop_average_tol_minus11_remains_required():
    calculator = EN14825Calculator()

    with pytest.raises(ValueError, match="Missing SCOP test point: TOL"):
        calculator.calculate_scop(
            test_points=scop_points_without("TOL", tbiv_temp_c=-10, tol_temp_c=-11),
            p_design_h=2.4,
            climate="average",
            tbiv_temp_c=-10,
            tol_temp_c=-11,
            **STANDBY_POWER_KW,
        )


def test_en14825_golden_scop_warmer():
    calculator = EN14825Calculator()
    result = calculator.calculate_scop(
        test_points=scop_points(tbiv_temp_c=2, tol_temp_c=-11),
        p_design_h=1.3,
        climate="warmer",
        tbiv_temp_c=2,
        tol_temp_c=-11,
        **STANDBY_POWER_KW,
    )

    assert_golden_close(result["scop"], 6.008, "SCOP warmer")


def test_en14825_golden_scop_colder():
    calculator = EN14825Calculator()
    result = calculator.calculate_scop(
        test_points=scop_points(tbiv_temp_c=-15, tol_temp_c=-22),
        p_design_h=2.942,
        climate="colder",
        tbiv_temp_c=-15,
        tol_temp_c=-22,
        **STANDBY_POWER_KW,
    )

    assert_golden_close(result["scop"], 4.190, "SCOP colder")
