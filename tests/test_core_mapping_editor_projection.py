"""User-facing mapping editor draft projection tests."""

import json

from core.mapping.editor_projection import (
    OWNED_RUNTIME_SECTIONS,
    load_runtime_mapping_editor_draft,
    project_runtime_mapping_to_editor_draft,
)


SAMPLE_MAPPING = {
    "idu": {"IDU-A": {"ID Volume": 1.25, "Size": "S1"}},
    "evap_index": {"EVAP-A": {"Size": "S1", "Evap Area": 8.2, "Evap Volume": 2.1}},
    "odu": {"ODU-A": {"OD Volume": 2.5}},
    "compressor": {"CMP-A": {"Comp EER": 3.2, "Comp cc": 11}},
    "ref_type": {"R410A": {}, "R32": {}},
    "exp_type": {"EEV": {}, "Capi": {}},
    "odu_cascade": {
        "ODU-A": {
            "Available_Fins": ["F&T"],
            "Available_Pis": ["7"],
            "Available_Rows": ["1", "2"],
        }
    },
    "cond_specs": {
        "ODU-A F&T 7 1": {"Cond Area": 3.5, "Cond Volume": 4.5},
        "ODU-Z Blue 9 1": {"Cond Area": 9, "Cond Volume": 10},
    },
    "vendor_notes": {"source": "kept"},
}


def test_runtime_mapping_projects_to_seven_user_facing_groups():
    draft = project_runtime_mapping_to_editor_draft(SAMPLE_MAPPING)

    assert [group.label for group in draft.groups] == [
        "IDU",
        "Evap Index",
        "ODU",
        "Compressor",
        "Refrigerant",
        "Expansion",
        "ODU Cond Specs",
    ]
    assert all(section in OWNED_RUNTIME_SECTIONS for section in ("idu", "ref_type"))


def test_simple_runtime_sections_project_domain_columns():
    draft = project_runtime_mapping_to_editor_draft(SAMPLE_MAPPING)

    idu = draft.group("idu")
    evap = draft.group("evap_index")
    odu = draft.group("odu")
    compressor = draft.group("compressor")

    assert idu is not None
    assert idu.columns == ("IDU", "ID Volume", "Size")
    assert idu.rows[0].value_for("IDU") == "IDU-A"
    assert idu.rows[0].value_for("ID Volume") == 1.25
    assert evap is not None
    assert evap.rows[0].value_for("Evap Area") == 8.2
    assert odu is not None
    assert odu.rows[0].value_for("OD Volume") == 2.5
    assert compressor is not None
    assert compressor.rows[0].value_for("Comp cc") == 11


def test_ref_and_exp_type_project_as_user_options():
    draft = project_runtime_mapping_to_editor_draft(SAMPLE_MAPPING)

    refrigerant = draft.group("refrigerant")
    expansion = draft.group("expansion")

    assert refrigerant is not None
    assert refrigerant.columns == ("Refrigerant",)
    assert [row.value_for("Refrigerant") for row in refrigerant.rows] == ["R32", "R410A"]
    assert expansion is not None
    assert [row.value_for("Expansion") for row in expansion.rows] == ["Capi", "EEV"]


def test_odu_cond_specs_matches_cascade_combinations_without_splitting_keys():
    draft = project_runtime_mapping_to_editor_draft(SAMPLE_MAPPING)
    group = draft.group("odu_cond_specs")

    assert group is not None
    assert group.columns == ("ODU", "Fin Type", "Pi", "Row", "Cond Area", "Cond Volume")
    matched = next(row for row in group.rows if row.source_key == "ODU-A F&T 7 1")
    assert matched.unresolved is False
    assert matched.value_for("ODU") == "ODU-A"
    assert matched.value_for("Fin Type") == "F&T"
    assert matched.value_for("Pi") == "7"
    assert matched.value_for("Row") == "1"
    assert matched.value_for("Cond Area") == 3.5


def test_pfc_cond_specs_projects_without_pi():
    mapping = {
        **SAMPLE_MAPPING,
        "odu_cascade": {
            "ODU-A": {
                "Available_Fins": ["PFC"],
                "Available_Pis": [],
                "Available_Rows": ["1"],
            }
        },
        "cond_specs": {"ODU-A PFC 1": {"Cond Area": 5, "Cond Volume": 6}},
    }

    group = project_runtime_mapping_to_editor_draft(mapping).group("odu_cond_specs")

    assert group is not None
    assert group.rows[0].source_key == "ODU-A PFC 1"
    assert group.rows[0].value_for("Pi") == ""
    assert group.rows[0].unresolved is False


def test_unmatched_cond_specs_are_preserved_as_unresolved_rows():
    draft = project_runtime_mapping_to_editor_draft(SAMPLE_MAPPING)
    group = draft.group("odu_cond_specs")

    assert group is not None
    unresolved = next(row for row in group.rows if row.source_key == "ODU-Z Blue 9 1")
    assert unresolved.unresolved is True
    assert unresolved.value_for("ODU") == "ODU-Z Blue 9 1"
    assert unresolved.value_for("Cond Volume") == 10


def test_unknown_sections_are_preserved_as_metadata():
    draft = project_runtime_mapping_to_editor_draft(SAMPLE_MAPPING)

    assert draft.unowned_sections == {"vendor_notes": {"source": "kept"}}


def test_load_runtime_mapping_editor_draft_rejects_missing_or_empty_data(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text(json.dumps(SAMPLE_MAPPING), encoding="utf-8")

    draft = load_runtime_mapping_editor_draft(str(mapping_file))

    assert draft.group("idu").rows[0].value_for("IDU") == "IDU-A"
    assert str(mapping_file) in draft.source_label
