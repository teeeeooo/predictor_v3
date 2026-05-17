import json
from pathlib import Path

from core.calculator_iso16358_legacy import ISO16358Calculator


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/region_configs/iso_t1_default_2point.json"
FIXTURE_PATH = ROOT / "tests/fixtures/iso16358_cspf_golden_fixtures.json"
FIXTURE_ID = "southeast_asia_iso_basic_cspf_4_665"
CSPF_TOLERANCE = 0.001


def load_fixture():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data["fixtures"][FIXTURE_ID]


def test_iso_t1_default_2point_production_config_cspf_4_665():
    """1-sample control regression, not certification-grade validation.

    Uses production iso_t1_default_2point.json config.
    """
    fixture = load_fixture()
    calculator = ISO16358Calculator(str(CONFIG_PATH))

    result = calculator.calculate_cspf(fixture["measured_points"])

    print(
        {
            "cspf": result["cspf"],
            "annual_cooling_kwh": result["annual_cooling_kwh"],
            "annual_power_kwh": result["annual_power_kwh"],
        }
    )
    assert abs(result["cspf"] - fixture["expected"]["cspf"]) <= CSPF_TOLERANCE
