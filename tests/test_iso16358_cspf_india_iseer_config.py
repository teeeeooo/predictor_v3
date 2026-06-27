import json
from pathlib import Path

from core.calculators.standards.iso16358 import ISO16358Calculator


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/region_configs/india_iseer.json"
FIXTURE_PATH = ROOT / "tests/fixtures/iso16358_cspf_golden_fixtures.json"
FIXTURE_ID = "india_iseer_5_00"
XLSX_COMPATIBLE_ISEER = 4.993
XLSX_COMPATIBLE_CSTL_KWH = 3950.96
XLSX_COMPATIBLE_CSEC_KWH = 791.36
CURRENT_ENGINE_TOLERANCE = 0.001
GOLDEN_ISEER_TOLERANCE = 0.01
ENERGY_TOLERANCE_KWH = 0.001
SOURCE_DISPLAY_ENERGY_TOLERANCE_KWH = 1.0


def load_fixture():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data["fixtures"][FIXTURE_ID]


def calculate_india_iseer():
    fixture = load_fixture()
    calculator = ISO16358Calculator(str(CONFIG_PATH))

    return fixture, calculator.calculate_cspf(fixture["measured_points"])


def test_india_iseer_production_config_xlsx_compatible_regression():
    """India official xlsx rounds ISO boundary temperatures with ROUND(..., 0)."""
    fixture, result = calculate_india_iseer()

    print(
        {
            "source_expected_iseer": fixture["expected"]["iseer"],
            "xlsx_compatible_iseer": result["cspf"],
            "source_expected_cstl_kwh": fixture["expected"]["cstl_kwh"],
            "xlsx_compatible_cstl_kwh": result["annual_cooling_kwh"],
            "source_expected_csec_kwh": fixture["expected"]["csec_kwh"],
            "xlsx_compatible_csec_kwh": result["annual_power_kwh"],
        }
    )

    assert abs(result["cspf"] - XLSX_COMPATIBLE_ISEER) <= CURRENT_ENGINE_TOLERANCE
    assert (
        abs(result["annual_cooling_kwh"] - XLSX_COMPATIBLE_CSTL_KWH)
        <= ENERGY_TOLERANCE_KWH
    )
    assert (
        abs(result["annual_power_kwh"] - XLSX_COMPATIBLE_CSEC_KWH)
        <= ENERGY_TOLERANCE_KWH
    )


def test_india_iseer_source_display_values_are_preserved_as_reference():
    fixture, result = calculate_india_iseer()
    expected = fixture["expected"]

    assert abs(result["cspf"] - expected["iseer"]) <= GOLDEN_ISEER_TOLERANCE
    assert (
        abs(result["annual_cooling_kwh"] - expected["cstl_kwh"])
        <= SOURCE_DISPLAY_ENERGY_TOLERANCE_KWH
    )
    assert (
        abs(result["annual_power_kwh"] - expected["csec_kwh"])
        <= SOURCE_DISPLAY_ENERGY_TOLERANCE_KWH
    )
