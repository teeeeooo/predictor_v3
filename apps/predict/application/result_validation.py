"""Fail-closed validation for canonical executed prediction results."""

from __future__ import annotations

from dataclasses import replace

from apps.predict.application.result_enrichment import enrich_target_outcomes
from apps.predict.application.target_applicability import (
    descriptors_for_requested_identities,
)
from apps.predict.application.target_outcome import PredictionTargetDescriptor
from apps.predict.state.result_row import ResultRow


_TARGET_OUTCOME_STATUSES = {"available", "unavailable", "failed"}
EXECUTED_RESULT_STATUSES = frozenset({"complete", "partial", "error", "cancelled"})
NON_EXECUTED_RESULT_STATUSES = frozenset({"pending", "running", "invalid"})


def canonical_result_rejection_reason(
    result: ResultRow,
    expected_targets: tuple[PredictionTargetDescriptor, ...],
) -> str:
    """Return a bounded reason when an executed result violates its pinned contract."""
    if result.status not in EXECUTED_RESULT_STATUSES:
        return "non_terminal_execution_status"
    if result.execution_context is None:
        return "missing_execution_context"
    if result._legacy_result_values:
        return "legacy_execution_payload_not_allowed"
    if result.freshness != "current" or result.stale_reason:
        return "incoming_result_not_current"

    context_requested = tuple(
        result.execution_context.requested_target_identities
    )
    if context_requested and context_requested != tuple(
        item.target_identity for item in expected_targets
    ):
        return "requested_target_context_mismatch"

    outcomes = result.target_outcomes
    if result.status == "cancelled":
        return "cancelled_has_execution_outcomes" if (
            outcomes or result.derived_metrics
        ) else ""
    if result.status == "error" and not outcomes:
        if result.derived_metrics:
            return "row_wide_error_has_derived_metrics"
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
    if not aggregate_matches:
        return "aggregate_status_mismatch"
    expected_metrics = enrich_target_outcomes(
        result.execution_context.capacity_inputs,
        outcomes,
    )
    return "" if result.derived_metrics == expected_metrics else "derived_metric_mismatch"


def canonical_stored_result_rejection_reason(
    result: ResultRow,
    expected_targets: tuple[PredictionTargetDescriptor, ...] | None,
) -> str:
    """Validate one row already held by the canonical session.

    Current executed results must still match the active runtime target contract.
    Stale results retain their historical typed contract; migration provenance is
    enforced by the session-issued projection artifact rather than by pretending
    the destination runtime produced those historical outcomes.
    """
    if result.status in NON_EXECUTED_RESULT_STATUSES:
        if (
            result.execution_context is not None
            or result.target_outcomes
            or result.derived_metrics
        ):
            return "non_executed_state_has_execution_payload"
        if result._legacy_result_values:
            return "non_executed_state_has_result_values"
        if result.freshness != "current" or result.stale_reason:
            return "non_executed_state_is_stale"
        return ""
    if result.status not in EXECUTED_RESULT_STATUSES:
        return "unknown_result_status"
    if result.execution_context is None:
        return "missing_execution_context"
    if result._legacy_result_values:
        return "legacy_execution_payload_not_allowed"
    if result.freshness == "current":
        if expected_targets is None:
            return "missing_active_target_contract"
        if result.execution_context.requested_target_identities:
            try:
                requested_targets = descriptors_for_requested_identities(
                    tuple(result.execution_context.requested_target_identities),
                    tuple(expected_targets),
                )
            except ValueError as exc:
                return str(exc).rsplit(": ", 1)[-1]
        else:
            requested_targets = tuple(expected_targets)
        return canonical_result_rejection_reason(result, requested_targets)

    requested_identities = tuple(
        result.execution_context.requested_target_identities
    )
    historical_targets = tuple(
        PredictionTargetDescriptor(
            outcome.target_identity,
            outcome.result_feature_identity,
            "historical",
            outcome.result_key,
            outcome.canonical_unit,
            outcome.value_source,
        )
        for outcome in result.target_outcomes
    )
    if (
        requested_identities
        and result.target_outcomes
        and requested_identities != tuple(
            item.target_identity for item in historical_targets
        )
    ):
        return "historical_requested_target_mismatch"
    historical = ResultRow(
        result.case_id,
        result.status,
        message=result.message,
        target_outcomes=result.target_outcomes,
        derived_metrics=result.derived_metrics,
        execution_context=replace(
            result.execution_context,
            requested_target_identities=tuple(
                item.target_identity for item in historical_targets
            ),
        ),
    )
    return canonical_result_rejection_reason(historical, historical_targets)
