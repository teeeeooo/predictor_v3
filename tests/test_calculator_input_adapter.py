import pytest

from core.calculator_dispatcher import create_calculator_for_profile
from core.calculator_input_adapter import build_calculator_input_envelope


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


def test_envelope_default_units_and_source_for_tuple_input():
    envelope = build_calculator_input_envelope("ahri_usa_seer2", SAMPLE_TUPLE_POINTS)

    assert envelope["calculator_profile_id"] == "ahri_usa_seer2"
    assert envelope["calculator_id"] == "ahri_seer2"
    assert envelope["source"] == "manual"
    assert envelope["units"] == {"capacity": "Btu/h", "power": "W"}
    assert envelope["test_points"] == {
        "A_Full": (36000.0, 3000.0),
        "B_Full": (30000.0, 2200.0),
        "B_Low": (18000.0, 1200.0),
        "E_Int": (24000.0, 1700.0),
        "F_Low": (12000.0, 900.0),
    }


def test_envelope_accepts_dict_point_form_and_records_source():
    envelope = build_calculator_input_envelope(
        "ahri_usa_seer2", SAMPLE_DICT_POINTS, source="predicted"
    )

    assert envelope["source"] == "predicted"
    assert envelope["test_points"]["A_Full"] == (36000.0, 3000.0)
    assert envelope["test_points"]["F_Low"] == (12000.0, 900.0)


def test_envelope_is_calculator_ready_for_ahri_seer2():
    """The envelope's test_points must be directly accepted by calculate_seer2."""
    envelope = build_calculator_input_envelope("ahri_usa_seer2", SAMPLE_TUPLE_POINTS)
    calculator = create_calculator_for_profile(profile_id="ahri_usa_seer2")

    result = calculator.calculate_seer2(envelope["test_points"])

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
