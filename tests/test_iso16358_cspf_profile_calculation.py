import pytest
from core.calculator_iso16358 import ISO16358Calculator
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
