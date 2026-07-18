"""Atomic One-hot group command transitions."""

from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from core.data_definition.command_contract import normalize_column_key
from core.data_definition.command_types import DataDefinitionCommandResult
from core.data_definition.contract.model import OneHotCategoryDefinition, OneHotGroupDefinition
from core.data_definition.draft import DataDefinitionDraft
from core.data_definition.one_hot.command_support import (
    MISSING_POLICIES,
    SOURCE_MODES,
    UNKNOWN_POLICIES,
    add_emitted_row,
    detached_selector_row,
    find_group,
    find_row_by_stable_id,
    group_identity,
    issue,
    rebuild_group_ml_order,
    reject,
    remove_row,
    replace_group,
    replace_row,
    selector_row,
    validate_transition,
    vocabulary_issue,
)
from core.data_definition.one_hot.intents import (
    AddOneHotGroupIntent,
    AssignOneHotSelectorIntent,
    ChangeOneHotSourceModeIntent,
    DuplicateOneHotGroupIntent,
    EditOneHotGroupIntent,
    RemoveOneHotGroupIntent,
    RenameOneHotGroupIntent,
    SetOneHotGroupActiveIntent,
)
from core.data_definition.one_hot.model import VocabularySnapshot, vocabulary_snapshot_for
from core.data_definition.one_hot.group_policy import (
    available_selector as _available_selector,
    dependency_blockers as _dependency_blockers,
    group_values_issue as _group_values_issue,
    source_available as _source_available,
)


def apply_group_command(
    draft: DataDefinitionDraft,
    intent: object,
    snapshots: tuple[VocabularySnapshot, ...] = (),
) -> DataDefinitionCommandResult:
    if isinstance(intent, AddOneHotGroupIntent):
        return _add(draft, intent, snapshots)
    identity = getattr(intent, "group_identity", "")
    group = find_group(draft, identity)
    action = _action(intent)
    if group is None:
        return reject(draft, action, issue(
            "one_hot_group_not_found", "identity", "One-hot group was not found.",
            "Refresh and select the group again.",
        ), group_identity(identity))
    if isinstance(intent, EditOneHotGroupIntent):
        return _edit(draft, group, intent)
    if isinstance(intent, RenameOneHotGroupIntent):
        return _rename(draft, group, intent)
    if isinstance(intent, DuplicateOneHotGroupIntent):
        return _duplicate(draft, group, intent, snapshots)
    if isinstance(intent, RemoveOneHotGroupIntent):
        return _remove(draft, group, intent)
    if isinstance(intent, SetOneHotGroupActiveIntent):
        return _set_active(draft, group, intent, snapshots)
    if isinstance(intent, ChangeOneHotSourceModeIntent):
        return _change_source(draft, group, intent, snapshots)
    if isinstance(intent, AssignOneHotSelectorIntent):
        return _assign_selector(draft, group, intent)
    raise TypeError(f"Unsupported One-hot group command: {type(intent).__name__}")


def _add(draft, intent, snapshots):  # noqa: ANN001
    action = "Add One-hot group"
    key = normalize_column_key(intent.group_key)
    problem = _group_values_issue(draft, key, intent.source_mode, intent.source_binding,
                                  intent.unknown_policy, intent.missing_policy)
    if problem:
        return reject(draft, action, problem)
    if intent.active:
        return reject(draft, action, issue(
            "one_hot_group_add_must_be_inactive", "active",
            "A new One-hot group must start inactive.",
        ))
    selector, problem = _available_selector(draft, intent.selector_feature_identity)
    if problem:
        return reject(draft, action, problem)
    source_problem = _source_available(intent.source_mode, intent.source_binding, snapshots)
    if source_problem:
        return reject(draft, action, source_problem)
    group = OneHotGroupDefinition(
        identity=f"ufm_onehot_group_{uuid4().hex}",
        group_key=key,
        selector_feature_identity=selector.stable_identity,
        category_source=intent.source_mode,
        source_binding=intent.source_binding.strip(),
        unknown_policy=intent.unknown_policy.strip(),
        missing_policy=intent.missing_policy.strip(),
        categories=(),
        active=False,
    )
    candidate = replace(draft, one_hot_groups=(*draft.one_hot_groups, group))
    candidate = replace_row(candidate, selector, selector_row(selector, group))
    return validate_transition(draft, candidate, action, group_identity(group.identity))


