"""Fail-closed validation for canonical executed prediction results."""

from __future__ import annotations

from apps.predict.application.target_outcome import PredictionTargetDescriptor
from apps.predict.state.result_row import ResultRow


_TARGET_OUTCOME_STATUSES = {"available", "unavailable", "failed"}
_EXECUTED_ROW_STATUSES = {"complete", "partial", "error", "cancelled"}


def canonical_result_rejection_reason(
    result: ResultRow,
    expected_targets: tuple[PredictionTargetDescriptor, ...],
) -> str:
    """Return a bounded reason when an executed result violates its pinned contract."""
    if result.status not in _EXECUTED_ROW_STATUSES:
        return "non_terminal_execution_status"
    if result.freshness != "current" or result.stale_reason:
        return "incoming_result_not_current"

    outcomes = result.target_outcomes
    if result.status == "cancelled":
        return "cancelled_has_target_outcomes" if outcomes else ""
    if result.status == "error" and not outcomes:
        return "" if result.message else "row_wide_error_detail_missing"
    if not outcomes:
        return "missing_expected_target"

    expected_by_identity = {
        descriptor.target_identity: descriptor for descriptor in expected_targets
    }
    if len(expected_by_identity) != len(expected_targets):
        return "invalid_expected_target_contract"

    identities = tuple(outcome.target_identity for outcome in outcomes)
    if len(identities) != len(set(identities)):
        return "duplicate_target_identity"
    if any(identity not in expected_by_identity for identity in identities):
        return "unknown_target_identity"
    if set(identities) != set(expected_by_identity):
        return "missing_expected_target"

    for outcome in outcomes:
        descriptor = expected_by_identity[outcome.target_identity]
        if outcome.result_feature_identity != descriptor.result_feature_identity:
            return "result_feature_identity_mismatch"
        if outcome.result_key != descriptor.result_key:
            return "result_key_mismatch"
        if outcome.canonical_unit != descriptor.canonical_unit:
            return "canonical_unit_mismatch"
        if outcome.value_source != descriptor.value_source:
            return "value_source_mismatch"
        if outcome.status not in _TARGET_OUTCOME_STATUSES:
            return "invalid_target_outcome_status"

    available = sum(outcome.status == "available" for outcome in outcomes)
    non_available = len(outcomes) - available
    aggregate_matches = (
        result.status == "complete" and available == len(outcomes)
        or result.status == "partial" and available > 0 and non_available > 0
        or result.status == "error" and available == 0
    )
    return "" if aggregate_matches else "aggregate_status_mismatch"
