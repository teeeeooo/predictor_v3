"""Core mapping autofill policy tests."""

from core.mapping.autofill import build_autofill_updates


SAMPLE_MAPPING = {
    "idu": {"IDU-A": {"ID Volume": 1.25}},
    "odu": {"ODU-A": {"OD Volume": 2.5}},
    "fin_type": {"F&T": {}, "Plate": {}},
    "pi": {"7": {}, "9": {}},
    "row": {"1": {}, "2": {}},
    "odu_cascade": {
        "ODU-A": {
            "Available_Fins": ["F&T"],
            "Available_Pis": ["7"],
            "Available_Rows": ["1", "2"],
        },
        "ODU With Space": {
            "Available_Fins": ["F&T"],
            "Available_Pis": ["7"],
            "Available_Rows": ["1"],
        }
    },
    "cond_specs": {
        "ODU-A F&T 7 1": {
            "Cond Area": 3.5,
            "Cond Volume": 4.5,
        },
        "ODU-A F&T 7 2": {
            "Cond Area": 7.5,
            "Cond Volume": 8.5,
        },
        "ODU With Space F&T 7 1": {
            "Cond Area": 9.5,
            "Cond Volume": 10.5,
        }
    },
}


def _updates_by_key(result):
    return {update.key: update.value for update in result.updates}


def test_idu_simple_mapping_autofills_id_volume():
    result = build_autofill_updates(
        {"idu": "IDU-A"},
        "idu",
        SAMPLE_MAPPING,
    )

    assert _updates_by_key(result)["id_volume"] == 1.25


def test_odu_change_autofills_volume_and_clears_dependent_fields():
    result = build_autofill_updates(
        {"odu": "ODU-A", "fin_type": "old", "pi": "old", "row": "old"},
        "odu",
        SAMPLE_MAPPING,
    )
    updates = _updates_by_key(result)

    assert updates["od_volume"] == 2.5
    assert updates["fin_type"] == ""
    assert updates["pi"] == ""
    assert updates["row"] == ""
    assert updates["cond_area"] == ""
    assert result.dropdown_options["fin_type"] == ("F&T",)
    assert result.dropdown_options["pi"] == ("7",)
    assert result.dropdown_options["row"] == ("1", "2")


def test_cond_specs_fill_when_cascade_selection_is_complete():
    result = build_autofill_updates(
        {"odu": "ODU-A", "fin_type": "F&T", "pi": "7", "row": "1"},
        "row",
        SAMPLE_MAPPING,
    )
    updates = _updates_by_key(result)

    assert updates["cond_area"] == 3.5
    assert updates["cond_volume"] == 4.5


def test_cond_specs_fill_distinct_row_specific_specs():
    result = build_autofill_updates(
        {"odu": "ODU-A", "fin_type": "F&T", "pi": "7", "row": "2"},
        "row",
        SAMPLE_MAPPING,
    )
    updates = _updates_by_key(result)

    assert updates["cond_area"] == 7.5
    assert updates["cond_volume"] == 8.5


def test_odu_unselected_returns_base_fin_pi_row_options():
    result = build_autofill_updates(
        {"odu": ""},
        "odu",
        SAMPLE_MAPPING,
    )

    assert result.dropdown_options["fin_type"] == ("F&T", "Plate")
    assert result.dropdown_options["pi"] == ("7", "9")
    assert result.dropdown_options["row"] == ("1", "2")


def test_missing_odu_cascade_returns_empty_row_specific_options():
    mapping = {key: value for key, value in SAMPLE_MAPPING.items() if key != "odu_cascade"}
    result = build_autofill_updates(
        {"odu": "ODU-A"},
        "odu",
        mapping,
    )

    assert result.dropdown_options["fin_type"] == ()
    assert result.dropdown_options["pi"] == ()
    assert result.dropdown_options["row"] == ()


def test_missing_cond_specs_returns_no_cond_autofill_values():
    mapping = {key: value for key, value in SAMPLE_MAPPING.items() if key != "cond_specs"}
    result = build_autofill_updates(
        {"odu": "ODU-A", "fin_type": "F&T", "pi": "7", "row": "1"},
        "row",
        mapping,
    )
    updates = _updates_by_key(result)

    assert updates["cond_area"] == ""
    assert updates["cond_volume"] == ""


def test_unmatched_cond_specs_composite_key_clears_cond_autofill_values():
    result = build_autofill_updates(
        {"odu": "ODU-A", "fin_type": "F&T", "pi": "9", "row": "1"},
        "row",
        SAMPLE_MAPPING,
    )
    updates = _updates_by_key(result)

    assert updates["cond_area"] == ""
    assert updates["cond_volume"] == ""


def test_odu_name_with_spaces_uses_direct_composite_lookup():
    result = build_autofill_updates(
        {"odu": "ODU With Space", "fin_type": "F&T", "pi": "7", "row": "1"},
        "row",
        SAMPLE_MAPPING,
    )
    updates = _updates_by_key(result)

    assert updates["cond_area"] == 9.5
    assert updates["cond_volume"] == 10.5


def test_invalid_odu_cascade_shape_returns_empty_row_specific_options():
    result = build_autofill_updates(
        {"odu": "ODU-A"},
        "odu",
        {**SAMPLE_MAPPING, "odu_cascade": []},
    )

    assert result.dropdown_options["fin_type"] == ()
    assert result.dropdown_options["pi"] == ()
    assert result.dropdown_options["row"] == ()


def test_invalid_cond_specs_shape_returns_no_cond_autofill_values():
    result = build_autofill_updates(
        {"odu": "ODU-A", "fin_type": "F&T", "pi": "7", "row": "1"},
        "row",
        {**SAMPLE_MAPPING, "cond_specs": []},
    )
    updates = _updates_by_key(result)

    assert updates["cond_area"] == ""
    assert updates["cond_volume"] == ""


def test_invalid_top_level_mapping_shape_does_not_crash():
    result = build_autofill_updates(
        {"odu": "ODU-A", "fin_type": "F&T", "pi": "7", "row": "1"},
        "row",
        [],
    )
    updates = _updates_by_key(result)

    assert updates["cond_area"] == ""
    assert updates["cond_volume"] == ""


def test_cond_specs_clear_when_cascade_selection_is_incomplete():
    result = build_autofill_updates(
        {"odu": "ODU-A", "fin_type": "F&T", "pi": "", "row": "1"},
        "row",
        SAMPLE_MAPPING,
    )
    updates = _updates_by_key(result)

    assert updates["cond_area"] == ""
    assert updates["cond_volume"] == ""
