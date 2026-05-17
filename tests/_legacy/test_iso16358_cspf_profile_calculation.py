import pytest
from core._legacy.calculator_iso16358_legacy import ISO16358Calculator
import json
import os

def test_cspf_profile_calculation_t1_required_only():
    config = {
        "cspf_test_profile": {
            "climate_profile": "T1",
            "test_selection": "required_only"
        },
        "bin_hours": [{"tj": 25.0, "nj": 1000}, {"tj": 35.0, "nj": 500}]
    }
    
    with open("temp_calc.json", "w") as f:
        json.dump(config, f)
        
    calc = ISO16358Calculator("temp_calc.json")
    measured = {
        "35_full": {"capacity": 10000, "power": 3000},
        "35_half": {"capacity": 5000, "power": 1200}
    }
    
    result = calc.calculate_cspf(measured)
    assert "cspf" in result
    assert result["cspf"] > 0
    os.remove("temp_calc.json")

def test_cspf_profile_calculation_t1_with_optional_test():
    # Base configuration mimicking ISO T1 default 2-point
    legacy_calc = ISO16358Calculator("data/region_configs/iso_t1_default_2point.json")
    
    # Run required_only
    config_req = {
        "cspf_test_profile": {
            "climate_profile": "T1",
            "test_selection": "required_only"
        },
        "bin_hours": legacy_calc.bin_hours,
        "t_100_load": 35.0,
        "t_0_load": 20.0,
        "Cd": 0.25,
        "power_interpolation_method": "iso_boundary_eer"
    }
    with open("temp_req.json", "w") as f:
        json.dump(config_req, f)
    calc_req = ISO16358Calculator("temp_req.json")
    
    measured_req = {
        "35_full": {"capacity": 10000, "power": 3000},
        "35_half": {"capacity": 5000, "power": 1200}
    }
    res_req = calc_req.calculate_cspf(measured_req)
    
    # Run with_optional_test
    config_opt = {
        "cspf_test_profile": {
            "climate_profile": "T1",
            "test_selection": "with_optional_test"
        },
        "bin_hours": legacy_calc.bin_hours,
        "t_100_load": 35.0,
        "t_0_load": 20.0,
        "Cd": 0.25,
        "power_interpolation_method": "iso_boundary_eer"
    }
    with open("temp_opt.json", "w") as f:
        json.dump(config_opt, f)
    calc_opt = ISO16358Calculator("temp_opt.json")
    
    # Include 35_min point for optional minimum test
    measured_opt = {
        "35_full": {"capacity": 10000, "power": 3000},
        "35_half": {"capacity": 5000, "power": 1200},
        "35_min": {"capacity": 2500, "power": 500}
    }
    
    # Check resolver generating 29_min
    resolved = calc_opt._resolve_cspf_profile_points(measured_opt)
    assert "29_min" in resolved
    assert resolved["29_min"]["capacity"] == pytest.approx(2500 * 1.077, abs=0.01)
    assert resolved["29_min"]["power"] == pytest.approx(500 * 0.914, abs=0.01)

    res_opt = calc_opt.calculate_cspf(measured_opt)
    
    # Verify outputs exist and are > 0
    assert "cspf" in res_opt
    assert res_opt["cspf"] > 0
    assert res_opt["annual_cooling_kwh"] > 0
    assert res_opt["annual_power_kwh"] > 0
    
    # Verify difference from required_only
    print(f"Required Only: CSPF={res_req['cspf']}")
    print(f"With Optional: CSPF={res_opt['cspf']}")
    assert res_opt["cspf"] != res_req["cspf"]
    
    os.remove("temp_req.json")
    os.remove("temp_opt.json")

def test_cspf_profile_vs_legacy_t1():
    # Load default T1 2-point config
    legacy_calc = ISO16358Calculator("data/region_configs/iso_t1_default_2point.json")
    measured = {
        "35_full": {"capacity": 10000, "power": 3000},
        "35_half": {"capacity": 5000, "power": 1200}
    }
    legacy_res = legacy_calc.calculate_cspf(measured)
    
    # Create profile config mirroring T1 2-point
    config = {
        "cspf_test_profile": {
            "climate_profile": "T1",
            "test_selection": "required_only"
        },
        "bin_hours": legacy_calc.bin_hours,
        "t_100_load": 35.0,
        "t_0_load": 20.0,
        "Cd": 0.25,
        "power_interpolation_method": "iso_boundary_eer"
    }
    with open("temp_profile.json", "w") as f:
        json.dump(config, f)
    
    profile_calc = ISO16358Calculator("temp_profile.json")
    profile_res = profile_calc.calculate_cspf(measured)
    
    # Compare
    assert abs(profile_res["cspf"] - legacy_res["cspf"]) < 0.05
    os.remove("temp_profile.json")
