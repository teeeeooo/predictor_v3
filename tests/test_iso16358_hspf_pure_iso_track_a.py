import pytest
import json
import pathlib
from core.calculators.standards.iso16358 import ISO16358Calculator

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
    path = "tests/fixtures/iso16358_hspf_pure_iso_track_a/branch_fixtures.json"
    content = pathlib.Path(path).read_text(encoding="utf-8")
    forbidden = ["4.33824", "1126.120", "1126120.47", "CH48", "H12", "H13", "ASNZS_EXCEL_COMPAT"]
    for val in forbidden:
        assert val not in content, f"Forbidden value {val} found in Pure ISO fixture"

def test_pure_iso_track_a_fixture_contains_cases():
    fixture = load_pure_iso_track_a_fixture()
    assert len(fixture["cases"]) > 0

def test_pure_iso_track_a_cycling_cd_one_bin_route_level(tmp_path):
    config_path = tmp_path / "iso16358_pure_iso_config.json"
    config = {
        "mode": "heating",
        "hspf": {
            "enabled": True,
            "profile": "iso16358_2_hspf",
            "correction": {"cd": 0.35, "aux_cop": 1.0},
            "load_line": {
                "source": "rated_heating_capacity",
                "zero_load_temp": 17.0,
                "full_load_temp": 0.0,
                "rated_capacity_factor": 1.0,
            },
            "bin_hours_key": "hspf_bin_hours",
        },
        "hspf_bin_hours": [{"tj": 7.0, "nj": 1.0}]
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    calculator = ISO16358Calculator(str(config_path))
    
    fixture = load_pure_iso_track_a_fixture()
    case = fixture["cases"]["cycling_cd_one_bin"]
    measured = {
        "rated_heating_capacity": 680.0,
        "7_full": case["measured_point_pool"]["7_full"],
        "7_half": case["measured_point_pool"]["7_half"],
        "7_min": case["measured_point_pool"]["7_min"],
    }
    result = calculator.calculate_hspf(measured)
    assert result["hstl_wh"] == pytest.approx(case["expected"]["hstl_wh"])
    assert result["hsec_wh"] == pytest.approx(case["expected"]["hsec_wh"], abs=1e-6)
    assert result["hspf"] == pytest.approx(case["expected"]["hspf"], abs=0.01)

def test_pure_iso_track_a_min_to_half_formula_44_48_route_level(tmp_path):
    config_path = tmp_path / "iso16358_pure_iso_config.json"
    config = {
        "mode": "heating",
        "hspf": {
            "enabled": True,
            "profile": "iso16358_2_hspf",
            "correction": {"cd": 0.0, "aux_cop": 1.0},
            "load_line": {
                "source": "rated_heating_capacity",
                "zero_load_temp": 17.0,
                "full_load_temp": 0.0,
                "rated_capacity_factor": 1.0,
            },
            "bin_hours_key": "hspf_bin_hours",
        },
        "hspf_bin_hours": [{"tj": 7.0, "nj": 1.0}]
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    calculator = ISO16358Calculator(str(config_path))
    
    fixture = load_pure_iso_track_a_fixture()
    case = fixture["cases"]["min_to_half_formula_44_48_one_bin"]
    measured = {
        "rated_heating_capacity": 2550.0,
        "7_full": case["measured_point_pool"]["7_full"],
        "7_half": case["measured_point_pool"]["7_half"],
        "7_min": case["measured_point_pool"]["7_min"],
    }
    result = calculator.calculate_hspf(measured)
    assert result["hstl_wh"] == pytest.approx(case["expected"]["hstl_wh"])
    assert result["hsec_wh"] == pytest.approx(case["expected"]["hsec_wh"], abs=1e-6)
    assert result["hspf"] == pytest.approx(case["expected"]["hspf"], abs=0.01)

def test_pure_iso_track_a_saturated_auxiliary_one_bin_route_level(tmp_path):
    config_path = tmp_path / "iso16358_pure_iso_config.json"
    config = {
        "mode": "heating",
        "hspf": {
            "enabled": True,
            "profile": "iso16358_2_hspf",
            "correction": {"cd": 0.0, "aux_cop": 1.0},
            "load_line": {
                "source": "rated_heating_capacity",
                "zero_load_temp": 17.0,
                "full_load_temp": 0.0,
                "rated_capacity_factor": 1.0,
            },
            "bin_hours_key": "hspf_bin_hours",
        },
        "hspf_bin_hours": [{"tj": 7.0, "nj": 1.0}]
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    calculator = ISO16358Calculator(str(config_path))
    
    fixture = load_pure_iso_track_a_fixture()
    case = fixture["cases"]["saturated_auxiliary_one_bin"]
    
    # Load = 3500W at 7C.
    # Ref_Cap: Load = 3500W at 7C. Ref_Cap = 3500 * 17 / 10 = 5950 W
    measured = {
        "rated_heating_capacity": 5950.0,
        "7_full": case["measured_point_pool"]["7_full"],
        "7_half": {"capacity": 1000.0, "power": 250.0},
    }

    result = calculator.calculate_hspf(measured)    
    assert result["hstl_wh"] == pytest.approx(case["expected"]["hstl_wh"])
    assert result["hsec_wh"] == pytest.approx(case["expected"]["hsec_wh"], abs=1e-6)
    assert result["hspf"] == pytest.approx(case["expected"]["hspf"], abs=0.01)
    
    detail = result["bin_details"][0]
    assert detail["case"] == "saturated"
    assert detail["auxiliary_energy"] > 0.0
