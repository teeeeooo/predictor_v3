"""Qt-free One-hot authoring presentation projection."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.draft import DataDefinitionDraft
from core.data_definition.one_hot import VocabularySnapshot
from core.data_definition.one_hot.drift import one_hot_drift_evidence


@dataclass(frozen=True)
class OneHotSelectorOption:
    identity: str
    label: str
    column_key: str
    assigned_group_key: str = ""
    selectable: bool = True


@dataclass(frozen=True)
class OneHotCategoryRow:
    identity: str
    source_value: str
    emitted_feature_identity: str
    emitted_ml_name: str
    order: int
    active: bool
    provider_category_identity: str
    source_editable: bool
    provider_readonly: bool
    drift_status: str
    drift_resolution: str


@dataclass(frozen=True)
class OneHotGroupRow:
    identity: str
    group_key: str
    selector_feature_identity: str
    selector_label: str
    selector_column_key: str
    source_mode: str
    source_binding: str
    vocabulary_owner: str
    unknown_policy: str
    missing_policy: str
    active: bool
    provider_available: bool | None
    categories: tuple[OneHotCategoryRow, ...]


@dataclass(frozen=True)
class OneHotAuthoringProjection:
    groups: tuple[OneHotGroupRow, ...]
    selectors: tuple[OneHotSelectorOption, ...]
    vocabulary_snapshots: tuple[VocabularySnapshot, ...]
    external_creation_enabled: bool
    external_disabled_reason: str
    mapping_values_editable: bool = False


def project_one_hot_authoring(
    draft: DataDefinitionDraft,
    snapshots: tuple[VocabularySnapshot, ...],
) -> OneHotAuthoringProjection:
    """Project identities, owner copy, and drift without mutation policy in View."""
    rows = {item.stable_identity: item for item in draft.rows if item.stable_identity}
    assigned = {
        item.selector_feature_identity: item.group_key for item in draft.one_hot_groups
    }
    selectors = tuple(
        OneHotSelectorOption(
            row.stable_identity,
            row.label or row.column_key,
            row.column_key,
            assigned.get(row.stable_identity, ""),
            not assigned.get(row.stable_identity),
        )
        for row in draft.rows
        if row.source_kind == "schema_row"
        and row.role == "input"
        and row.data_type == "string"
        and not row.ml_name
    )
    drift = one_hot_drift_evidence(tuple(draft.one_hot_groups), snapshots)
    drift_by_category = {
        item.category_identity: item for item in drift if item.category_identity
    }
    source_available = {
        (item.source_mode, item.source_binding): item.available for item in snapshots
    }
    groups = []
    for group in draft.one_hot_groups:
        selector = rows.get(group.selector_feature_identity)
        categories = []
        for category in sorted(group.categories, key=lambda item: item.order):
            item_drift = drift_by_category.get(category.identity)
            categories.append(OneHotCategoryRow(
                category.identity,
                category.source_value,
                category.emitted_feature_identity,
                category.emitted_ml_name,
                category.order,
                category.active,
                category.provider_category_identity,
                group.category_source == "static",
                group.category_source == "external",
                item_drift.code if item_drift else "matched",
                item_drift.resolution if item_drift else "",
            ))
        provider_available = (
            source_available.get(("external", group.source_binding), False)
            if group.category_source == "external" else None
        )
        groups.append(OneHotGroupRow(
            group.identity,
            group.group_key,
            group.selector_feature_identity,
            (selector.label or selector.column_key) if selector else "Missing selector",
            selector.column_key if selector else "",
            group.category_source,
            group.source_binding,
            {
                "static": "Data Definition owns category values",
                "mapping_backed": "Data Mapping owns persisted option values",
                "external": "External provider owns category identity and value",
            }.get(group.category_source, group.category_source),
            group.unknown_policy,
            group.missing_policy,
            group.active,
            provider_available,
            tuple(categories),
        ))
    external_available = any(
        item.source_mode == "external" and item.available for item in snapshots
    )
    return OneHotAuthoringProjection(
        tuple(groups),
        selectors,
        snapshots,
        external_available,
        "No production external One-hot provider is registered."
        if not external_available else "",
    )
