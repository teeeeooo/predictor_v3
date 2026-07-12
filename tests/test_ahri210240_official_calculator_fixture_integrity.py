import csv
import hashlib
import json
from pathlib import Path

import pytest


FIXTURE_ROOT = (
    Path(__file__).resolve().parent
    / "fixtures/ahri210240/official_calculator"
)
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"


def load_manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_expected(fixture):
    path = FIXTURE_ROOT / fixture["directory"] / "expected.json"
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def result_row(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return next(csv.DictReader(stream))


def fixture_params():
    return [
        pytest.param(fixture, id=fixture["fixture_id"])
        for fixture in load_manifest()["fixtures"]
    ]


@pytest.mark.parametrize("fixture", fixture_params())
def test_manifest_registers_complete_fixture_files(fixture):
    case_dir = FIXTURE_ROOT / fixture["directory"]

    assert fixture["fixture_id"]
    assert fixture["files"]
    for filename in fixture["files"]:
        assert (case_dir / filename).is_file(), (
            f"{fixture['fixture_id']} missing {filename}"
        )


@pytest.mark.parametrize("fixture", fixture_params())
def test_raw_checksums_match_expected_and_provenance(fixture):
    case_dir = FIXTURE_ROOT / fixture["directory"]
    expected = load_expected(fixture)
    provenance = (case_dir / "provenance.md").read_text(encoding="utf-8")

    for filename, expected_digest in expected["checksums"].items():
        actual_digest = sha256(case_dir / filename)
        assert actual_digest == expected_digest
        assert f"| `{filename}` | `{expected_digest}` |" in provenance


@pytest.mark.parametrize("fixture", fixture_params())
def test_headline_metrics_match_raw_and_screen_rounding(fixture):
    case_dir = FIXTURE_ROOT / fixture["directory"]
    expected = load_expected(fixture)
    metric = expected["results"]["M"]["headline_raw_field"].split(".", 1)[1]

    for label, filename, prefix in (
        ("M", "result_m.csv", "M"),
        ("M1", "result_m1.csv", "M1"),
    ):
        row = result_row(case_dir / filename)
        raw_value = float(row[f"{prefix}.{metric}"])
        result = expected["results"][label]

        assert raw_value == pytest.approx(result["raw_headline"])
        assert f"{raw_value:.2f}" == f"{result['screen_headline']:.2f}"
        assert row.get("") == "1"


@pytest.mark.parametrize("fixture", fixture_params())
def test_expected_keeps_m_and_m1_bin_trace_and_operating_case(fixture):
    expected = load_expected(fixture)

    assert expected["fixture_id"] == fixture["fixture_id"]
    assert expected["calculation_date"]
    assert expected["calculator_url"] == (
        "https://seerhspf2.ahrianalytics.org/app/seerhspf2"
    )
    assert expected["calculator_version"] == "not displayed"
    assert expected["activated_operating_cases"]["values"]

    for label in ("M", "M1"):
        result = expected["results"][label]
        assert result["bin_trace"], f"{fixture['fixture_id']} {label} has no bins"
        assert result["seasonal_totals"]["delivered_capacity_or_load"][
            "raw_columns"
        ]
        assert result["seasonal_totals"]["electrical_energy"]["raw_columns"]


@pytest.mark.parametrize("fixture", fixture_params())
def test_input_points_are_positive_and_stage_order_is_physical(fixture):
    expected = load_expected(fixture)
    points = expected["input_test_points"]

    for name, value in points.items():
        if value is not None and any(
            token in name.lower() for token in ("capacity", "powerconsumption", "scfm")
        ):
            assert value > 0, f"{fixture['fixture_id']}.{name} must be positive"

    if expected["product_classification"] == "dual_stage_cooling":
        assert points["coolCapacity82min"] < points["coolCapacity82full"]
    elif expected["product_classification"] == "dual_stage_heat_pump":
        assert points["heatCapacity47min"] < points["heatCapacity47full"]
    else:
        assert points["heatCapacity35full"] < points["heatCapacity35boost"]
        assert points["heatCapacity35min"] < points["heatCapacity35full"]


@pytest.mark.parametrize("fixture", fixture_params())
def test_provenance_does_not_record_session_or_auth_material(fixture):
    provenance = (
        FIXTURE_ROOT / fixture["directory"] / "provenance.md"
    ).read_text(encoding="utf-8").lower()

    assert "session/" not in provenance
    assert "cookie" not in provenance
    assert "token" not in provenance
