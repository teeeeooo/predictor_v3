"""Shared mapping-cell requirement contract tests."""

from dataclasses import replace

from core.data_definition import (
    DataDefinitionDraft,
    MappingRequirement,
    build_data_definition_draft,
    build_data_definition_report,
    build_data_definition_save_plan,
)
from core.data_definition.mapping_requirement_contract import (
    resolve_mapping_requirement_contracts,
)
from core.data_definition.validation import validate_data_definition_candidate


def test_required_aggregation_and_duplicate_sources_are_order_independent():
    optional = _requirement("fan_attribute_b", required=False)
    required = _requirement("fan_attribute_a", required=True)

    forward = resolve_mapping_requirement_contracts((optional, required))
    reverse = resolve_mapping_requirement_contracts((required, optional))

    assert forward == reverse
    assert forward.conflicts == ()
    assert len(forward.contracts) == 1
    contract = forward.contracts[0]
    assert contract.resolved_group_key == "idu"
    assert contract.mapping_attribute == "Fan Attribute"
    assert contract.data_type == "number"
    assert contract.required
    assert contract.definition_column_keys == (
        "fan_attribute_a",
        "fan_attribute_b",
    )


def test_data_type_and_relation_conflicts_preserve_all_source_identities():
    string_requirement = _requirement(
        "fan_attribute_a",
        data_type="string",
        required=False,
    )
    number_requirement = _requirement("fan_attribute_b", data_type="number")
    data_type_conflict = resolve_mapping_requirement_contracts(
        (string_requirement, number_requirement)
    )

    assert data_type_conflict.contracts == ()
    conflict = data_type_conflict.conflicts[0]
    assert conflict.resolved_group_key == "idu"
    assert conflict.mapping_attribute == "Fan Attribute"
    assert conflict.definition_column_keys == (
        "fan_attribute_a",
        "fan_attribute_b",
    )
    assert conflict.data_types == ("number", "string")
    assert conflict.reasons == ("data_type",)
    assert data_type_conflict == resolve_mapping_requirement_contracts(
        (number_requirement, string_requirement)
    )

    relation_conflict = resolve_mapping_requirement_contracts(
        (
            _requirement("fan_attribute_a", trigger_column="idu"),
            _requirement(
                "fan_attribute_b",
                trigger_column="odu",
                rule_id="alternate_lookup",
            ),
        )
    ).conflicts[0]
    assert relation_conflict.reasons == ("relation",)
    assert relation_conflict.relation_signatures == (
        ("idu", ""),
        ("odu", "alternate_lookup"),
    )


def test_resolved_group_aliases_share_one_compatible_cell():
    resolution = resolve_mapping_requirement_contracts(
        (
            _requirement(
                "cond_inner_a",
                mapping_entity="cond_specs",
                mapping_attribute="Cond Inner Area",
                trigger_column="odu",
                rule_id="cond_specs_lookup",
            ),
            _requirement(
                "cond_inner_b",
                mapping_entity="odu_cond_specs",
                mapping_attribute="Cond Inner Area",
                trigger_column="odu",
                rule_id="cond_specs_lookup",
            ),
        )
    )

    assert resolution.conflicts == ()
    assert len(resolution.contracts) == 1
    assert resolution.contracts[0].resolved_group_key == "odu_cond_specs"


def test_full_data_definition_candidate_validation_blocks_shared_cell_conflict():
    baseline = build_data_definition_draft()
    existing = next(row for row in baseline.rows if row.column_key == "id_volume")
    conflicting = replace(
        existing,
        column_key="id_volume_string_contract",
        label="ID Volume string contract",
        data_type="string",
        ml_name="",
        model_input_enabled=False,
    )
    candidate = DataDefinitionDraft(
        rows=(*baseline.rows, conflicting),
        baseline_rows=baseline.baseline_rows,
    )

    issues = validate_data_definition_candidate(
        candidate,
        build_data_definition_report(),
    )
    conflicts = tuple(
        issue
        for issue in issues
        if issue.code == "mapping_requirement_contract_conflict"
    )

    assert {issue.row_identity for issue in conflicts} == {
        ("schema_row", "id_volume"),
        ("schema_row", "id_volume_string_contract"),
    }
    assert {issue.field_name for issue in conflicts} == {"data_type"}
    assert all("idu.ID Volume" in issue.message for issue in conflicts)
    plan = build_data_definition_save_plan(candidate)
    assert not plan.can_save_schema
    assert "candidate_mapping_requirement_contract_conflict" in {
        blocker.code for blocker in plan.blocked_reasons
    }


def _requirement(
    column_key: str,
    *,
    data_type: str = "number",
    required: bool = True,
    mapping_entity: str = "idu",
    mapping_attribute: str = "Fan Attribute",
    trigger_column: str = "idu",
    rule_id: str = "",
) -> MappingRequirement:
    return MappingRequirement(
        column_key=column_key,
        ml_name=column_key,
        mapping_entity=mapping_entity,
        mapping_attribute=mapping_attribute,
        trigger_column=trigger_column,
        rule_id=rule_id,
        data_type=data_type,
        required=required,
    )
