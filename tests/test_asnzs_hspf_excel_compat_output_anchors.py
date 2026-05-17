import pytest
import inspect
from core.calculator_asnzs_hspf_excel import WORKBOOK_OUTPUT_ANCHORS, get_workbook_output_anchor_map
import core.calculator_iso16358_legacy as iso

def test_workbook_helper_column_map_contains_expected_anchors():
    keys = ["CG", "CH", "CH48"]
    for k in keys:
        assert k in WORKBOOK_OUTPUT_ANCHORS
        entry = WORKBOOK_OUTPUT_ANCHORS[k]
        assert "semantic_name" in entry
        assert "status" in entry
        assert "description" in entry
        assert "compatibility" in entry["description"].lower() or "workbook" in entry["description"].lower()

def test_workbook_helper_column_map_marks_uncertain_anchors_for_implementation_check():
    uncertain = ["CG", "CH"]
    for k in uncertain:
        assert WORKBOOK_OUTPUT_ANCHORS[k]["status"] == "implementation_check_required"

def test_ch48_anchor_is_compatibility_reference_only():
    assert "CH48" in WORKBOOK_OUTPUT_ANCHORS
    desc = WORKBOOK_OUTPUT_ANCHORS["CH48"]["description"].lower()
    assert "reference" in desc
    assert "not iso common expected" in desc

def test_workbook_output_anchor_names_do_not_enter_iso_common_path():
    source = inspect.getsource(iso.ISO16358Calculator.calculate_hspf_iso16358_common)
    assert "WORKBOOK_OUTPUT_ANCHORS" not in source

def test_get_workbook_output_anchor_map_returns_copy():
    map1 = get_workbook_output_anchor_map()
    map1["CG"]["status"] = "mutated"
    assert WORKBOOK_OUTPUT_ANCHORS["CG"]["status"] == "implementation_check_required"
