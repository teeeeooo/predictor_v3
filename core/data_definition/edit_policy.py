"""Editable field policy for Data Definition drafts."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.draft import DataDefinitionDraftRow

SCHEMA_BACKED_EDITABLE_FIELDS = frozenset(
    {
        "label",
        "editor",
        "data_type",
        "visible",
        "required",
        "readonly",
        "value_source",
        "mapping_entity",
        "mapping_attribute",
        "trigger_column",
        "rule_id",
        "model_input_enabled",
        "ml_name",
        "one_hot_group",
        "active",
        "notes",
    }
)
SCHEMA_BACKED_RESTRICTED_FIELDS = frozenset({"display_order", "column_key", "role"})
MAPPING_VALUE_FIELDS = frozenset(
    {"mapping_value", "mapping_row", "row_value", "value", "mapping_json"}
)
RUNTIME_OWNED_FIELDS = frozenset(
    {"training_data_path", "model_artifact_path", "model_activation"}
)


@dataclass(frozen=True)
class FieldEditability:
    """Editability decision for one draft field."""

    field_name: str
    editable: bool
    category: str
    reason: str


def field_editability(
    row: DataDefinitionDraftRow,
    field_name: str,
) -> FieldEditability:
    """Return whether a draft field can be edited in future Arc 15C UI."""
    if field_name in MAPPING_VALUE_FIELDS:
        return _blocked(field_name, "mapping_value_owned", "Data Mapping owns mapping values.")
    if field_name in RUNTIME_OWNED_FIELDS:
        return _blocked(field_name, "runtime_owned", "Readiness/runtime paths are not draft fields.")
    if row.source_kind == "derived_policy":
        return _blocked(
            field_name,
            "derived_policy_blocked",
            "Derived policy persistence is required before editing derived rows.",
        )
    if row.source_kind == "feature_projection":
        return _blocked(
            field_name,
            "projection_only",
            "Feature projection rows are generated compatibility output.",
        )
    if row.source_kind != "schema_row":
        return _blocked(field_name, "unknown_source", f"Unknown source kind: {row.source_kind}")
    if field_name in SCHEMA_BACKED_EDITABLE_FIELDS:
        return FieldEditability(
            field_name=field_name,
            editable=True,
            category="schema_backed_editable",
            reason="Schema-backed field is editable after validation.",
        )
    if field_name in SCHEMA_BACKED_RESTRICTED_FIELDS:
        return _blocked(
            field_name,
            "schema_backed_restricted",
            "Field requires a controlled Add Feature command, not direct editing.",
        )
    return _blocked(field_name, "unsupported_field", "Field is not part of the edit policy.")


def is_field_editable(row: DataDefinitionDraftRow, field_name: str) -> bool:
    """Return a boolean editability decision."""
    return field_editability(row, field_name).editable


def _blocked(field_name: str, category: str, reason: str) -> FieldEditability:
    return FieldEditability(
        field_name=field_name,
        editable=False,
        category=category,
        reason=reason,
    )
