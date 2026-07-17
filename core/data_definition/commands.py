"""Atomic controlled commands for Data Definition Add/Edit intent."""

from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from core.data_definition.draft import (
    DataDefinitionDraft,
    DataDefinitionDraftRow,
    replace_draft_row,
)
from core.data_definition.edit_policy import field_editability
from core.data_definition.command_contract import (
    mapping_template_for_relation,
    normalize_column_key,
)
from core.data_definition.command_types import (
    AddDefinitionIntent,
    DataDefinitionCommandIssue,
    DataDefinitionCommandResult,
    EditDefinitionIntent,
)
from core.data_definition.command_validation import (
    coerce_edit_field,
    validate_complete_row,
)


def apply_add_definition_command(
    draft: DataDefinitionDraft,
    intent: AddDefinitionIntent,
) -> DataDefinitionCommandResult:
    """Validate all Add intent, then append one complete authorized row."""
    row, issues = _row_from_add_intent(draft, intent)
    if issues or row is None:
        return DataDefinitionCommandResult(draft, False, None, "Add", issues)
    schema_rows = tuple(item for item in draft.rows if item.source_kind == "schema_row")
    other_rows = tuple(item for item in draft.rows if item.source_kind != "schema_row")
    updated = replace(
        draft,
        rows=(*schema_rows, row, *other_rows),
        controlled_row_additions=frozenset(
            (*draft.controlled_row_additions, row.identity)
        ),
        controlled_addition_initial_rows=(
            *draft.controlled_addition_initial_rows,
            row,
        ),
        predict_order=(*draft.predict_order, row.identity),
        ml_order=_append_ml_identity(draft, row),
    )
    return DataDefinitionCommandResult(updated, True, row.identity, "Add")


def apply_edit_definition_command(
    draft: DataDefinitionDraft,
    intent: EditDefinitionIntent,
) -> DataDefinitionCommandResult:
    """Validate a complete Edit intent before applying any field."""
    resolved_identity = draft.resolve_identity(intent.identity)
    row = next((item for item in draft.rows if item.identity == resolved_identity), None)
    if row is None:
        return _rejected(draft, "Edit", "definition_not_found", "identity", "Definition not found.")
    updates, issues = _validated_edit_updates(row, intent.updates)
    if issues:
        return DataDefinitionCommandResult(draft, False, resolved_identity, "Edit", issues)
    updates, transition_issues = _normalize_source_transition(row, updates)
    if transition_issues:
        return DataDefinitionCommandResult(
            draft,
            False,
            resolved_identity,
            "Edit",
            transition_issues,
        )
    candidate = _row_with_updates(row, updates)
    issues = validate_complete_row(candidate)
    if issues:
        return DataDefinitionCommandResult(draft, False, resolved_identity, "Edit", issues)
    updated = replace_draft_row(draft, resolved_identity, **updates)
    return DataDefinitionCommandResult(updated, True, resolved_identity, "Edit")


def _row_from_add_intent(
    draft: DataDefinitionDraft,
    intent: AddDefinitionIntent,
) -> tuple[DataDefinitionDraftRow | None, tuple[DataDefinitionCommandIssue, ...]]:
    label = intent.label.strip()
    column_key = normalize_column_key(intent.column_key)
    data_type = intent.data_type.strip()
    issues: list[DataDefinitionCommandIssue] = []
    if not label:
        issues.append(_issue("label_required", "label", "Label is required."))
    if not column_key or not column_key[0].isalpha():
        issues.append(_issue(
            "column_key_invalid",
            "column_key",
            "Internal key must normalize to snake_case and start with a letter.",
        ))
    existing_keys = {row.column_key for row in draft.rows if row.column_key}
    if column_key and column_key in existing_keys:
        issues.append(_issue(
            "column_key_duplicate",
            "column_key",
            f"Internal key '{column_key}' already exists in the current draft or baseline.",
        ))
    if data_type not in {"string", "number"}:
        issues.append(_issue(
            "data_type_unsupported",
            "data_type",
            "Add supports current string or number schema types.",
        ))
    supported_kinds = {
        "manual_predict", "mapping_predict", "mapping_attribute",
        "predict_only", "ml_only", "mapping_backed", "helper_hidden",
    }
    if intent.kind not in supported_kinds:
        issues.append(_issue("intent_unsupported", "kind", "Unsupported definition intent."))
    relation = None
    mapping = intent.kind in {"mapping_predict", "mapping_attribute", "mapping_backed"}
    if mapping:
        if not intent.mapping_attribute.strip():
            issues.append(_issue(
                "mapping_attribute_required",
                "mapping_attribute",
                "Mapping attribute is required.",
            ))
        relation = mapping_template_for_relation(
            intent.mapping_entity,
            intent.trigger_column,
            intent.rule_id,
        )
        if relation is None:
            issues.append(_issue(
                "mapping_template_unsupported",
                "mapping_entity",
                "The selected mapping entity, trigger, and rule are not a supported current template.",
            ))
    elif any(
        value.strip()
        for value in (
            intent.mapping_entity,
            intent.mapping_attribute,
            intent.trigger_column,
            intent.rule_id,
        )
    ):
        issues.append(_issue(
            "mapping_metadata_not_allowed",
            "mapping_entity",
            "Manual Predict Input cannot include mapping metadata or values.",
        ))
    if issues:
        return None, tuple(issues)
    ml_name = intent.ml_name.strip()
    model_input_enabled = bool(intent.model_input_enabled or intent.kind == "ml_only")
    if model_input_enabled and not ml_name:
        issues.append(_issue(
            "ml_name_required",
            "ml_name",
            "ML input intent requires an explicit ML name.",
        ))
    if ml_name and any(item.ml_name == ml_name for item in draft.rows):
        issues.append(_issue(
            "ml_name_duplicate",
            "ml_name",
            f"ML name '{ml_name}' already exists in the current draft.",
        ))
    if issues:
        return None, tuple(issues)
    helper = intent.kind in {"mapping_attribute", "helper_hidden"}
    predict_visible = False if helper or intent.kind == "ml_only" else bool(intent.visible)
    role = "helper" if mapping and helper else "auto" if mapping else "hidden" if helper else "input"
    readonly = mapping or helper
    row = DataDefinitionDraftRow(
        source_kind="schema_row",
        stable_identity=f"ufm_feature_{uuid4().hex}",
        display_order=_next_display_order(draft),
        column_key=column_key,
        label=label,
        role=role,
        editor="readonly" if readonly else ("number" if data_type == "number" else "text"),
        data_type=data_type,
        visible=predict_visible,
        required=bool(intent.required),
        readonly=readonly,
        value_source="mapping_lookup" if mapping else "manual",
        mapping_entity=relation.mapping_entity if relation else "",
        mapping_attribute=intent.mapping_attribute.strip() if mapping else "",
        trigger_column=relation.trigger_column if relation else "",
        rule_id=relation.rule_id if relation else "",
        model_input_enabled=model_input_enabled,
        ml_name=ml_name,
        one_hot_group="",
        active=bool(intent.active),
        notes=intent.notes.strip(),
    )
    return row, validate_complete_row(row)


