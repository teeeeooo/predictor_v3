import json
from pathlib import Path

from core.calculator_iso16358 import ISO16358Calculator


FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures/iso16358_cspf_golden_fixtures.json"
)
FIXTURE_ID = "asean_report_table7_variable_speed_cspf_4_76"
CSPF_TOLERANCE = 0.01
ENERGY_TOLERANCE_KWH = 1.0
PROVENANCE_PENDING_REASON = (
    "provenance-pending: 4개 control sample 확보, "
    "ISO xlsm audit 결과 엔진 수식 구조 동일 확인, "
    "xlsm cached output 불일치로 golden 신뢰 불가. "
    "Phase 2에서 재검토."
)


def load_fixture():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data["fixtures"][FIXTURE_ID]


def make_config(fixture):
    return {
        "region": "ASEAN Report Table 7 Control",
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


def calculate_control_sample(tmp_path, fixture):
    config_path = tmp_path / "asean_report_table7_control.json"
    config_path.write_text(json.dumps(make_config(fixture)), encoding="utf-8")
    calculator = ISO16358Calculator(str(config_path))
    return calculator.calculate_cspf(fixture["measured_points"])


def test_asean_report_table7_variable_speed_cspf_control_sample(tmp_path):
    """Diagnostic control sample from published report; not certification golden."""
    assert PROVENANCE_PENDING_REASON.startswith("provenance-pending")
    fixture = load_fixture()
    result = calculate_control_sample(tmp_path, fixture)

    print(
        {
            "expected_cspf": fixture["expected"]["cspf"],
            "actual_cspf": result["cspf"],
            "annual_cooling_kwh": result["annual_cooling_kwh"],
            "annual_power_kwh": result["annual_power_kwh"],
            "expected_annual_energy_kwh": fixture["expected"][
                "annual_energy_consumption_kwh"
            ],
        }
    )

    assert abs(result["cspf"] - fixture["expected"]["cspf"]) <= CSPF_TOLERANCE
    assert (
        abs(
            result["annual_power_kwh"]
            - fixture["expected"]["annual_energy_consumption_kwh"]
        )
        <= ENERGY_TOLERANCE_KWH
    )
