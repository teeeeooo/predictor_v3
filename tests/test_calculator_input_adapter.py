import pytest

from core.calculator_dispatcher import create_calculator_for_profile
from core.calculator_input_adapter import (
    ALLOWED_SOURCE_VALUES,
    build_calculator_input_envelope,
    measured_inputs_as_test_points,
)


SAMPLE_TUPLE_POINTS = {
    "A_Full": (36000, 3000),
    "B_Full": (30000, 2200),
    "B_Low": (18000, 1200),
    "E_Int": (24000, 1700),
    "F_Low": (12000, 900),
}

SAMPLE_DICT_POINTS = {
    "A_Full": {"capacity": 36000, "power": 3000},
    "B_Full": {"capacity": 30000, "power": 2200},
    "B_Low": {"capacity": 18000, "power": 1200},
    "E_Int": {"capacity": 24000, "power": 1700},
    "F_Low": {"capacity": 12000, "power": 900},
}


def test_envelope_top_level_matches_design_doc_shape():
    envelope = build_calculator_input_envelope("ahri_usa_seer2", SAMPLE_TUPLE_POINTS)

    assert envelope["calculator_profile_id"] == "ahri_usa_seer2"
    assert envelope["standard"] == "AHRI_210_240"
    assert envelope["region"] == "usa"
    assert envelope["mode"] == "cooling"
    assert envelope["metric"] == "SEER2"
    assert "measured_inputs" in envelope
    assert "options" in envelope
    # design doc shape: no calculator_id at top level; no test_points alias
    assert "calculator_id" not in envelope
    assert "test_points" not in envelope


def test_envelope_measured_inputs_use_capacity_power_dicts():
    envelope = build_calculator_input_envelope("ahri_usa_seer2", SAMPLE_TUPLE_POINTS)

    measured = envelope["measured_inputs"]
    assert set(measured) == {"A_Full", "B_Full", "B_Low", "E_Int", "F_Low"}
    assert measured["A_Full"] == {"capacity": 36000.0, "power": 3000.0}
    assert measured["F_Low"] == {"capacity": 12000.0, "power": 900.0}


def test_envelope_options_carries_units_and_source_with_design_vocab():
    envelope = build_calculator_input_envelope(
        "ahri_usa_seer2", SAMPLE_DICT_POINTS, source="ml_prediction"
    )

    options = envelope["options"]
    assert options["units"] == {"capacity": "Btu/h", "power": "W"}
    assert options["source"] == "ml_prediction"


def test_envelope_default_source_is_manual_candidate():
    envelope = build_calculator_input_envelope("ahri_usa_seer2", SAMPLE_TUPLE_POINTS)

    assert envelope["options"]["source"] == "manual_candidate"


@pytest.mark.parametrize("source", ALLOWED_SOURCE_VALUES)
def test_envelope_accepts_all_design_doc_source_values(source):
    envelope = build_calculator_input_envelope(
        "ahri_usa_seer2", SAMPLE_TUPLE_POINTS, source=source
    )
    assert envelope["options"]["source"] == source


def test_envelope_rejects_legacy_source_vocabulary():
    with pytest.raises(ValueError, match="Unknown source value"):
        build_calculator_input_envelope(
            "ahri_usa_seer2", SAMPLE_TUPLE_POINTS, source="manual"
        )
    with pytest.raises(ValueError, match="Unknown source value"):
        build_calculator_input_envelope(
            "ahri_usa_seer2", SAMPLE_TUPLE_POINTS, source="predicted"
        )


def test_envelope_rejects_extra_point_keys():
    bad = dict(SAMPLE_TUPLE_POINTS)
    bad["Z_Extra"] = (10000, 800)
    with pytest.raises(ValueError, match="Unexpected point keys"):
        build_calculator_input_envelope("ahri_usa_seer2", bad)


def test_envelope_rejects_extra_inner_point_keys():
    bad = {key: dict(value) for key, value in SAMPLE_DICT_POINTS.items()}
    bad["A_Full"]["temp_f"] = 95
    with pytest.raises(ValueError, match="unexpected keys"):
        build_calculator_input_envelope("ahri_usa_seer2", bad)


def test_envelope_rejects_extra_unit_keys():
    with pytest.raises(ValueError, match="Unexpected unit keys"):
        build_calculator_input_envelope(
            "ahri_usa_seer2",
            SAMPLE_TUPLE_POINTS,
            units={"capacity": "Btu/h", "power": "W", "temperature": "F"},
        )


def test_envelope_rejects_options_overriding_reserved_keys():
    with pytest.raises(ValueError, match="reserved key"):
        build_calculator_input_envelope(
            "ahri_usa_seer2",
            SAMPLE_TUPLE_POINTS,
            options={"source": "fixture"},
        )


def test_envelope_carries_caller_supplied_options_through():
    envelope = build_calculator_input_envelope(
        "ahri_usa_seer2",
        SAMPLE_TUPLE_POINTS,
        options={"cd_low": 0.20},
    )
    assert envelope["options"]["cd_low"] == 0.20


def test_envelope_helper_converts_measured_inputs_to_calculator_tuple_form():
    envelope = build_calculator_input_envelope("ahri_usa_seer2", SAMPLE_TUPLE_POINTS)
    test_points = measured_inputs_as_test_points(envelope)

    assert test_points == {
        "A_Full": (36000.0, 3000.0),
        "B_Full": (30000.0, 2200.0),
        "B_Low": (18000.0, 1200.0),
        "E_Int": (24000.0, 1700.0),
        "F_Low": (12000.0, 900.0),
    }


def test_envelope_is_calculator_ready_for_ahri_seer2_via_helper():
    envelope = build_calculator_input_envelope("ahri_usa_seer2", SAMPLE_TUPLE_POINTS)
    calculator = create_calculator_for_profile(profile_id="ahri_usa_seer2")

    result = calculator.calculate_seer2(measured_inputs_as_test_points(envelope))

    assert "SEER2" in result
    assert result["SEER2"] > 0


def test_envelope_rejects_unsupported_profile():
    with pytest.raises(ValueError, match="Unsupported calculator input envelope profile"):
        build_calculator_input_envelope("ahri_usa_hspf2", SAMPLE_TUPLE_POINTS)


def test_envelope_rejects_missing_required_points():
    incomplete = dict(SAMPLE_TUPLE_POINTS)
    del incomplete["E_Int"]
    with pytest.raises(KeyError, match="Missing required points"):
        build_calculator_input_envelope("ahri_usa_seer2", incomplete)


def test_envelope_rejects_non_positive_capacity():
    bad = dict(SAMPLE_TUPLE_POINTS)
    bad["B_Low"] = (0.0, 1200)
    with pytest.raises(ValueError, match="positive capacity and power"):
        build_calculator_input_envelope("ahri_usa_seer2", bad)


def test_envelope_rejects_unit_conversion_attempts():
    with pytest.raises(ValueError, match="Unsupported unit for 'capacity'"):
        build_calculator_input_envelope(
            "ahri_usa_seer2",
            SAMPLE_TUPLE_POINTS,
            units={"capacity": "kW", "power": "W"},
        )


def test_envelope_rejects_malformed_point_value():
    bad = dict(SAMPLE_TUPLE_POINTS)
    bad["A_Full"] = "36000,3000"
    with pytest.raises(TypeError, match="must be a .capacity, power."):
        build_calculator_input_envelope("ahri_usa_seer2", bad)
