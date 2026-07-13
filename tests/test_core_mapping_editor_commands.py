"""Mapping editor draft command tests."""

from core.mapping.editor_commands import (
    add_draft_row,
    delete_draft_row,
    duplicate_draft_row,
    set_draft_cell,
)
from core.mapping.editor_projection import project_runtime_mapping_to_editor_draft


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
    assert draft.group("odu_cond_specs").rows[0].value_for("Pi") == ""

    draft = set_draft_cell(draft, "odu_cond_specs", 0, "Fin Type", "F&T")
    draft = set_draft_cell(draft, "odu_cond_specs", 0, "Pi", "7")
    draft = set_draft_cell(draft, "odu_cond_specs", 0, "Fin Type", "PFC")
    assert draft.group("odu_cond_specs").rows[0].value_for("Pi") == ""
