"""Structured Data Definition full-candidate issue contracts."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.mapping_requirement_contract import MappingRequirementConflict
from core.data_definition.report_model import DataDefinitionIssue


@dataclass(frozen=True)
class DataDefinitionCandidateIssue:
    """Structured full-candidate issue used by save planning and writing."""

    code: str
    message: str
    row_identity: tuple[str, str] | None = None
    field_name: str = ""


def mapping_contract_report_issues(
    conflicts: tuple[MappingRequirementConflict, ...],
) -> tuple[DataDefinitionIssue, ...]:
    """Project shared-cell conflicts into the read-only definition report."""
    return tuple(
        DataDefinitionIssue(
            severity="error",
            code="mapping_requirement_contract_conflict",
            subject=f"{conflict.resolved_group_key}.{conflict.mapping_attribute}",
            message=conflict.message,
        )
        for conflict in conflicts
    )


def candidate_mapping_contract_issues(
    conflicts: tuple[MappingRequirementConflict, ...],
) -> tuple[DataDefinitionCandidateIssue, ...]:
    """Attribute each shared-cell conflict to every source definition field."""
    return tuple(
        DataDefinitionCandidateIssue(
            code="mapping_requirement_contract_conflict",
            message=conflict.message,
            row_identity=("schema_row", definition_key) if definition_key else None,
            field_name=field_name,
        )
        for conflict in conflicts
        for definition_key in conflict.definition_column_keys
        for field_name in _mapping_contract_conflict_fields(conflict)
    )


def _mapping_contract_conflict_fields(
    conflict: MappingRequirementConflict,
) -> tuple[str, ...]:
    fields: list[str] = []
    if "data_type" in conflict.reasons or "unsupported_data_type" in conflict.reasons:
        fields.append("data_type")
    if "relation" in conflict.reasons:
        if len({trigger for trigger, _rule in conflict.relation_signatures}) > 1:
            fields.append("trigger_column")
        if len({rule for _trigger, rule in conflict.relation_signatures}) > 1:
            fields.append("rule_id")
    return tuple(fields or ("mapping_attribute",))
