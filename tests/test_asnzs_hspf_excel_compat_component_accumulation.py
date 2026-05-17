import pytest
import inspect
from core.calculator_asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator
import core.calculator_iso16358 as iso

def test_component_accumulation_result_sums_hsec_from_components():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    details = [
        {"name": "a", "energy_wh": 100.0},
        {"name": "b", "energy_wh": 250.0},
        {"name": "c", "energy_wh": 50.0},
    ]
    result = calc._build_component_accumulation_result(
        hstl_wh=2000.0, component_details=details, hspf=5.0
    )
    assert result["hsec_wh"] == pytest.approx(400.0)
    assert result["hstl_wh"] == 2000.0
    assert result["hspf"] == 5.0

def test_component_accumulation_result_keeps_components_in_workbook_diagnostics():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    details = [{"name": "a", "energy_wh": 100.0}]
    result = calc._build_component_accumulation_result(
        hstl_wh=2000.0, component_details=details, hspf=5.0
    )
    assert "component_details" in result["workbook_diagnostics"]
    assert "a" == result["workbook_diagnostics"]["component_details"][0]["name"]
    # Top level should not have component_details
    assert "component_details" not in result

def test_component_accumulation_result_rejects_invalid_component_energy():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    with pytest.raises(KeyError):
        calc._build_component_accumulation_result(
            hstl_wh=2000.0, component_details=[{"name": "a"}], hspf=5.0
        )
    with pytest.raises(ValueError):
        calc._build_component_accumulation_result(
            hstl_wh=2000.0, component_details=[{"name": "a", "energy_wh": -10.0}], hspf=5.0
        )

def test_component_accumulation_result_copies_component_details():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    details = [{"name": "a", "energy_wh": 100.0}]
    result = calc._build_component_accumulation_result(
        hstl_wh=2000.0, component_details=details, hspf=5.0
    )
    details[0]["energy_wh"] = 999.0
    assert result["workbook_diagnostics"]["component_details"][0]["energy_wh"] == 100.0

def test_component_accumulation_result_does_not_claim_case3_exact_match():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    result = calc._build_component_accumulation_result(
        hstl_wh=100.0, component_details=[{"name": "a", "energy_wh": 100.0}], hspf=1.0, 
        matched_reference={"case_id": "micro"}
    )
    assert result["matched_reference"]["case_id"] == "micro"
    # Ensure no exact case3 match values
    assert result["hstl_wh"] != 1126.120

def test_component_accumulation_helper_stays_in_asnzs_module():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    assert hasattr(calc, "_build_component_accumulation_result")
    
    # Common path guard
    source = inspect.getsource(iso.ISO16358Calculator.calculate_hspf_iso16358_common)
    assert "_build_component_accumulation_result" not in source
