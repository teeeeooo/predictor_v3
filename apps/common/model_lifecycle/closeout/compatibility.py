"""Read-only historical dispositions without silent persisted reinterpretation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from apps.common.model_lifecycle.active_contracts import (
    ACTIVE_REFERENCE_SCHEMA_VERSION,
    active_reference_from_payload,
)
from apps.common.model_lifecycle.candidate_contracts import (
    CANDIDATE_SCHEMA_VERSION,
    LEGACY_CANDIDATE_SCHEMA_VERSION,
    RESULT_SCHEMA_VERSION,
    CandidateManifest,
    CandidateResult,
)
from apps.common.model_lifecycle.training_result_contracts import (
    TRAINING_RESULT_SCHEMA_VERSION,
    TrainingAnalysisResult,
)

from .canonical import canonical_payload
from .contracts import (
    CONFIRMATION_VERSION,
    FINAL_DECISION_VERSION,
    LOCKED_FINAL_TEST_RESULT_VERSION,
    LOCKED_FINAL_TEST_VERSION,
    SNAPSHOT_VERSION,
    ContractDisposition,
    validate_confirmation_record,
    validate_final_decision,
    validate_locked_final_test,
    validate_locked_final_test_result,
    validate_snapshot_record,
)
from .experiment_compatibility import (
    EXPERIMENT_VERSIONS,
    inspect_experiment,
    validate_recommendation_evidence,
)

CURRENT_EXECUTABLE = "current_and_executable"
CURRENT_BLOCKED = "current_but_blocked"
HISTORICAL_ONLY = "readable_historical_only"
UNSUPPORTED_FUTURE = "unsupported_future_version"
CORRUPT_INCOMPLETE = "corrupt_or_incomplete"

def inspect_persisted_contract(
    kind: str,
    payload: Any,
) -> ContractDisposition:
    """Classify readability separately from resume/confirmation eligibility."""
    try:
        if kind == "candidate_manifest":
            return _candidate_manifest(payload)
        if kind == "candidate_result":
            CandidateResult.from_payload(payload)
            return _executable(payload)
        if kind == "training_analysis":
            TrainingAnalysisResult.from_payload(payload)
            return _executable(payload)
        if kind == "active_reference":
            active_reference_from_payload(payload)
            return _executable(payload)
        if kind == "snapshot":
            return _validated(validate_snapshot_record, payload)
        if kind == "confirmation":
            return _validated(validate_confirmation_record, payload)
        if kind == "final_decision":
            return _validated(validate_final_decision, payload)
        if kind == "locked_final_test":
            return _validated(validate_locked_final_test, payload)
        if kind == "locked_final_test_result":
            return _validated(validate_locked_final_test_result, payload)
        if kind in EXPERIMENT_VERSIONS:
            return inspect_experiment(kind, payload)
        return ContractDisposition(
            CORRUPT_INCOMPLETE,
            False,
            "contract_kind_unknown",
            f"Unknown persisted contract kind: {kind}.",
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _invalid_or_future(kind, payload, exc)


def _candidate_manifest(payload: Any) -> ContractDisposition:
    manifest = CandidateManifest.from_payload(payload)
    if manifest.schema_version == LEGACY_CANDIDATE_SCHEMA_VERSION:
        return ContractDisposition(
            HISTORICAL_ONLY,
            False,
            "legacy_candidate_requires_current_revalidation",
            "Legacy Candidate is readable but not executable through historical defaults.",
            canonical_payload(payload),
        )
    return _executable(payload)


def _validated(
    reader: Callable[[Any], dict[str, Any]], payload: Any
) -> ContractDisposition:
    value = reader(payload)
    status = value.get("status")
    blocked_states = {
        "creating",
        "failed",
        "blocked_incomplete",
        "failed",
        "blocked",
        "cancelled",
        "rejected",
        "stale",
        "consumed",
    }
    if status in blocked_states:
        return ContractDisposition(
            CURRENT_BLOCKED,
            False,
            f"{status}_not_executable",
            "Contract is current but its lifecycle state blocks execution.",
            value,
        )
    return _executable(value)


def _invalid_or_future(
    kind: str, payload: Any, exc: Exception
) -> ContractDisposition:
    version = payload.get("schema_version") if isinstance(payload, dict) else None
    expected = {
        **EXPERIMENT_VERSIONS,
        "candidate_manifest": CANDIDATE_SCHEMA_VERSION,
        "candidate_result": RESULT_SCHEMA_VERSION,
        "training_analysis": TRAINING_RESULT_SCHEMA_VERSION,
        "active_reference": ACTIVE_REFERENCE_SCHEMA_VERSION,
        "snapshot": SNAPSHOT_VERSION,
        "confirmation": CONFIRMATION_VERSION,
        "final_decision": FINAL_DECISION_VERSION,
        "locked_final_test": LOCKED_FINAL_TEST_VERSION,
        "locked_final_test_result": LOCKED_FINAL_TEST_RESULT_VERSION,
    }.get(kind)
    if isinstance(version, str) and expected is not None and version != expected:
        return ContractDisposition(
            UNSUPPORTED_FUTURE,
            False,
            "unsupported_contract_version",
            str(exc),
        )
    return ContractDisposition(
        CORRUPT_INCOMPLETE,
        False,
        "contract_corrupt_or_incomplete",
        str(exc),
    )


def _executable(payload: Any) -> ContractDisposition:
    return ContractDisposition(
        CURRENT_EXECUTABLE,
        True,
        projection=deepcopy(canonical_payload(payload)),
    )
