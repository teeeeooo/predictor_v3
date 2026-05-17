import pytest
import inspect
from core.calculator_asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator
import core.calculator_iso16358_legacy as iso

def test_build_component_detail_from_workbook_row():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    row = {
        "temperature_c": 2.0,
        "BA": 3600.0,
        "CA": 3.0,
        "hours": 2.0
    }
    result = calc._build_component_detail_from_workbook_row(
        row,
        component_anchor="CB",
        load_key="BA",
        helper_anchor="CA",
        hours_key="hours"
    )
    assert result["name"] == "CB"
    assert result["anchor"] == "CB"
    assert result["helper_anchor"] == "CA"
    assert result["power_w"] == 1200.0
    assert result["energy_wh"] == 2400.0

def test_component_row_mapping_rejects_missing_keys():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    row = {"BA": 3600.0, "CA": 3.0}
    with pytest.raises(KeyError):
        calc._build_component_detail_from_workbook_row(
            row, component_anchor="CB", load_key="BA", helper_anchor="CA", hours_key="hours"
        )

def test_component_row_mapping_rejects_invalid_values():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    # Negative load
    row = {"BA": -100.0, "CA": 3.0, "hours": 2.0}
    with pytest.raises(ValueError):
        calc._build_component_detail_from_workbook_row(
            row, component_anchor="CB", load_key="BA", helper_anchor="CA", hours_key="hours"
        )
    # Non-numeric
    row = {"BA": "abc", "CA": 3.0, "hours": 2.0}
    with pytest.raises(ValueError):
        calc._build_component_detail_from_workbook_row(
            row, component_anchor="CB", load_key="BA", helper_anchor="CA", hours_key="hours"
        )

def test_component_row_mapping_rejects_empty_component_anchor():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    row = {"BA": 3600.0, "CA": 3.0, "hours": 2.0}
    with pytest.raises(ValueError, match="cannot be empty"):
        calc._build_component_detail_from_workbook_row(
            row, component_anchor="", load_key="BA", helper_anchor="CA", hours_key="hours"
        )

def test_helper_column_reconstruction_stays_in_asnzs_module():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    assert hasattr(calc, "_build_component_detail_from_workbook_row")
    
    # Common path guard
    source = inspect.getsource(iso.ISO16358Calculator.calculate_hspf_iso16358_common)
    assert "_build_component_detail_from_workbook_row" not in source
