import json
from pathlib import Path

from core.calculator_iso16358_legacy import ISO16358Calculator


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/region_configs/saso.json"
FIXTURE_PATH = ROOT / "tests/fixtures/iso16358_cspf_golden_fixtures.json"
FIXTURE_ID = "saso_cspf_4_95"
CSPF_TOLERANCE = 0.01


def load_fixture():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data["fixtures"][FIXTURE_ID]


def calculate_saso_cspf():
    fixture = load_fixture()
    calculator = ISO16358Calculator(str(CONFIG_PATH))

    return fixture, calculator.calculate_cspf(fixture["measured_points"])


def test_saso_production_config_current_engine_requires_29c_boundary_points():
    """SASO config uses T3 with_optional_test and ISO boundary EER."""
    fixture = load_fixture()
    calculator = ISO16358Calculator(str(CONFIG_PATH))
    
    assert "cspf_test_profile" in calculator.config
    assert calculator.config["cspf_test_profile"]["climate_profile"] == "T3"
    assert calculator.config["cspf_test_profile"]["test_selection"] == "with_optional_test"
    assert calculator.t_100_load == 46.0
    assert calculator.reference_point == "46_full"
    assert calculator.power_interpolation_method == "iso_boundary_eer"

    result = calculator.calculate_cspf(fixture["measured_points"])
    
    assert result["cspf"] > 0
    assert result["annual_cooling_kwh"] > 0
    assert result["annual_power_kwh"] > 0


def test_saso_source_golden_cspf_4_95():
    fixture, result = calculate_saso_cspf()

    assert abs(result["cspf"] - fixture["expected"]["cspf"]) <= CSPF_TOLERANCE
