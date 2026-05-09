import pytest
import inspect
from core.calculator_asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator, REFERENCE_TYPE
import core.calculator_iso16358 as iso

def build_minimal_hybrid_input():
    return {
        "reference_type": REFERENCE_TYPE,
        "component_details": [
            {"name": "a", "energy_wh": 100.0},
            {"name": "b", "energy_wh": 250.0}
        ],
        "hstl_wh": 2000.0,
        "hspf": 5.0
    }

def test_calculate_hspf_partial_component_details_returns_compatibility_envelope():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    result = calc.calculate_hspf(build_minimal_hybrid_input(), {"matched_reference": {"case_id": "micro"}})
    
    assert result["hsec_wh"] == pytest.approx(350.0)
    assert result["hstl_wh"] == 2000.0
    assert result["hspf"] == 5.0
    assert result["reference_type"] == REFERENCE_TYPE
    assert result["matched_reference"]["case_id"] == "micro"

def test_calculate_hspf_partial_requires_asnzs_reference_type():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    data = build_minimal_hybrid_input()
    data["reference_type"] = "ISO_COMMON"
    with pytest.raises(ValueError, match="reference_type must be"):
        calc.calculate_hspf(data)

def test_calculate_hspf_partial_requires_component_details_hstl_and_hspf():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    for field in ["component_details", "hstl_wh", "hspf"]:
        data = build_minimal_hybrid_input()
        del data[field]
        with pytest.raises(ValueError, match="Missing required field"):
            calc.calculate_hspf(data)

def test_calculate_hspf_partial_keeps_workbook_diagnostics_namespaced():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    result = calc.calculate_hspf(build_minimal_hybrid_input())
    
    assert "workbook_diagnostics" in result
    assert "component_details" in result["workbook_diagnostics"]
    assert "component_details" not in result
    forbidden = ["BN", "BP", "BY", "CA", "CC", "CG", "CH", "CH48"]
    for word in forbidden:
        assert word not in result

def test_calculate_hspf_partial_does_not_claim_case3_exact_match():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    result = calc.calculate_hspf(build_minimal_hybrid_input(), {"matched_reference": {"case_id": "micro"}})
    assert result["matched_reference"]["case_id"] == "micro"
    assert result["hstl_wh"] != 1126.120

def test_calculate_hspf_partial_rejects_invalid_component_energy():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    data = build_minimal_hybrid_input()
    data["component_details"] = [{"name": "a", "energy_wh": -1.0}]
    with pytest.raises(ValueError):
        calc.calculate_hspf(data)

def test_calculate_hspf_partial_common_path_not_modified():
    # Verify common path does not mention the *implementation* method
    source = inspect.getsource(iso.ISO16358Calculator.calculate_hspf_iso16358_common)
    assert "_build_compatibility_result_envelope" not in source
