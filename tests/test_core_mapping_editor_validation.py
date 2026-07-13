"""User-facing mapping editor draft validation tests."""

from dataclasses import replace

from core.mapping.editor_model import MappingEditorGroup, MappingEditorRow
from core.mapping.editor_projection import project_runtime_mapping_to_editor_draft
from core.mapping.editor_validation import validate_mapping_editor_draft


VALID_MAPPING = {
    "idu": {"IDU-A": {"ID Volume": 1.25}},
    "evap_index": {"EVAP-A": {"Evap Area": 8.2, "Evap Volume": 2.1}},
    "odu": {"ODU-A": {"OD Volume": 2.5}},
    "compressor": {"CMP-A": {"Comp EER": 3.2, "Comp cc": 11}},
    "ref_type": {"R410A": {}, "R32": {}},
    "exp_type": {"EEV": {}, "Capi": {}},
    "odu_cascade": {
        "ODU-A": {
            "Available_Fins": ["F&T"],
            "Available_Pis": ["7"],
            "Available_Rows": ["1"],
        }
    },
    "cond_specs": {"ODU-A F&T 7 1": {"Cond Area": 3.5, "Cond Volume": 4.5}},
}


def _codes(mapping: dict) -> list[str]:
    draft = project_runtime_mapping_to_editor_draft(mapping)
    return [issue.code for issue in validate_mapping_editor_draft(draft).issues]


def test_valid_draft_has_no_blocking_issues():
    draft = project_runtime_mapping_to_editor_draft(VALID_MAPPING)
    result = validate_mapping_editor_draft(draft)

    assert result.issues == ()
    assert result.save_enabled


def test_blank_key_issue():
    mapping = {**VALID_MAPPING, "idu": {"": {"ID Volume": 1.25}}}

    assert "blank_key" in _codes(mapping)


def test_duplicate_key_issue():
    draft = project_runtime_mapping_to_editor_draft(VALID_MAPPING)
    idu = draft.group("idu")
    duplicate = MappingEditorGroup(
        idu.group_key,
        idu.label,
        idu.columns,
        rows=(
            MappingEditorRow({"IDU": "IDU-A", "ID Volume": "1"}),
            MappingEditorRow({"IDU": "IDU-A", "ID Volume": "2"}),
        ),
    )
    draft = replace(draft, groups=(duplicate, *draft.groups[1:]))

    assert "duplicate_key" in [issue.code for issue in validate_mapping_editor_draft(draft).issues]


def test_invalid_number_issue():
    mapping = {**VALID_MAPPING, "idu": {"IDU-A": {"ID Volume": "bad"}}}

    assert "invalid_number" in _codes(mapping)


def test_missing_ref_type_issue():
    mapping = {key: value for key, value in VALID_MAPPING.items() if key != "ref_type"}

    assert "required_section_missing" in _codes(mapping)


def test_missing_exp_type_issue():
    mapping = {key: value for key, value in VALID_MAPPING.items() if key != "exp_type"}

    assert "required_section_missing" in _codes(mapping)


def test_missing_odu_reference_in_cond_specs_issue():
    mapping = {
        **VALID_MAPPING,
        "odu": {},
        "odu_cascade": {
            "ODU-Z": {
                "Available_Fins": ["F&T"],
                "Available_Pis": ["7"],
                "Available_Rows": ["1"],
            }
        },
        "cond_specs": {"ODU-Z F&T 7 1": {"Cond Area": 3.5, "Cond Volume": 4.5}},
    }

    assert "referenced_row_missing" in _codes(mapping)


def test_odu_cond_specs_allows_same_odu_with_different_composite_rows():
    mapping = {
        **VALID_MAPPING,
        "odu_cascade": {
            "ODU-A": {
                "Available_Fins": ["F&T"],
                "Available_Pis": ["7"],
                "Available_Rows": ["1", "2"],
            }
        },
        "cond_specs": {
            "ODU-A F&T 7 1": {"Cond Area": 3.5, "Cond Volume": 4.5},
            "ODU-A F&T 7 2": {"Cond Area": 4.5, "Cond Volume": 5.5},
        },
    }

    assert "duplicate_key" not in _codes(mapping)
    assert "duplicate_cond_specs_key" not in _codes(mapping)


