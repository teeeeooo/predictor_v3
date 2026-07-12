import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import pytest


FIXTURE_ROOT = (
    Path(__file__).resolve().parent
    / "fixtures/ahri210240/official_calculator"
)
MANIFEST_PATH = FIXTURE_ROOT / "manifest.json"
REGIME_ORDER = [
    "load_at_or_below_low_stage",
    "between_low_and_high_stage",
    "above_high_stage",
]


def load_manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_expected(fixture):
    path = FIXTURE_ROOT / fixture["directory"] / "expected.json"
    return json.loads(path.read_text(encoding="utf-8"))


def raw_row(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return next(csv.DictReader(stream))


def parse_csv_value(field, value):
    if value == "":
        return None
    if ".case_name" in field:
        return value
    if value.upper() == "TRUE":
        return True
    if value.upper() == "FALSE":
        return False
    if re.fullmatch(r"[-+]?\d+", value):
        return int(value)
    try:
        return float(value)
    except ValueError:
        return value


def parsed_row(path):
    return {
        field: parse_csv_value(field, value)
        for field, value in raw_row(path).items()
    }


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def natural_key(value):
    return [
        int(part) if part.isdigit() else part
        for part in re.split(r"(\d+)", value)
    ]


def result_index(field):
    base = field.split(".", 1)[-1]
    match = re.search(r"_k(?:1|2|3)(\d+)$", base)
    if match:
        return int(match.group(1))
    match = re.search(
        r"(?:building(?:Cool|Heat)Load|case_name|cutOut_delta(?:_prime|_doublePrime)?|ratioTotal[A-Za-z]+)(\d+)$",
        base,
    )
    return int(match.group(1)) if match else None


def snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def input_groups(fields):
    ui_names = [
        "compressorDesignStage",
        "indoorBlowerType",
        "needCoilOnlyAdjust",
        "isMobileHomeAndSpaceConstrained",
        "isNonmobileHomeAndNonSpaceConstrained",
        "lockOutLowCapacityOps",
        "ODTempWhenLockOut",
    ]
    tested_names = [
        name
        for name in fields
        if name.endswith("Tested")
        or name in {"T_off", "T_on", "isDemandDefrost", "demandDefrostCredit"}
    ]
    cut_in_out_names = [
        name
        for name in fields
        if name in {"ODTempWhenLockOut", "T_off", "T_on"}
        or name.startswith("compOperationTemp_")
    ]
    degradation_names = [name for name in fields if name.startswith("degCoeff")]
    test_point_names = [
        name
        for name in fields
        if name != "lockOutLowCapacityOps"
        and re.search(r"(?:capacity|powerConsumption|scfm)", name, re.IGNORECASE)
    ]
    groups = {
        "ui_options": ui_names,
        "tested_optional_points": tested_names,
        "compressor_cut_in_cut_out": cut_in_out_names,
        "degradation_coefficients": degradation_names,
        "input_test_points": test_point_names,
    }
    projections = {
        group: {name: fields[name] for name in names if name in fields}
        for group, names in groups.items()
    }
    return groups, projections


def per_bin_projection(raw):
    count = max(result_index(field) or 0 for field in raw)
    return [
        {
            "bin_index": index,
            "bin_key": f"bin_{index}",
            "temperature_f": None,
            "hours_or_fractional_hours": None,
            "raw_values": {
                field: raw[field]
                for field in sorted(
                    [field for field in raw if result_index(field) == index],
                    key=natural_key,
                )
            },
        }
        for index in range(1, count + 1)
    ]


def seasonal_projection(raw):
    groups = {}
    for field in raw:
        match = re.match(
            r"(ratioTotal[A-Za-z]+)(\d+)$", field.split(".", 1)[-1]
        )
        if match:
            groups.setdefault(match.group(1), []).append(field)
    return [
        (
            group,
            sorted(columns, key=natural_key),
        )
        for group, columns in groups.items()
    ]


def cutout_projection(raw):
    raw_values = {}
    distributions = {}
    for family in (
        "cutOut_delta_doublePrime",
        "cutOut_delta_prime",
        "cutOut_delta",
    ):
        columns = sorted(
            [
                field
                for field in raw
                if re.search(rf"\.{family}\d+$", field)
            ],
            key=natural_key,
        )
        if not columns:
            continue
        values = [raw[field] for field in columns]
        raw_values.update({field: raw[field] for field in columns})
        counts = Counter()
        for value in values:
            if value is None:
                counts["blank"] += 1
            elif abs(float(value)) <= 1e-12:
                counts["zero"] += 1
            elif abs(float(value) - 1.0) <= 1e-12:
                counts["one"] += 1
            elif 0 < float(value) < 1:
                counts["fractional"] += 1
            else:
                counts["other"] += 1
        distributions[family] = {
            "raw_columns": columns,
            "raw_values": values,
            "counts": {
                name: counts.get(name, 0)
                for name in ("one", "fractional", "zero", "other", "blank")
            },
        }
    return raw_values, distributions


def availability_projection(raw, label):
    columns = sorted(
        [
            field
            for field in raw
            if re.fullmatch(rf"{label}\.cutOut_delta\d+", field)
        ],
        key=natural_key,
    )
    if not columns:
        return [], "not_exposed", {
            "available": 0,
            "fractional": 0,
            "unavailable": 0,
            "other": 0,
            "blank": 0,
        }
    entries = []
    counts = Counter()
    for field in columns:
        value = raw[field]
        state = (
            "available"
            if value is not None and abs(float(value) - 1) <= 1e-12
            else "fractional"
            if value is not None and 0 < float(value) < 1
            else "unavailable"
            if value is not None and abs(float(value)) <= 1e-12
            else "blank"
            if value is None
            else "other"
        )
        counts[state] += 1
        entries.append(
            {
                "bin_index": int(re.search(r"(\d+)$", field).group(1)),
                "raw_field": field,
                "raw_value": value,
                "state": state,
            }
        )
    return entries, "raw_cutOut_delta", {
        name: counts.get(name, 0)
        for name in ("available", "fractional", "unavailable", "other", "blank")
    }


def auxiliary_projection(raw, label):
    columns = sorted(
        [
            field
            for field in raw
            if re.fullmatch(rf"{label}\.ratioTotalResistHeating\d+", field)
        ],
        key=natural_key,
    )
    if not columns:
        return [], "not_exposed", {
            "active": 0,
            "inactive": 0,
            "other": 0,
            "blank": 0,
        }
    entries = []
    counts = Counter()
    for field in columns:
        value = raw[field]
        state = (
            "active"
            if value is not None and float(value) > 0
            else "inactive"
            if value is not None and float(value) == 0
            else "blank"
            if value is None
            else "other"
        )
        counts[state] += 1
        entries.append(
            {
                "bin_index": int(re.search(r"(\d+)$", field).group(1)),
                "raw_field": field,
                "raw_value": value,
                "state": state,
            }
        )
    return entries, "raw_ratioTotalResistHeating", {
        name: counts.get(name, 0)
        for name in ("active", "inactive", "other", "blank")
    }


def dual_regimes(fixture, raw, label):
    if not fixture["product_classification"].startswith("dual_stage"):
        return [], {}
    mode = "cooling" if fixture["product_classification"] == "dual_stage_cooling" else "heating"
    prefix = label
    count = max(result_index(field) or 0 for field in raw)
    entries = []
    distribution = Counter()
    for index in range(1, count + 1):
        load_field = (
            f"{prefix}.buildingCoolLoad{index}"
            if mode == "cooling"
            else f"{prefix}.buildingHeatLoad{index}"
        )
        capacity_prefix = (
            f"{prefix}.binCoolCapacity_k"
            if mode == "cooling"
            else f"{prefix}.binHeatCapacity_k"
        )
        low_field = f"{capacity_prefix}1{index}"
        high_field = f"{capacity_prefix}2{index}"
        raw_fields = {
            "building_load": load_field,
            "low_stage_capacity": low_field,
            "high_stage_capacity": high_field,
        }
        raw_values = {name: raw[field] for name, field in raw_fields.items()}
        load = float(raw_values["building_load"])
        low = float(raw_values["low_stage_capacity"])
        high = float(raw_values["high_stage_capacity"])
        regime = (
            "load_at_or_below_low_stage"
            if load <= low
            else "between_low_and_high_stage"
            if load <= high
            else "above_high_stage"
        )
        distribution[regime] += 1
        entries.append(
            {
                "bin_index": index,
                "raw_fields": raw_fields,
                "raw_values": raw_values,
                "load_capacity_regime": regime,
            }
        )
    return entries, dict(distribution)


def fixture_params():
    return [
        pytest.param(fixture, id=fixture["fixture_id"])
        for fixture in load_manifest()["fixtures"]
    ]


@pytest.mark.parametrize("fixture", fixture_params())
def test_manifest_registers_complete_fixture_files(fixture):
    manifest = load_manifest()
    case_dir = FIXTURE_ROOT / fixture["directory"]

    assert manifest["schema_version"] == 2
    assert manifest["oracle_status"] == "official AHRI Analytics Appendix M/M1 evidence oracle"
    assert manifest["official_standard"] == (
        "AHRI 210/240 (2023), Appendix M and Appendix M1"
    )
    assert fixture["fixture_id"]
    for filename in fixture["files"]:
        assert (case_dir / filename).is_file(), (
            f"{fixture['fixture_id']} missing {filename}"
        )


@pytest.mark.parametrize("fixture", fixture_params())
def test_raw_checksums_match_expected_and_provenance(fixture):
    case_dir = FIXTURE_ROOT / fixture["directory"]
    expected = load_expected(fixture)
    provenance = (case_dir / "provenance.md").read_text(encoding="utf-8")

    assert set(expected["checksums"]) == {
        "input_template.csv",
        "input.csv",
        "result_m.csv",
        "result_m1.csv",
    }
    for filename, expected_digest in expected["checksums"].items():
        assert sha256(case_dir / filename) == expected_digest
        assert f"| `{filename}` | `{expected_digest}` |" in provenance


@pytest.mark.parametrize("fixture", fixture_params())
def test_input_projection_matches_csv_including_booleans_and_blanks(fixture):
    case_dir = FIXTURE_ROOT / fixture["directory"]
    expected = load_expected(fixture)
    fields = parsed_row(case_dir / "input.csv")
    groups, projections = input_groups(fields)

    assert expected["input_fields"] == fields
    assert expected["input_field_groups"] == groups
    for group in projections:
        assert expected[group] == projections[group]


@pytest.mark.parametrize("fixture", fixture_params())
def test_every_m_and_m1_raw_field_matches_expected(fixture):
    case_dir = FIXTURE_ROOT / fixture["directory"]
    expected = load_expected(fixture)

    for label, filename in (("M", "result_m.csv"), ("M1", "result_m1.csv")):
        raw_text = raw_row(case_dir / filename)
        raw = parsed_row(case_dir / filename)
        expected_fields = expected["results"][label]["raw_fields"]

        assert set(expected_fields) == set(raw_text), (
            f"{fixture['fixture_id']} {label} raw field set changed"
        )
        for field, value in raw.items():
            assert expected_fields[field] == value, (
                f"{fixture['fixture_id']} {label} raw field {field} changed"
            )


@pytest.mark.parametrize("fixture", fixture_params())
def test_headlines_dhr_and_screen_rounding_match_raw(fixture):
    case_dir = FIXTURE_ROOT / fixture["directory"]
    expected = load_expected(fixture)

    for label, filename in (("M", "result_m.csv"), ("M1", "result_m1.csv")):
        raw = parsed_row(case_dir / filename)
        result = expected["results"][label]
        raw_field = result["headline_raw_field"]
        assert raw_field in raw
        assert raw[raw_field] == pytest.approx(result["raw_headline"])
        assert f"{float(raw[raw_field]):.2f}" == f"{result['screen_headline']:.2f}"
        design_load = result["design_load"]
        if design_load["raw_field"] is None:
            assert design_load["raw_value"] is None
        else:
            assert design_load["raw_field"] in raw
            assert raw[design_load["raw_field"]] == pytest.approx(
                design_load["raw_value"]
            )
        assert raw[""] == 1


@pytest.mark.parametrize("fixture", fixture_params())
def test_bin_load_cutout_case_and_seasonal_projections_match_raw(fixture):
    case_dir = FIXTURE_ROOT / fixture["directory"]
    expected = load_expected(fixture)

    for label, filename in (("M", "result_m.csv"), ("M1", "result_m1.csv")):
        raw = parsed_row(case_dir / filename)
        result = expected["results"][label]
        expected_bins = result["bin_trace"]
        actual_bins = per_bin_projection(raw)
        assert len(expected_bins) == len(actual_bins)
        for expected_bin, actual_bin in zip(expected_bins, actual_bins):
            assert expected_bin["bin_index"] == actual_bin["bin_index"]
            assert expected_bin["raw_values"] == actual_bin["raw_values"]
            case_fields = [
                field for field in actual_bin["raw_values"] if ".case_name" in field
            ]
            if case_fields:
                assert expected_bin["operating_case"] == actual_bin["raw_values"][case_fields[0]]

        expected_building = {
            field: value for field, value in raw.items() if ".building" in field
        }
        assert result["building_loads"]["raw_values"] == expected_building

        expected_cutout, expected_distribution = cutout_projection(raw)
        assert result["cutout"]["raw_values"] == expected_cutout
        assert result["cutout"]["delta_distribution"] == expected_distribution

        expected_resistance = {
            field: value
            for field, value in raw.items()
            if ".ratioTotalResistHeating" in field
        }
        assert result["resistance_auxiliary"]["raw_values"] == expected_resistance
        assert result["resistance_auxiliary"]["sum"] == pytest.approx(
            sum(float(value) for value in expected_resistance.values())
        )

        expected_cases = {
            field: value for field, value in raw.items() if ".case_name" in field
        }
        assert result["case_names"]["raw_values"] == expected_cases

        actual_seasonal = seasonal_projection(raw)
        expected_seasonal = result["seasonal_aggregates"]
        assert [item["normalized_name"] for item in expected_seasonal] == [
            f"raw_{snake(group)}" for group, _ in actual_seasonal
        ]
        for expected_item, (group, columns) in zip(expected_seasonal, actual_seasonal):
            assert expected_item["raw_columns"] == columns
            assert expected_item["value"] == pytest.approx(
                sum(float(raw[field]) for field in columns)
            )
            assert expected_item["unit"] == "not exposed"
            assert "candidate seasonal aggregate" in expected_item["interpretation"]


@pytest.mark.parametrize("fixture", fixture_params())
def test_regimes_are_reclassified_and_curve_groups_are_not_cases(fixture):
    case_dir = FIXTURE_ROOT / fixture["directory"]
    expected = load_expected(fixture)
    curve_groups = expected["performance_curve_groups"]["values"]
    for label, filename in (("M", "result_m.csv"), ("M1", "result_m1.csv")):
        raw = parsed_row(case_dir / filename)
        result = expected["results"][label]
        if fixture["product_classification"].startswith("dual_stage"):
            active_regimes = expected["activated_load_capacity_regimes"]["values"]
            assert "activated_operating_cases" not in expected
            assert not set(curve_groups).intersection(active_regimes)
            actual_entries, actual_distribution = dual_regimes(fixture, raw, label)
            assert result["load_capacity_regime_by_bin"] == actual_entries
            assert result["load_capacity_regime_distribution"] == actual_distribution
            expected_active = [
                regime
                for regime in REGIME_ORDER
                if regime in actual_distribution
            ]
            assert expected["activated_load_capacity_regimes"]["by_result"][label] == expected_active
            assert set(REGIME_ORDER[:3]).issubset(actual_distribution)
            availability, availability_status, availability_counts = availability_projection(raw, label)
            assert result["compressor_availability_by_bin"] == availability
            assert result["compressor_availability_status"] == availability_status
            assert result["compressor_availability_distribution"] == {
                "status": availability_status,
                "counts": availability_counts,
            }
            auxiliary, auxiliary_status, auxiliary_counts = auxiliary_projection(raw, label)
            assert result["auxiliary_heat_by_bin"] == auxiliary
            assert result["auxiliary_heat_status"] == auxiliary_status
            assert result["auxiliary_heat_distribution"] == {
                "status": auxiliary_status,
                "counts": auxiliary_counts,
            }
        else:
            active_cases = expected["activated_operating_cases"]["values"]
            assert "activated_load_capacity_regimes" not in expected
            assert not set(curve_groups).intersection(active_cases)
            raw_cases = [
                value for field, value in raw.items() if ".case_name" in field
            ]
            assert expected["activated_operating_cases"]["by_result"][label] == list(
                dict.fromkeys(raw_cases)
            )
            assert expected["operating_case_distribution"]["by_result"][label] == dict(
                Counter(raw_cases)
            )


@pytest.mark.parametrize("label", ("M", "M1"))
def test_cutout_fixture_requires_exact_branch_coverage(label):
    fixture = next(
        fixture
        for fixture in load_manifest()["fixtures"]
        if fixture["fixture_id"]
        == "ahri210240_dual_stage_hspf2_cutout_synthetic_01"
    )
    case_dir = FIXTURE_ROOT / fixture["directory"]
    expected = load_expected(fixture)
    raw = parsed_row(case_dir / ("result_m.csv" if label == "M" else "result_m1.csv"))
    required_counts = {
        "one": 4,
        "fractional": 2,
        "zero": 12,
        "other": 0,
        "blank": 0,
    }

    _, raw_distribution = cutout_projection(raw)
    for family in ("cutOut_delta", "cutOut_delta_prime"):
        assert raw_distribution[family]["counts"] == required_counts
        assert expected["results"][label]["cutout"]["delta_distribution"][family][
            "counts"
        ] == required_counts


@pytest.mark.parametrize("fixture", fixture_params())
def test_input_test_points_are_positive_and_stage_order_is_physical(fixture):
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
def test_oracle_boundary_and_provenance_are_explicit_and_non_sensitive(fixture):
    expected = load_expected(fixture)
    provenance = (
        FIXTURE_ROOT / fixture["directory"] / "provenance.md"
    ).read_text(encoding="utf-8").lower()
    oracle = expected["oracle_status"]

    assert oracle["official_standard"] == (
        "AHRI 210/240 (2023), Appendix M and Appendix M1"
    )
    assert "2026" in oracle["target_2026_boundary"]
    assert oracle["certification_claim"] is False
    input_test_point_lines = [
        line
        for line in provenance.splitlines()
        if line.startswith("| `input_test_points` |")
    ]
    ui_option_lines = [
        line
        for line in provenance.splitlines()
        if line.startswith("| `ui_options` |")
    ]
    assert len(input_test_point_lines) == 1
    assert len(ui_option_lines) == 1
    assert "lockoutlowcapacityops" not in input_test_point_lines[0].lower()
    assert "lockoutlowcapacityops" in ui_option_lines[0].lower()
    assert "session/" not in provenance
    assert "cookie" not in provenance
    assert "token" not in provenance
