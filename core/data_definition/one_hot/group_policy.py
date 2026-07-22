"""Validation policy shared by One-hot group transitions."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.dependency_policy import FeatureDependency, feature_dependencies
from core.data_definition.one_hot.command_support import (
    MISSING_POLICIES,
    SOURCE_MODES,
    UNKNOWN_POLICIES,
    find_row_by_stable_id,
    issue,
)
from core.data_definition.one_hot.model import vocabulary_snapshot_for


@dataclass(frozen=True)
class SelectorEligibility:
    """Single domain-owned selector reservation/takeover decision."""

    selectable: bool
    blocker_code: str = ""
    reason: str = ""
    takeover_state: str = "eligible"
    affected_owners: tuple[str, ...] = ()


def selector_eligibility(draft, identity, excluding_group=""):  # noqa: ANN001
    row = find_row_by_stable_id(draft, identity)
    if row is None or row.source_kind != "schema_row":
        return SelectorEligibility(
            False, "one_hot_selector_missing", "Select an existing schema Feature.", "blocked"
        )
    assigned = next(
        (
            item for item in draft.one_hot_groups
            if item.selector_feature_identity == identity
            and item.identity != excluding_group
        ),
        None,
    )
    if assigned is not None:
        return SelectorEligibility(
            False,
            "one_hot_selector_duplicate",
            f"Selector is already reserved by group '{assigned.group_key}'.",
            "reserved",
            (f"One-hot/{assigned.group_key}",),
        )
    if not row.active:
        return SelectorEligibility(
            False,
            "one_hot_selector_inactive",
            "Enable the Feature before reserving it as a selector.",
            "blocked",
        )
    if row.role != "input" or row.data_type != "string" or row.ml_name:
        return SelectorEligibility(
            False,
            "one_hot_selector_incompatible",
            "Selector must be an active string input without a direct ML name.",
            "blocked",
        )
    blockers = takeover_blockers(draft, row)
    if blockers:
        owners = tuple(dict.fromkeys(item.owner for item in blockers))
        return SelectorEligibility(
            True,
            blockers[0].code,
            "Reservation is safe while inactive; activation is blocked until dependencies are migrated.",
            "activation_blocked",
            owners,
        )
    return SelectorEligibility(True, takeover_state="takeover_ready")


def available_selector(draft, identity, excluding_group=""):  # noqa: ANN001
    row = find_row_by_stable_id(draft, identity)
    eligibility = selector_eligibility(draft, identity, excluding_group)
    if not eligibility.selectable:
        return None, issue(
            eligibility.blocker_code,
            "selector",
            eligibility.reason,
            "Resolve the selector blocker and open a new Impact Preview.",
        )
    return row, None


def takeover_blockers(draft, row):  # noqa: ANN001
    """Return dependencies whose runtime meaning takeover would suspend."""
    blockers = [
        item for item in feature_dependencies(draft, row)
        if item.blocks_disable and item.owner != "One-hot"
    ]
    if row.value_source in {"mapping_lookup", "rule_options"} or (
        row.trigger_column or row.mapping_attribute
    ):
        blockers.append(FeatureDependency(
            "one_hot_selector_shape_dependency",
            "Feature runtime metadata",
            row.stable_identity,
            "Mapping/rule/cascade metadata must be migrated before selector takeover.",
            blocks_disable=True,
            resolution=(
                "Keep the group inactive or migrate the dependent runtime relation first."
            ),
        ))
    return tuple(blockers)


def group_values_issue(draft, key, mode, binding, unknown, missing):  # noqa: ANN001
    if not key or any(item.group_key == key for item in draft.one_hot_groups):
        return issue("one_hot_group_key_duplicate", "group_key", "Enter a unique group key.")
    if mode not in SOURCE_MODES:
        return issue("one_hot_category_source_invalid", "source_mode", "Select a supported source mode.")
    if mode in {"mapping_backed", "external"} and not binding.strip():
        return issue("one_hot_source_binding_invalid", "source_binding", "Source binding is required.")
    if mode == "static" and binding.strip():
        return issue("one_hot_source_binding_invalid", "source_binding", "Static groups do not use a source binding.")
    if unknown not in UNKNOWN_POLICIES or missing not in MISSING_POLICIES:
        return issue("one_hot_policy_invalid", "policy", "Choose explicit supported policies.")
    return None


def source_available(mode, binding, snapshots):  # noqa: ANN001
    if mode == "static":
        return None
    snapshot = vocabulary_snapshot_for(snapshots, mode, binding.strip())
    if snapshot is None or not snapshot.available:
        return issue(
            "one_hot_provider_unavailable", "source_binding",
            f"No available {mode} vocabulary is registered for '{binding}'.",
            "Refresh persisted Mapping vocabulary or register the provider snapshot.",
        )
    return None


def dependency_blockers(draft, row, verb, ignored_identities=()):  # noqa: ANN001
    if row is None:
        return (issue("one_hot_feature_missing", "identity", "Related Feature is missing."),)
    return tuple(
        issue(
            dependency.code, "dependency",
            f"{verb} would break {dependency.owner}: {dependency.message}",
            dependency.resolution,
        )
        for dependency in feature_dependencies(draft, row)
        if dependency.blocks_remove
        and dependency.affected_identity not in ignored_identities
    )
