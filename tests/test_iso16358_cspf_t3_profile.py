import pytest
import json
from core.calculator_iso16358 import ISO16358Calculator

def create_calc(tmp_path, profile, selection, bin_hours):
    config = {
        "cspf_test_profile": {
            "climate_profile": profile,
            "test_selection": selection
        },
        "bin_hours": bin_hours,
        "t_100_load": 35.0,
        "t_0_load": 20.0,
        "power_interpolation_method": "iso_boundary_eer"
    }
    path = tmp_path / "config.json"
    with open(path, "w") as f:
        json.dump(config, f)
    return ISO16358Calculator(str(path))

def test_t3_required_only_resolver_defaults(tmp_path):
    calc = create_calc(tmp_path, "T3", "required_only", [])
    measured = {
        "46_full": {"capacity": 5418, "power": 1971},
        "35_full": {"capacity": 6058, "power": 1611},
        "35_half": {"capacity": 3036, "power": 566}
    }
    
    assert calc._get_cspf_profile_cd() == 0.27
    
    resolved = calc._resolve_cspf_profile_points(measured)
    
    assert "46_half" in resolved
    assert resolved["46_half"]["capacity"] == pytest.approx(3036 * 0.859, abs=0.01)
    assert resolved["46_half"]["power"] == pytest.approx(566 * 1.25, abs=0.01)
    
    assert "29_half" in resolved
    assert resolved["29_half"]["capacity"] == pytest.approx(3036 * 1.077, abs=0.01)
    assert resolved["29_half"]["power"] == pytest.approx(566 * 0.914, abs=0.01)
    
    assert "35_min" not in resolved
    assert "29_min" not in resolved
    assert "46_min" not in resolved

def test_t3_required_only_smoke(tmp_path):
    bin_hours = [
        {"tj": 25.0, "nj": 1000}, # tj <= 35
        {"tj": 40.0, "nj": 500}   # tj > 35
    ]
    calc = create_calc(tmp_path, "T3", "required_only", bin_hours)
    measured = {
        "46_full": {"capacity": 5418, "power": 1971},
        "35_full": {"capacity": 6058, "power": 1611},
        "35_half": {"capacity": 3036, "power": 566}
    }
    
    res = calc.calculate_cspf(measured)
    
    assert "cspf" in res
    assert res["cspf"] > 0
    assert res["annual_cooling_kwh"] > 0
    assert res["annual_power_kwh"] > 0

def test_t3_with_optional_test_resolver_defaults(tmp_path):
    calc = create_calc(tmp_path, "T3", "with_optional_test", [])
    measured = {
        "46_full": {"capacity": 5418, "power": 1971},
        "35_full": {"capacity": 6058, "power": 1611},
        "35_half": {"capacity": 3036, "power": 566},
        "35_min":  {"capacity": 1780, "power": 284}
    }
    
    assert calc._get_active_load_levels() == ["full", "half", "min"]
    
    resolved = calc._resolve_cspf_profile_points(measured)
    
    assert "35_min" in resolved
    
    assert "46_min" in resolved
    assert resolved["46_min"]["capacity"] == pytest.approx(1780 * 0.859, abs=0.01)
    assert resolved["46_min"]["power"] == pytest.approx(284 * 1.25, abs=0.01)
    
    assert "29_min" in resolved
    assert resolved["29_min"]["capacity"] == pytest.approx(1780 * 1.077, abs=0.01)
    assert resolved["29_min"]["power"] == pytest.approx(284 * 0.914, abs=0.01)

def test_t3_with_optional_test_smoke_changes_result(tmp_path):
    bin_hours = [
        {"tj": 25.0, "nj": 1000}, # tj <= 35
        {"tj": 40.0, "nj": 500}   # tj > 35
    ]
    calc_req = create_calc(tmp_path, "T3", "required_only", bin_hours)
    calc_opt = create_calc(tmp_path, "T3", "with_optional_test", bin_hours)
    
    measured_req = {
        "46_full": {"capacity": 5418, "power": 1971},
        "35_full": {"capacity": 6058, "power": 1611},
        "35_half": {"capacity": 3036, "power": 566}
    }
    res_req = calc_req.calculate_cspf(measured_req)
    
    measured_opt = {
        "46_full": {"capacity": 5418, "power": 1971},
        "35_full": {"capacity": 6058, "power": 1611},
        "35_half": {"capacity": 3036, "power": 566},
        "35_min":  {"capacity": 1780, "power": 284}
    }
    res_opt = calc_opt.calculate_cspf(measured_opt)
    
    assert res_opt["cspf"] > 0
    assert res_opt["annual_cooling_kwh"] > 0
    assert res_opt["annual_power_kwh"] > 0
    
    print(f"\nT3 Required Only: CSPF={res_req['cspf']}")
    print(f"T3 With Optional: CSPF={res_opt['cspf']}")
    assert res_req["cspf"] != res_opt["cspf"]

def test_iso16358_cspf_t3_saso_diagnostic(tmp_path):
    bin_hours = [
        {"tj": 20, "nj": 0}, {"tj": 21, "nj": 267}, {"tj": 22, "nj": 279}, {"tj": 23, "nj": 281}, 
        {"tj": 24, "nj": 314}, {"tj": 25, "nj": 309}, {"tj": 26, "nj": 341}, {"tj": 27, "nj": 357}, 
        {"tj": 28, "nj": 366}, {"tj": 29, "nj": 411}, {"tj": 30, "nj": 435}, {"tj": 31, "nj": 464}, 
        {"tj": 32, "nj": 501}, {"tj": 33, "nj": 492}, {"tj": 34, "nj": 456}, {"tj": 35, "nj": 408}, 
        {"tj": 36, "nj": 395}, {"tj": 37, "nj": 360}, {"tj": 38, "nj": 357}, {"tj": 39, "nj": 335}, 
        {"tj": 40, "nj": 325}, {"tj": 41, "nj": 290}, {"tj": 42, "nj": 240}, {"tj": 43, "nj": 200}, 
        {"tj": 44, "nj": 130}, {"tj": 45, "nj": 78}, {"tj": 46, "nj": 24}
    ]
    
    calc = create_calc(tmp_path, "T3", "with_optional_test", bin_hours)
    measured = {
        "46_full": {"capacity": 5418, "power": 1971},
        "35_full": {"capacity": 6058, "power": 1611},
        "35_half": {"capacity": 3036, "power": 566},
        "35_min":  {"capacity": 1780, "power": 284}
    }
    
    res = calc.calculate_cspf(measured)
    
    assert res["cspf"] > 0
    assert res["annual_cooling_kwh"] > 0
    assert res["annual_power_kwh"] > 0
    
    actual_cspf = res["cspf"]
    target_cspf = 4.95
    abs_diff = abs(actual_cspf - target_cspf)
    
    print(f"\nSASO Diagnostic:")
    print(f"Actual CSPF: {actual_cspf}")
    print(f"Target CSPF: {target_cspf}")
    print(f"Absolute Diff: {abs_diff:.3f}")
    
    if abs_diff < 0.5:
        print("Note: The actual CSPF is naturally within 0.5 of the target 4.95.")
