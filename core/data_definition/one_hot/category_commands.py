"""Atomic One-hot category and emitted-Feature command transitions."""

from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from core.data_definition.command_types import DataDefinitionCommandResult
from core.data_definition.contract.model import OneHotCategoryDefinition
from core.data_definition.dependency_policy import feature_dependencies
from core.data_definition.draft import DataDefinitionDraft
from core.data_definition.one_hot.command_support import (
    add_emitted_row,
    category_identity,
    find_category,
    find_row_by_stable_id,
    issue,
    rebuild_group_ml_order,
    reject,
    remove_row,
    replace_group,
    replace_row,
    validate_transition,
    vocabulary_issue,
)
from core.data_definition.one_hot.intents import (
    AddOneHotCategoryIntent,
    DuplicateOneHotCategoryIntent,
    EditOneHotCategoryIntent,
    MoveOneHotCategoryIntent,
    RemoveOneHotCategoryIntent,
    RenameOneHotEmittedFeatureIntent,
    SetOneHotCategoryActiveIntent,
)
from core.data_definition.one_hot.model import VocabularySnapshot


def apply_category_command(
    draft: DataDefinitionDraft,
    intent: object,
    snapshots: tuple[VocabularySnapshot, ...] = (),
) -> DataDefinitionCommandResult:
    if isinstance(intent, AddOneHotCategoryIntent):
        group = next(
            (item for item in draft.one_hot_groups if item.identity == intent.group_identity), None
        )
        if group is None:
            return reject(draft, "Add One-hot category", issue(
                "one_hot_group_not_found", "group_identity", "One-hot group was not found."
            ))
        return _add(draft, group, intent, snapshots, "Add One-hot category")
    category_id = getattr(intent, "category_identity", "")
    group, category = find_category(draft, category_id)
    action = _action(intent)
    if group is None or category is None:
        return reject(draft, action, issue(
            "one_hot_category_not_found", "identity", "One-hot category was not found.",
            "Refresh and select the category again.",
        ), category_identity(category_id))
    if isinstance(intent, EditOneHotCategoryIntent):
        return _edit(draft, group, category, intent, snapshots)
    if isinstance(intent, RenameOneHotEmittedFeatureIntent):
        return _rename(draft, group, category, intent.emitted_ml_name)
    if isinstance(intent, DuplicateOneHotCategoryIntent):
        add_intent = AddOneHotCategoryIntent(
            group.identity,
            intent.source_value,
            intent.emitted_ml_name,
            intent.provider_category_identity,
            intent.position,
            False,
        )
        return _add(draft, group, add_intent, snapshots, "Duplicate One-hot category")
    if isinstance(intent, RemoveOneHotCategoryIntent):
        return _remove(draft, group, category)
    if isinstance(intent, SetOneHotCategoryActiveIntent):
        return _set_active(draft, group, category, intent.active, snapshots)
    if isinstance(intent, MoveOneHotCategoryIntent):
        return _move(draft, group, category, intent.direction)
    raise TypeError(f"Unsupported One-hot category command: {type(intent).__name__}")


def _add(draft, group, intent, snapshots, action):  # noqa: ANN001
    if intent.active:
        return reject(draft, action, issue(
            "one_hot_category_add_must_be_inactive", "active",
            "A new One-hot category must start inactive.",
        ))
    source_value = intent.source_value.strip()
    emitted_name = intent.emitted_ml_name.strip()
    problem = _new_values_issue(
        draft, group, source_value, emitted_name, intent.provider_category_identity
    )
    if problem:
        return reject(draft, action, problem)
    if problem := vocabulary_issue(
        group, source_value, intent.provider_category_identity, snapshots
    ):
        return reject(draft, action, problem)
    candidate, row = add_emitted_row(draft, group, emitted_name)
    position = intent.position or len(group.categories) + 1
    if not 1 <= position <= len(group.categories) + 1:
        return reject(draft, action, issue(
            "one_hot_category_position_invalid", "position", "Choose a position inside this group."
        ))
    category = OneHotCategoryDefinition(
        identity=f"ufm_onehot_category_{uuid4().hex}",
        source_value=source_value,
        emitted_feature_identity=row.stable_identity,
        emitted_ml_name=emitted_name,
        order=position,
        active=False,
        provider_category_identity=intent.provider_category_identity.strip(),
    )
    categories = list(group.categories)
    categories.insert(position - 1, category)
    updated_group = replace(group, categories=_ordered(categories))
    current_group = next(item for item in candidate.one_hot_groups if item.identity == group.identity)
    candidate = replace_group(candidate, current_group, updated_group)
    return validate_transition(
        draft, candidate, action, category_identity(category.identity)
    )


