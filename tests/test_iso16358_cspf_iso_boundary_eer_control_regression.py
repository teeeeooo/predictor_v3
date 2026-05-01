import json
from pathlib import Path

from core.calculator_iso16358 import ISO16358Calculator


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

CSPF_TOLERANCES = {
    "southeast_asia_iso_basic_cspf_4_665": 0.005,
    "asean_report_table7_variable_speed_cspf_4_76": 0.01,
    "jatl_slide_variable_capacity_cspf_4_86": 0.01,
    "jatl_tool_required_test_only_cspf_4_93": 0.01,
}
ENERGY_TOLERANCE_KWH = 1.0
PROVENANCE_PENDING_REASON = (
    "provenance-pending: 4개 control sample 확보, "
    "ISO xlsm audit 결과 엔진 수식 구조 동일 확인, "
    "xlsm cached output 불일치로 golden 신뢰 불가. "
    "Phase 2에서 재검토."
)


def load_fixtures():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data["fixtures"]


def make_config(fixture):
    return {
        "region": "ISO T1 Default 2-Point Boundary EER Control",
        "standard": "ISO16358-1",
        "t_100_load": 35.0,
        "t_0_load": 20.0,
        "reference_point": "35_full",
        "Cd": 0.25,
        "building_load_source": "measured",
        "power_interpolation_method": "iso_boundary_eer",
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


def calculate_sample(tmp_path, sample_id, fixture):
    config_path = tmp_path / f"{sample_id}.json"
    config_path.write_text(json.dumps(make_config(fixture)), encoding="utf-8")
    return ISO16358Calculator(str(config_path)).calculate_cspf(
        fixture["measured_points"]
    )


def expected_csec(fixture):
    expected = fixture["expected"]
    return expected.get("csec_kwh", expected.get("annual_energy_consumption_kwh"))


def test_iso_boundary_eer_four_control_sample_regression(tmp_path):
    """Control regression only; references remain provenance-pending."""
    assert PROVENANCE_PENDING_REASON.startswith("provenance-pending")
    fixtures = load_fixtures()
    results = []

    for sample_id in CONTROL_SAMPLE_IDS:
        fixture = fixtures[sample_id]
        result = calculate_sample(tmp_path, sample_id, fixture)
        expected = fixture["expected"]
        sample_result = {
            "sample_id": sample_id,
            "expected_cspf": expected["cspf"],
            "actual_cspf": result["cspf"],
            "actual_csec_kwh": result["annual_power_kwh"],
            "actual_cstl_kwh": result["annual_cooling_kwh"],
            "expected_csec_kwh": expected_csec(fixture),
            "expected_cstl_kwh": expected.get("cstl_kwh"),
        }
        results.append(sample_result)

        assert abs(result["cspf"] - expected["cspf"]) <= CSPF_TOLERANCES[sample_id]

        csec = expected_csec(fixture)
        if csec is not None:
            assert abs(result["annual_power_kwh"] - csec) <= ENERGY_TOLERANCE_KWH

        if "cstl_kwh" in expected:
            assert (
                abs(result["annual_cooling_kwh"] - expected["cstl_kwh"])
                <= ENERGY_TOLERANCE_KWH
            )

    print(json.dumps(results, indent=2, sort_keys=True))
