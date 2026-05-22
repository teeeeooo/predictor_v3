import pytest

from core.calculator_dispatcher import create_calculator_for_profile
from core.calculator_input_adapter import measured_inputs_as_test_points
from core.calculator_prediction_adapter import (
    ALLOWED_MODEL_TARGETS,
    build_predicted_points_envelope,
    predicted_points_to_calculator_input_envelope,
)
from core.calculator_unit_adapter import W_TO_BTU_PER_HOUR


def _full_predicted_points():
    """AHRI SEER2 points in profile-native units (capacity Btu/h, power W).

    Used by ``manual_candidate`` and ``fixture`` source tests.
    """
    return {
        "A_Full": {
            "capacity": 36000,
            "power": 3000,
            "capacity_unit": "Btu/h",
            "power_unit": "W",
        },
        "B_Full": {
            "capacity": 30000,
            "power": 2200,
            "capacity_unit": "Btu/h",
            "power_unit": "W",
        },
        "B_Low": {
            "capacity": 18000,
            "power": 1200,
            "capacity_unit": "Btu/h",
            "power_unit": "W",
        },
        "E_Int": {
            "capacity": 24000,
            "power": 1700,
            "capacity_unit": "Btu/h",
            "power_unit": "W",
        },
        "F_Low": {
            "capacity": 12000,
            "power": 900,
            "capacity_unit": "Btu/h",
            "power_unit": "W",
        },
    }


def _ml_predicted_points():
    """AHRI SEER2 points in ML canonical units (capacity W, power W).

    Used by ``ml_prediction`` source tests.
    """
    return {
        "A_Full": {
            "capacity": 10000.0,
            "power": 3000.0,
            "capacity_unit": "W",
            "power_unit": "W",
        },
        "B_Full": {
            "capacity": 8500.0,
            "power": 2200.0,
            "capacity_unit": "W",
            "power_unit": "W",
        },
        "B_Low": {
            "capacity": 5000.0,
            "power": 1200.0,
            "capacity_unit": "W",
            "power_unit": "W",
        },
        "E_Int": {
            "capacity": 7000.0,
            "power": 1700.0,
            "capacity_unit": "W",
            "power_unit": "W",
        },
        "F_Low": {
            "capacity": 3500.0,
            "power": 900.0,
            "capacity_unit": "W",
            "power_unit": "W",
        },
    }


def test_envelope_shape_matches_design_doc():
    envelope = build_predicted_points_envelope(
        "ahri_usa_seer2",
        _full_predicted_points(),
    )

    assert set(envelope.keys()) == {"source", "model_target", "points", "metadata"}
    assert envelope["source"] == "manual_candidate"
    assert envelope["model_target"] == "cooling"
    assert envelope["metadata"] == {"model_version": None, "candidate_id": None}
    assert set(envelope["points"]) == {"A_Full", "B_Full", "B_Low", "E_Int", "F_Low"}
    assert envelope["points"]["A_Full"] == {
        "capacity": 36000.0,
        "power": 3000.0,
        "capacity_unit": "Btu/h",
        "power_unit": "W",
    }


@pytest.mark.parametrize("source", ["manual_candidate", "fixture"])
def test_envelope_accepts_profile_native_for_manual_and_fixture(source):
    envelope = build_predicted_points_envelope(
        "ahri_usa_seer2",
        _full_predicted_points(),
        source=source,
    )
    assert envelope["source"] == source


def test_envelope_accepts_w_canonical_for_ml_prediction():
    envelope = build_predicted_points_envelope(
        "ahri_usa_seer2",
        _ml_predicted_points(),
        source="ml_prediction",
    )
    assert envelope["source"] == "ml_prediction"
    assert envelope["points"]["A_Full"]["capacity_unit"] == "W"
    assert envelope["points"]["A_Full"]["power_unit"] == "W"


def test_envelope_rejects_legacy_source_vocabulary():
    with pytest.raises(ValueError, match="Unknown source value"):
        build_predicted_points_envelope(
            "ahri_usa_seer2",
            _full_predicted_points(),
            source="predicted",
        )