def _edit(draft, group, intent):  # noqa: ANN001
    if intent.source_binding is not None and intent.source_binding.strip() != group.source_binding:
        return reject(draft, "Edit One-hot group", issue(
            "one_hot_source_change_requires_command", "source_binding",
            "Source binding changes require Change Source Mode Preview.",
        ), group_identity(group.identity))
    if intent.unknown_policy not in UNKNOWN_POLICIES or intent.missing_policy not in MISSING_POLICIES:
        return reject(draft, "Edit One-hot group", issue(
            "one_hot_policy_invalid", "policy", "Select supported unknown and missing policies.",
        ), group_identity(group.identity))
    updated = replace(group, unknown_policy=intent.unknown_policy,
                      missing_policy=intent.missing_policy)
    return validate_transition(
        draft, replace_group(draft, group, updated), "Edit One-hot group",
        group_identity(group.identity),
    )


def _rename(draft, group, intent):  # noqa: ANN001
    key = normalize_column_key(intent.group_key)
    if not key or any(item.group_key == key and item.identity != group.identity
                      for item in draft.one_hot_groups):
        return reject(draft, "Rename One-hot group", issue(
            "one_hot_group_key_duplicate", "group_key", "Enter a unique group key.",
        ), group_identity(group.identity))
    updated = replace(group, group_key=key)
    candidate = replace_group(draft, group, updated)
    related = {group.selector_feature_identity, *(
        item.emitted_feature_identity for item in group.categories
    )}
    for stable_id in related:
        row = find_row_by_stable_id(candidate, stable_id)
        if row is not None:
            candidate = replace_row(candidate, row, replace(row, one_hot_group=key))
    return validate_transition(
        draft, candidate, "Rename One-hot group", group_identity(group.identity)
    )


def _duplicate(draft, group, intent, snapshots):  # noqa: ANN001
    key = normalize_column_key(intent.group_key)
    problem = _group_values_issue(
        draft, key, group.category_source, group.source_binding,
        group.unknown_policy, group.missing_policy,
    )
    if problem:
        return reject(draft, "Duplicate One-hot group", problem, group_identity(group.identity))
    selector, problem = _available_selector(draft, intent.selector_feature_identity)
    if problem:
        return reject(draft, "Duplicate One-hot group", problem, group_identity(group.identity))
    source_problem = _source_available(group.category_source, group.source_binding, snapshots)
    if source_problem:
        return reject(draft, "Duplicate One-hot group", source_problem, group_identity(group.identity))
    duplicate = replace(
        group,
        identity=f"ufm_onehot_group_{uuid4().hex}",
        group_key=key,
        selector_feature_identity=selector.stable_identity,
        categories=(),
        active=False,
    )
    candidate = replace(draft, one_hot_groups=(*draft.one_hot_groups, duplicate))
    candidate = replace_row(candidate, selector, selector_row(selector, duplicate))
    categories = []
    for original in group.categories:
        candidate, row = add_emitted_row(
            candidate, duplicate, original.emitted_ml_name + intent.emitted_name_suffix
        )
        categories.append(OneHotCategoryDefinition(
            identity=f"ufm_onehot_category_{uuid4().hex}",
            source_value=original.source_value,
            emitted_feature_identity=row.stable_identity,
            emitted_ml_name=row.ml_name,
            order=original.order,
            active=False,
            provider_category_identity=original.provider_category_identity,
        ))
    duplicate = replace(duplicate, categories=tuple(categories))
    current = find_group(candidate, duplicate.identity)
    candidate = replace_group(candidate, current, duplicate)
    return validate_transition(
        draft, candidate, "Duplicate One-hot group", group_identity(duplicate.identity)
    )


def _remove(draft, group, intent):  # noqa: ANN001
    action = "Remove One-hot group"
    if intent.selector_disposition == "block":
        return reject(draft, action, issue(
            "one_hot_selector_disposition_required", "selector_disposition",
            "Choose whether to detach or remove the selector.",
        ), group_identity(group.identity))
    candidate = draft
    for category in group.categories:
        row = find_row_by_stable_id(candidate, category.emitted_feature_identity)
        blockers = _dependency_blockers(candidate, row, "Remove")
        if blockers:
            return reject(draft, action, blockers[0], group_identity(group.identity))
        candidate = remove_row(candidate, row)
    selector = find_row_by_stable_id(candidate, group.selector_feature_identity)
    if intent.selector_disposition == "remove":
        blockers = _dependency_blockers(candidate, selector, "Remove")
        if blockers:
            return reject(draft, action, blockers[0], group_identity(group.identity))
        candidate = remove_row(candidate, selector)
    else:
        candidate = replace_row(candidate, selector, detached_selector_row(selector))
    candidate = replace(
        candidate,
        one_hot_groups=tuple(item for item in candidate.one_hot_groups
                             if item.identity != group.identity),
    )
    return validate_transition(
        draft, candidate, action, None, (group_identity(group.identity),)
    )


