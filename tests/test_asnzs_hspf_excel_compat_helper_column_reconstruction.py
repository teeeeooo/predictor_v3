import pytest
import inspect
from core.calculators.standards.asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator
import core.calculators.standards.iso16358 as iso

def test_reconstruct_helper_cops_from_row():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    row = {
        "temperature_c": 2.0,
        "BN": 2.1, "BP": 2.3, "BY": 2.5, "CA": 2.7, "CC": 2.9
    }
    result = calc._reconstruct_helper_cops_from_row(row)
    assert result["temperature_c"] == 2.0
    assert result["helper_cops"]["BN"] == 2.1
    assert result["helper_cops"]["CC"] == 2.9

def test_reconstruct_helper_cops_rejects_missing_column():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    row = {"temperature_c": 2.0, "BN": 2.1} # Missing others
    with pytest.raises(KeyError):
        calc._reconstruct_helper_cops_from_row(row)

def test_reconstruct_helper_cops_rejects_non_positive_cop():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    row = {"temperature_c": 2.0, "BN": 0.0, "BP": 2.3, "BY": 2.5, "CA": 2.7, "CC": 2.9}
    with pytest.raises(ValueError):
        calc._reconstruct_helper_cops_from_row(row)

def test_reconstruct_helper_cops_rejects_non_numeric_value():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    row = {"temperature_c": 2.0, "BN": "abc", "BP": 2.3, "BY": 2.5, "CA": 2.7, "CC": 2.9}
    with pytest.raises(ValueError):
        calc._reconstruct_helper_cops_from_row(row)

def test_select_helper_cop():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    cops = {"BN": 2.1, "CA": 2.7}
    assert calc._select_helper_cop(cops, "CA") == 2.7

def test_select_helper_cop_rejects_missing_or_invalid_anchor():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    cops = {"BN": 2.1}
    with pytest.raises(KeyError):
        calc._select_helper_cop(cops, "CA")
    cops["CA"] = 0.0
    with pytest.raises(ValueError):
        calc._select_helper_cop(cops, "CA")

def test_helper_column_reconstruction_stays_in_asnzs_module():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    assert hasattr(calc, "_reconstruct_helper_cops_from_row")
    
    # Common path guard
    source = inspect.getsource(iso.ISO16358Calculator.calculate_hspf_iso16358_common)
    assert "_reconstruct_helper_cops_from_row" not in source
