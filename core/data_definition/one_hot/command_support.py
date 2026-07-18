"""Shared atomic-transition helpers for One-hot commands."""

from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from core.data_definition.command_contract import normalize_column_key
from core.data_definition.command_types import (
    DataDefinitionCommandIssue,
    DataDefinitionCommandResult,
)
from core.data_definition.contract import candidate_manifest_from_draft, validate_contract
from core.data_definition.contract.model import (
    OneHotCategoryDefinition,
    OneHotGroupDefinition,
)
from core.data_definition.draft import DataDefinitionDraft, DataDefinitionDraftRow
from core.data_definition.one_hot.model import (
    VocabularySnapshot,
    vocabulary_snapshot_for,
)

UNKNOWN_POLICIES = frozenset({"warn_all_zero"})
MISSING_POLICIES = frozenset({"all_zero"})
SOURCE_MODES = frozenset({"static", "mapping_backed", "external"})


def issue(code: str, field: str, message: str, resolution: str = "") -> DataDefinitionCommandIssue:
    return DataDefinitionCommandIssue(code, field, message, resolution)


def reject(
    draft: DataDefinitionDraft,
    action: str,
    problem: DataDefinitionCommandIssue,
    identity: tuple[str, str] | None = None,
) -> DataDefinitionCommandResult:
    return DataDefinitionCommandResult(draft, False, identity, action, (problem,))


def group_identity(identity: str) -> tuple[str, str]:
    return ("one_hot_group", identity)


def category_identity(identity: str) -> tuple[str, str]:
    return ("one_hot_category", identity)


def find_group(draft: DataDefinitionDraft, identity: str) -> OneHotGroupDefinition | None:
    return next((item for item in draft.one_hot_groups if item.identity == identity), None)


def find_category(
    draft: DataDefinitionDraft,
    identity: str,
) -> tuple[OneHotGroupDefinition | None, OneHotCategoryDefinition | None]:
    for group in draft.one_hot_groups:
        category = next((item for item in group.categories if item.identity == identity), None)
        if category is not None:
            return group, category
    return None, None


def find_row_by_stable_id(
    draft: DataDefinitionDraft,
    identity: str,
) -> DataDefinitionDraftRow | None:
    return next((item for item in draft.rows if item.stable_identity == identity), None)


def replace_group(
    draft: DataDefinitionDraft,
    before: OneHotGroupDefinition,
    after: OneHotGroupDefinition,
) -> DataDefinitionDraft:
    return replace(
        draft,
        one_hot_groups=tuple(
            after if item.identity == before.identity else item
            for item in draft.one_hot_groups
        ),
    )


def replace_row(
    draft: DataDefinitionDraft,
    before: DataDefinitionDraftRow,
    after: DataDefinitionDraftRow,
) -> DataDefinitionDraft:
    changed_fields = tuple(
        field for field in DataDefinitionDraftRow.__dataclass_fields__
        if getattr(before, field) != getattr(after, field)
    )
    return replace(
        draft,
        rows=tuple(after if item.identity == before.identity else item for item in draft.rows),
        controlled_field_changes=frozenset((
            *draft.controlled_field_changes,
            *((before.identity, field) for field in changed_fields),
        )),
    )


def add_emitted_row(
    draft: DataDefinitionDraft,
    group: OneHotGroupDefinition,
    emitted_ml_name: str,
) -> tuple[DataDefinitionDraft, DataDefinitionDraftRow]:
    stable_identity = f"ufm_feature_{uuid4().hex}"
    column_key = _unique_column_key(
        draft,
        f"one_hot_{normalize_column_key(group.group_key)}_{stable_identity[-8:]}",
    )
    display_order = max((item.display_order for item in draft.rows), default=0) + 10
    row = DataDefinitionDraftRow(
        source_kind="schema_row",
        stable_identity=stable_identity,
        display_order=display_order,
        column_key=column_key,
        label=emitted_ml_name,
        role="one_hot_feature",
        editor="readonly",
        data_type="number",
        visible=False,
        required=False,
        readonly=True,
        value_source="one_hot",
        model_input_enabled=True,
        ml_name=emitted_ml_name,
        one_hot_group=group.group_key,
        active=False,
        notes="Canonical emitted One-hot ML Feature.",
    )
    schema_rows = tuple(item for item in draft.rows if item.source_kind == "schema_row")
    other_rows = tuple(item for item in draft.rows if item.source_kind != "schema_row")
    updated = replace(
        draft,
        rows=(*schema_rows, row, *other_rows),
        predict_order=(*draft.predict_order, row.identity),
        controlled_row_additions=frozenset((*draft.controlled_row_additions, row.identity)),
        controlled_addition_initial_rows=(*draft.controlled_addition_initial_rows, row),
    )
    return updated, row


def remove_row(draft: DataDefinitionDraft, row: DataDefinitionDraftRow) -> DataDefinitionDraft:
    newly_added = draft.is_controlled_row_addition(row.identity)
    return replace(
        draft,
        rows=tuple(item for item in draft.rows if item.identity != row.identity),
        predict_order=tuple(item for item in draft.predict_order if item != row.identity),
        ml_order=tuple(item for item in draft.ml_order if item != row.identity),
        controlled_row_additions=frozenset(
            item for item in draft.controlled_row_additions if item != row.identity
        ),
        controlled_addition_initial_rows=tuple(
            item for item in draft.controlled_addition_initial_rows if item.identity != row.identity
        ),
        controlled_row_removals=(
            draft.controlled_row_removals if newly_added
            else frozenset((*draft.controlled_row_removals, row.identity))
        ),
        controlled_field_changes=frozenset(
            item for item in draft.controlled_field_changes if item[0] != row.identity
        ),
    )


