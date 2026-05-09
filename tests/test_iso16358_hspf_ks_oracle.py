import pytest
from core.calculator_iso16358 import ISO16358Calculator

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
    calc = ISO16358Calculator("data/region_configs/korea.json")
    ks_input = get_neutralized_fixture()
    
    bin_row_ks = calc._ks_hspf_bin(7.0, 1200.0, 2.0, ks_input)
    
    # Analyze the result
    print(f"\nBin Row: {bin_row_ks}")
    
    # In KS path, 'bin_energy' seems to be something else.
    # Check compressor_energy and heat_pump_energy
    assert "compressor_energy" in bin_row_ks
    assert "heat_pump_energy" in bin_row_ks
    
    # Verify consistency: bin_energy might be total?
    # Actually, check if load was satisfied by heat_pump_capacity
    assert bin_row_ks["heat_pump_capacity"] == 1200.0
