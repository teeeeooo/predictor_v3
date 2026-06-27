import pytest
from core.calculators.standards.asnzs_hspf_excel import WORKBOOK_HELPER_COLUMNS, get_workbook_helper_column_map
import core.calculators.standards.iso16358 as iso
import inspect

def test_workbook_helper_column_map_contains_expected_anchors():
    keys = ["BN", "BP", "BY", "CA", "CC"]
    for k in keys:
        assert k in WORKBOOK_HELPER_COLUMNS
        entry = WORKBOOK_HELPER_COLUMNS[k]
        assert "semantic_name" in entry
        assert "status" in entry
        assert "description" in entry
        assert "compatibility" in entry["description"].lower() or "workbook" in entry["description"].lower()

def test_workbook_helper_column_map_marks_uncertain_columns_for_implementation_check():
    # BN, BP, BY are marked as implementation_check_required
    uncertain = ["BN", "BP", "BY"]
    for k in uncertain:
        assert WORKBOOK_HELPER_COLUMNS[k]["status"] == "implementation_check_required"

def test_workbook_helper_column_map_is_compatibility_only():
    from core.calculators.standards.asnzs_hspf_excel import REFERENCE_TYPE
    assert REFERENCE_TYPE == "ASNZS_EXCEL_COMPAT"
    # Ensure no reference to common ISO logic
    for k, v in WORKBOOK_HELPER_COLUMNS.items():
        assert "ISO" not in v["description"]

def test_workbook_helper_column_names_do_not_enter_iso_common_path():
    # Ensure common path function doesn't mention the map
    source = inspect.getsource(iso.ISO16358Calculator.calculate_hspf_iso16358_common)
    assert "WORKBOOK_HELPER_COLUMNS" not in source

def test_get_workbook_helper_column_map_returns_copy():
    map1 = get_workbook_helper_column_map()
    map1["BN"]["status"] = "mutated"
    assert WORKBOOK_HELPER_COLUMNS["BN"]["status"] == "implementation_check_required"
