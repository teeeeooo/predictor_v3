import pytest
import json
from pathlib import Path

FIXTURE_PATH = Path("tests/fixtures/asnzs_excel_hspf_compat/case3_packet.json")

def load_packet_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text())

def test_case3_packet_fixture_identity():
    data = load_packet_fixture()
    assert data["reference_type"] == "ASNZS_EXCEL_COMPAT"
    assert data["calculator_id"] == "asnzs_excel_hspf"
    assert data["case_id"] == "case3"
    assert data["packet_kind"] == "excel_com_chat_packet_subset"

def test_case3_packet_fixture_namespace_guards():
    data = load_packet_fixture()
    g = data["namespace_guard"]
    assert g["not_iso_common_expected"] is True
    assert g["not_region_config"] is True
    assert g["not_ui_visible"] is True
    assert g["not_full_dump"] is True

def test_case3_packet_fixture_contains_required_source_metadata():
    data = load_packet_fixture()
    s = data["source"]
    assert s["kind"] == "windows_excel_com"
    assert "workbook_family" in s
    assert "workbook_version" in s
    assert "packet_id" in s
    # "not iso common" check
    # Printing debug to be sure what pytest sees
    print(f"\nDEBUG: '{s['note']}'")
    assert "not iso common" in s["note"].lower()

def test_case3_packet_fixture_contains_output_anchor_candidates():
    data = load_packet_fixture()
    a = data["anchors"]["outputs"]
    assert a["H12"]["value"] == pytest.approx(1126.120)
    assert a["H13"]["value"] == pytest.approx(4.33824)
    assert a["CH48"]["value"] == pytest.approx(1126120.47)
    assert a["H12"]["status"] in ["candidate", "implementation_check_required"]

def test_case3_packet_fixture_does_not_contain_full_dump():
    data = load_packet_fixture()
    assert "full_dump" not in data

def test_case3_packet_fixture_is_not_region_config():
    assert FIXTURE_PATH.exists()
    assert not Path("data/region_configs/asnzs_excel_hspf.json").exists()

def test_case3_packet_values_not_in_iso_common_golden_fixture():
    with open("tests/fixtures/iso16358_hspf_golden_fixtures.json", "r") as f:
        content = f.read()
    forbidden = ["4.33824", "1126.120", "1126120.47"]
    for val in forbidden:
        assert val not in content, f"Forbidden value {val} found in ISO common golden fixtures"
