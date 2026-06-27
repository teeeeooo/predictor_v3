import pytest
from core.calculators.standards.asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator, REFERENCE_TYPE
import json
from pathlib import Path

def load_case3_packet_fixture():
    path = Path("tests/fixtures/asnzs_excel_hspf_compat/case3_packet.json")
    return json.loads(path.read_text())

def extract_component_details_from_packet_rows(packet: dict) -> list[dict]:
    rows = packet.get("component_rows")
    if rows is None:
        raise ValueError("Missing component_rows in packet.")
    
    details = []
    for row in rows:
        if row.get("status") not in ["source_verified", "implementation_check_required"]:
            continue
            
        # Basic mapping of verified diagnostic row to component detail format
        detail = {
            "name": row.get("anchor", f"tj_{row.get('tj')}"),
            "anchor": row.get("anchor"),
            "tj": row.get("tj"),
            "status": row.get("status")
        }
        
        # If we have energy_wh directly, we can use it
        if "energy_wh" in row:
            detail["energy_wh"] = row["energy_wh"]
        elif "observed_power_w" in row and "hours" in row:
            # We could calculate here, but current subset lacks hours
            detail["power_w"] = row["observed_power_w"]
            detail["hours"] = row["hours"]
            detail["energy_wh"] = detail["power_w"] * detail["hours"]
        elif "observed_power_w" in row:
            # Diagnostic only - keep the power
            detail["observed_power_w"] = row["observed_power_w"]
            
        details.append(detail)
    return details

def normalize_packet_to_partial_input(packet: dict) -> tuple[dict, dict]:
    if packet.get("reference_type") != REFERENCE_TYPE:
        raise ValueError(f"reference_type must be {REFERENCE_TYPE}.")
    
    if "full_dump" in packet:
        raise ValueError("full_dump is not supported.")
        
    outputs = packet["anchors"]["outputs"]
    
    # In H-5h-2, we manually added a reference component.
    # Now we can also use extracted rows if they have energy_wh.
    extracted_details = extract_component_details_from_packet_rows(packet)
    
    # For now, we still need the single reference component for partial implementation 
    # to satisfy energy_wh requirement in calculate_hspf
    component_details = [
        {"name": "ch48_reference_component", "energy_wh": outputs["CH48"]["value"], "anchor": "CH48"}
    ]
    
    # We can append extracted ones only if they have energy_wh
    for d in extracted_details:
        if "energy_wh" in d:
            component_details.append(d)
    
    measured_inputs = {
        "reference_type": REFERENCE_TYPE,
        "component_details": component_details,
        "hstl_wh": outputs["H12"]["value"] * 1000.0,
        "hspf": outputs["H13"]["value"]
    }
    
    options = {
        "matched_reference": {
            "case_id": packet["case_id"],
            "source": packet["source"]["kind"],
            "packet_id": packet["source"]["packet_id"]
        }
    }
    
    return measured_inputs, options

def test_packet_mapper_requires_asnzs_reference_type():
    packet = load_case3_packet_fixture()
    packet["reference_type"] = "INVALID"
    with pytest.raises(ValueError, match="reference_type must be"):
        normalize_packet_to_partial_input(packet)

def test_packet_mapper_extracts_source_metadata():
    packet = load_case3_packet_fixture()
    _, options = normalize_packet_to_partial_input(packet)
    ref = options["matched_reference"]
    assert ref["case_id"] == "case3"
    assert ref["source"] == "windows_excel_com"
    assert ref["packet_id"] == "case3"

def test_packet_mapper_extracts_source_verified_component_rows():
    packet = load_case3_packet_fixture()
    extracted = extract_component_details_from_packet_rows(packet)
    assert len(extracted) == 5
    for row in extracted:
        assert row["status"] == "source_verified"
        assert "anchor" in row

def test_packet_component_rows_are_not_sufficient_for_final_energy_reconstruction_yet():
    # current subset is source-verified diagnostic rows, not full reconstruction input.
    packet = load_case3_packet_fixture()
    extracted = extract_component_details_from_packet_rows(packet)
    # Check that none of the extracted rows have energy_wh because 'hours' is missing
    for row in extracted:
        assert "energy_wh" not in row

def test_packet_mapper_does_not_fabricate_missing_load_or_hours():
    packet = load_case3_packet_fixture()
    extracted = extract_component_details_from_packet_rows(packet)
    for row in extracted:
        assert "hours" not in row
        assert "load_w" not in row

@pytest.mark.xfail(
    reason=(
        "AS/NZS Excel compatibility external-reference prerequisite: "
        "component rows need full load/hour/energy_wh/helper fields for "
        "exact reconstruction; current packet subset is diagnostic-only "
        "and remains deferred to the Z-phase AS/NZS compatibility work."
    )
)
def test_packet_rows_to_component_details_xfail_until_load_hours_available():
    packet = load_case3_packet_fixture()
    extracted = extract_component_details_from_packet_rows(packet)
    
    # Try to build energy-sufficient details
    for row in extracted:
        if "energy_wh" not in row:
            raise ValueError("Insufficient data for energy reconstruction")

def test_packet_mapper_output_runs_through_partial_calculate_hspf():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    packet = load_case3_packet_fixture()
    inputs, options = normalize_packet_to_partial_input(packet)
    
    result = calc.calculate_hspf(inputs, options)
    assert result["reference_type"] == REFERENCE_TYPE
    assert result["matched_reference"]["case_id"] == "case3"

def test_packet_mapper_fixture_is_not_region_config():
    assert not Path("data/region_configs/asnzs_excel_hspf.json").exists()
