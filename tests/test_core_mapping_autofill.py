"""Core mapping autofill policy tests."""

from core.mapping.autofill import build_autofill_updates


SAMPLE_MAPPING = {
    "idu": {"IDU-A": {"ID Volume": 1.25}},
    "odu": {"ODU-A": {"OD Volume": 2.5}},
    "odu_cascade": {
        "ODU-A": {
            "Available_Fins": ["F&T"],
            "Available_Pis": ["7"],
            "Available_Rows": ["1"],
        }
    },
    "cond_specs": {
        "ODU-A F&T 7 1": {
            "Cond Area": 3.5,
            "Cond Volume": 4.5,
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


def test_cond_specs_fill_when_cascade_selection_is_complete():
    result = build_autofill_updates(
        {"odu": "ODU-A", "fin_type": "F&T", "pi": "7", "row": "1"},
        "row",
        SAMPLE_MAPPING,
    )
    updates = _updates_by_key(result)

    assert updates["cond_area"] == 3.5
    assert updates["cond_volume"] == 4.5


def test_cond_specs_clear_when_cascade_selection_is_incomplete():
    result = build_autofill_updates(
        {"odu": "ODU-A", "fin_type": "F&T", "pi": "", "row": "1"},
        "row",
        SAMPLE_MAPPING,
    )
    updates = _updates_by_key(result)

    assert updates["cond_area"] == ""
    assert updates["cond_volume"] == ""
