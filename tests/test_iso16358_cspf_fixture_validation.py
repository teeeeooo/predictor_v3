import json
from pathlib import Path


FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures/iso16358_cspf_golden_fixtures.json"
)


def load_fixtures():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data["fixtures"]


def test_iso16358_cspf_fixtures_have_required_shape():
    for fixture_id, fixture in load_fixtures().items():
        assert fixture["id"] == fixture_id
        for key in ("id", "name", "standard", "expected", "measured_points", "bin_hours"):
            assert key in fixture, f"{fixture_id} missing {key}"


def test_iso16358_cspf_fixture_bin_hours_match_expected_total():
    for fixture_id, fixture in load_fixtures().items():
        total = sum(row["nj"] for row in fixture["bin_hours"])

        assert total == fixture["expected"]["total_bin_hours"], (
            f"{fixture_id} total bin hours mismatch: "
            f"expected={fixture['expected']['total_bin_hours']}, actual={total}"
        )


def test_iso16358_cspf_fixture_bin_rows_are_valid():
    for fixture_id, fixture in load_fixtures().items():
        assert fixture["bin_hours"], f"{fixture_id} bin_hours must not be empty"
        for index, row in enumerate(fixture["bin_hours"]):
            assert "tj" in row, f"{fixture_id} bin_hours[{index}] missing tj"
            assert "nj" in row, f"{fixture_id} bin_hours[{index}] missing nj"
            assert isinstance(
                row["nj"], (int, float)
            ), f"{fixture_id} bin_hours[{index}].nj must be numeric"
            assert row["nj"] >= 0, f"{fixture_id} bin_hours[{index}].nj must be >= 0"


def test_iso16358_cspf_fixture_measured_points_are_positive():
    for fixture_id, fixture in load_fixtures().items():
        for point_name, point in fixture["measured_points"].items():
            assert point["capacity"] > 0, f"{fixture_id}.{point_name} capacity must be > 0"
            assert point["power"] > 0, f"{fixture_id}.{point_name} power must be > 0"


def test_saso_blank_50c_bin_is_explicitly_interpreted_as_zero():
    fixture = load_fixtures()["saso_cspf_4_95"]
    bin_50c = next(row for row in fixture["bin_hours"] if row["tj"] == 50)

    assert bin_50c["nj"] == 0
    assert bin_50c["source"] == "blank"
    assert any(
        "source blank interpreted as 0 for total consistency" in note
        for note in fixture["notes"]
    )
