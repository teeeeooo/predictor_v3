import pytest
from pathlib import Path
from core.calculator_asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator, REFERENCE_TYPE, CALCULATOR_ID

def test_asnzs_excel_hspf_skeleton_identity():
    assert REFERENCE_TYPE == "ASNZS_EXCEL_COMPAT"
    assert CALCULATOR_ID == "asnzs_excel_hspf"

def test_asnzs_excel_hspf_production_region_config_not_created():
    path = Path("data/region_configs/asnzs_excel_hspf.json")
    assert not path.exists()

def test_asnzs_skeleton_does_not_import_iso_common_calculator():
    import core.calculator_asnzs_hspf_excel as mod
    import sys
    assert "core.calculator_iso16358" not in sys.modules or \
           "ISO16358Calculator" not in vars(mod)
