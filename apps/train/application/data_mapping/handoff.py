"""Build saved Data Definition handoffs without reading mapping values."""

from __future__ import annotations

from apps.train.application.data_mapping.contracts import DataMappingNavigationRequest
from core.data_definition import DataDefinitionDraft, DataDefinitionReport
from core.mapping.editor_projection import mapping_group_key_for_requirement


def build_saved_mapping_handoffs(
    saved_report: DataDefinitionReport,
    saved_draft: DataDefinitionDraft,
    changed_identities: frozenset[tuple[str, str]],
) -> tuple[DataMappingNavigationRequest, ...]:
    """Return canonical saved requirements affected by one successful write."""
    changed_column_keys = {
        row.column_key
        for row in saved_draft.rows
        if row.identity in changed_identities
        or (row.source_kind, row.column_key) in changed_identities
    }
    labels = {
        row.column_key: row.label
        for row in saved_draft.rows
        if row.source_kind == "schema_row"
    }
    return tuple(
        DataMappingNavigationRequest(
            definition_identity=("schema_row", requirement.column_key),
            definition_column_key=requirement.column_key,
            definition_label=labels.get(requirement.column_key, requirement.column_key),
            mapping_entity=requirement.mapping_entity,
            mapping_attribute=requirement.mapping_attribute,
            resolved_group_key=mapping_group_key_for_requirement(requirement),
            required=requirement.required,
            data_type=requirement.data_type,
        )
        for requirement in saved_report.mapping_requirements
        if requirement.column_key in changed_column_keys
    )
