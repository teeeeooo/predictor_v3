"""Atomic Result Feature and Target lifecycle commands."""

from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from core.data_definition.command_types import DataDefinitionCommandIssue, DataDefinitionCommandResult
from core.data_definition.contract.candidate import candidate_manifest_from_draft
from core.data_definition.contract.model import TargetDefinition
from core.data_definition.contract.validation import validate_contract
from core.data_definition.draft import DataDefinitionDraft, DataDefinitionDraftRow
from core.data_definition.mutation_support import new_name_issues
from core.data_definition.target_registry.intents import (
    AddTargetIntent, ChangeTargetModelGroupIntent, ChangeTargetPolicyIntent,
    DuplicateTargetIntent, EditTargetIntent, MoveTargetIntent, RemoveTargetIntent,
    RenameTargetIntent, SetTargetActiveIntent, TargetCommandIntent,
)


def apply_target_command(draft: DataDefinitionDraft, intent: TargetCommandIntent) -> DataDefinitionCommandResult:
    if isinstance(intent, AddTargetIntent):
        return _add(draft, intent)
    target = next((item for item in draft.targets if item.identity == intent.identity), None)
    if target is None:
        return _reject(draft, "Target", "target_not_found", "Target was not found.")
    row = next((item for item in draft.rows if item.stable_identity == target.feature_identity), None)
    if row is None:
        return _reject(draft, "Target", "target_result_missing", "Target Result Feature is missing.")

    if isinstance(intent, EditTargetIntent):
        return _replace_pair(draft, target, replace(target), row, replace(
            row, label=intent.label.strip(), visible=bool(intent.visible)
        ), "Edit")
    if isinstance(intent, RenameTargetIntent):
        issues = new_name_issues(
            draft, intent.label.strip(), intent.column_key.strip(), intent.ml_name.strip(),
            exclude=row.identity,
        )
        if issues:
            return DataDefinitionCommandResult(draft, False, row.identity, "Rename", issues)
        return _replace_pair(
            draft, target, replace(target, ml_name=intent.ml_name.strip()), row,
            replace(row, label=intent.label.strip(), column_key=intent.column_key.strip(), ml_name=intent.ml_name.strip()),
            "Rename",
        )
    if isinstance(intent, DuplicateTargetIntent):
        return _duplicate(draft, target, intent)
    if isinstance(intent, RemoveTargetIntent):
        was_added = draft.is_controlled_row_addition(row.identity)
        candidate = replace(
            draft,
            rows=tuple(item for item in draft.rows if item.identity != row.identity),
            targets=_normalized_targets(
                replace(
                    item,
                    legacy_noop_result_identities=tuple(
                        identity for identity in item.legacy_noop_result_identities
                        if identity != target.feature_identity
                    ),
                )
                for item in draft.targets if item.identity != target.identity
            ),
            predict_order=tuple(item for item in draft.predict_order if item != row.identity),
            ml_order=tuple(item for item in draft.ml_order if item != row.identity),
            controlled_row_additions=frozenset(item for item in draft.controlled_row_additions if item != row.identity),
            controlled_addition_initial_rows=tuple(item for item in draft.controlled_addition_initial_rows if item.identity != row.identity),
            controlled_row_removals=(draft.controlled_row_removals if was_added else frozenset((*draft.controlled_row_removals, row.identity))),
        )
        return _validated(draft, candidate, row.identity, "Remove")
    if isinstance(intent, SetTargetActiveIntent):
        if target.active == intent.active:
            return _reject(draft, "Enable" if intent.active else "Disable", "target_active_state_unchanged", "Target active state is unchanged.")
        changed_row = replace(row, active=intent.active)
        changed_target = replace(target, active=intent.active)
        return _replace_pair(draft, target, changed_target, row, changed_row, "Enable" if intent.active else "Disable")
    if isinstance(intent, MoveTargetIntent):
        return _move(draft, target, intent.direction)
    if isinstance(intent, ChangeTargetModelGroupIntent):
        registry_order = 1 + max(
            (item.registry_order for item in draft.targets
             if item.model_group_identity == intent.model_group_identity),
            default=0,
        )
        return _replace_pair(draft, target, replace(
            target,
            model_group_identity=intent.model_group_identity,
            registry_order=registry_order,
        ), row, row, "Change Model Group")
    if isinstance(intent, ChangeTargetPolicyIntent):
        return _replace_pair(draft, target, replace(
            target,
            policy_mode=intent.mode.strip(),
            policy_owner_identities=tuple(intent.owner_identities),
            legacy_noop_result_identities=(),
        ), row, row, "Change Target Policy")
    raise TypeError(f"Unsupported Target command: {type(intent).__name__}")


