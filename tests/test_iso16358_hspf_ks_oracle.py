import pytest
from core.calculators.standards.iso16358 import ISO16358Calculator
from core.calculators.standards.ks_c9306 import KSC9306Calculator

# This test is a test-only shared-formula oracle probe. 
# It does not define ISO official expected values.

def get_neutralized_fixture():
    return {
        "capacity": {
            "min": {"7": 1000.0},
            "intermediate": {"7": 2000.0},
            "rated": {"7": 3000.0},
            "max": {"-7": 3200.0, "2": 4000.0, "def": 3500.0}
        },
        "power": {
            "min": {"7": 200.0},
            "intermediate": {"7": 500.0},
            "rated": {"7": 800.0},
            "max": {"-7": 1000.0, "2": 1300.0, "def": 1100.0}
        },
        "correction": {"cd": 0.0},
        "load_line": {"slope": 100.0, "intercept": 500.0, "source": "test"}
    }

def test_iso_hspf_common_matches_ks_oracle_on_neutralized_fixture():
    """
    H-2a/H-2b: Verify consistency for base points (no cycling, Cd=0).
    At exact test points, both paths should yield identical results.
    """
    ks_calc = KSC9306Calculator.from_config_path("data/region_configs/korea.json")
    iso_calc = ISO16358Calculator("data/region_configs/korea.json")
    ks_calc.Cd = 0.0
    iso_calc.Cd = 0.0
    
    ks_input = get_neutralized_fixture()
    ks_input["correction"]["cd"] = 0.0
    
    tj = 7.0
    load = 1000.0 # Exactly at min_capacity
    hours = 2.0
    
    bin_row_ks = ks_calc._ks_hspf_bin(tj, load, hours, ks_input)
    
    # Equivalent ISO inputs
    measured_inputs = {
        "7_full": {"capacity": 3000.0, "power": 800.0, "temp": 7.0},
        "7_half": {"capacity": 2000.0, "power": 500.0, "temp": 7.0},
        "7_min": {"capacity": 1000.0, "power": 200.0, "temp": 7.0},
        "-7_full": {"capacity": 3000.0, "power": 800.0, "temp": -7.0},
        "2_full": {"capacity": 3000.0, "power": 800.0, "temp": 2.0},
    }
    
    bin_row_iso = iso_calc._variable_heating_bin(tj, load, hours, measured_inputs)
    
    # Analyze the result
    print(f"\nBin Row (non-cycling, Cd=0): {bin_row_ks}")
    
    assert bin_row_ks["heat_pump_capacity"] == 1000.0
    assert bin_row_ks["heat_pump_energy"] == pytest.approx(bin_row_iso["heat_pump_energy"])
    assert bin_row_ks["heat_pump_energy"] == pytest.approx(200.0 * 2.0)

def test_iso_hspf_common_matches_ks_oracle_on_neutralized_cycling_fixture():
    """
    H-2b: Verify consistency for cycling and non-zero Cd cases.
    Ensures that both ISO common path and KS path follow the same shared formula
    for cycling (load < min_capacity) when Cd > 0.
    """
    ks_calc = KSC9306Calculator.from_config_path("data/region_configs/korea.json")
    iso_calc = ISO16358Calculator("data/region_configs/korea.json")
    
    # Set Cd = 0.35 for both paths
    cd_val = 0.35
    ks_calc.Cd = cd_val
    iso_calc.Cd = cd_val
    
    # 1. Neutralized KS fixture for cycling
    # Load < Min Capacity
    ks_input = {
        "capacity": {
            "min": {"7": 1000.0, "-7": 1000.0},
            "intermediate": {"7": 2000.0, "-7": 2000.0},
            "rated": {"7": 3000.0, "-7": 3000.0},
            "max": {"-7": 3000.0, "def": 3000.0}
        },
        "power": {
            "min": {"7": 200.0, "-7": 200.0},
            "intermediate": {"7": 500.0, "-7": 500.0},
            "rated": {"7": 800.0, "-7": 800.0},
            "max": {"-7": 1000.0, "def": 1000.0}
        },
        "correction": {"cd": cd_val},
        "load_line": {"slope": 100.0, "intercept": 500.0, "source": "test"}
    }
    
    tj = 7.0
    load = 400.0 # CR = 400 / 1000 = 0.4
    hours = 10.0
    
    bin_row_ks = ks_calc._ks_hspf_bin(tj, load, hours, ks_input)
    
    # 2. Equivalent ISO common inputs
    measured_inputs = {
        "7_full": {"capacity": 3000.0, "power": 800.0, "temp": 7.0},
        "7_half": {"capacity": 2000.0, "power": 500.0, "temp": 7.0},
        "7_min": {"capacity": 1000.0, "power": 200.0, "temp": 7.0},
        "-7_full": {"capacity": 3000.0, "power": 800.0, "temp": -7.0},
        "2_full": {"capacity": 3000.0, "power": 800.0, "temp": 2.0},
    }
    
    bin_row_iso = iso_calc._variable_heating_bin(tj, load, hours, measured_inputs)
    
    # 3. Compare
    print(f"\nTJ: {tj}, Load: {load}, Cd: {cd_val}")
    print(f"KS Bin: {bin_row_ks}")
    print(f"ISO Bin: {bin_row_iso}")
    
    assert bin_row_ks["operating_case"] == "cyclic_minimum"
    assert bin_row_iso["operating_case"] == "cyclic_min"
    
    # Manual verification:
    # CR = 400 / 1000 = 0.4
    # PLF = 1.0 - 0.35 * (1.0 - 0.4) = 1.0 - 0.35 * 0.6 = 1.0 - 0.21 = 0.79
    # Power = (200 * 0.4) / 0.79 = 80 / 0.79 = 101.2658227848
    # Energy = 101.2658227848 * 10 = 1012.658227848
    
    assert bin_row_ks["heat_pump_energy"] == pytest.approx(1012.658227848)
    assert bin_row_ks["heat_pump_energy"] == pytest.approx(bin_row_iso["heat_pump_energy"])
    assert bin_row_ks["compressor_energy"] == pytest.approx(bin_row_iso["compressor_energy"])
    assert bin_row_ks["capacity_load_ratio"] == pytest.approx(0.4)
    assert bin_row_ks["part_load_factor"] == pytest.approx(0.79)
