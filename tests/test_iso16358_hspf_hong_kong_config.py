import pytest
from pathlib import Path
from core.calculators.standards.iso16358 import ISO16358Calculator

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/region_configs/hong_kong.json"

def get_calculator():
    return ISO16358Calculator(str(CONFIG_PATH))

def test_hong_kong_hspf_golden_case_1():
    calc = get_calculator()
    measured_inputs = {
        "7_full": {"capacity": 6300, "power": 1500},
        "7_half": {"capacity": 3200, "power": 800}
    }
    
    # Golden value verified by manual calculation:
    # -7_full derived: cap=6300*0.64=4032, pwr=1500*0.82=1230
    # -7_half derived: cap=3200*0.64=2048, pwr=800*0.82=656
    # 2_full footnote d: cap=5490.0, pwr=1403.57
    # 2_half footnote d: cap=2788.57, pwr=748.57
    # L_h_ref=7_full_capacity*0.82=5166, HSTL=273190.24, HSEC=74988.35
    # HSPF raw=3.6431 → round(3)=3.643
    result = calc.calculate_hspf(measured_inputs)
    assert result["hspf"] == pytest.approx(3.643, abs=0.001)

def test_hong_kong_hspf_golden_case_2():
    calc = get_calculator()
    measured_inputs = {
        "7_full": {"capacity": 6100, "power": 1300},
        "7_half": {"capacity": 3000, "power": 600}
    }

    # Golden value verified by manual calculation:
    # -7_full derived: cap=6100*0.64=3904, pwr=1300*0.82=1066
    # -7_half derived: cap=3000*0.64=1920, pwr=600*0.82=492
    # 2_full footnote d: cap=5315.71, pwr=1216.43
    # 2_half footnote d: cap=2614.29, pwr=561.43
    # L_h_ref=7_full_capacity*0.82=5002, HSTL=264517.53, HSEC=57860.69
    # HSPF raw=4.5716 → round(3)=4.572

    result = calc.calculate_hspf(measured_inputs)
    assert result["hspf"] == pytest.approx(4.572, abs=0.001)

def test_hong_kong_hspf_bin_hours_total_240():
    calc = get_calculator()
    hspf_bin_hours = calc.config.get("hspf_bin_hours", [])
    total_hours = sum(bin_data.get("nj", 0) for bin_data in hspf_bin_hours)
    # Adjust config to total 240
    assert total_hours == 240

def test_hong_kong_hspf_load_line_uses_measured_7_full_capacity():
    calc = get_calculator()
    load_line = calc.config["hspf"]["load_line"]
    assert load_line["source"] == "measured_point_capacity"
    assert load_line["point_key"] == "7_full"
    assert load_line["field"] == "capacity"

    base = {
        "7_full": {"capacity": 6300, "power": 1500},
        "7_half": {"capacity": 3200, "power": 800}
    }
    with_mismatched_rated = {
        **base,
        "rated_heating_capacity": 9999,
    }

    assert calc.calculate_hspf(base)["hspf"] == pytest.approx(
        calc.calculate_hspf(with_mismatched_rated)["hspf"],
        abs=0.000001,
    )

def test_hong_kong_hspf_ignores_optional_rated_heating_capacity_value():
    calc = get_calculator()
    measured_inputs = {
        "rated_heating_capacity": 0,
        "7_full": {"capacity": 6300, "power": 1500},
        "7_half": {"capacity": 3200, "power": 800},
    }
    assert calc.calculate_hspf(measured_inputs)["hspf"] == pytest.approx(3.643, abs=0.001)

def test_hong_kong_hspf_missing_7_full():
    calc = get_calculator()
    with pytest.raises(ValueError, match="7_full"):
        calc.calculate_hspf({"7_half": {"capacity": 3200, "power": 800}})

def test_hong_kong_hspf_missing_7_half():
    calc = get_calculator()
    with pytest.raises(ValueError, match="7_half"):
        calc.calculate_hspf({"7_full": {"capacity": 6300, "power": 1500}})

def test_hong_kong_hspf_invalid_point_values():
    calc = get_calculator()
    with pytest.raises(ValueError):
        calc.calculate_hspf({"7_full": {"capacity": 6300, "power": 0}, "7_half": {"capacity": 3200, "power": 800}})
    with pytest.raises(ValueError):
        calc.calculate_hspf({"7_full": {"capacity": -1, "power": 1500}, "7_half": {"capacity": 3200, "power": 800}})
    with pytest.raises(ValueError):
        calc.calculate_hspf({"7_full": {"capacity": 6300}, "7_half": {"capacity": 3200, "power": 800}})

def test_hong_kong_hspf_aux_cop_zero():
    calc = get_calculator()
    measured_inputs = {"7_full": {"capacity": 6300, "power": 1500}, "7_half": {"capacity": 3200, "power": 800}}
    with pytest.raises(ValueError):
        calc.calculate_hspf(measured_inputs, aux_cop=0)

def test_hong_kong_hspf_2half_measured_ignored():
    calc = get_calculator()
    base = {
        "7_full": {"capacity": 6300, "power": 1500},
        "7_half": {"capacity": 3200, "power": 800}
    }
    variant = base.copy()
    variant["2_half"] = {"capacity": 999999, "power": 1}
    
    base_res = calc.calculate_hspf(base)
    variant_res = calc.calculate_hspf(variant)
    assert base_res["hspf"] == pytest.approx(variant_res["hspf"], abs=0.000001)
