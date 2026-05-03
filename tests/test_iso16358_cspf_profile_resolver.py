import pytest
from core.calculator_iso16358 import ISO16358Calculator
import json
import os

def test_cspf_profile_resolver_t1_required_only():
    config = {
        "cspf_test_profile": {
            "climate_profile": "T1",
            "test_selection": "required_only"
        },
        "points": {"35_full": "measure", "35_half": "measure"}
    }
    
    with open("temp_t1_req.json", "w") as f:
        json.dump(config, f)
        
    calc = ISO16358Calculator("temp_t1_req.json")
    measured = {
        "35_full": {"capacity": 10000, "power": 3000},
        "35_half": {"capacity": 5000, "power": 1200}
    }
    
    resolved = calc.resolve_points(measured)
    
    assert "29_full" in resolved
    assert "29_half" in resolved
    assert "35_min" not in resolved
    assert "29_min" not in resolved
    
    # 1.077 * 10000 = 10770, 0.914 * 3000 = 2742
    assert resolved["29_full"]["capacity"] == 10770
    assert resolved["29_full"]["power"] == 2742
    
    assert calc._get_cspf_profile_cd() == 0.25
    assert calc._get_active_load_levels() == ["full", "half"]
    
    os.remove("temp_t1_req.json")

def test_cspf_profile_resolver_t1_with_optional():
    config = {
        "cspf_test_profile": {
            "climate_profile": "T1",
            "test_selection": "with_optional_test"
        },
        "points": {"35_full": "measure", "35_half": "measure", "35_min": "measure"}
    }
    
    with open("temp_t1_opt.json", "w") as f:
        json.dump(config, f)
        
    calc = ISO16358Calculator("temp_t1_opt.json")
    measured = {
        "35_full": {"capacity": 10000, "power": 3000},
        "35_half": {"capacity": 5000, "power": 1200},
        "35_min": {"capacity": 3000, "power": 600}
    }
    
    resolved = calc.resolve_points(measured)
    assert "29_min" in resolved
    assert calc._get_active_load_levels() == ["full", "half", "min"]
    os.remove("temp_t1_opt.json")

def test_cspf_profile_resolver_t3_required_only():
    config = {
        "cspf_test_profile": {
            "climate_profile": "T3",
            "test_selection": "required_only"
        },
        "points": {"46_full": "measure", "35_full": "measure", "35_half": "measure"}
    }
    
    with open("temp_t3_req.json", "w") as f:
        json.dump(config, f)
        
    calc = ISO16358Calculator("temp_t3_req.json")
    measured = {
        "46_full": {"capacity": 9000, "power": 3500},
        "35_full": {"capacity": 10000, "power": 3000},
        "35_half": {"capacity": 5000, "power": 1200}
    }
    
    resolved = calc.resolve_points(measured)
    assert "46_half" in resolved
    assert "29_half" in resolved
    assert calc._get_cspf_profile_cd() == 0.27
    os.remove("temp_t3_req.json")

def test_legacy_config_integrity():
    # Legacy config (no cspf_test_profile)
    # Reusing an existing config file that doesn't have the key
    calc = ISO16358Calculator("data/region_configs/iso_t1_default_2point.json")
    
    measured = {
        "35_full": {"capacity": 10000, "power": 3000},
        "35_half": {"capacity": 5000, "power": 1200}
    }
    
    # Should not raise, should perform normal resolve_points
    resolved = calc.resolve_points(measured)
    assert resolved["35_full"]["capacity"] == 10000
    assert "29_half" in resolved
    assert resolved["29_half"]["capacity"] == 5000 * 1.077
