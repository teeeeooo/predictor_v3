"""Stable-identity Mapping requirement reconciliation evidence."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MappingReconciliationItem:
    identity: str
    classification: str
    summary: str
    blocking: bool = False


def reconcile_mapping_requirements(active_manifest, candidate_manifest) -> tuple[MappingReconciliationItem, ...]:  # noqa: ANN001
    """Classify requirement drift strictly by canonical identity."""
    old = {item.identity: item for item in active_manifest.mapping_requirements}
    new = {item.identity: item for item in candidate_manifest.mapping_requirements}
    evidence = []
    for identity in sorted(old.keys() | new.keys()):
        before, after = old.get(identity), new.get(identity)
        if before is None:
            evidence.append(MappingReconciliationItem(identity, "added requirement", identity))
            continue
        if after is None:
            evidence.append(MappingReconciliationItem(identity, "removed requirement", identity, True))
            continue
        if before == after:
            evidence.append(MappingReconciliationItem(identity, "compatible unchanged requirement", identity))
            continue
        changes = []
        if before.mapping_attribute != after.mapping_attribute:
            changes.append("renamed attribute")
        if before.data_type != after.data_type:
            changes.append("type change")
        if (
            before.trigger_feature_identity != after.trigger_feature_identity
            or before.rule_id != after.rule_id
        ):
            changes.append("trigger/relation change")
        if before.mapping_entity != after.mapping_entity:
            changes.append("conflicting declaration")
        classification = ", ".join(changes) or "coverage impact"
        evidence.append(MappingReconciliationItem(identity, classification, identity, True))
    return tuple(evidence)