@pytest.mark.parametrize("model_target", ALLOWED_MODEL_TARGETS)
def test_envelope_accepts_design_model_targets_consistent_with_profile_mode(model_target):
    # AHRI SEER2 is cooling, so only cooling / multi are valid;
    # heating must be rejected.
    if model_target == "heating":
        with pytest.raises(ValueError, match="inconsistent with profile mode"):
            build_predicted_points_envelope(
                "ahri_usa_seer2",
                _full_predicted_points(),
                model_target=model_target,
            )
        return
    envelope = build_predicted_points_envelope(
        "ahri_usa_seer2",
        _full_predicted_points(),
        model_target=model_target,
    )
    assert envelope["model_target"] == model_target


def test_envelope_rejects_unknown_model_target():
    with pytest.raises(ValueError, match="Unknown model_target value"):
        build_predicted_points_envelope(
            "ahri_usa_seer2",
            _full_predicted_points(),
            model_target="auto",
        )


def test_envelope_validates_metadata_keys():
    envelope = build_predicted_points_envelope(
        "ahri_usa_seer2",
        _full_predicted_points(),
        metadata={"model_version": "lgbm-2026.05", "candidate_id": "cand-001"},
    )
    assert envelope["metadata"] == {
        "model_version": "lgbm-2026.05",
        "candidate_id": "cand-001",
    }


def test_envelope_rejects_unexpected_metadata_keys():
    with pytest.raises(ValueError, match="Unexpected metadata keys"):
        build_predicted_points_envelope(
            "ahri_usa_seer2",
            _full_predicted_points(),
            metadata={"model_version": "v1", "feature_set": "v3"},
        )


def test_envelope_rejects_missing_required_points():
    incomplete = _full_predicted_points()
    del incomplete["E_Int"]
    with pytest.raises(KeyError, match="Missing required points"):
        build_predicted_points_envelope("ahri_usa_seer2", incomplete)


def test_envelope_rejects_extra_point_keys():
    extra = _full_predicted_points()
    extra["Z_Extra"] = {
        "capacity": 1000,
        "power": 100,
        "capacity_unit": "Btu/h",
        "power_unit": "W",
    }
    with pytest.raises(ValueError, match="Unexpected point keys"):
        build_predicted_points_envelope("ahri_usa_seer2", extra)


def test_envelope_rejects_extra_inner_keys():
    bad = _full_predicted_points()
    bad["A_Full"]["temp_f"] = 95
    with pytest.raises(ValueError, match="unexpected keys"):
        build_predicted_points_envelope("ahri_usa_seer2", bad)


def test_envelope_rejects_missing_inner_keys():
    bad = _full_predicted_points()
    del bad["A_Full"]["capacity_unit"]
    with pytest.raises(KeyError, match="missing required key 'capacity_unit'"):
        build_predicted_points_envelope("ahri_usa_seer2", bad)


def test_envelope_rejects_unsupported_capacity_unit_for_manual():
    bad = _full_predicted_points()
    bad["A_Full"]["capacity_unit"] = "kW"
    with pytest.raises(
        ValueError,
        match="capacity_unit must be 'Btu/h' when source is 'manual_candidate'",
    ):
        build_predicted_points_envelope("ahri_usa_seer2", bad)


def test_envelope_rejects_unsupported_power_unit_for_manual():
    bad = _full_predicted_points()
    bad["A_Full"]["power_unit"] = "kW"
    with pytest.raises(
        ValueError,
        match="power_unit must be 'W' when source is 'manual_candidate'",
    ):
        build_predicted_points_envelope("ahri_usa_seer2", bad)


def test_envelope_rejects_btu_per_hour_capacity_for_ml_prediction():
    bad = _full_predicted_points()  # Btu/h but source=ml_prediction is wrong
    with pytest.raises(
        ValueError,
        match="capacity_unit must be 'W' when source is 'ml_prediction'",
    ):
        build_predicted_points_envelope(
            "ahri_usa_seer2", bad, source="ml_prediction"
        )


def test_envelope_rejects_non_positive_values():
    bad = _full_predicted_points()
    bad["B_Low"]["capacity"] = 0
    with pytest.raises(ValueError, match="positive capacity and power"):
        build_predicted_points_envelope("ahri_usa_seer2", bad)


