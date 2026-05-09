import pytest
import json
from pathlib import Path

FIXTURE_PATH = Path("tests/fixtures/asnzs_excel_hspf_compat/case3.json")

def load_asnzs_case3_reference() -> dict:
    return json.loads(FIXTURE_PATH.read_text())

def test_asnzs_excel_compat_case3_fixture_identity():
    data = load_asnzs_case3_reference()
    assert data["reference_type"] == "ASNZS_EXCEL_COMPAT"
    assert data["calculator_id"] == "asnzs_excel_hspf"
    assert data["case_id"] == "case3"
    assert data["namespace_guard"]["not_iso_common_expected"] is True
    assert data["namespace_guard"]["not_region_config"] is True
    assert data["namespace_guard"]["not_ui_visible"] is True

def test_asnzs_excel_compat_case3_reference_values():
    data = load_asnzs_case3_reference()
    expected = data["expected"]
    assert expected["hstl_kwh"] == 1126.120
    assert expected["hspf"] == 4.33824
    assert expected["ch48_wh"] == 1126120.47
    assert data["source"]["kind"] == "windows_excel_com"

def test_asnzs_excel_compat_fixture_is_not_region_config():
    assert FIXTURE_PATH.exists()
    assert not Path("data/region_configs/asnzs_excel_hspf.json").exists()

def test_asnzs_excel_compat_values_not_in_iso_common_golden_fixture():
    with open("tests/fixtures/iso16358_hspf_golden_fixtures.json", "r") as f:
        content = f.read()
    forbidden = ["4.33824", "1126.120", "1126120.47"]
    for val in forbidden:
        assert val not in content, f"Forbidden value {val} found in golden fixtures"
