"""Validation policy shared by One-hot group transitions."""

from __future__ import annotations

from core.data_definition.dependency_policy import feature_dependencies
from core.data_definition.one_hot.command_support import (
    MISSING_POLICIES,
    SOURCE_MODES,
    UNKNOWN_POLICIES,
    find_row_by_stable_id,
    issue,
)
from core.data_definition.one_hot.model import vocabulary_snapshot_for


def available_selector(draft, identity, excluding_group=""):  # noqa: ANN001
    row = find_row_by_stable_id(draft, identity)
    if row is None or row.source_kind != "schema_row":
        return None, issue("one_hot_selector_missing", "selector", "Select an existing Feature.")
    assigned = next((item for item in draft.one_hot_groups
                     if item.selector_feature_identity == identity
                     and item.identity != excluding_group), None)
    if assigned is not None:
        return None, issue(
            "one_hot_selector_duplicate", "selector",
            f"Selector is already assigned to group '{assigned.group_key}'.",
        )
    if row.role != "input" or row.data_type != "string" or row.ml_name:
        return None, issue(
            "one_hot_selector_incompatible", "selector",
            "Selector must be a string input without a direct ML name.",
        )
    return row, None


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


def dependency_blockers(draft, row, verb):  # noqa: ANN001
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
    )
