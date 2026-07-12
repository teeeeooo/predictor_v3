import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pytest

_FIXTURE_DIR = Path("tests/fixtures/ahri210240/official_calculator")


def _round_nearest_005(value: float) -> float:
    increment = Decimal("0.05")
    rounded = (Decimal(str(value)) / increment).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    return float(rounded * increment)


def _validate_schema_subset(instance, schema, path="$"):
    """Validate the JSON-Schema keywords used by this fixture without extras."""
    expected_type = schema.get("type")
    if expected_type == "object":
        assert isinstance(instance, dict), f"{path} must be an object"
    elif expected_type == "string":
        assert isinstance(instance, str), f"{path} must be a string"
    elif expected_type == "number":
        assert isinstance(instance, (int, float)) and not isinstance(
            instance, bool
        ), f"{path} must be a number"
    if "const" in schema:
        assert instance == schema["const"], f"{path} must equal schema const"
    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            assert key in instance, f"{path}.{key} is required"
        if schema.get("additionalProperties") is False:
            assert set(instance) <= set(properties), (
                f"{path} has unexpected keys: {set(instance) - set(properties)}"
            )
        for key, child_schema in properties.items():
            if key in instance:
                _validate_schema_subset(
                    instance[key], child_schema, f"{path}.{key}"
                )


def _assert_hspf_overlay_case(case, raw_key, published_key):
    normalized_energy = (
        case["normalized_compressor_energy_wh"]
        + case["normalized_resistance_energy_wh"]
    )
    raw = (
        case["normalized_heating_aggregate"]
        / normalized_energy
        * case["defrost_factor"]
    )
    hours = case["heating_load_hours"]

    assert case[raw_key] == pytest.approx(raw)
    assert case[published_key] == _round_nearest_005(raw)
    assert case["seasonal_heating_btu"] == pytest.approx(
        case["normalized_heating_aggregate"] * hours
    )
    assert case["seasonal_compressor_energy_wh"] == pytest.approx(
        case["normalized_compressor_energy_wh"] * hours
    )
    assert case["seasonal_resistance_energy_wh"] == pytest.approx(
        case["normalized_resistance_energy_wh"] * hours
    )
    assert case["seasonal_total_energy_wh"] == pytest.approx(
        normalized_energy * hours
    )
    assert case["resistance_btu_per_wh"] == 3.412


def test_ahri_2026_expected_overlay_schema_and_numerical_integrity():
    overlay = json.loads(
        (_FIXTURE_DIR / "2026_expected_overlay.json").read_text(
            encoding="utf-8"
        )
    )
    schema = json.loads(
        (_FIXTURE_DIR / "2026_expected_overlay.schema.json").read_text(
            encoding="utf-8"
        )
    )
    _validate_schema_subset(overlay, schema)

    seer = overlay["dual_stage_seer2_synthetic_01"]
    raw_seer2 = (
        seer["normalized_cooling_aggregate"]
        / seer["normalized_energy_aggregate"]
    )
    assert seer["raw_seer2"] == pytest.approx(raw_seer2)
    assert seer["published_seer2"] == _round_nearest_005(raw_seer2)

    _assert_hspf_overlay_case(
        overlay["dual_stage_hspf2_synthetic_01"],
        "raw_hspf2",
        "published_hspf2",
    )
    _assert_hspf_overlay_case(
        overlay["dual_stage_hspf2_cutout_synthetic_01"],
        "raw_hspf2",
        "published_hspf2",
    )
    triple = overlay["triple_capacity_northern_hspf2_synthetic_01"]
    _assert_hspf_overlay_case(
        triple,
        "raw_hspf2_candidate",
        "published_hspf2_candidate",
    )

    expected_h2low_capacity = 0.90 * (
        14500.0 + 0.6 * (21000.0 - 14500.0)
    )
    expected_h2low_power = 0.985 * (
        1750.0 + 0.6 * (1300.0 - 1750.0)
    )
    assert triple["corrected_h2low_capacity"] == pytest.approx(
        expected_h2low_capacity
    )
    assert triple["corrected_h2low_power"] == pytest.approx(
        expected_h2low_power
    )
