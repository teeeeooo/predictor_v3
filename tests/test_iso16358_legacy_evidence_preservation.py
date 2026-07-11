"""Focused guards for evidence retained after legacy ISO test retirement."""

import json
from pathlib import Path

from core.calculators.standards.ks_c9306 import KSC9306Calculator


HSPF_MATRIX_PATH = Path("tests/fixtures/iso16358_hspf_golden_fixtures.json")
CASE3_EVIDENCE_PATH = Path(
    "tests/fixtures/asnzs_excel_hspf_compat/legacy_case3_diagnostic_observations.json"
)


def test_retired_legacy_ks_c9306_cspf_golden_is_active():
    calculator = KSC9306Calculator.from_config_path("data/region_configs/korea.json")

    result = calculator.calculate_cspf(
        {
            "35_full": {"capacity": 6035.8, "power": 1641.4},
            "35_half": {"capacity": 3420.4, "power": 679.4},
            "29_min": {"capacity": 1759.6, "power": 201.7},
        },
        declared_capacity=6000,
    )

    assert result["cspf"] == 6.504
    assert result["annual_cooling_kwh"] == 1943.798
    assert result["annual_power_kwh"] == 298.852


def test_retired_seven_case_matrix_and_xfail_context_remain_preserved():
    data = json.loads(HSPF_MATRIX_PATH.read_text(encoding="utf-8"))
    fixture = data["fixtures"]["iso16358_2_hspf_default_bin_seven_case_matrix"]
    expected = {
        1: (4.222, 4885.0, 1157.0),
        2: (4.289, 4885.0, 1139.0),
        3: (4.338, 4885.0, 1126.0),
        4: (4.426, 4885.0, 1104.0),
        5: (4.462, 4885.0, 1095.0),
        6: (4.397, 4885.0, 1111.0),
        7: (4.375, 4885.0, 1117.0),
        8: (4.396, 4885.0, 1111.0),
    }

    assert fixture["status"] == "xfail_until_common_hspf_optional_matrix_supported"
    assert {
        case["case_id"]: (
            case["expected"]["hspf"],
            case["expected"]["lhst_kwh"],
            case["expected"]["chse_kwh"],
        )
        for case in fixture["cases"]
    } == expected


def test_retired_case3_workbook_observations_keep_evidence_only_namespace():
    evidence = json.loads(CASE3_EVIDENCE_PATH.read_text(encoding="utf-8"))
    guard = evidence["namespace_guard"]
    excel = evidence["windows_excel_com"]

    assert all(guard.values())
    assert "not the production" in evidence["former_strict_xfail_context"]
    assert excel["case3_hsec_wh"] == 1126120.47
    assert {
        row["tj"]: (row["cell"], row["observed_power_w"])
        for row in excel["component_observations"]
    } == {
        -1.0: ("CD21", 1504.01),
        0.0: ("CD22", 1330.47),
        1.0: ("CB23", 0.0),
        2.0: ("CB24", 1001.64),
        3.0: ("CB25", 850.55),
        4.0: ("CB26", 724.45),
        5.0: ("CB27", 617.63),
        6.0: ("BO28", 0.0),
        7.0: ("BO29", 412.16),
        8.0: ("BO30", 372.91),
        14.0: ("BM36", 134.33),
        15.0: ("BM37", 95.49),
        16.0: ("BM38", 51.06),
    }
    assert evidence["converted_workbook_diagnostic"]["status"] == (
        "diagnostic_only_not_reference"
    )
