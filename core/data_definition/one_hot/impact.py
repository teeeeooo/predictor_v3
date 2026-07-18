"""One-hot-specific evidence for prepared Impact Preview."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.contract.compatibility import (
    current_derived_definitions,
    current_one_hot_definitions,
)
from core.data_definition.contract.model import UnifiedFeatureManifest
from core.data_definition.contract.projections import generate_projections
from core.data_definition.one_hot.drift import one_hot_drift_evidence
from core.data_definition.one_hot.model import (
    OneHotDriftEvidence,
    VocabularySnapshot,
    vocabulary_snapshot_for,
)


@dataclass(frozen=True)
class OneHotImpactEvidence:
    group_identity: str
    group_key: str
    selector_feature_identity: str
    selector_display_name: str
    source_mode: str
    vocabulary_owner: str
    source_binding: str
    category_identity: str = ""
    source_value: str = ""
    emitted_feature_identity: str = ""
    emitted_ml_name: str = ""
    order_before: int | None = None
    order_after: int | None = None
    active_before: bool | None = None
    active_after: bool | None = None
    unknown_policy_before: str = ""
    unknown_policy_after: str = ""
    missing_policy_before: str = ""
    missing_policy_after: str = ""
    external_provider_available: bool | None = None
    affected_derived_identities: tuple[str, ...] = ()
    mapping_concrete_values_changed: bool = False


def build_one_hot_impact_evidence(
    before: UnifiedFeatureManifest,
    after: UnifiedFeatureManifest,
    snapshots: tuple[VocabularySnapshot, ...],
) -> tuple[
    tuple[OneHotImpactEvidence, ...],
    tuple[OneHotDriftEvidence, ...],
    tuple[str, ...],
    tuple[str, ...],
]:
    """Return changed group/category evidence without external mutation."""
    before_groups = {item.identity: item for item in current_one_hot_definitions(before)}
    after_groups = {item.identity: item for item in current_one_hot_definitions(after)}
    before_features = {item.identity: item for item in before.features}
    after_features = {item.identity: item for item in after.features}
    derived = current_derived_definitions(after)
    evidence = []
    for identity in dict.fromkeys((*before_groups, *after_groups)):
        old_group = before_groups.get(identity)
        new_group = after_groups.get(identity)
        if old_group == new_group:
            continue
        group = new_group or old_group
        selector = (
            after_features.get(group.selector_feature_identity)
            or before_features.get(group.selector_feature_identity)
        )
        old_categories = {
            item.identity: item for item in old_group.categories
        } if old_group else {}
        new_categories = {
            item.identity: item for item in new_group.categories
        } if new_group else {}
        category_ids = tuple(dict.fromkeys((*old_categories, *new_categories))) or ("",)
        snapshot = vocabulary_snapshot_for(
            snapshots, group.category_source, group.source_binding
        )
        provider_available = (
            snapshot.available if group.category_source == "external" and snapshot else
            False if group.category_source == "external" else None
        )
        for category_id in category_ids:
            old = old_categories.get(category_id)
            new = new_categories.get(category_id)
            category = new or old
            emitted_identity = category.emitted_feature_identity if category else ""
            emitted = after_features.get(emitted_identity) or before_features.get(emitted_identity)
            affected_derived = tuple(
                item.identity for item in derived
                if emitted_identity in {item.numerator_identity, item.denominator_identity}
            )
            evidence.append(OneHotImpactEvidence(
                group_identity=group.identity,
                group_key=group.group_key,
                selector_feature_identity=group.selector_feature_identity,
                selector_display_name=(selector.label or selector.column_key) if selector else "",
                source_mode=group.category_source,
                vocabulary_owner={
                    "static": "Canonical Data Definition",
                    "mapping_backed": "Data Mapping (persisted read-only vocabulary)",
                    "external": "External provider (read-only identity/value)",
                }.get(group.category_source, group.category_source),
                source_binding=group.source_binding,
                category_identity=category.identity if category else "",
                source_value=category.source_value if category else "",
                emitted_feature_identity=emitted_identity,
                emitted_ml_name=emitted.ml_name if emitted else "",
                order_before=old.order if old else None,
                order_after=new.order if new else None,
                active_before=(old_group.active and old.active) if old_group and old else None,
                active_after=(new_group.active and new.active) if new_group and new else None,
                unknown_policy_before=old_group.unknown_policy if old_group else "",
                unknown_policy_after=new_group.unknown_policy if new_group else "",
                missing_policy_before=old_group.missing_policy if old_group else "",
                missing_policy_after=new_group.missing_policy if new_group else "",
                external_provider_available=provider_available,
                affected_derived_identities=affected_derived,
            ))
    return (
        tuple(evidence),
        one_hot_drift_evidence(tuple(after_groups.values()), snapshots),
        _ml_headers(before),
        _ml_headers(after),
    )


def _ml_headers(manifest: UnifiedFeatureManifest) -> tuple[str, ...]:
    return tuple(
        item.ml_name for item in generate_projections(manifest).ml
        if item.active and item.ml_name
    )