def test_duplicate_odu_cond_specs_composite_key_issue():
    draft = project_runtime_mapping_to_editor_draft(VALID_MAPPING)
    group = draft.group("odu_cond_specs")
    duplicate = MappingEditorGroup(
        group.group_key,
        group.label,
        group.columns,
        rows=(group.rows[0], group.rows[0]),
    )
    groups = tuple(duplicate if item.group_key == group.group_key else item for item in draft.groups)
    draft = replace(draft, groups=groups)

    assert "duplicate_cond_specs_key" in [
        issue.code for issue in validate_mapping_editor_draft(draft).issues
    ]


def test_pfc_cond_specs_does_not_require_pi_and_detects_conditional_duplicate():
    draft = project_runtime_mapping_to_editor_draft(
        {
            **VALID_MAPPING,
            "odu_cascade": {
                "ODU-A": {
                    "Available_Fins": ["PFC"],
                    "Available_Pis": [],
                    "Available_Rows": ["1"],
                }
            },
            "cond_specs": {"ODU-A PFC 1": {"Cond Area": 5, "Cond Volume": 6}},
        }
    )
    group = draft.group("odu_cond_specs")
    stale_placeholder = replace(
        group.rows[0], values={**group.rows[0].values, "Pi": "PFC"}
    )
    stale_numeric = replace(
        group.rows[0], values={**group.rows[0].values, "Pi": "7"}
    )
    duplicate = replace(group, rows=(stale_placeholder, stale_numeric))
    draft = replace(
        draft,
        groups=tuple(duplicate if item.group_key == group.group_key else item for item in draft.groups),
    )

    issues = validate_mapping_editor_draft(draft).issues

    assert not any(issue.field == "Pi" and issue.code == "required_field_missing" for issue in issues)
    duplicate_issue = next(issue for issue in issues if issue.code == "duplicate_cond_specs_key")
    assert duplicate_issue.message == "Duplicate condenser specification identity."


def test_unregistered_fin_type_requires_pi():
    draft = project_runtime_mapping_to_editor_draft(VALID_MAPPING)
    group = draft.group("odu_cond_specs")
    future_fin = replace(
        group.rows[0],
        values={**group.rows[0].values, "Fin Type": "Future Fin", "Pi": ""},
    )
    draft = replace(
        draft,
        groups=tuple(
            replace(group, rows=(future_fin,)) if item.group_key == group.group_key else item
            for item in draft.groups
        ),
    )

    issues = validate_mapping_editor_draft(draft).issues

    assert any(
        issue.code == "required_field_missing" and issue.field == "Pi"
        for issue in issues
    )


def test_general_groups_still_block_duplicate_keys():
    draft = project_runtime_mapping_to_editor_draft(VALID_MAPPING)
    odu = draft.group("odu")
    duplicate = MappingEditorGroup(
        odu.group_key,
        odu.label,
        odu.columns,
        rows=(
            MappingEditorRow({"ODU": "ODU-A", "OD Volume": "1"}),
            MappingEditorRow({"ODU": "ODU-A", "OD Volume": "2"}),
        ),
    )
    draft = replace(
        draft,
        groups=tuple(duplicate if group.group_key == "odu" else group for group in draft.groups),
    )

    assert "duplicate_key" in [
        issue.code for issue in validate_mapping_editor_draft(draft).issues
    ]


def test_blank_cond_area_and_volume_issues():
    mapping = {
        **VALID_MAPPING,
        "cond_specs": {"ODU-A F&T 7 1": {"Cond Area": "", "Cond Volume": ""}},
    }

    codes = _codes(mapping)
    assert codes.count("required_field_missing") >= 2


def test_unresolved_cond_specs_issue():
    mapping = {
        **VALID_MAPPING,
        "cond_specs": {
            "ODU-A F&T 7 1": {"Cond Area": 3.5, "Cond Volume": 4.5},
            "ODU-Z Blue 9 1": {"Cond Area": 9, "Cond Volume": 10},
        },
    }

    assert "unresolved_cond_specs" in _codes(mapping)