def test_envelope_rejects_unsupported_profile():
    with pytest.raises(ValueError, match="Unsupported predicted points envelope profile"):
        build_predicted_points_envelope(
            "ahri_usa_hspf2",
            _full_predicted_points(),
        )


def test_convert_to_calculator_input_envelope_preserves_source_and_metadata():
    envelope = build_predicted_points_envelope(
        "ahri_usa_seer2",
        _ml_predicted_points(),
        source="ml_prediction",
        metadata={"model_version": "lgbm-2026.05", "candidate_id": "cand-001"},
    )

    calc_input = predicted_points_to_calculator_input_envelope(
        envelope, profile_id="ahri_usa_seer2"
    )

    assert calc_input["calculator_profile_id"] == "ahri_usa_seer2"
    assert calc_input["metric"] == "SEER2"
    assert calc_input["options"]["source"] == "ml_prediction"
    assert calc_input["options"]["candidate_id"] == "cand-001"
    assert calc_input["options"]["model_version"] == "lgbm-2026.05"
    assert calc_input["options"]["model_target"] == "cooling"
    assert calc_input["options"]["units"] == {"capacity": "Btu/h", "power": "W"}


def test_convert_ml_prediction_converts_capacity_w_to_btu_per_hour_in_measured_inputs():
    envelope = build_predicted_points_envelope(
        "ahri_usa_seer2",
        _ml_predicted_points(),
        source="ml_prediction",
    )

    calc_input = predicted_points_to_calculator_input_envelope(
        envelope, profile_id="ahri_usa_seer2"
    )

    assert calc_input["measured_inputs"]["A_Full"]["capacity"] == pytest.approx(
        10000.0 * W_TO_BTU_PER_HOUR
    )
    assert calc_input["measured_inputs"]["A_Full"]["power"] == 3000.0


def test_convert_ml_prediction_emits_units_trace_with_conversion_applied_true():
    envelope = build_predicted_points_envelope(
        "ahri_usa_seer2",
        _ml_predicted_points(),
        source="ml_prediction",
    )

    calc_input = predicted_points_to_calculator_input_envelope(
        envelope, profile_id="ahri_usa_seer2"
    )

    assert calc_input["options"]["units_trace"] == {
        "source_units": {"capacity": "W", "power": "W"},
        "target_units": {"capacity": "Btu/h", "power": "W"},
        "conversion_applied": True,
    }


@pytest.mark.parametrize("source", ["manual_candidate", "fixture"])
def test_convert_manual_or_fixture_emits_no_op_units_trace(source):
    envelope = build_predicted_points_envelope(
        "ahri_usa_seer2",
        _full_predicted_points(),
        source=source,
    )

    calc_input = predicted_points_to_calculator_input_envelope(
        envelope, profile_id="ahri_usa_seer2"
    )

    assert calc_input["options"]["units_trace"] == {
        "source_units": {"capacity": "Btu/h", "power": "W"},
        "target_units": {"capacity": "Btu/h", "power": "W"},
        "conversion_applied": False,
    }
    # Profile-native values are passed through unchanged.
    assert calc_input["measured_inputs"]["A_Full"] == {
        "capacity": 36000.0,
        "power": 3000.0,
    }


def test_predicted_points_flow_is_calculator_ready_end_to_end():
    predicted = build_predicted_points_envelope(
        "ahri_usa_seer2",
        _ml_predicted_points(),
        source="ml_prediction",
    )
    calc_input = predicted_points_to_calculator_input_envelope(
        predicted, profile_id="ahri_usa_seer2"
    )
    calculator = create_calculator_for_profile(profile_id="ahri_usa_seer2")

    result = calculator.calculate_seer2(measured_inputs_as_test_points(calc_input))

    assert "SEER2" in result
    assert result["SEER2"] > 0


def test_convert_rejects_unvalidated_dict_missing_points_or_source():
    with pytest.raises(KeyError, match="envelope must contain"):
        predicted_points_to_calculator_input_envelope(
            {"model_target": "cooling"}, profile_id="ahri_usa_seer2"
        )
