import pytest
from core.calculator_asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator, REFERENCE_TYPE, CALCULATOR_ID

def build_minimal_hybrid_input():
    return {
        "reference_type": "ASNZS_EXCEL_COMPAT",
        "canonical_performance_points": {
            "full": {"capacity": 3000.0, "power": 800.0},
            "half": {"capacity": 1500.0, "power": 400.0},
            "min": {"capacity": 750.0, "power": 200.0},
            "extended": {"capacity": 4000.0, "power": 1200.0}
        },
        "bin_hours": []
    }

def build_workbook_options():
    return {
        "helper_column_convention": "workbook_boundary_lookup",
        "rounding_mode": "excel_compat"
    }

def test_asnzs_excel_hspf_skeleton_identity():
    assert REFERENCE_TYPE == "ASNZS_EXCEL_COMPAT"
    assert CALCULATOR_ID == "asnzs_excel_hspf"

def test_asnzs_excel_hspf_not_implemented_message_names_boundary():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    with pytest.raises(NotImplementedError) as excinfo:
        calc.calculate_hspf(build_minimal_hybrid_input(), build_workbook_options())
    
    msg = str(excinfo.value)
    assert "ASNZS_EXCEL_COMPAT" in msg
    assert "not implemented" in msg.lower()
    # Ensure it's not the ISO common HSPF
    assert "not be used as" in msg
    assert "common hspf" in msg.lower()

def test_asnzs_excel_hspf_production_region_config_not_created():
    from pathlib import Path
    path = Path("data/region_configs/asnzs_excel_hspf.json")
    assert not path.exists()

def test_asnzs_skeleton_does_not_import_iso_common_calculator():
    import core.calculator_asnzs_hspf_excel as mod
    import sys
    assert "core.calculator_iso16358" not in sys.modules or \
           "ISO16358Calculator" not in vars(mod)
