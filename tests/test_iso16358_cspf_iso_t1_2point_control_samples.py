import json
from pathlib import Path

from core.calculators.standards.iso16358 import ISO16358Calculator


FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures/iso16358_cspf_golden_fixtures.json"
)
CONTROL_SAMPLE_IDS = [
    "southeast_asia_iso_basic_cspf_4_665",
    "asean_report_table7_variable_speed_cspf_4_76",
    "jatl_slide_variable_capacity_cspf_4_86",
    "jatl_tool_required_test_only_cspf_4_93",
]


def load_fixtures():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data["fixtures"]


def make_config(fixture):
    return {
        "region": "ISO T1 Default 2-Point Diagnostic",
        "standard": "ISO16358-1",
        "t_100_load": 35.0,
        "t_0_load": 20.0,
        "reference_point": "35_full",
        "Cd": 0.25,
        "building_load_source": "measured",
        "points": {
            "35_full": "measure",
            "35_half": "measure",
            "29_full": "default",
            "29_half": "default",
        },
        "derived_rules": {
            "29_full": {
                "source": "35_full",
                "capacity_factor": 1.077,
                "power_factor": 0.914,
            },
            "29_half": {
                "source": "35_half",
                "capacity_factor": 1.077,
                "power_factor": 0.914,
            },
        },
        "bin_hours": fixture["bin_hours"],
    }


def run_sample(tmp_path, sample_id, fixture):
    config_path = tmp_path / f"{sample_id}.json"
    config_path.write_text(json.dumps(make_config(fixture)), encoding="utf-8")
    calculator = ISO16358Calculator(str(config_path))
    result = calculator.calculate_cspf(fixture["measured_points"])
    expected = fixture["expected"]
    return {
        "sample_id": sample_id,
        "expected_cspf": expected["cspf"],
        "current_cspf": result["cspf"],
        "delta_cspf": result["cspf"] - expected["cspf"],
        "expected_csec_kwh": expected.get(
            "csec_kwh", expected.get("annual_energy_consumption_kwh")
        ),
        "current_csec_kwh": result["annual_power_kwh"],
        "expected_cstl_kwh": expected.get("cstl_kwh"),
        "current_cstl_kwh": result["annual_cooling_kwh"],
    }


def test_iso_t1_default_2point_control_samples_current_engine_direction(tmp_path):
    """Diagnostic only: compares current engine against four ISO T1 2-point controls."""
    fixtures = load_fixtures()
    results = [
        run_sample(tmp_path, sample_id, fixtures[sample_id])
        for sample_id in CONTROL_SAMPLE_IDS
    ]

    print(json.dumps(results, indent=2, sort_keys=True))

    assert all(result["current_cspf"] > 0 for result in results)
    assert all(result["current_csec_kwh"] > 0 for result in results)
    assert all(result["current_cstl_kwh"] > 0 for result in results)
    assert all(result["delta_cspf"] < 0 for result in results)
