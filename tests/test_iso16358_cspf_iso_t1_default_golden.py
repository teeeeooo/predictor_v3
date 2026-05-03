import json
from pathlib import Path

from core.calculator_iso16358 import ISO16358Calculator


FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures/iso16358_cspf_golden_fixtures.json"
)
FIXTURE_ID = "southeast_asia_iso_basic_cspf_4_665"
CSPF_TOLERANCE = 0.001
PROVENANCE_PENDING_REASON = (
    "provenance-pending: 4개 control sample 확보, "
    "ISO xlsm audit 결과 엔진 수식 구조 동일 확인, "
    "xlsm cached output 불일치로 golden 신뢰 불가. "
    "Phase 2에서 재검토."
)


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
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return ISO16358Calculator(str(config_path))


def test_iso_t1_default_2point_cspf_4_665_one_sample_regression(tmp_path):
    """1-sample regression, not certification-grade validation.

    The reference remains provenance-pending; see PROVENANCE_PENDING_REASON.
    """
    assert PROVENANCE_PENDING_REASON.startswith("provenance-pending")
    fixture = load_iso_t1_fixture()
    calculator = make_iso_t1_default_2point_calculator(tmp_path, fixture)

    result = calculator.calculate_cspf(fixture["measured_points"])

    assert abs(result["cspf"] - fixture["expected"]["cspf"]) <= CSPF_TOLERANCE, (
        "ISO T1 default 2-point CSPF 1-sample regression mismatch: "
        f"expected={fixture['expected']['cspf']}, actual={result['cspf']}, "
        "not certification-grade validation"
    )

def test_iso_t1_default_2point_bin_details_structure(tmp_path):
    fixture = load_iso_t1_fixture()
    calculator = make_iso_t1_default_2point_calculator(tmp_path, fixture)
    result = calculator.calculate_cspf(fixture["measured_points"])

    assert "bin_details" in result
    bin_details = result["bin_details"]
    assert isinstance(bin_details, list)
    
    # check that we have bin details and keys are correct
    assert len(bin_details) > 0
    for detail in bin_details:
        assert "bin_no" in detail
        assert "tj" in detail
        assert "nj" in detail
        assert "lc" in detail
        assert "capacity" in detail
        assert "power" in detail
        assert "eer" in detail
        assert "cstl_bin" in detail
        assert "csec_bin" in detail
