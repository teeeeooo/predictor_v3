import pytest
from core.calculator_asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator, REFERENCE_TYPE
import json
from pathlib import Path

def load_case3_packet_fixture():
    path = Path("tests/fixtures/asnzs_excel_hspf_compat/case3_packet.json")
    return json.loads(path.read_text())

def normalize_packet_to_partial_input(packet: dict) -> tuple[dict, dict]:
    if packet.get("reference_type") != REFERENCE_TYPE:
        raise ValueError(f"reference_type must be {REFERENCE_TYPE}.")
    
    if "full_dump" in packet:
        raise ValueError("full_dump is not supported.")
        
    outputs = packet["anchors"]["outputs"]
    
    measured_inputs = {
        "reference_type": REFERENCE_TYPE,
        "component_details": [
            {"name": "ch48_reference_component", "energy_wh": outputs["CH48"]["value"], "anchor": "CH48"}
        ],
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

def test_packet_mapper_normalizes_required_partial_input_fields():
    packet = load_case3_packet_fixture()
    inputs, _ = normalize_packet_to_partial_input(packet)
    assert inputs["reference_type"] == REFERENCE_TYPE
    assert inputs["hstl_wh"] == pytest.approx(1126120.0)
    assert inputs["hspf"] == pytest.approx(4.33824)
    assert inputs["component_details"][0]["energy_wh"] == pytest.approx(1126120.47)
    assert inputs["component_details"][0]["anchor"] == "CH48"

def test_packet_mapper_output_runs_through_partial_calculate_hspf():
    calc = ASNZSExcelHSPFCompatibilityCalculator()
    packet = load_case3_packet_fixture()
    inputs, options = normalize_packet_to_partial_input(packet)
    
    result = calc.calculate_hspf(inputs, options)
    assert result["reference_type"] == REFERENCE_TYPE
    assert result["matched_reference"]["case_id"] == "case3"
    assert "component_details" in result["workbook_diagnostics"]

def test_packet_mapper_does_not_require_full_dump():
    packet = load_case3_packet_fixture()
    # Ensure no full_dump exists and mapping works
    assert "full_dump" not in packet
    normalize_packet_to_partial_input(packet)

def test_packet_mapper_fixture_is_not_region_config():
    assert not Path("data/region_configs/asnzs_excel_hspf.json").exists()