def _add(draft: DataDefinitionDraft, intent: AddTargetIntent) -> DataDefinitionCommandResult:
    issues = new_name_issues(draft, intent.label.strip(), intent.column_key.strip(), intent.ml_name.strip())
    if issues:
        return DataDefinitionCommandResult(draft, False, None, "Add", issues)
    feature_identity = f"ufm_feature_{uuid4().hex}"
    target_identity = f"ufm_target_{uuid4().hex}"
    display_order = (max((item.display_order for item in draft.rows if item.source_kind == "schema_row"), default=0) // 10 + 1) * 10
    row = DataDefinitionDraftRow(
        source_kind="schema_row", stable_identity=feature_identity,
        display_order=display_order, column_key=intent.column_key.strip(), label=intent.label.strip(),
        role="result", editor="readonly", data_type="number", visible=bool(intent.visible),
        readonly=True, value_source="result", ml_name=intent.ml_name.strip(), active=False,
        notes="Canonical ML Target result column.",
    )
    target = TargetDefinition(
        identity=target_identity, feature_identity=feature_identity, ml_name=row.ml_name,
        model_group_identity=intent.model_group_identity,
        presentation_order=len(draft.targets) + 1,
        policy_mode=intent.policy_mode.strip(),
        policy_owner_identities=tuple(intent.policy_owner_identities), active=False,
        registry_order=1 + max(
            (item.registry_order for item in draft.targets if item.model_group_identity == intent.model_group_identity),
            default=0,
        ),
    )
    candidate = replace(
        draft, rows=(*draft.rows, row), targets=(*draft.targets, target),
        predict_order=(*draft.predict_order, row.identity),
        controlled_row_additions=frozenset((*draft.controlled_row_additions, row.identity)),
        controlled_addition_initial_rows=(*draft.controlled_addition_initial_rows, row),
    )
    return _validated(draft, candidate, row.identity, "Add")


def _duplicate(draft, source, intent):  # noqa: ANN001
    row = next(item for item in draft.rows if item.stable_identity == source.feature_identity)
    add = AddTargetIntent(
        label=intent.label, column_key=intent.column_key, ml_name=intent.ml_name,
        model_group_identity=source.model_group_identity, policy_mode=source.policy_mode,
        policy_owner_identities=source.policy_owner_identities, visible=row.visible,
    )
    result = _add(draft, add)
    if not result.accepted or not source.legacy_noop_result_identities:
        return result
    duplicated = result.draft.targets[-1]
    candidate = replace(
        result.draft,
        targets=(*result.draft.targets[:-1], replace(
            duplicated,
            legacy_noop_result_identities=source.legacy_noop_result_identities,
        )),
    )
    return _validated(draft, candidate, result.identity, "Duplicate")


def _move(draft, target, direction):  # noqa: ANN001
    ordered = list(draft.targets)
    index = ordered.index(target)
    offset = -1 if direction == "up" else 1 if direction == "down" else 0
    destination = index + offset
    if offset == 0 or destination < 0 or destination >= len(ordered):
        return _reject(draft, "Move", "target_move_unavailable", "Target cannot move in that direction.")
    ordered[index], ordered[destination] = ordered[destination], ordered[index]
    candidate = replace(draft, targets=_normalized_targets(ordered))
    return _validated(draft, candidate, ("target", target.identity), "Move Up" if offset < 0 else "Move Down")


def _replace_pair(draft, before_target, after_target, before_row, after_row, action):  # noqa: ANN001
    ml_order = draft.ml_order
    if before_row.active and not after_row.active:
        ml_order = tuple(item for item in ml_order if item != before_row.identity)
    elif not before_row.active and after_row.active:
        ml_order = (*ml_order, after_row.identity)
    changed_fields = tuple(
        field for field in DataDefinitionDraftRow.__dataclass_fields__
        if getattr(before_row, field) != getattr(after_row, field)
    )
    candidate = replace(
        draft,
        rows=tuple(after_row if item.identity == before_row.identity else item for item in draft.rows),
        targets=_normalized_targets(
            after_target if item.identity == before_target.identity else item
            for item in draft.targets
        ),
        ml_order=ml_order,
        controlled_field_changes=frozenset((
            *draft.controlled_field_changes,
            *((before_row.identity, field) for field in changed_fields),
        )),
    )
    return _validated(draft, candidate, before_row.identity, action)


def _normalized_targets(targets) -> tuple[TargetDefinition, ...]:  # noqa: ANN001
    presented = tuple(replace(item, presentation_order=index) for index, item in enumerate(targets, 1))
    registry_order = {
        item.identity: index
        for group_identity in {item.model_group_identity for item in presented}
        for index, item in enumerate(sorted(
            (target for target in presented if target.model_group_identity == group_identity),
            key=lambda target: (target.registry_order, target.identity),
        ), 1)
    }
    return tuple(replace(item, registry_order=registry_order[item.identity]) for item in presented)


def _validated(original, candidate, identity, action):  # noqa: ANN001
    if candidate.base_manifest is None:
        return _reject(original, action, "target_canonical_manifest_required", "Target authoring requires a canonical generation draft.")
    try:
        manifest = candidate_manifest_from_draft(candidate, candidate.base_manifest)
        issues = validate_contract(manifest)
    except (KeyError, TypeError, ValueError) as exc:
        return _reject(original, action, "target_candidate_invalid", str(exc))
    if issues:
        first = issues[0]
        return _reject(original, action, first.code, first.message)
    return DataDefinitionCommandResult(candidate, True, identity, action)


def _reject(draft, action, code, message):  # noqa: ANN001
    return DataDefinitionCommandResult(
        draft, False, None, action,
        (DataDefinitionCommandIssue(code, "target", message, "Refresh the draft and choose valid Target inputs."),),
    )
