"""Data Mapping dynamic requirement projection tests."""

from core.data_definition.model import MappingRequirement
from core.mapping.editor_projection import (
    apply_mapping_requirements_to_editor_draft,
    project_runtime_mapping_to_editor_draft,
)


def test_mapping_projection_adds_data_definition_required_attribute_column():
    draft = project_runtime_mapping_to_editor_draft(
        {
            "idu": {"IDU-A": {"ID Volume": 1.25}},
            "ref_type": {"R32": {}},
            "exp_type": {"EEV": {}},
        }
    )
    requirement = MappingRequirement(
        column_key="fan_diameter",
        ml_name="Fan_Diameter",
        mapping_entity="idu",
        mapping_attribute="Fan Diameter",
        trigger_column="idu",
    )

    updated = apply_mapping_requirements_to_editor_draft(draft, (requirement,))
    idu = updated.group("idu")

    assert idu is not None
    assert idu.columns == ("IDU", "ID Volume", "Size", "Fan Diameter")
    assert idu.rows[0].value_for("Fan Diameter") == ""
    assert "Required by Data Definition: Fan Diameter" in idu.notes


def test_mapping_projection_maps_cond_specs_requirement_to_editor_group():
    draft = project_runtime_mapping_to_editor_draft(
        {
            "odu_cascade": {
                "ODU-A": {
                    "Available_Fins": ["F&T"],
                    "Available_Pis": ["7"],
                    "Available_Rows": ["1"],
                }
            },
            "cond_specs": {
                "ODU-A F&T 7 1": {"Cond Area": 3.5, "Cond Volume": 4.5}
            },
            "ref_type": {"R32": {}},
            "exp_type": {"EEV": {}},
        }
    )
    requirement = MappingRequirement(
        column_key="cond_depth",
        ml_name="Cond_Depth",
        mapping_entity="cond_specs",
        mapping_attribute="Cond Depth",
        trigger_column="odu",
    )

    updated = apply_mapping_requirements_to_editor_draft(draft, (requirement,))
    group = updated.group("odu_cond_specs")

    assert group is not None
    assert group.columns[-1] == "Cond Depth"
    assert group.rows[0].value_for("Cond Depth") == ""


def test_definition_backed_cond_attribute_restores_existing_runtime_value():
    draft = project_runtime_mapping_to_editor_draft(
        {
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
                    "Cond Inner Area": 2.25,
                    "Unknown Raw Attribute": "not-a-schema-column",
                }
            },
            "ref_type": {"R32": {}},
            "exp_type": {"EEV": {}},
        }
    )
    requirement = MappingRequirement(
        column_key="cond_inner_area",
        ml_name="Cond Inner Area",
        mapping_entity="cond_specs",
        mapping_attribute="Cond Inner Area",
        trigger_column="odu",
        data_type="number",
        required=False,
    )

    updated = apply_mapping_requirements_to_editor_draft(draft, (requirement,))
    group = updated.group("odu_cond_specs")

    assert group.columns[-1] == "Cond Inner Area"
    assert group.rows[0].value_for("Cond Inner Area") == 2.25
    assert "Unknown Raw Attribute" not in group.columns
    assert group.column_data_types["Cond Inner Area"] == "number"
    assert "Cond Inner Area" not in group.required_columns


def test_option_payload_is_backed_but_only_definition_attributes_are_visible():
    draft = project_runtime_mapping_to_editor_draft(
        {
            "ref_type": {
                "R32": {"GWP": 675, "Unknown Raw Attribute": "hidden"}
            },
            "exp_type": {"EEV": {"Control Mode": "Electronic"}},
        }
    )

    ref_before = draft.group("refrigerant")
    assert ref_before.columns == ("Refrigerant",)
    assert ref_before.rows[0].value_for("GWP") == 675
    assert "Unknown Raw Attribute" not in ref_before.columns

    requirements = (
        MappingRequirement(
            column_key="refrigerant_gwp",
            ml_name="Refrigerant GWP",
            mapping_entity="ref_type",
            mapping_attribute="GWP",
            trigger_column="ref_type",
            data_type="number",
        ),
        MappingRequirement(
            column_key="expansion_control_mode",
            ml_name="Expansion Control Mode",
            mapping_entity="exp_type",
            mapping_attribute="Control Mode",
            trigger_column="exp_type",
        ),
    )

    updated = apply_mapping_requirements_to_editor_draft(draft, requirements)
    ref_group = updated.group("refrigerant")
    exp_group = updated.group("expansion")

    assert ref_group.columns == ("Refrigerant", "GWP")
    assert ref_group.rows[0].value_for("GWP") == 675
    assert ref_group.column_data_types["GWP"] == "number"
    assert "Unknown Raw Attribute" not in ref_group.columns
    assert ref_group.rows[0].value_for("Unknown Raw Attribute") == "hidden"
    assert exp_group.columns == ("Expansion", "Control Mode")
    assert exp_group.rows[0].value_for("Control Mode") == "Electronic"


def test_unsupported_mapping_attribute_type_fails_fast():
    draft = project_runtime_mapping_to_editor_draft({})
    requirement = MappingRequirement(
        column_key="cond_inner_area",
        ml_name="Cond Inner Area",
        mapping_entity="cond_specs",
        mapping_attribute="Cond Inner Area",
        trigger_column="odu",
        data_type="matrix",
    )

    try:
        apply_mapping_requirements_to_editor_draft(draft, (requirement,))
    except ValueError as exc:
        assert "unsupported mapping attribute data type 'matrix'" in str(exc)
    else:
        raise AssertionError("unsupported mapping attribute type must fail")
