import pytest
import inspect
import json
from core.calculator_iso16358 import ISO16358Calculator

def get_base_input():
    return {
        "7_full": {"capacity": 3000.0, "power": 800.0},
        "7_half": {"capacity": 1500.0, "power": 400.0}
    }

def test_iso_common_hspf_ignores_asnzs_reference_metadata():
    # Use hong_kong.json as it has a generic hspf profile
    calc = ISO16358Calculator("data/region_configs/hong_kong.json")
    base_input = get_base_input()
    
    # Calculate baseline (must pass rated_heating_capacity)
    result_base = calc.calculate_hspf_iso16358_common(base_input, 3000.0)
    
    # Calculate with metadata contamination
    contaminated_input = base_input.copy()
    contaminated_input.update({
        "reference_type": "ASNZS_EXCEL_COMPAT",
        "standard": "ASNZS",
        "region": "au_nz",
        "profile_id": "asnzs_excel_hspf_compat",
        "calculator_id": "asnzs_excel_hspf"
    })
    
    result_contaminated = calc.calculate_hspf_iso16358_common(contaminated_input, 3000.0)
    
    assert result_base["hstl_wh"] == result_contaminated["hstl_wh"]
    assert result_base["hsec_wh"] == result_contaminated["hsec_wh"]
    assert result_base["hspf"] == result_contaminated["hspf"]

def test_iso_common_hspf_does_not_embed_excel_helper_convention():
    source = inspect.getsource(ISO16358Calculator.calculate_hspf_iso16358_common)
    forbidden = ["BN", "BP", "BY", "CA", "CC", "COP_helper", "BA /", "CH48"]
    for word in forbidden:
        assert word not in source, f"Forbidden keyword '{word}' found in common path source code."

def test_asnzs_excel_reference_values_stay_out_of_iso_common_golden_namespace():
    files_to_check = [
        "tests/fixtures/iso16358_hspf_golden_fixtures.json",
        "tests/test_iso16358_hspf_validation.py"
    ]
    forbidden_values = ["1126120.47"]
    
    for file_path in files_to_check:
        with open(file_path, 'r') as f:
            content = f.read()
            for val in forbidden_values:
                assert val not in content, f"Forbidden value {val} found in {file_path}"
