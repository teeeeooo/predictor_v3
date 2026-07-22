"""Stable-identity Mapping requirement reconciliation evidence."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.mapping_requirement_contract import (
    mapping_group_key_for_requirement,
)
from core.mapping.exchange.identity import exchange_row_identity


@dataclass(frozen=True)
class MappingReconciliationItem:
    identity: str
    classification: str
    summary: str
    blocking: bool = False


def reconcile_mapping_requirements(
    active_snapshot,
    candidate_snapshot,
    *,
    draft=None,
    baseline=None,
) -> tuple[MappingReconciliationItem, ...]:  # noqa: ANN001
    """Classify requirement drift strictly by canonical identity."""
    active_manifest = active_snapshot.manifest
    candidate_manifest = candidate_snapshot.manifest
    old = {item.identity: item for item in active_manifest.mapping_requirements}
    new = {item.identity: item for item in candidate_manifest.mapping_requirements}
    old_projection = dict(zip(
        (item.identity for item in active_manifest.mapping_requirements),
        active_snapshot.projections.mapping_requirements,
        strict=True,
    ))
    evidence = []
    for identity in sorted(old.keys() | new.keys()):
        before, after = old.get(identity), new.get(identity)
        if before is None:
            evidence.append(MappingReconciliationItem(identity, "added requirement", identity))
            continue
        if after is None:
            dirty = _requirement_values_changed(
                old_projection[identity], draft, baseline
            )
            evidence.append(MappingReconciliationItem(
                identity,
                "dirty column removal" if dirty else "removed clean requirement",
                identity,
                dirty,
            ))
            continue
        if before == after:
            dirty = _requirement_values_changed(
                old_projection[identity], draft, baseline
            )
            evidence.append(MappingReconciliationItem(
                identity,
                (
                    "compatible requirement with preserved unsaved values"
                    if dirty else "compatible unchanged requirement"
                ),
                identity,
            ))
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


def _requirement_values_changed(requirement, draft, baseline) -> bool:  # noqa: ANN001
    if draft is None or baseline is None:
        return False
    group_key = mapping_group_key_for_requirement(requirement)
    column = requirement.mapping_attribute
    current_group = draft.group(group_key)
    baseline_group = baseline.group(group_key)
    return _column_values(current_group, column) != _column_values(
        baseline_group, column
    )


def _column_values(group, column: str) -> tuple[tuple[object, object], ...]:  # noqa: ANN001
    if group is None:
        return ()
    values = []
    for index, row in enumerate(group.rows):
        value = row.value_for(column, "")
        if not row.has_concrete_value_for(column) and value in (None, ""):
            continue
        identity = exchange_row_identity(group, row)
        stable = identity or (("source", row.source_key) if row.source_key else ("row", index))
        values.append((stable, value))
    return tuple(sorted(values, key=lambda item: repr(item[0])))