def _validated_edit_updates(
    row: DataDefinitionDraftRow,
    update_pairs: tuple[tuple[str, object], ...],
) -> tuple[dict[str, object], tuple[DataDefinitionCommandIssue, ...]]:
    updates: dict[str, object] = {}
    issues: list[DataDefinitionCommandIssue] = []
    for field_name, value in update_pairs:
        if field_name in updates:
            issues.append(_issue(
                "duplicate_edit_field", field_name, f"Edit field '{field_name}' was provided twice."
            ))
            continue
        decision = field_editability(row, field_name)
        if not decision.editable:
            issues.append(_issue("restricted_edit", field_name, decision.reason))
            continue
        coerced, error = coerce_edit_field(field_name, value)
        if error:
            issues.append(_issue("field_value_invalid", field_name, error))
            continue
        updates[field_name] = coerced
    if not update_pairs:
        issues.append(_issue("edit_empty", "", "At least one editable field is required."))
    return updates, tuple(issues)


def _row_with_updates(
    row: DataDefinitionDraftRow,
    updates: dict[str, object],
) -> DataDefinitionDraftRow:
    values = {
        field_name: getattr(row, field_name)
        for field_name in DataDefinitionDraftRow.__dataclass_fields__
    }
    values.update(updates)
    return DataDefinitionDraftRow(**values)


def _normalize_source_transition(
    row: DataDefinitionDraftRow,
    updates: dict[str, object],
) -> tuple[dict[str, object], tuple[DataDefinitionCommandIssue, ...]]:
    """Apply complete source-owned metadata transitions to the candidate only."""
    before = row.value_source
    after = str(updates.get("value_source", before))
    if before == after:
        return updates, ()
    normalized = dict(updates)
    mapping_fields = {
        "mapping_entity",
        "mapping_attribute",
        "trigger_column",
        "rule_id",
    }
    if after == "mapping_lookup" and not mapping_fields.issubset(updates):
        return updates, (_issue(
            "mapping_transition_incomplete",
            "value_source",
            "Changing to Mapping Lookup requires one complete supported mapping relation.",
        ),)
    if before in {"mapping_lookup", "rule_options", "one_hot"} and after not in {
        "mapping_lookup",
        "rule_options",
        "one_hot",
    }:
        normalized.update({field_name: "" for field_name in mapping_fields})
    if before == "one_hot" and after != "one_hot":
        normalized["one_hot_group"] = ""
    return normalized, ()


def _next_display_order(draft: DataDefinitionDraft) -> int:
    existing = [
        row.display_order
        for row in draft.rows
        if row.source_kind == "schema_row"
    ]
    return (max(existing, default=0) // 10 + 1) * 10


def _append_ml_identity(
    draft: DataDefinitionDraft,
    row: DataDefinitionDraftRow,
) -> tuple[tuple[str, str], ...]:
    if not row.active or not row.ml_name or not row.model_input_enabled:
        return draft.ml_order
    first_derived = next(
        (index for index, identity in enumerate(draft.ml_order) if identity[0] == "derived_policy"),
        len(draft.ml_order),
    )
    return (*draft.ml_order[:first_derived], row.identity, *draft.ml_order[first_derived:])


def _issue(code: str, field_name: str, message: str) -> DataDefinitionCommandIssue:
    return DataDefinitionCommandIssue(code, field_name, message)


def _rejected(
    draft: DataDefinitionDraft,
    action: str,
    code: str,
    field_name: str,
    message: str,
) -> DataDefinitionCommandResult:
    return DataDefinitionCommandResult(
        draft, False, None, action, (_issue(code, field_name, message),)
    )
