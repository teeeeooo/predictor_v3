import json

import pytest

from core.calculator_iso16358_legacy import ISO16358Calculator


FULL_CAPACITY = 1700.0
FULL_POWER = 500.0
HALF_CAPACITY = 1000.0
HALF_POWER = 300.0
MIN_CAPACITY = 400.0
MIN_POWER = 100.0
EXTENDED_CAPACITY = 2200.0
EXTENDED_POWER = 700.0
CD = 0.25


def make_iso_micro_calculator(tmp_path, bin_hours):
    config_path = tmp_path / "iso16358_hspf_formula_micro_config.json"
    config = {
        "mode": "heating",
        "hspf": {
            "enabled": True,
            "profile": "iso16358_2_hspf",
            "correction": {"cd": CD, "aux_cop": 1.0},
            "frost_boundaries": {"lower": -7.0, "upper": 5.5},
            "load_line": {
                "source": "rated_heating_capacity",
                "zero_load_temp": 17.0,
                "full_load_temp": 0.0,
                "rated_capacity_factor": 1.0,
            },
            "bin_hours_key": "hspf_bin_hours",
            "external_calculator_minus7_fallback_override": {
                "minus7_capacity_factor": 1.0,
                "minus7_power_factor": 1.0,
            },
        },
        "hspf_bin_hours": bin_hours,
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return ISO16358Calculator(str(config_path))


def iso_points(*, rated_heating_capacity, include_min=False):
    points = {
        "rated_heating_capacity": rated_heating_capacity,
        "7_full": {"capacity": FULL_CAPACITY, "power": FULL_POWER},
        "7_half": {"capacity": HALF_CAPACITY, "power": HALF_POWER},
    }
    if include_min:
        points["7_min"] = {"capacity": MIN_CAPACITY, "power": MIN_POWER}
    return points


def iso_points_with_extended(*, rated_heating_capacity):
    points = iso_points(rated_heating_capacity=rated_heating_capacity)
    points["2_ext"] = {"capacity": EXTENDED_CAPACITY, "power": EXTENDED_POWER}
    points["-7_ext"] = {"capacity": EXTENDED_CAPACITY, "power": EXTENDED_POWER}
    return points


def rated_for_load_at_7c(load):
    return load * 17.0 / 10.0


def single_detail(result):
    assert len(result["bin_details"]) == 1
    return result["bin_details"][0]


def test_hspf_power_at_half_load_equals_half_power(tmp_path):
    calculator = make_iso_micro_calculator(
        tmp_path,
        [{"j": 1, "tj": 7.0, "nj": 2.0}],
    )
    result = calculator.calculate_hspf(
        iso_points(rated_heating_capacity=rated_for_load_at_7c(HALF_CAPACITY))
    )
    detail = single_detail(result)

    assert detail["bl_h"] == pytest.approx(HALF_CAPACITY)
    assert detail["pi_j"] == pytest.approx(HALF_CAPACITY)
    assert detail["P_j"] == pytest.approx(HALF_POWER)
    assert detail["E_j"] == pytest.approx(HALF_POWER * detail["nj"])
    assert detail["auxiliary_energy"] == pytest.approx(0.0)
    assert detail["case"] == "cycling"


def test_hspf_power_at_full_load_equals_full_power(tmp_path):
    calculator = make_iso_micro_calculator(
        tmp_path,
        [{"j": 1, "tj": 0.0, "nj": 3.0}],
    )
    result = calculator.calculate_hspf(
        iso_points(rated_heating_capacity=FULL_CAPACITY)
    )
    detail = single_detail(result)

    assert detail["bl_h"] == pytest.approx(FULL_CAPACITY)
    assert detail["pi_j"] == pytest.approx(FULL_CAPACITY)
    assert detail["P_j"] == pytest.approx(FULL_POWER)
    assert detail["E_j"] == pytest.approx(FULL_POWER * detail["nj"])
    assert detail["auxiliary_energy"] == pytest.approx(0.0)
    assert detail["case"] == "interpolation"


def test_hspf_cycling_below_min_uses_plf(tmp_path):
    load = 0.5 * MIN_CAPACITY
    hours = 4.0
    calculator = make_iso_micro_calculator(
        tmp_path,
        [{"j": 1, "tj": 7.0, "nj": hours}],
    )
    result = calculator.calculate_hspf(
        iso_points(
            rated_heating_capacity=rated_for_load_at_7c(load),
            include_min=True,
        )
    )
    detail = single_detail(result)
    x = load / MIN_CAPACITY
    plf = 1.0 - CD * (1.0 - x)
    expected_power = x * MIN_POWER / plf

    assert x == pytest.approx(0.5)
    assert detail["case"] == "cycling"
    assert detail["bl_h"] == pytest.approx(load)
    assert detail["P_j"] == pytest.approx(expected_power)
    assert detail["E_j"] == pytest.approx(expected_power * hours)
    assert detail["auxiliary_energy"] == pytest.approx(0.0)


def test_hspf_half_to_full_interpolation_matches_hand_calculation(tmp_path):
    load = 1350.0
    calculator = make_iso_micro_calculator(
        tmp_path,
        [{"j": 1, "tj": 7.0, "nj": 2.5}],
    )
    result = calculator.calculate_hspf(
        iso_points(rated_heating_capacity=rated_for_load_at_7c(load))
    )
    detail = single_detail(result)
    expected_power = HALF_POWER + (
        (FULL_POWER - HALF_POWER)
        * (load - HALF_CAPACITY)
        / (FULL_CAPACITY - HALF_CAPACITY)
    )

    assert detail["case"] == "interpolation"
    assert detail["bl_h"] == pytest.approx(load)
    assert detail["P_j"] == pytest.approx(expected_power)
    assert detail["E_j"] == pytest.approx(expected_power * detail["nj"])
    assert detail["auxiliary_energy"] == pytest.approx(0.0)


def test_hspf_formula50_full_to_extended_matches_boundary_cop(tmp_path):
    load = 1900.0
    hours = 2.0
    calculator = make_iso_micro_calculator(
        tmp_path,
        [{"j": 1, "tj": 0.0, "nj": hours}],
    )
    result = calculator.calculate_hspf(
        iso_points_with_extended(rated_heating_capacity=load)
    )
    detail = single_detail(result)

    expected_tg = 17.0 * (load - FULL_CAPACITY) / load
    expected_tf = 17.0 * (load - EXTENDED_CAPACITY) / load
    full_boundary_cop = FULL_CAPACITY / FULL_POWER
    extended_boundary_cop = EXTENDED_CAPACITY / EXTENDED_POWER
    expected_cop = full_boundary_cop + (
        (extended_boundary_cop - full_boundary_cop)
        * (0.0 - expected_tg)
        / (expected_tf - expected_tg)
    )
    expected_power = load / expected_cop

    assert detail["case"] == "formula50_full_extended_frost"
    assert detail["branch"] == "formula50_full_extended_frost"
    assert detail["bl_h"] == pytest.approx(load)
    assert detail["pi_ext_f"] == pytest.approx(EXTENDED_CAPACITY)
    assert detail["p_ext_f"] == pytest.approx(EXTENDED_POWER)
    assert detail["tg"] == pytest.approx(expected_tg)
    assert detail["tf"] == pytest.approx(expected_tf)
    assert detail["cop_fe_f"] == pytest.approx(expected_cop)
    assert detail["P_fe"] == pytest.approx(expected_power)
    assert detail["P_j"] == pytest.approx(expected_power)
    assert detail["E_j"] == pytest.approx(expected_power * hours)
    assert detail["auxiliary_energy"] == pytest.approx(0.0)
    assert result["hstl_wh"] == pytest.approx(load * hours)
    assert result["hsec_wh"] == pytest.approx(expected_power * hours)


def test_hspf_above_extended_uses_extended_cap_and_auxiliary(tmp_path):
    load = 2400.0
    hours = 2.0
    aux_cop = 1.0
    calculator = make_iso_micro_calculator(
        tmp_path,
        [{"j": 1, "tj": 0.0, "nj": hours}],
    )
    result = calculator.calculate_hspf(
        iso_points_with_extended(rated_heating_capacity=load),
        aux_cop=aux_cop,
    )
    detail = single_detail(result)
    expected_unmet_load = load - EXTENDED_CAPACITY
    expected_heat_pump_energy = EXTENDED_POWER * hours
    expected_auxiliary_energy = expected_unmet_load * hours / aux_cop
    expected_e_j = expected_heat_pump_energy + expected_auxiliary_energy

    assert detail["case"] == "saturated"
    assert detail["pi_j"] == pytest.approx(EXTENDED_CAPACITY)
    assert detail["P_j"] == pytest.approx(EXTENDED_POWER)
    assert detail["heat_pump_energy"] == pytest.approx(expected_heat_pump_energy)
    assert detail["auxiliary_energy"] == pytest.approx(expected_auxiliary_energy)
    assert detail["E_j"] == pytest.approx(expected_e_j)
    assert result["hstl_wh"] == pytest.approx(load * hours)
    assert result["hsec_wh"] == pytest.approx(expected_e_j)


def test_hspf_tiny_bin_accumulation_matches_hand_calculation(tmp_path):
    calculator = make_iso_micro_calculator(
        tmp_path,
        [
            {"j": 1, "tj": 7.0, "nj": 2.0},
            {"j": 2, "tj": 0.0, "nj": 3.0},
        ],
    )
    result = calculator.calculate_hspf(
        iso_points(rated_heating_capacity=FULL_CAPACITY)
    )
    expected_hstl = HALF_CAPACITY * 2.0 + FULL_CAPACITY * 3.0
    expected_hsec = HALF_POWER * 2.0 + FULL_POWER * 3.0

    assert [detail["case"] for detail in result["bin_details"]] == [
        "cycling",
        "interpolation",
    ]
    assert result["hstl_wh"] == pytest.approx(expected_hstl)
    assert result["hsec_wh"] == pytest.approx(expected_hsec)
    assert result["heat_pump_energy_wh"] == pytest.approx(expected_hsec)
    assert result["auxiliary_energy_wh"] == pytest.approx(0.0)
    assert result["hspf"] == pytest.approx(round(expected_hstl / expected_hsec, 3))


def test_hspf_formula45_half_to_full_matches_boundary_cop(tmp_path):
    calculator = make_iso_micro_calculator(tmp_path, [])
    resolved = {
        "7_full": {"capacity": 2000.0, "power": 400.0},
        "7_half": {"capacity": 1000.0, "power": 250.0},
        "2_full": {"capacity": 2000.0, "power": 400.0},
        "2_half": {"capacity": 1000.0, "power": 250.0},
        "-7_full": {"capacity": 2000.0, "power": 400.0},
        "-7_half": {"capacity": 1000.0, "power": 250.0},
    }
    load_line = (-100.0, 1700.0)
    tj = 2.0
    bl_h = 1500.0
    
    result = calculator._iso_hspf_half_full_power_by_formula_45_49(
        tj, bl_h, resolved, False, load_line
    )
    
    assert result["branch"] == "formula45_half_full"
    assert result["cop_half"] == pytest.approx(4.0)
    assert result["cop_full"] == pytest.approx(5.0)
    assert result["cop_hf"] == pytest.approx(4.5)
    assert result["P_hf"] == pytest.approx(1500.0 / 4.5)


def test_hspf_formula49_frost_half_to_full_matches_boundary_cop(tmp_path):
    calculator = make_iso_micro_calculator(tmp_path, [])
    resolved = {
        "7_full": {"capacity": 2000.0, "power": 400.0},
        "7_half": {"capacity": 1000.0, "power": 250.0},
        "2_full": {"capacity": 2000.0, "power": 400.0},
        "2_half": {"capacity": 1000.0, "power": 250.0},
        "-7_full": {"capacity": 2000.0, "power": 400.0},
        "-7_half": {"capacity": 1000.0, "power": 250.0},
    }
    load_line = (-100.0, 1700.0)
    tj = 0.0
    bl_h = 1500.0
    
    result = calculator._iso_hspf_half_full_power_by_formula_45_49(
        tj, bl_h, resolved, True, load_line
    )
    
    assert result["branch"] == "formula49_half_full_frost"
    assert result["cop_half"] == pytest.approx(4.0)
    assert result["cop_full"] == pytest.approx(5.0)
    assert result["cop_hf"] == pytest.approx(4.7)
    assert result["P_hf"] == pytest.approx(1500.0 / 4.7)


def test_hspf_formula45_49_rejects_load_outside_half_full_range(tmp_path):
    calculator = make_iso_micro_calculator(tmp_path, [])
    resolved = {
        "7_full": {"capacity": 2000.0, "power": 400.0},
        "7_half": {"capacity": 1000.0, "power": 250.0},
        "2_full": {"capacity": 2000.0, "power": 400.0},
        "2_half": {"capacity": 1000.0, "power": 250.0},
        "-7_full": {"capacity": 2000.0, "power": 400.0},
        "-7_half": {"capacity": 1000.0, "power": 250.0},
    }
    load_line = (-100.0, 1700.0)
    tj = 2.0
    
    with pytest.raises(ValueError, match="outside the half"):
        calculator._iso_hspf_half_full_power_by_formula_45_49(
            tj, 500.0, resolved, False, load_line
        )
        
    with pytest.raises(ValueError, match="outside the half"):
        calculator._iso_hspf_half_full_power_by_formula_45_49(
            tj, 2500.0, resolved, False, load_line
        )


def test_hspf_formula45_49_boundary_identity(tmp_path):
    calculator = make_iso_micro_calculator(tmp_path, [])
    resolved = {
        "7_full": {"capacity": 2000.0, "power": 400.0},
        "7_half": {"capacity": 1000.0, "power": 250.0},
        "2_full": {"capacity": 2000.0, "power": 400.0},
        "2_half": {"capacity": 1000.0, "power": 250.0},
        "-7_full": {"capacity": 2000.0, "power": 400.0},
        "-7_half": {"capacity": 1000.0, "power": 250.0},
    }
    load_line = (-100.0, 1700.0)
    
    tj_half = 7.0
    bl_h_half = 1000.0
    result_half = calculator._iso_hspf_half_full_power_by_formula_45_49(
        tj_half, bl_h_half, resolved, False, load_line
    )
    assert result_half["P_hf"] == pytest.approx(250.0)
    
    tj_full = -3.0
    bl_h_full = 2000.0
    result_full = calculator._iso_hspf_half_full_power_by_formula_45_49(
        tj_full, bl_h_full, resolved, False, load_line
    )
    assert result_full["P_hf"] == pytest.approx(400.0)


def test_hspf_formula47_full_to_extended_matches_boundary_cop(tmp_path):
    calculator = make_iso_micro_calculator(tmp_path, [])
    resolved = {
        "7_full": {"capacity": 2000.0, "power": 400.0},
        "7_ext": {"capacity": 3000.0, "power": 750.0},
        "2_full": {"capacity": 2000.0, "power": 400.0},
        "2_ext": {"capacity": 3000.0, "power": 750.0},
        "-7_full": {"capacity": 2000.0, "power": 400.0},
        "-7_ext": {"capacity": 3000.0, "power": 750.0},
    }
    load_line = (-100.0, 1700.0)
    tj = 6.0
    bl_h = 2500.0
    
    result = calculator._iso_hspf_formula47_full_extended_non_frost_power(
        tj, bl_h, resolved, load_line
    )
    
    # Calculate the intersection temperatures for validation
    full_temp = calculator._iso_hspf_intersection_temp("full", resolved, False, load_line)
    ext_temp = calculator._iso_hspf_intersection_temp("ext", resolved, False, load_line)
    
    assert result["branch"] == "formula47_full_extended"
    assert result["cop_full"] == pytest.approx(5.0)
    assert result["cop_ext"] == pytest.approx(4.0)
    
    expected_cop_fe = 4.0 + (5.0 - 4.0) * (tj - ext_temp) / (full_temp - ext_temp)
    assert result["cop_fe"] == pytest.approx(expected_cop_fe)
    assert result["P_fe"] == pytest.approx(2500.0 / expected_cop_fe)


def test_hspf_formula47_boundary_identity(tmp_path):
    calculator = make_iso_micro_calculator(tmp_path, [])
    resolved = {
        "7_full": {"capacity": 2000.0, "power": 400.0},
        "7_ext": {"capacity": 3000.0, "power": 750.0},
        "2_full": {"capacity": 2000.0, "power": 400.0},
        "2_ext": {"capacity": 3000.0, "power": 750.0},
        "-7_full": {"capacity": 2000.0, "power": 400.0},
        "-7_ext": {"capacity": 3000.0, "power": 750.0},
    }
    load_line = (-100.0, 1700.0)
    
    tj_full = calculator._iso_hspf_intersection_temp("full", resolved, False, load_line)
    bl_h_full = calculator._iso_hspf_capacity_curve(tj_full, "full", resolved, False)
    result_full = calculator._iso_hspf_formula47_full_extended_non_frost_power(
        tj_full, bl_h_full, resolved, load_line
    )
    expected_p_full = calculator._iso_hspf_power_curve(tj_full, "full", resolved, False)
    assert result_full["P_fe"] == pytest.approx(expected_p_full)
    
    tj_ext = calculator._iso_hspf_intersection_temp("ext", resolved, False, load_line)
    bl_h_ext = calculator._iso_hspf_capacity_curve(tj_ext, "ext", resolved, False)
    result_ext = calculator._iso_hspf_formula47_full_extended_non_frost_power(
        tj_ext, bl_h_ext, resolved, load_line
    )
    expected_p_ext = calculator._iso_hspf_power_curve(tj_ext, "ext", resolved, False)
    assert result_ext["P_fe"] == pytest.approx(expected_p_ext)


def test_hspf_formula47_rejects_load_outside_full_extended_range(tmp_path):
    calculator = make_iso_micro_calculator(tmp_path, [])
    resolved = {
        "7_full": {"capacity": 2000.0, "power": 400.0},
        "7_ext": {"capacity": 3000.0, "power": 750.0},
        "2_full": {"capacity": 2000.0, "power": 400.0},
        "2_ext": {"capacity": 3000.0, "power": 750.0},
        "-7_full": {"capacity": 2000.0, "power": 400.0},
        "-7_ext": {"capacity": 3000.0, "power": 750.0},
    }
    load_line = (-100.0, 1700.0)
    tj = 6.0
    
    with pytest.raises(ValueError, match="outside the full .* to extended"):
        calculator._iso_hspf_formula47_full_extended_non_frost_power(
            tj, 1500.0, resolved, load_line
        )
        
    with pytest.raises(ValueError, match="outside the full .* to extended"):
        calculator._iso_hspf_formula47_full_extended_non_frost_power(
            tj, 3500.0, resolved, load_line
        )
