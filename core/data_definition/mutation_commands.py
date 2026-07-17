"""Atomic Rename, Duplicate, Remove, and active-state Feature commands."""

from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from core.data_definition.command_contract import normalize_column_key
from core.data_definition.command_types import DataDefinitionCommandResult
from core.data_definition.feature_command_types import (
    DuplicateDefinitionIntent,
    RemoveDefinitionIntent,
    SetDefinitionActiveIntent,
)
from core.data_definition.command_validation import validate_complete_row
from core.data_definition.dependency_policy import feature_dependencies
from core.data_definition.draft import DataDefinitionDraft, DataDefinitionDraftRow
from core.data_definition.mutation_support import (
    append_ml_identity,
    dependency_issue,
    find_row,
    issue,
    new_name_issues,
    next_display_order,
    reject,
    unsupported,
)


def apply_duplicate_definition_command(
    draft: DataDefinitionDraft,
    intent: DuplicateDefinitionIntent,
) -> DataDefinitionCommandResult:
    row = find_row(draft, intent.identity)
    unsupported_result = unsupported(draft, row, "Duplicate")
    if unsupported_result is not None:
        return unsupported_result
    assert row is not None
    column_key = normalize_column_key(intent.column_key)
    ml_name = intent.ml_name.strip()
    issues = list(new_name_issues(draft, intent.label.strip(), column_key, ml_name))
    if row.model_input_enabled and not ml_name:
        issues.append(issue(
            "duplicate_ml_name_required",
            "ml_name",
            "Duplicating an ML input requires an explicit new ML name.",
            "Enter a unique ML name for the duplicate.",
        ))
    duplicate = replace(
        row,
        stable_identity=f"ufm_feature_{uuid4().hex}",
        display_order=next_display_order(draft),
        column_key=column_key,
        label=intent.label.strip(),
        ml_name=ml_name if row.model_input_enabled else "",
        required=False,
        active=True,
        notes="",
    )
    issues.extend(validate_complete_row(duplicate))
    if issues:
        return DataDefinitionCommandResult(draft, False, row.identity, "Duplicate", tuple(issues))
    schema_rows = tuple(item for item in draft.rows if item.source_kind == "schema_row")
    other_rows = tuple(item for item in draft.rows if item.source_kind != "schema_row")
    updated = replace(
        draft,
        rows=(*schema_rows, duplicate, *other_rows),
        controlled_row_additions=frozenset((*draft.controlled_row_additions, duplicate.identity)),
        controlled_addition_initial_rows=(*draft.controlled_addition_initial_rows, duplicate),
        predict_order=(*draft.predict_order, duplicate.identity),
        ml_order=append_ml_identity(draft, duplicate),
    )
    return DataDefinitionCommandResult(updated, True, duplicate.identity, "Duplicate")


def apply_remove_definition_command(
    draft: DataDefinitionDraft,
    intent: RemoveDefinitionIntent,
) -> DataDefinitionCommandResult:
    row = find_row(draft, intent.identity)
    unsupported_result = unsupported(draft, row, "Remove")
    if unsupported_result is not None:
        return unsupported_result
    assert row is not None
    dependencies = feature_dependencies(draft, row)
    blockers = tuple(dependency_issue(item) for item in dependencies if item.blocks_remove)
    if blockers:
        return DataDefinitionCommandResult(draft, False, row.identity, "Remove", blockers)
    rows = tuple(item for item in draft.rows if item.identity != row.identity)
    was_added = draft.is_controlled_row_addition(row.identity)
    updated = replace(
        draft,
        rows=rows,
        controlled_row_additions=frozenset(
            item for item in draft.controlled_row_additions if item != row.identity
        ),
        controlled_addition_initial_rows=tuple(
            item for item in draft.controlled_addition_initial_rows
            if item.identity != row.identity
        ),
        controlled_row_removals=(
            draft.controlled_row_removals
            if was_added
            else frozenset((*draft.controlled_row_removals, row.identity))
        ),
        controlled_field_changes=frozenset(
            item for item in draft.controlled_field_changes if item[0] != row.identity
        ),
        predict_order=tuple(item for item in draft.predict_order if item != row.identity),
        ml_order=tuple(item for item in draft.ml_order if item != row.identity),
    )
    return DataDefinitionCommandResult(updated, True, None, "Remove", affected_identities=(row.identity,))


def apply_set_definition_active_command(
    draft: DataDefinitionDraft,
    intent: SetDefinitionActiveIntent,
) -> DataDefinitionCommandResult:
    action = "Enable" if intent.active else "Disable"
    row = find_row(draft, intent.identity)
    unsupported_result = unsupported(draft, row, action)
    if unsupported_result is not None:
        return unsupported_result
    assert row is not None
    if row.active == intent.active:
        return reject(
            draft,
            action,
            "active_state_unchanged",
            "active",
            f"Feature is already {'enabled' if intent.active else 'disabled'}.",
            "Choose the opposite state or leave the draft unchanged.",
            row.identity,
        )
    if not intent.active:
        blockers = tuple(
            dependency_issue(item)
            for item in feature_dependencies(draft, row)
            if item.blocks_disable
        )
        if blockers:
            return DataDefinitionCommandResult(draft, False, row.identity, action, blockers)
    ml_order = tuple(item for item in draft.ml_order if item != row.identity)
    if intent.active:
        ml_order = append_ml_identity(replace(draft, ml_order=ml_order), replace(row, active=True))
    updated = replace(
        draft,
        rows=tuple(
            replace(item, active=intent.active) if item.identity == row.identity else item
            for item in draft.rows
        ),
        ml_order=ml_order,
        controlled_field_changes=frozenset(
            (*draft.controlled_field_changes, (row.identity, "active"))
        ),
    )
    return DataDefinitionCommandResult(updated, True, row.identity, action)
