import json
from pathlib import Path

import pytest

from core.calculator_iso16358 import ISO16358Calculator


FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures/iso16358_cspf_golden_fixtures.json"
)
FIXTURE_ID = "southeast_asia_iso_basic_cspf_4_665"
CSPF_TOLERANCE = 0.001


def load_iso_t1_fixture():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data["fixtures"][FIXTURE_ID]


def make_iso_t1_default_2point_calculator(tmp_path, fixture):
    config_path = tmp_path / "iso_t1_default_2point.json"
    config = {
        "region": "ISO T1 Default 2-Point",
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
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return ISO16358Calculator(str(config_path))


@pytest.mark.xfail(
    strict=True,
    reason=(
        "provenance-pending: 4개 control sample 확보, "
        "ISO xlsm audit 결과 엔진 수식 구조 동일 확인, "
        "xlsm cached output 불일치로 golden 신뢰 불가. "
        "Phase 2에서 재검토."
    ),
)
def test_iso_t1_default_2point_cspf_4_665_one_sample_regression(tmp_path):
    """1-sample regression, not certification-grade validation."""
    fixture = load_iso_t1_fixture()
    calculator = make_iso_t1_default_2point_calculator(tmp_path, fixture)

    result = calculator.calculate_cspf(fixture["measured_points"])

    assert abs(result["cspf"] - fixture["expected"]["cspf"]) <= CSPF_TOLERANCE, (
        "ISO T1 default 2-point CSPF 1-sample regression mismatch: "
        f"expected={fixture['expected']['cspf']}, actual={result['cspf']}, "
        "not certification-grade validation"
    )