def _edit(draft, group, category, intent, snapshots):  # noqa: ANN001
    source_value = (
        category.source_value if intent.source_value is None else intent.source_value.strip()
    )
    provider_identity = (
        category.provider_category_identity
        if intent.provider_category_identity is None
        else intent.provider_category_identity.strip()
    )
    emitted_name = (
        category.emitted_ml_name
        if intent.emitted_ml_name is None else intent.emitted_ml_name.strip()
    )
    if group.category_source == "external" and (
        source_value != category.source_value
        or provider_identity != category.provider_category_identity
    ):
        problem = vocabulary_issue(group, source_value, provider_identity, snapshots)
        if problem:
            return reject(draft, "Edit One-hot category", problem, category_identity(category.identity))
    elif group.category_source != "static" and source_value != category.source_value:
        problem = vocabulary_issue(group, source_value, provider_identity, snapshots)
        if problem:
            return reject(draft, "Edit One-hot category", problem, category_identity(category.identity))
    problem = _new_values_issue(
        draft, group, source_value, emitted_name, provider_identity,
        excluding=category.identity,
    )
    if problem:
        return reject(draft, "Edit One-hot category", problem, category_identity(category.identity))
    updated = replace(
        category,
        source_value=source_value,
        emitted_ml_name=emitted_name,
        provider_category_identity=provider_identity,
        active=category.active if intent.active is None else intent.active,
    )
    if group.active and category.active and not updated.active:
        if sum(item.active for item in group.categories) == 1:
            return reject(draft, "Edit One-hot category", issue(
                "one_hot_active_category_required", "active",
                "An active group must retain at least one active category.",
            ), category_identity(category.identity))
    if updated.active and group.category_source == "external":
        if problem := vocabulary_issue(group, source_value, provider_identity, snapshots):
            return reject(draft, "Edit One-hot category", problem, category_identity(category.identity))
    return _replace_category(draft, group, category, updated, "Edit One-hot category")


def _rename(draft, group, category, emitted_name):  # noqa: ANN001
    name = emitted_name.strip()
    problem = _new_values_issue(
        draft, group, category.source_value, name,
        category.provider_category_identity, excluding=category.identity,
    )
    if problem:
        return reject(draft, "Rename emitted ML Feature", problem,
                      category_identity(category.identity))
    return _replace_category(
        draft, group, category, replace(category, emitted_ml_name=name),
        "Rename emitted ML Feature",
    )


def _remove(draft, group, category):  # noqa: ANN001
    action = "Remove One-hot category"
    if group.active and category.active and sum(item.active for item in group.categories) == 1:
        return reject(draft, action, issue(
            "one_hot_active_category_required", "categories",
            "Disable the group or enable another category before removal.",
        ), category_identity(category.identity))
    row = find_row_by_stable_id(draft, category.emitted_feature_identity)
    draft_derived = next(
        (
            item for item in draft.rows
            if item.source_kind == "derived_policy"
            and row is not None
            and row.stable_identity in {
                item.numerator_identity,
                item.denominator_identity,
            }
        ),
        None,
    )
    if draft_derived is not None:
        return reject(draft, action, issue(
            "derived_operand_reference",
            "dependency",
            f"Derived Feature '{draft_derived.ml_name}' references this emitted Feature.",
            "Remove or retarget the dependent Derived definition first.",
        ), category_identity(category.identity))
    blockers = tuple(
        dependency for dependency in feature_dependencies(draft, row)
        if dependency.blocks_remove and dependency.affected_identity != category.identity
    )
    if blockers:
        first = blockers[0]
        return reject(draft, action, issue(
            first.code, "dependency", first.message, first.resolution
        ), category_identity(category.identity))
    candidate = remove_row(draft, row)
    updated_group = replace(
        group,
        categories=_ordered(
            [item for item in group.categories if item.identity != category.identity]
        ),
    )
    candidate = replace_group(candidate, group, updated_group)
    candidate = rebuild_group_ml_order(candidate, updated_group)
    return validate_transition(
        draft, candidate, action, None, (category_identity(category.identity),)
    )


