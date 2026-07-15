"""Qt-free Mapping Requirement coverage tests."""

from copy import deepcopy

from apps.train.application.data_mapping.coverage import project_mapping_coverage
from core.data_definition import MappingRequirement
from core.mapping.editor_projection import (
    apply_mapping_requirements_to_editor_draft,
    project_runtime_mapping_to_editor_draft,
)


def test_required_coverage_counts_ready_missing_invalid_in_canonical_order():
    requirements = (
        _requirement("fan_diameter", "Fan Diameter", required=True, data_type="number"),
        _requirement("fan_enabled", "Fan Enabled", required=True, data_type="boolean"),
    )
    draft = apply_mapping_requirements_to_editor_draft(
        project_runtime_mapping_to_editor_draft(
            {
                "idu": {
                    "IDU-A": {"Fan Diameter": ""},
                    "IDU-B": {"Fan Diameter": "bad"},
                    "IDU-C": {"Fan Diameter": 2.5},
                },
                "ref_type": {"R32": {}},
                "exp_type": {"EEV": {}},
            }
        ),
        requirements,
    )
    before = deepcopy(draft)

    coverage = project_mapping_coverage(requirements, draft)

    assert [item.definition_column_key for item in coverage] == [
        "fan_diameter",
        "fan_enabled",
    ]
    diameter = coverage[0]
    assert (diameter.total_rows, diameter.ready_rows) == (3, 1)
    assert (diameter.missing_rows, diameter.invalid_rows) == (1, 1)
    assert [target.row_key for target in diameter.unresolved_targets] == [
        "IDU-A",
        "IDU-B",
    ]
    assert diameter.status == "incomplete"
    assert draft == before


def test_optional_missing_is_incomplete_without_becoming_required():
    requirement = _requirement(
        "fan_note",
        "Fan Note",
        required=False,
        data_type="string",
    )
    draft = apply_mapping_requirements_to_editor_draft(
        project_runtime_mapping_to_editor_draft(
            {
                "idu": {"IDU-A": {}, "IDU-B": {"Fan Note": "reviewed"}},
                "ref_type": {"R32": {}},
                "exp_type": {"EEV": {}},
            }
        ),
        (requirement,),
    )

    item = project_mapping_coverage((requirement,), draft)[0]

    assert not item.required
    assert (item.ready_rows, item.missing_rows, item.invalid_rows) == (1, 1, 0)
    assert item.status == "incomplete"
    assert "Optional — 1 of 2 populated" in item.summary
    assert "Save not blocked" in item.summary
    assert "Fan Note" not in draft.group("idu").required_columns


def test_empty_group_is_no_rows_not_ready():
    requirement = _requirement("fan_diameter", "Fan Diameter", required=True)
    draft = apply_mapping_requirements_to_editor_draft(
        project_runtime_mapping_to_editor_draft(
            {"idu": {}, "ref_type": {"R32": {}}, "exp_type": {"EEV": {}}}
        ),
        (requirement,),
    )

    item = project_mapping_coverage((requirement,), draft)[0]

    assert item.status == "no_rows"
    assert item.total_rows == item.ready_rows == 0
    assert item.summary == "No applicable mapping rows."


def test_missing_group_and_attribute_are_explicit():
    missing_group = MappingRequirement(
        "unknown", "", "unknown_group", "Value", "unknown"
    )
    missing_attribute = _requirement("fan_diameter", "Fan Diameter")
    draft = project_runtime_mapping_to_editor_draft(
        {"idu": {"IDU-A": {}}, "ref_type": {"R32": {}}, "exp_type": {"EEV": {}}}
    )

    coverage = project_mapping_coverage((missing_group, missing_attribute), draft)

    assert [item.status for item in coverage] == [
        "group_unavailable",
        "attribute_unavailable",
    ]


def test_duplicate_blank_row_keys_keep_distinct_stable_occurrences():
    requirement = _requirement("fan_diameter", "Fan Diameter")
    draft = apply_mapping_requirements_to_editor_draft(
        project_runtime_mapping_to_editor_draft(
            {
                "idu": {"IDU-A": {}},
                "ref_type": {"R32": {}},
                "exp_type": {"EEV": {}},
            }
        ),
        (requirement,),
    )
    group = draft.group("idu")
    blank_row = type(group.rows[0])(values={"IDU": "", "Fan Diameter": ""})
    group = type(group)(
        group.group_key,
        group.label,
        group.columns,
        (blank_row, blank_row),
        group.runtime_sections,
        group.notes,
        group.column_data_types,
        group.required_columns,
    )
    draft = type(draft)((group, *draft.groups[1:]), draft.unowned_sections, draft.source_label)

    targets = project_mapping_coverage((requirement,), draft)[0].unresolved_targets

    assert [(target.row_key, target.row_occurrence) for target in targets] == [
        ("", 0),
        ("", 1),
    ]


def _requirement(
    column_key: str,
    attribute: str,
    *,
    required: bool = True,
    data_type: str = "number",
) -> MappingRequirement:
    return MappingRequirement(
        column_key=column_key,
        ml_name="",
        mapping_entity="idu",
        mapping_attribute=attribute,
        trigger_column="idu",
        required=required,
        data_type=data_type,
    )
