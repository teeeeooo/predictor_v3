import pytest
import copy
from core.calculator_asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator, REFERENCE_TYPE, CALCULATOR_ID
import core.calculator_iso16358 as iso
import inspect

def test_result_envelope_contains_compatibility_identity():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    envelope = calc._build_compatibility_result_envelope(
        hstl_wh=1000.0, hsec_wh=250.0, hspf=4.0
    )
    assert envelope["reference_type"] == REFERENCE_TYPE
    assert envelope["calculator_id"] == CALCULATOR_ID
    assert envelope["hstl_wh"] == 1000.0
    assert envelope["hspf"] == 4.0

def test_result_envelope_keeps_workbook_diagnostics_separate():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    diagnostics = {"BN": {"energy_wh": 10.0}}
    envelope = calc._build_compatibility_result_envelope(
        hstl_wh=1000.0, hsec_wh=250.0, hspf=4.0, workbook_diagnostics=diagnostics
    )
    assert "workbook_diagnostics" in envelope
    assert "BN" in envelope["workbook_diagnostics"]
    # Ensure no top-level BN
    assert "BN" not in envelope

def test_result_envelope_keeps_reference_metadata_separate():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    meta = {"case_id": "case3"}
    envelope = calc._build_compatibility_result_envelope(
        hstl_wh=1000.0, hsec_wh=250.0, hspf=4.0, matched_reference=meta
    )
    assert "matched_reference" in envelope
    assert envelope["matched_reference"]["case_id"] == "case3"
    assert "case_id" not in envelope

def test_result_envelope_rejects_invalid_energy_values():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    with pytest.raises(ValueError):
        calc._build_compatibility_result_envelope(hstl_wh=-1.0, hsec_wh=10.0, hspf=1.0)
    with pytest.raises(ValueError):
        calc._build_compatibility_result_envelope(hstl_wh=10.0, hsec_wh=0.0, hspf=1.0)
    with pytest.raises(ValueError):
        calc._build_compatibility_result_envelope(hstl_wh=10.0, hsec_wh=10.0, hspf=-1.0)

def test_result_envelope_copies_nested_inputs():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    diag = {"a": 1}
    envelope = calc._build_compatibility_result_envelope(
        hstl_wh=1000.0, hsec_wh=250.0, hspf=4.0, workbook_diagnostics=diag
    )
    diag["a"] = 99
    assert envelope["workbook_diagnostics"]["a"] == 1

def test_result_envelope_helper_stays_in_asnzs_module():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    assert hasattr(calc, "_build_compatibility_result_envelope")
    
    # Common path guard
    source = inspect.getsource(iso.ISO16358Calculator.calculate_hspf_iso16358_common)
    assert "_build_compatibility_result_envelope" not in source