def _set_active(draft, group, category, active, snapshots):  # noqa: ANN001
    action = "Enable One-hot category" if active else "Disable One-hot category"
    if category.active == active:
        return reject(draft, action, issue(
            "one_hot_category_active_unchanged", "active", "Category active state is unchanged."
        ), category_identity(category.identity))
    if not active and group.active and sum(item.active for item in group.categories) == 1:
        return reject(draft, action, issue(
            "one_hot_active_category_required", "active",
            "An active group must retain at least one active category.",
        ), category_identity(category.identity))
    if active and (problem := vocabulary_issue(
        group, category.source_value, category.provider_category_identity, snapshots
    )):
        return reject(draft, action, problem, category_identity(category.identity))
    return _replace_category(
        draft, group, category, replace(category, active=active), action
    )


def _move(draft, group, category, direction):  # noqa: ANN001
    categories = list(sorted(group.categories, key=lambda item: item.order))
    index = categories.index(category)
    target = index - 1 if direction == "up" else index + 1 if direction == "down" else -1
    if target < 0 or target >= len(categories):
        return reject(draft, "Move One-hot category", issue(
            "one_hot_category_move_boundary", "order",
            "Category cannot move farther in that direction.",
        ), category_identity(category.identity))
    categories[index], categories[target] = categories[target], categories[index]
    updated_group = replace(group, categories=_ordered(categories))
    candidate = replace_group(draft, group, updated_group)
    candidate = rebuild_group_ml_order(candidate, updated_group)
    return validate_transition(
        draft, candidate, "Move One-hot category", category_identity(category.identity)
    )


def _replace_category(draft, group, before, after, action):  # noqa: ANN001
    updated_group = replace(
        group,
        categories=tuple(after if item.identity == before.identity else item
                         for item in group.categories),
    )
    candidate = replace_group(draft, group, updated_group)
    row = find_row_by_stable_id(candidate, before.emitted_feature_identity)
    candidate = replace_row(candidate, row, replace(
        row,
        label=after.emitted_ml_name,
        ml_name=after.emitted_ml_name,
        active=updated_group.active and after.active,
    ))
    candidate = rebuild_group_ml_order(candidate, updated_group)
    return validate_transition(
        draft, candidate, action, category_identity(after.identity)
    )


def _new_values_issue(draft, group, source, emitted, provider, excluding=""):  # noqa: ANN001
    if not source:
        return issue("one_hot_source_value_invalid", "source_value", "Source value is required.")
    if not emitted:
        return issue("one_hot_emitted_name_invalid", "emitted_ml_name", "Emitted ML name is required.")
    if any(item.source_value == source and item.identity != excluding for item in group.categories):
        return issue("one_hot_category_source_duplicate", "source_value", "Source value already has a rule.")
    existing_category = next((item for owner in draft.one_hot_groups for item in owner.categories
                              if item.identity == excluding), None)
    own_feature = existing_category.emitted_feature_identity if existing_category else ""
    if any(row.ml_name == emitted and row.stable_identity != own_feature for row in draft.rows):
        return issue("ml_name_collision", "emitted_ml_name", "Emitted ML name already exists.")
    if any(row.ml_name == emitted for row in draft.rows if row.source_kind == "derived_policy"):
        return issue("ml_name_collision", "emitted_ml_name", "Emitted ML name collides with Derived.")
    if group.category_source == "external":
        if not provider:
            return issue("one_hot_provider_category_invalid", "provider_category_identity",
                         "Select a provider-owned category.")
        if any(item.provider_category_identity == provider and item.identity != excluding
               for item in group.categories):
            return issue("one_hot_provider_category_duplicate", "provider_category_identity",
                         "Provider category already has an overlay.")
    elif provider:
        return issue("one_hot_provider_category_not_allowed", "provider_category_identity",
                     "Only external groups store provider category identities.")
    return None


def _ordered(categories):  # noqa: ANN001
    return tuple(replace(item, order=index) for index, item in enumerate(categories, 1))


def _action(intent):  # noqa: ANN001
    return type(intent).__name__.removesuffix("Intent").replace("OneHot", " One-hot ").strip()
