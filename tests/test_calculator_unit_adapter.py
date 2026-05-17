import pytest

from core.calculator_unit_adapter import (
    ALLOWED_SOURCE_VALUES,
    W_TO_BTU_PER_HOUR,
    expected_source_units,
    normalize_points_to_profile_native,
    profile_native_units,
    supported_profile_ids,
)


def _ml_canonical_points():
    """5 AHRI SEER2 points in ML canonical units (capacity W, power W)."""
    return {
        "A_Full": {"capacity": 10000.0, "power": 3000.0, "capacity_unit": "W", "power_unit": "W"},
        "B_Full": {"capacity": 8500.0, "power": 2200.0, "capacity_unit": "W", "power_unit": "W"},
        "B_Low": {"capacity": 5000.0, "power": 1200.0, "capacity_unit": "W", "power_unit": "W"},
        "E_Int": {"capacity": 7000.0, "power": 1700.0, "capacity_unit": "W", "power_unit": "W"},
        "F_Low": {"capacity": 3500.0, "power": 900.0, "capacity_unit": "W", "power_unit": "W"},
    }


def _ahri_native_points():
    """5 AHRI SEER2 points in AHRI-native units (capacity Btu/h, power W)."""
    return {
        "A_Full": {"capacity": 36000.0, "power": 3000.0, "capacity_unit": "Btu/h", "power_unit": "W"},
        "B_Full": {"capacity": 30000.0, "power": 2200.0, "capacity_unit": "Btu/h", "power_unit": "W"},
        "B_Low": {"capacity": 18000.0, "power": 1200.0, "capacity_unit": "Btu/h", "power_unit": "W"},
        "E_Int": {"capacity": 24000.0, "power": 1700.0, "capacity_unit": "Btu/h", "power_unit": "W"},
        "F_Low": {"capacity": 12000.0, "power": 900.0, "capacity_unit": "Btu/h", "power_unit": "W"},
    }


def test_supported_profile_ids_first_slice_is_ahri_seer2_only():
    assert supported_profile_ids() == ("ahri_usa_seer2",)


def test_profile_native_units_for_ahri_seer2():
    assert profile_native_units("ahri_usa_seer2") == {
        "capacity": "Btu/h",
        "power": "W",
    }


def test_profile_native_units_rejects_unsupported_profile():
    with pytest.raises(ValueError, match="Unsupported calculator_unit_adapter profile"):
        profile_native_units("ahri_usa_hspf2")


def test_expected_source_units_for_ml_prediction_is_w_canonical():
    assert expected_source_units("ahri_usa_seer2", "ml_prediction") == {
        "capacity": "W",
        "power": "W",
    }


@pytest.mark.parametrize("source", ["manual_candidate", "fixture"])
def test_expected_source_units_for_manual_and_fixture_is_profile_native(source):
    assert expected_source_units("ahri_usa_seer2", source) == {
        "capacity": "Btu/h",
        "power": "W",
    }


def test_normalize_ml_prediction_converts_capacity_w_to_btu_per_hour():
    points, units_trace = normalize_points_to_profile_native(
        "ahri_usa_seer2", _ml_canonical_points(), source="ml_prediction"
    )

    assert points["A_Full"]["capacity"] == pytest.approx(10000.0 * W_TO_BTU_PER_HOUR)
    assert points["A_Full"]["power"] == 3000.0
    assert points["F_Low"]["capacity"] == pytest.approx(3500.0 * W_TO_BTU_PER_HOUR)
    assert points["F_Low"]["power"] == 900.0


def test_normalize_ml_prediction_emits_units_trace_with_conversion_applied_true():
    _, units_trace = normalize_points_to_profile_native(
        "ahri_usa_seer2", _ml_canonical_points(), source="ml_prediction"
    )

    assert units_trace == {
        "source_units": {"capacity": "W", "power": "W"},
        "target_units": {"capacity": "Btu/h", "power": "W"},
        "conversion_applied": True,
    }


@pytest.mark.parametrize("source", ["manual_candidate", "fixture"])
def test_normalize_manual_and_fixture_passes_through_without_conversion(source):
    points, units_trace = normalize_points_to_profile_native(
        "ahri_usa_seer2", _ahri_native_points(), source=source
    )

    assert points["A_Full"]["capacity"] == 36000.0
    assert points["A_Full"]["power"] == 3000.0
    assert units_trace == {
        "source_units": {"capacity": "Btu/h", "power": "W"},
        "target_units": {"capacity": "Btu/h", "power": "W"},
        "conversion_applied": False,
    }


def test_normalize_ml_prediction_rejects_btu_per_hour_capacity():
    bad = _ahri_native_points()  # capacity_unit = Btu/h but source = ml_prediction
    with pytest.raises(ValueError, match="capacity_unit must be 'W' when source is 'ml_prediction'"):
        normalize_points_to_profile_native(
            "ahri_usa_seer2", bad, source="ml_prediction"
        )


def test_normalize_manual_rejects_w_capacity():
    bad = _ml_canonical_points()  # capacity_unit = W but source = manual_candidate
    with pytest.raises(ValueError, match="capacity_unit must be 'Btu/h' when source is 'manual_candidate'"):
        normalize_points_to_profile_native(
            "ahri_usa_seer2", bad, source="manual_candidate"
        )


def test_normalize_rejects_unsupported_profile():
    with pytest.raises(ValueError, match="Unsupported calculator_unit_adapter profile"):
        normalize_points_to_profile_native(
            "en14825_scop", _ahri_native_points(), source="manual_candidate"
        )


def test_normalize_rejects_unknown_source_value():
    with pytest.raises(ValueError, match="Unknown source value"):
        normalize_points_to_profile_native(
            "ahri_usa_seer2", _ahri_native_points(), source="predicted"
        )


def test_normalize_rejects_non_mapping_points():
    with pytest.raises(TypeError, match="points must be a mapping"):
        normalize_points_to_profile_native(
            "ahri_usa_seer2", ["A_Full", "B_Full"], source="manual_candidate"  # type: ignore[arg-type]
        )


def test_normalize_rejects_missing_unit_keys():
    bad = _ml_canonical_points()
    del bad["A_Full"]["capacity_unit"]
    with pytest.raises(KeyError, match="must specify capacity_unit and power_unit"):
        normalize_points_to_profile_native(
            "ahri_usa_seer2", bad, source="ml_prediction"
        )


def test_normalize_rejects_non_positive_values():
    bad = _ml_canonical_points()
    bad["B_Low"]["capacity"] = 0
    with pytest.raises(ValueError, match="positive capacity and power"):
        normalize_points_to_profile_native(
            "ahri_usa_seer2", bad, source="ml_prediction"
        )


def test_normalize_rejects_power_unit_other_than_w():
    bad = _ml_canonical_points()
    bad["A_Full"]["power_unit"] = "kW"
    with pytest.raises(ValueError, match="power_unit must be 'W' when source is 'ml_prediction'"):
        normalize_points_to_profile_native(
            "ahri_usa_seer2", bad, source="ml_prediction"
        )


def test_allowed_source_values_matches_design_vocab():
    assert set(ALLOWED_SOURCE_VALUES) == {"manual_candidate", "ml_prediction", "fixture"}
