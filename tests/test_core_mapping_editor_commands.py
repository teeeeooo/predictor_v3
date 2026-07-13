"""Mapping editor draft command tests."""

from core.mapping.editor_commands import (
    add_draft_row,
    delete_draft_row,
    duplicate_draft_row,
    set_draft_cell,
)
from core.mapping.editor_projection import project_runtime_mapping_to_editor_draft
from core.mapping.editor_validation import validate_mapping_editor_draft


MAPPING = {
    "idu": {"IDU-A": {"ID Volume": 1.25}},
    "evap_index": {},
    "odu": {},
    "compressor": {},
    "ref_type": {"R32": {}},
    "exp_type": {"EEV": {}},
}


PFC_MAPPING = {
    **MAPPING,
    "odu": {"ODU-A": {"OD Volume": 2.5}},
    "odu_cascade": {
        "ODU-A": {
            "Available_Fins": ["PFC"],
            "Available_Pis": [],
            "Available_Rows": ["1"],
        }
    },
    "cond_specs": {"ODU-A PFC 1": {"Cond Area": 5, "Cond Volume": 6}},
}


F_AND_T_MAPPING = {
    **MAPPING,
    "odu": {"ODU-A": {"OD Volume": 2.5}},
    "odu_cascade": {
        "ODU-A": {
            "Available_Fins": ["F&T"],
            "Available_Pis": ["7"],
            "Available_Rows": ["1"],
        }
    },
    "cond_specs": {"ODU-A F&T 7 1": {"Cond Area": 5, "Cond Volume": 6}},
}


def test_set_draft_cell_updates_row_value_and_source_key():
    draft = project_runtime_mapping_to_editor_draft(MAPPING)

    draft = set_draft_cell(draft, "idu", 0, "IDU", "IDU-B")

    row = draft.group("idu").rows[0]
    assert row.value_for("IDU") == "IDU-B"
    assert row.source_key == "IDU-B"


def test_add_duplicate_and_delete_draft_rows():
    draft = project_runtime_mapping_to_editor_draft(MAPPING)

    draft = add_draft_row(draft, "idu")
    assert len(draft.group("idu").rows) == 2
    assert draft.group("idu").rows[1].value_for("IDU") == ""

    draft = duplicate_draft_row(draft, "idu", 0)
    assert len(draft.group("idu").rows) == 3
    assert draft.group("idu").rows[1].value_for("ID Volume") == 1.25

    draft = delete_draft_row(draft, "idu", 1)
    assert len(draft.group("idu").rows) == 2


def test_pfc_pi_edit_and_fin_type_change_clear_pi_in_draft():
    draft = project_runtime_mapping_to_editor_draft(PFC_MAPPING)

    draft = set_draft_cell(draft, "odu_cond_specs", 0, "Pi", "7")
    row = draft.group("odu_cond_specs").rows[0]
    assert row.value_for("Pi") == ""
    assert row.source_key == "ODU-A PFC 1"

    draft = set_draft_cell(draft, "odu_cond_specs", 0, "Fin Type", "F&T")
    draft = set_draft_cell(draft, "odu_cond_specs", 0, "Pi", "7")
    draft = set_draft_cell(draft, "odu_cond_specs", 0, "Fin Type", "PFC")
    row = draft.group("odu_cond_specs").rows[0]
    assert row.value_for("Pi") == ""
    assert row.source_key == "ODU-A PFC 1"


def test_cond_specs_identity_edits_recalculate_source_key_from_current_values():
    draft = project_runtime_mapping_to_editor_draft(F_AND_T_MAPPING)

    for column, value, expected in (
        ("ODU", "ODU-B", "ODU-B F&T 7 1"),
        ("Fin Type", "Future Fin", "ODU-B Future Fin 7 1"),
        ("Pi", "9", "ODU-B Future Fin 9 1"),
        ("Row", "2", "ODU-B Future Fin 9 2"),
    ):
        draft = set_draft_cell(draft, "odu_cond_specs", 0, column, value)
        assert draft.group("odu_cond_specs").rows[0].source_key == expected


def test_incomplete_non_pfc_identity_reaches_validation_with_current_source_key():
    draft = project_runtime_mapping_to_editor_draft(F_AND_T_MAPPING)

    draft = set_draft_cell(draft, "odu_cond_specs", 0, "Pi", "")

    row = draft.group("odu_cond_specs").rows[0]
    issues = validate_mapping_editor_draft(draft).issues
    assert row.source_key == "ODU-A F&T  1"
    assert any(
        issue.code == "required_field_missing"
        and issue.field == "Pi"
        and issue.row_key == row.source_key
        for issue in issues
    )