def selector_row(
    row: DataDefinitionDraftRow,
    group: OneHotGroupDefinition,
) -> DataDefinitionDraftRow:
    return replace(
        row,
        role="input",
        editor="dropdown",
        data_type="string",
        visible=True,
        readonly=False,
        value_source="one_hot",
        mapping_entity=group.source_binding if group.category_source == "mapping_backed" else "",
        mapping_attribute="",
        trigger_column="",
        rule_id=f"one_hot:{group.identity}",
        model_input_enabled=True,
        ml_name="",
        one_hot_group=group.group_key,
        active=group.active,
    )


def detached_selector_row(row: DataDefinitionDraftRow) -> DataDefinitionDraftRow:
    return replace(
        row,
        value_source="manual",
        mapping_attribute="",
        trigger_column="",
        rule_id="",
        model_input_enabled=False,
        ml_name="",
        one_hot_group="",
        active=True,
    )


def rebuild_group_ml_order(
    draft: DataDefinitionDraft,
    group: OneHotGroupDefinition,
) -> DataDefinitionDraft:
    all_ids = {
        ("schema_row", item.emitted_feature_identity) for item in group.categories
    }
    existing = list(draft.ml_order)
    positions = [index for index, identity in enumerate(existing) if identity in all_ids]
    without = [identity for identity in existing if identity not in all_ids]
    active = [
        ("schema_row", item.emitted_feature_identity)
        for item in sorted(group.categories, key=lambda category: category.order)
        if group.active and item.active
    ]
    anchor = min(positions) if positions else _group_anchor(draft, group, without)
    return replace(draft, ml_order=tuple((*without[:anchor], *active, *without[anchor:])))


def vocabulary_issue(
    group: OneHotGroupDefinition,
    source_value: str,
    provider_identity: str,
    snapshots: tuple[VocabularySnapshot, ...],
) -> DataDefinitionCommandIssue | None:
    if group.category_source == "static":
        return None
    snapshot = vocabulary_snapshot_for(snapshots, group.category_source, group.source_binding)
    if snapshot is None or not snapshot.available:
        return issue(
            "one_hot_provider_unavailable",
            "source_binding",
            f"Vocabulary source '{group.source_binding}' is unavailable.",
            "Refresh the persisted vocabulary or register the external provider.",
        )
    match = (
        snapshot.category_by_identity(provider_identity)
        if group.category_source == "external" else snapshot.category_by_value(source_value)
    )
    if match is None or match.value != source_value:
        return issue(
            "one_hot_source_value_unavailable",
            "source_value",
            f"Source value '{source_value}' is not in the immutable vocabulary snapshot.",
            "Select one of the current persisted/provider vocabulary values.",
        )
    return None


def validate_transition(
    original: DataDefinitionDraft,
    candidate: DataDefinitionDraft,
    action: str,
    identity: tuple[str, str] | None,
    affected: tuple[tuple[str, str], ...] = (),
) -> DataDefinitionCommandResult:
    if candidate.base_manifest is None:
        return reject(original, action, issue(
            "one_hot_canonical_manifest_required",
            "contract",
            "One-hot authoring requires a canonical generation draft.",
            "Reload through the generation repository.",
        ), identity)
    try:
        manifest = candidate_manifest_from_draft(candidate, candidate.base_manifest)
        issues = validate_contract(manifest)
    except (KeyError, TypeError, ValueError) as exc:
        return reject(original, action, issue(
            "one_hot_candidate_invalid", "contract", str(exc),
            "Resolve the One-hot relation or collision and preview again.",
        ), identity)
    if issues:
        first = issues[0]
        return reject(original, action, issue(
            first.code, "one_hot", first.message,
            "Resolve the One-hot relation or collision and preview again.",
        ), identity)
    return DataDefinitionCommandResult(candidate, True, identity, action, affected_identities=affected)


def _group_anchor(draft, group, order):  # noqa: ANN001
    groups = list(draft.one_hot_groups)
    index = next((i for i, item in enumerate(groups) if item.identity == group.identity), len(groups))
    preceding = {
        ("schema_row", category.emitted_feature_identity)
        for item in groups[:index] for category in item.categories
    }
    positions = [i for i, identity in enumerate(order) if identity in preceding]
    if positions:
        return max(positions) + 1
    following = {
        ("schema_row", category.emitted_feature_identity)
        for item in groups[index + 1:] for category in item.categories
    }
    positions = [i for i, identity in enumerate(order) if identity in following]
    if positions:
        return min(positions)
    rows = {item.identity: item for item in draft.rows}
    return next(
        (i for i, identity in enumerate(order)
         if rows.get(identity) and rows[identity].role in {"result", "derived"}),
        len(order),
    )


def _unique_column_key(draft: DataDefinitionDraft, base: str) -> str:
    existing = {item.column_key for item in draft.rows}
    if base not in existing:
        return base
    index = 2
    while f"{base}_{index}" in existing:
        index += 1
    return f"{base}_{index}"
