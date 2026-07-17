"""Editable field policy for Data Definition drafts."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.draft import DataDefinitionDraft, DataDefinitionDraftRow

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
        "one_hot_group",
        "notes",
    }
)
SCHEMA_BACKED_RESTRICTED_FIELDS = frozenset(
    {"display_order", "column_key", "ml_name", "role", "stable_identity", "active"}
)
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


@dataclass(frozen=True)
class RestrictedDraftFieldChange:
    """Non-editable field change detected in a draft diff."""

    row_identity: tuple[str, str]
    field_name: str
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
        if field_name in {"column_key", "ml_name"}:
            reason = "Predict key and ML name changes require the controlled Rename command."
        elif field_name == "active":
            reason = "Active-state changes require the controlled Enable or Disable command."
        else:
            reason = "Field requires a dedicated controlled Feature command, not direct editing."
        return _blocked(
            field_name,
            "schema_backed_restricted",
            reason,
        )
    return _blocked(field_name, "unsupported_field", "Field is not part of the edit policy.")


def is_field_editable(row: DataDefinitionDraftRow, field_name: str) -> bool:
    """Return a boolean editability decision."""
    return field_editability(row, field_name).editable


def restricted_draft_field_changes(
    draft: DataDefinitionDraft,
) -> tuple[RestrictedDraftFieldChange, ...]:
    """Return direct draft edits that violate the field edit policy."""
    changes: list[RestrictedDraftFieldChange] = []
    baseline_by_identity = {row.identity: row for row in draft.baseline_rows}
    for row in draft.rows:
        before = baseline_by_identity.get(row.identity)
        if before is not None:
            changes.extend(_restricted_field_changes(draft, before, row))
    if len(draft.rows) == len(draft.baseline_rows):
        for before, after in zip(draft.baseline_rows, draft.rows, strict=True):
            if before.identity != after.identity:
                changes.extend(_restricted_field_changes(draft, before, after))
    return _dedupe_restricted_changes(changes)


def _blocked(field_name: str, category: str, reason: str) -> FieldEditability:
    return FieldEditability(
        field_name=field_name,
        editable=False,
        category=category,
        reason=reason,
    )


def _restricted_field_changes(
    draft: DataDefinitionDraft,
    before: DataDefinitionDraftRow,
    after: DataDefinitionDraftRow,
) -> tuple[RestrictedDraftFieldChange, ...]:
    changes: list[RestrictedDraftFieldChange] = []
    for field_name in DataDefinitionDraftRow.__dataclass_fields__:
        if getattr(before, field_name) == getattr(after, field_name):
            continue
        if draft.is_controlled_field_change(before.identity, field_name):
            continue
        editability = field_editability(before, field_name)
        if not editability.editable:
            changes.append(
                RestrictedDraftFieldChange(
                    before.identity,
                    field_name,
                    editability.reason,
                )
            )
    return tuple(changes)


def _dedupe_restricted_changes(
    changes: list[RestrictedDraftFieldChange],
) -> tuple[RestrictedDraftFieldChange, ...]:
    seen: set[tuple[tuple[str, str], str, str]] = set()
    unique: list[RestrictedDraftFieldChange] = []
    for change in changes:
        key = (change.row_identity, change.field_name, change.reason)
        if key in seen:
            continue
        seen.add(key)
        unique.append(change)
    return tuple(unique)
