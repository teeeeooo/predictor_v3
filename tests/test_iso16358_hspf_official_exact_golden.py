import json
from pathlib import Path

import pytest

from core.calculators.standards.iso16358 import ISO16358Calculator


FIXTURE_PATH = Path("tests/fixtures/iso16358_hspf_official_exact_cases.json")

# Per-case xfail status reflects the *current calculator implementation*, not the
# official-exact reference. Fixture JSON intentionally holds only official data
# (input, description, expected HSTL/HSEC/HSPF) so it stays a clean source of
# truth. When a case starts matching after a calculator change, remove its id
# from this set; do not edit expected values in the fixture.
XFAIL_CASE_IDS: frozenset[int] = frozenset()


def load_official_exact_fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def make_official_exact_calculator(tmp_path):
    fixture = load_official_exact_fixture()
    config_path = tmp_path / "iso16358_hspf_official_exact.json"
    config = {
        "mode": "heating",
        "hspf": {
            "enabled": True,
            "profile": "iso16358_2_hspf",
            "correction": {
                "cd": fixture["config"]["cd"],
                "aux_cop": fixture["config"]["aux_cop"],
            },
            "frost_boundaries": fixture["config"]["frost_boundaries"],
            "load_line": fixture["config"]["load_line"],
            "bin_hours_key": "hspf_bin_hours",
        },
        "hspf_bin_hours": fixture["bin_hours"],
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return ISO16358Calculator(str(config_path))


def measured_inputs_for_case(case):
    point_pool = load_official_exact_fixture()["point_pool"]
    measured = {
        "rated_heating_capacity": point_pool["7_full"]["capacity"],
        "7_full": dict(point_pool["7_full"]),
        "7_half": dict(point_pool["7_half"]),
    }
    for point_key in case["points"]:
        measured[point_key] = dict(point_pool[point_key])
    return measured


def official_exact_actuals(result):
    return {
        "HSTL": round(result["hstl_wh"] / 1000.0, 1),
        "HSEC": round(result["hsec_wh"] / 1000.0, 1),
        "HSPF": round(result["hspf"], 3),
        "branches": ",".join(
            sorted({item["case"] for item in result.get("bin_details", [])})
        ),
    }


def assert_official_exact_case_matches(case, actual):
    expected = case["expected"]
    assert actual["HSTL"] == expected["HSTL"]
    assert actual["HSEC"] == expected["HSEC"]
    assert actual["HSPF"] == expected["HSPF"]


def official_exact_case_params():
    params = []
    for case in load_official_exact_fixture()["cases"]:
        marks = []
        if case["case_id"] in XFAIL_CASE_IDS:
            marks.append(
                pytest.mark.xfail(
                    reason=(
                        "Current ISO16358-2 HSPF actual does not match "
                        "user-provided official exact expected values."
                    ),
                    strict=True,
                )
            )
        params.append(pytest.param(case, marks=marks, id=f"case_{case['case_id']:02d}"))
    return params


def test_official_exact_fixture_preserves_16_cases_and_duplicate_13_14():
    fixture = load_official_exact_fixture()

    assert len(fixture["cases"]) == 16
    case_13 = fixture["cases"][12]
    case_14 = fixture["cases"][13]
    assert case_13["case_id"] == 13
    assert case_14["case_id"] == 14
    assert case_13["description"] == case_14["description"]
    assert case_13["expected"] == case_14["expected"]
    assert "case #13/#14 description duplicate" in fixture["notes"][0]


@pytest.mark.parametrize("case", official_exact_case_params())
def test_iso16358_hspf_official_exact_golden_case(tmp_path, case):
    calculator = make_official_exact_calculator(tmp_path)
    result = calculator.calculate_hspf(measured_inputs_for_case(case))
    actual = official_exact_actuals(result)

    assert_official_exact_case_matches(case, actual)
