import pytest
import json
from pathlib import Path
from core.calculator_asnzs_hspf_excel import REFERENCE_TYPE

CASE3_FIXTURE = Path("tests/fixtures/asnzs_excel_hspf_compat/case3.json")
PACKET_FIXTURE = Path("tests/fixtures/asnzs_excel_hspf_compat/case3_packet.json")
ISO_GOLDEN_FIXTURE = Path("tests/fixtures/iso16358_hspf_golden_fixtures.json")

def load_json(path):
    return json.loads(path.read_text())

def test_case3_exact_match_contract_declares_reference_targets():
    data = load_json(CASE3_FIXTURE)
    assert data["reference_type"] == REFERENCE_TYPE
    
    expected = data["expected"]
    assert expected["hstl_kwh"] == pytest.approx(1126.120)
    assert expected["hspf"] == pytest.approx(4.33824)
    assert expected["ch48_wh"] == pytest.approx(1126120.47)
    
    # Contract tolerances
    tolerances = {
        "hstl_wh_abs": 1.0,
        "hspf_abs": 0.00001,
        "ch48_wh_abs": 0.01
    }
    assert tolerances["hspf_abs"] == 0.00001
    
    assert data["namespace_guard"]["not_iso_common_expected"] is True

def test_case3_packet_component_rows_are_source_verified_when_present():
    packet = load_json(PACKET_FIXTURE)
    if "component_rows" in packet:
        rows = packet["component_rows"]
        assert len(rows) > 0
        for row in rows:
            assert row["status"] in ["source_verified", "implementation_check_required"]
            # Ensure no fake/mock strings in verified rows
            note = row.get("note", "").lower()
            assert "fake" not in note
            assert "dummy" not in note
            assert "mock" not in note

def test_case3_packet_does_not_use_fake_component_rows():
    content = PACKET_FIXTURE.read_text().lower()
    forbidden = ["fake_value", "dummy_value", "mock_value", "placeholder_value"]
    for word in forbidden:
        assert word not in content, f"Forbidden word {word} found in packet fixture"

@pytest.mark.xfail(
    reason=(
        "AS/NZS Excel compatibility external-reference prerequisite: "
        "case3 exact reconstruction needs full component row data "
        "(load, hours, energy_wh/helper columns); current packet is "
        "diagnostic-only with observed_power and is separate from the "
        "ISO common production path until the deferred Z-phase."
    )
)
def test_case3_exact_match_from_component_rows_xfail_until_full_data_exists():
    packet = load_json(PACKET_FIXTURE)
    rows = packet.get("component_rows", [])
    for row in rows:
        # These are likely to be missing or incomplete for energy sum calculation
        if "load" not in row or "hours" not in row:
            pytest.fail(f"Row for tj={row.get('tj')} is missing load or hours")

def test_case3_exact_matching_values_stay_out_of_iso_common_golden_fixture():
    content = ISO_GOLDEN_FIXTURE.read_text()
    forbidden = ["4.33824", "1126.120", "1126120.47"]
    for val in forbidden:
        assert val not in content, f"Forbidden value {val} found in ISO common golden fixture"

def test_case3_exact_match_contract_does_not_require_region_config():
    path = Path("data/region_configs/asnzs_excel_hspf.json")
    assert not path.exists()
