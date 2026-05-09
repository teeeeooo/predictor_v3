import pytest
import json
import pathlib

def load_pure_iso_track_a_fixture():
    path = "tests/fixtures/iso16358_hspf_pure_iso_track_a/branch_fixtures.json"
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))

def test_pure_iso_track_a_fixture_identity():
    fixture = load_pure_iso_track_a_fixture()
    assert fixture["metadata"]["reference_type"] == "ISO16358_COMMON_TRACK_A"

def test_pure_iso_track_a_fixture_is_not_external_workbook_reference():
    fixture = load_pure_iso_track_a_fixture()
    assert fixture["metadata"]["not_external_workbook_reference"] is True
    assert fixture["metadata"]["not_asnzs_energy_rating_workbook"] is True

def test_pure_iso_track_a_fixture_has_no_asnzs_workbook_anchor_values():
    # Verify the fixture content does not contain forbidden strings
    path = "tests/fixtures/iso16358_hspf_pure_iso_track_a/branch_fixtures.json"
    content = pathlib.Path(path).read_text(encoding="utf-8")
    forbidden = ["4.33824", "1126.120", "1126120.47", "CH48", "H12", "H13", "ASNZS_EXCEL_COMPAT"]
    for val in forbidden:
        assert val not in content, f"Forbidden value {val} found in Pure ISO fixture"

def test_pure_iso_track_a_fixture_starts_without_workbook_derived_cases():
    fixture = load_pure_iso_track_a_fixture()
    assert fixture["cases"] == {}

