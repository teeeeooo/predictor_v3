"""Source-owner vocabulary drift projection for One-hot authoring."""

from __future__ import annotations

from core.data_definition.contract.model import OneHotGroupDefinition
from core.data_definition.one_hot.model import (
    OneHotDriftEvidence,
    VocabularySnapshot,
    vocabulary_snapshot_for,
)


def one_hot_drift_evidence(
    groups: tuple[OneHotGroupDefinition, ...],
    snapshots: tuple[VocabularySnapshot, ...],
) -> tuple[OneHotDriftEvidence, ...]:
    """Report Mapping warnings and External availability blockers."""
    evidence: list[OneHotDriftEvidence] = []
    for group in groups:
        if group.category_source == "static":
            continue
        snapshot = vocabulary_snapshot_for(
            snapshots, group.category_source, group.source_binding
        )
        external = group.category_source == "external"
        if snapshot is None or not snapshot.available:
            evidence.append(OneHotDriftEvidence(
                "one_hot_provider_unavailable" if external else "one_hot_mapping_vocabulary_unavailable",
                group.source_binding,
                "",
                blocking=external,
                resolution=(
                    "Register and refresh the external provider snapshot."
                    if external else "Refresh the persisted Mapping vocabulary snapshot."
                ),
            ))
            continue
        by_value = {item.value: item for item in snapshot.categories}
        by_identity = {item.identity: item for item in snapshot.categories}
        rule_values = {item.source_value for item in group.categories}
        for category in group.categories:
            provider = (
                by_identity.get(category.provider_category_identity)
                if external else by_value.get(category.source_value)
            )
            if provider is not None and provider.value == category.source_value:
                continue
            evidence.append(OneHotDriftEvidence(
                "one_hot_external_category_missing" if external else "one_hot_mapping_rule_stale",
                group.source_binding,
                category.source_value,
                category.identity,
                category.emitted_feature_identity,
                category.emitted_ml_name,
                category.provider_category_identity,
                blocking=external,
                resolution=(
                    "Select an available provider category or disable the overlay."
                    if external else "Retarget the rule to a persisted Mapping value or keep it as explicit drift."
                ),
            ))
        for provider in snapshot.categories:
            if provider.value not in rule_values:
                evidence.append(OneHotDriftEvidence(
                    "one_hot_provider_value_unmatched",
                    group.source_binding,
                    provider.value,
                    provider_category_identity=provider.identity if external else "",
                    resolution="Add an emitted mapping rule or let the unknown policy handle this value.",
                ))
    return tuple(evidence)
