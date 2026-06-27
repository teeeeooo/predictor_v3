import json
from pathlib import Path

from core.calculators.standards.iso16358 import ISO16358Calculator


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/region_configs/hong_kong.json"
FIXTURE_PATH = ROOT / "tests/fixtures/iso16358_cspf_golden_fixtures.json"
FIXTURE_ID = "hong_kong_cspf_4_83"
RATED_LOAD_ANCHOR_CAPACITY = 3500
RATED_SOURCE_CSPF = 4.746
CSPF_TOLERANCE = 0.05


def load_fixture():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data["fixtures"][FIXTURE_ID]


def calculate_hong_kong_cspf(measured_points: dict, declared_capacity: float):
    calculator = ISO16358Calculator(str(CONFIG_PATH))

    return calculator.calculate_cspf(
        measured_points,
        declared_capacity=declared_capacity,
    )


def test_hong_kong_production_config_uses_declared_load_anchor():
    calculator = ISO16358Calculator(str(CONFIG_PATH))

    assert calculator.t_0_load == 23.0
    assert calculator.building_load_source == "declared"
    assert calculator.reference_point == "35_full"
    assert calculator.power_interpolation_method == "iso_boundary_eer"


def test_hong_kong_rated_cspf_source_golden():
    fixture = load_fixture()
    result = calculate_hong_kong_cspf(
        fixture["measured_points"],
        declared_capacity=RATED_LOAD_ANCHOR_CAPACITY,
    )

    assert abs(result["cspf"] - RATED_SOURCE_CSPF) <= CSPF_TOLERANCE


def test_hong_kong_measured_cspf_source_golden_samples():
    samples = [
        (
            "measure_1",
            {
                "35_full": {"capacity": 3600, "power": 900},
                "35_half": {"capacity": 1700, "power": 380},
            },
            4.939,
        ),
        (
            "measure_2",
            {
                "35_full": {"capacity": 3400, "power": 800},
                "35_half": {"capacity": 1800, "power": 410},
            },
            4.880,
        ),
    ]

    for sample_name, measured_points, expected_cspf in samples:
        result = calculate_hong_kong_cspf(
            measured_points,
            declared_capacity=RATED_LOAD_ANCHOR_CAPACITY,
        )
        print(
            {
                "sample": sample_name,
                "cspf": result["cspf"],
                "expected_cspf": expected_cspf,
                "annual_cooling_kwh": result["annual_cooling_kwh"],
                "annual_power_kwh": result["annual_power_kwh"],
            }
        )

        assert abs(result["cspf"] - expected_cspf) <= CSPF_TOLERANCE
