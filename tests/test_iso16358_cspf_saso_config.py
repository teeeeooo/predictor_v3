import json
from pathlib import Path

import pytest

from core.calculator_iso16358 import ISO16358Calculator


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
    """Current engine cannot run SASO iso_boundary_eer without 29 C points."""
    fixture = load_fixture()
    calculator = ISO16358Calculator(str(CONFIG_PATH))

    with pytest.raises(ValueError, match="ISO boundary EER requires 35_full and 29_full"):
        calculator.calculate_cspf(fixture["measured_points"])


@pytest.mark.xfail(
    strict=True,
    reason=(
        "SASO source fixture expects CSPF 4.95, but current iso_boundary_eer "
        "implementation requires 29 C full/half points for half-full branches. "
        "SASO config intentionally has no derived 29 C points."
    ),
)
def test_saso_source_golden_cspf_4_95_pending_formula_review():
    fixture, result = calculate_saso_cspf()

    assert abs(result["cspf"] - fixture["expected"]["cspf"]) <= CSPF_TOLERANCE
