import json
from pathlib import Path
import pytest

from core.calculator_iso16358_legacy import ISO16358Calculator

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/region_configs/saso.json"

@pytest.fixture
def saso_measured():
    return {
        "46_full": {"capacity": 5418, "power": 1971},
        "35_full": {"capacity": 6058, "power": 1611},
        "35_half": {"capacity": 3036, "power": 566},
        "35_min":  {"capacity": 1780, "power": 284}
    }

def test_saso_t3_config_resolves_profile_points(saso_measured):
    calc = ISO16358Calculator(str(CONFIG_PATH))
    
    assert calc.t_100_load == 46.0
    assert calc.t_0_load == 20.0
    assert calc.reference_point == "46_full"
    assert calc.config.get("Cd") == 0.27
    
    active_levels = calc._get_active_load_levels()
    assert active_levels == ["full", "half", "min"]
    
    resolved = calc._resolve_cspf_profile_points(saso_measured)
    
    assert "46_half" in resolved
    assert resolved["46_half"]["capacity"] == pytest.approx(3036 * 0.859, abs=0.01)
    assert resolved["46_half"]["power"] == pytest.approx(566 * 1.25, abs=0.01)
    
    assert "46_min" in resolved
    assert resolved["46_min"]["capacity"] == pytest.approx(1780 * 0.859, abs=0.01)
    assert resolved["46_min"]["power"] == pytest.approx(284 * 1.25, abs=0.01)
    
    assert "29_full" in resolved
    assert resolved["29_full"]["capacity"] == pytest.approx(6058 * 1.077, abs=0.01)
    assert resolved["29_full"]["power"] == pytest.approx(1611 * 0.914, abs=0.01)

    assert "29_half" in resolved
    assert resolved["29_half"]["capacity"] == pytest.approx(3036 * 1.077, abs=0.01)
    assert resolved["29_half"]["power"] == pytest.approx(566 * 0.914, abs=0.01)
    
    assert "29_min" in resolved
    assert resolved["29_min"]["capacity"] == pytest.approx(1780 * 1.077, abs=0.01)
    assert resolved["29_min"]["power"] == pytest.approx(284 * 0.914, abs=0.01)


def test_saso_t3_golden_regression(saso_measured):
    """SASO T3 hard regression matching official xlsm tool."""
    calc = ISO16358Calculator(str(CONFIG_PATH))
    res = calc.calculate_cspf(saso_measured)
    
    # Official xlsm:
    # CSTL = 21,546,478 Wh ≈ 21,546.48 kWh
    # CSEC = 4,349,360 Wh  ≈ 4,349.36 kWh
    # CSPF = 4.954
    
    print(f"\n[SASO T3 Final Regression Check]")
    print(f"annual_cooling_kwh: {res['annual_cooling_kwh']} (Target: 21546.48)")
    print(f"annual_power_kwh:   {res['annual_power_kwh']} (Target: 4349.36)")
    print(f"cspf:               {res['cspf']} (Target: 4.954)")
    
    assert abs(res["annual_cooling_kwh"] - 21546.48) < 5
    assert abs(res["annual_power_kwh"] - 4349.36) < 5
    assert abs(res["cspf"] - 4.954) < 0.01

def test_saso_t3_representative_bins(saso_measured):
    """Verify specific bin values from official xlsm trace."""
    calc = ISO16358Calculator(str(CONFIG_PATH))
    resolved = calc._resolve_cspf_profile_points(saso_measured)
    delta_t = calc.t_100_load - calc.t_0_load
    L_c_ref = resolved[calc.reference_point]["capacity"]
    
    def get_bin_calc(tj):
        Lc = L_c_ref * (tj - calc.t_0_load) / delta_t
        interp = calc.interpolate(tj, resolved)
        loads = sorted([(data["capacity"], data["power"], load_type) for load_type, data in interp.items()], key=lambda x: x[0])
        low_cap, low_pow, _ = loads[0]
        high_cap, high_pow, _ = loads[-1]
        
        cooling = Lc
        pwr = 0.0
        if Lc <= low_cap:
            X = Lc / low_cap
            PLF = 1.0 - 0.27 * (1.0 - X)
            pwr = (X * low_pow) / PLF
        elif Lc > high_cap:
            cooling = high_cap
            pwr = high_pow
        else:
            # direct linear
            for i in range(len(loads)-1):
                c1, p1, _ = loads[i]
                c2, p2, _ = loads[i+1]
                if c1 < Lc <= c2:
                    pwr = p1 + (p2 - p1) * (Lc - c1) / (c2 - c1)
                    break
        return cooling, pwr

    # 25°C: cooling_output≈1041.92, P_tj≈145.07
    c25, p25 = get_bin_calc(25.0)
    assert c25 == pytest.approx(1041.92, abs=0.1)
    assert p25 == pytest.approx(145.07, abs=0.1)

    # 35°C: cooling_output≈3125.77, P_tj≈597.04
    c35, p35 = get_bin_calc(35.0)
    assert c35 == pytest.approx(3125.77, abs=0.1)
    assert p35 == pytest.approx(597.04, abs=0.1)

    # 40°C: cooling_output≈4167.69, P_tj≈1149.00
    c40, p40 = get_bin_calc(40.0)
    assert c40 == pytest.approx(4167.69, abs=0.1)
    assert p40 == pytest.approx(1149.00, abs=0.1)

    # 46°C: cooling_output≈5418.00, P_tj≈1971.00
    c46, p46 = get_bin_calc(46.0)
    assert c46 == pytest.approx(5418.00, abs=0.1)
    assert p46 == pytest.approx(1971.00, abs=0.1)


def test_saso_t3_diagnostic_reports_current_cspf(saso_measured):
    calc = ISO16358Calculator(str(CONFIG_PATH))
    res = calc.calculate_cspf(saso_measured)
    
    assert res["cspf"] > 0
    assert res["annual_power_kwh"] > 0
    
    print(f"\n--- SASO T3 Diagnostic ---")
    print(f"Current CSPF: {res['cspf']}")
    print(f"Golden CSPF: 4.954")
    print(f"CSPF Diff: {abs(res['cspf'] - 4.954):.3f}")
    print(f"Current CSEC (kWh): {res['annual_power_kwh']}")
    print(f"Golden CSEC (kWh): 4349.360")
    print(f"CSEC Diff (kWh): {abs(res['annual_power_kwh'] - 4349.360):.3f}")
