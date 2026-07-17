"""Atomic stable-identity Rename command for Basic Features."""

from __future__ import annotations

from dataclasses import replace

from core.data_definition.command_contract import normalize_column_key
from core.data_definition.command_types import DataDefinitionCommandResult
from core.data_definition.feature_command_types import RenameDefinitionIntent
from core.data_definition.command_validation import validate_complete_row
from core.data_definition.dependency_policy import feature_dependencies
from core.data_definition.draft import DataDefinitionDraft
from core.data_definition.mutation_support import (
    dependency_issue,
    find_row,
    new_name_issues,
    reject,
    unsupported,
)


def apply_rename_definition_command(
    draft: DataDefinitionDraft,
    intent: RenameDefinitionIntent,
) -> DataDefinitionCommandResult:
    row = find_row(draft, intent.identity)
    unsupported_result = unsupported(draft, row, "Rename")
    if unsupported_result is not None:
        return unsupported_result
    assert row is not None
    updates: dict[str, object] = {}
    if intent.column_key is not None:
        updates["column_key"] = normalize_column_key(intent.column_key)
    if intent.ml_name is not None:
        updates["ml_name"] = intent.ml_name.strip()
    if intent.label is not None:
        updates["label"] = intent.label.strip()
    identifier_changes = {
        field for field in ("column_key", "ml_name")
        if field in updates and updates[field] != getattr(row, field)
    }
    if not identifier_changes:
        return reject(
            draft, "Rename", "rename_identifier_required", "column_key",
            "Rename requires at least one changed Predict key or ML name.",
            "Use Edit for a label-only change.", row.identity,
        )
    issues = list(new_name_issues(
        draft,
        str(updates.get("label", row.label)),
        str(updates.get("column_key", row.column_key)),
        str(updates.get("ml_name", row.ml_name)),
        exclude=row.identity,
    ))
    issues.extend(_dependency_issues(feature_dependencies(draft, row), identifier_changes))
    candidate_row = replace(row, **updates)
    issues.extend(validate_complete_row(candidate_row))
    if issues:
        return DataDefinitionCommandResult(draft, False, row.identity, "Rename", tuple(issues))
    rows = []
    affected = [row.identity]
    old_key = row.column_key
    new_key = str(updates.get("column_key", old_key))
    authorized = {(row.identity, field) for field in updates}
    for item in draft.rows:
        if item.identity == row.identity:
            rows.append(candidate_row)
        elif old_key != new_key and item.trigger_column == old_key:
            rows.append(replace(item, trigger_column=new_key))
            affected.append(item.identity)
            authorized.add((item.identity, "trigger_column"))
        else:
            rows.append(item)
    updated = replace(
        draft,
        rows=tuple(rows),
        controlled_field_changes=frozenset((*draft.controlled_field_changes, *authorized)),
    )
    return DataDefinitionCommandResult(
        updated, True, row.identity, "Rename", affected_identities=tuple(affected)
    )


def _dependency_issues(dependencies, changed_fields):  # noqa: ANN001
    ml_codes = {
        "derived_expression_reference", "one_hot_emitted_reference",
        "target_feature_reference", "ordered_ml_projection", "model_group_target_rule",
    }
    return tuple(
        dependency_issue(item)
        for item in dependencies
        if item.blocks_rename and (
            ("ml_name" in changed_fields and item.code in ml_codes)
            or ("column_key" in changed_fields and item.code == "protected_predict_consumer")
        )
    )