def _set_active(draft, group, intent, snapshots):  # noqa: ANN001
    action = "Enable One-hot group" if intent.active else "Disable One-hot group"
    if group.active == intent.active:
        return reject(draft, action, issue(
            "one_hot_group_active_unchanged", "active", "Group active state is unchanged."
        ), group_identity(group.identity))
    if intent.active and not any(item.active for item in group.categories):
        return reject(draft, action, issue(
            "one_hot_active_category_required", "categories",
            "Enable at least one category before enabling the group.",
        ), group_identity(group.identity))
    if intent.active and group.category_source == "external":
        for category in group.categories:
            if category.active and (problem := vocabulary_issue(
                group, category.source_value, category.provider_category_identity, snapshots
            )):
                return reject(draft, action, problem, group_identity(group.identity))
    updated = replace(group, active=intent.active)
    candidate = replace_group(draft, group, updated)
    selector = find_row_by_stable_id(candidate, group.selector_feature_identity)
    candidate = replace_row(candidate, selector, replace(selector, active=intent.active))
    for category in updated.categories:
        row = find_row_by_stable_id(candidate, category.emitted_feature_identity)
        candidate = replace_row(
            candidate, row, replace(row, active=intent.active and category.active)
        )
    candidate = rebuild_group_ml_order(candidate, updated)
    return validate_transition(draft, candidate, action, group_identity(group.identity))


def _change_source(draft, group, intent, snapshots):  # noqa: ANN001
    action = "Change One-hot source mode"
    if intent.source_mode not in SOURCE_MODES:
        return reject(draft, action, issue(
            "one_hot_category_source_invalid", "source_mode", "Select a supported source mode."
        ), group_identity(group.identity))
    problem = _source_available(intent.source_mode, intent.source_binding, snapshots)
    if problem:
        return reject(draft, action, problem, group_identity(group.identity))
    categories = list(group.categories)
    if intent.source_mode == "external":
        snapshot = vocabulary_snapshot_for(snapshots, "external", intent.source_binding.strip())
        provider_map = dict(intent.provider_categories)
        if set(provider_map) != {item.identity for item in categories}:
            return reject(draft, action, issue(
                "one_hot_external_overlay_incomplete", "provider_categories",
                "Map every preserved category identity to one provider category.",
            ), group_identity(group.identity))
        categories = [
            replace(
                item,
                provider_category_identity=provider_map[item.identity],
                source_value=snapshot.category_by_identity(provider_map[item.identity]).value,
            )
            for item in categories
        ]
    else:
        categories = [replace(item, provider_category_identity="") for item in categories]
        if intent.source_mode == "mapping_backed":
            snapshot = vocabulary_snapshot_for(
                snapshots, "mapping_backed", intent.source_binding.strip()
            )
            if any(snapshot.category_by_value(item.source_value) is None for item in categories):
                return reject(draft, action, issue(
                    "one_hot_source_mode_rule_unresolved", "source_value",
                    "Every preserved category rule must match the persisted Mapping vocabulary.",
                ), group_identity(group.identity))
    updated = replace(
        group,
        category_source=intent.source_mode,
        source_binding=intent.source_binding.strip(),
        categories=tuple(categories),
    )
    candidate = replace_group(draft, group, updated)
    selector = find_row_by_stable_id(candidate, group.selector_feature_identity)
    candidate = replace_row(candidate, selector, selector_row(selector, updated))
    return validate_transition(draft, candidate, action, group_identity(group.identity))


def _assign_selector(draft, group, intent):  # noqa: ANN001
    action = "Assign One-hot selector"
    new_selector, problem = _available_selector(
        draft, intent.selector_feature_identity, excluding_group=group.identity
    )
    if problem:
        return reject(draft, action, problem, group_identity(group.identity))
    old_selector = find_row_by_stable_id(draft, group.selector_feature_identity)
    candidate = draft
    if intent.previous_selector_disposition == "block":
        return reject(draft, action, issue(
            "one_hot_selector_disposition_required", "previous_selector_disposition",
            "Choose detach or remove for the previous selector.",
        ), group_identity(group.identity))
    if intent.previous_selector_disposition == "remove":
        blockers = _dependency_blockers(candidate, old_selector, "Remove")
        if blockers:
            return reject(draft, action, blockers[0], group_identity(group.identity))
        candidate = remove_row(candidate, old_selector)
    else:
        candidate = replace_row(candidate, old_selector, detached_selector_row(old_selector))
    updated = replace(group, selector_feature_identity=new_selector.stable_identity)
    candidate = replace_group(candidate, group, updated)
    candidate = replace_row(candidate, new_selector, selector_row(new_selector, updated))
    return validate_transition(draft, candidate, action, group_identity(group.identity))


def _action(intent):  # noqa: ANN001
    return type(intent).__name__.removesuffix("Intent").replace("OneHot", " One-hot ").strip()
