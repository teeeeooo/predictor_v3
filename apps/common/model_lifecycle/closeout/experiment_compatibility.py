"""Strict Phase 5F/5G historical readers and nested evidence checks."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .canonical import canonical_payload
from .contracts import ContractDisposition

CURRENT_EXECUTABLE = "current_and_executable"
CURRENT_BLOCKED = "current_but_blocked"
HISTORICAL_ONLY = "readable_historical_only"

EXPERIMENT_VERSIONS = {
    "experiment_specification": "predictor_v3.experiment.v1",
    "run": "predictor_v3.experiment_run.v1",
    "phase5f_campaign": "predictor_v3.campaign.v1",
    "agent_campaign": "predictor_v3.agent_campaign.v1",
    "proposal": "predictor_v3.experiment_proposal.v1",
    "gate": "predictor_v3.candidate_gate.v1",
    "leaderboard": "predictor_v3.campaign_leaderboard.v1",
    "recommendation": "predictor_v3.campaign_recommendation.v1",
}


def inspect_experiment(kind: str, payload: Any) -> ContractDisposition:
    if not isinstance(payload, dict):
        raise ValueError("persisted experiment contract must be an object")
    if payload.get("schema_version") != EXPERIMENT_VERSIONS[kind]:
        raise ValueError(f"unsupported {kind} version")
    if kind == "experiment_specification":
        return _strict_resolved_specification(payload)
    if kind == "run":
        return _run_disposition(payload)
    if kind in {"phase5f_campaign", "agent_campaign"}:
        return _campaign_disposition(kind, payload)
    required = {
        "proposal": {
            "schema_version", "proposal_id", "hypothesis",
            "primary_change_category", "baseline_reference", "delta",
            "expected_effect", "rationale",
        },
        "gate": {
            "schema_version", "candidate_id", "gate_pass", "blocking_reasons",
        },
        "leaderboard": {"schema_version", "entries"},
        "recommendation": {
            "schema_version", "recommendation_id", "campaign_id",
            "recommended_candidate", "hard_gate_results", "approval_required",
            "final_confirmation_required",
        },
    }[kind]
    _require_keys(payload, required)
    if kind == "leaderboard" and not isinstance(payload["entries"], list):
        raise ValueError("leaderboard entries must be an array")
    if kind == "recommendation" and (
        payload["approval_required"] is not True
        or payload["final_confirmation_required"] is not True
    ):
        return ContractDisposition(
            CURRENT_BLOCKED,
            False,
            "recommendation_authority_invalid",
            "Recommendation does not preserve user approval authority.",
            canonical_payload(payload),
        )
    if kind == "recommendation":
        if not isinstance(payload["hard_gate_results"], list):
            raise ValueError("recommendation hard_gate_results must be an array")
        for gate in payload["hard_gate_results"]:
            if not isinstance(gate, dict):
                raise ValueError("recommendation gate projection is invalid")
            _require_keys(
                gate,
                {"candidate_id", "run_id", "gate_pass", "blocking_reasons"},
            )
    return _executable(payload)


def validate_recommendation_evidence(
    recommendation: dict[str, Any],
    *,
    campaign: dict[str, Any],
) -> ContractDisposition:
    recommendation_state = inspect_experiment("recommendation", recommendation)
    if not recommendation_state.executable:
        return recommendation_state
    campaign_kind = (
        "agent_campaign"
        if campaign.get("schema_version") == EXPERIMENT_VERSIONS["agent_campaign"]
        else "phase5f_campaign"
    )
    campaign_state = inspect_experiment(campaign_kind, campaign)
    if not campaign_state.executable:
        return campaign_state
    if recommendation["campaign_id"] != campaign.get("campaign_id"):
        return _blocked(
            "recommendation_campaign_mismatch",
            "Recommendation does not belong to the selected campaign.",
        )
    selected = recommendation.get("recommended_candidate")
    if not isinstance(selected, dict) or not selected.get("candidate_id"):
        return _blocked(
            "recommendation_candidate_missing",
            "Recommendation has no selected Candidate.",
        )
    gates = recommendation.get("hard_gate_results")
    matching = [
        item for item in gates
        if isinstance(item, dict)
        and item.get("candidate_id") == selected["candidate_id"]
    ]
    if len(matching) != 1 or matching[0].get("gate_pass") is not True:
        return _blocked(
            "recommendation_gate_evidence_invalid",
            "Selected Candidate lacks one passing persisted gate result.",
        )
    persisted_gates = [
        gate for gate in campaign.get("gates", ())
        if isinstance(gate, dict)
        and gate.get("candidate_id") == selected["candidate_id"]
    ]
    if len(persisted_gates) != 1:
        return _blocked(
            "recommendation_referenced_gate_missing",
            "Selected Candidate does not resolve to one persisted versioned gate.",
        )
    gate_state = inspect_experiment("gate", persisted_gates[0])
    if not gate_state.executable:
        return gate_state
    if persisted_gates[0].get("gate_pass") != matching[0].get("gate_pass"):
        return _blocked(
            "recommendation_gate_projection_mismatch",
            "Recommendation gate summary differs from persisted gate evidence.",
        )
    return _executable(recommendation)


def _strict_resolved_specification(payload: dict[str, Any]) -> ContractDisposition:
    required = {
        "schema_version", "experiment", "data", "targets", "features",
        "preprocessing", "rfecv", "optuna", "evaluation", "campaign",
        "early_stopping", "retry", "recommendation_thresholds",
    }
    if set(payload) != required:
        return ContractDisposition(
            HISTORICAL_ONLY,
            False,
            "persisted_specification_not_fully_resolved",
            "Persisted specification cannot receive current defaults.",
            canonical_payload(payload),
        )
    return _executable(payload)


def _run_disposition(payload: dict[str, Any]) -> ContractDisposition:
    _require_keys(
        payload,
        {"schema_version", "run_id", "status", "resolved_specification",
         "contract_identity"},
    )
    specification = inspect_experiment(
        "experiment_specification", payload["resolved_specification"]
    )
    if not specification.executable:
        return specification
    identity = payload["contract_identity"]
    if not isinstance(identity, dict) or not identity.get("data_sha256"):
        return ContractDisposition(
            HISTORICAL_ONLY,
            False,
            "run_execution_identity_incomplete",
            "Run is readable but cannot be resumed or confirmed.",
            canonical_payload(payload),
        )
    return _executable(payload)


def _campaign_disposition(
    kind: str, payload: dict[str, Any]
) -> ContractDisposition:
    _require_keys(payload, {"schema_version", "campaign_id", "status"})
    if kind == "agent_campaign":
        _require_keys(
            payload,
            {"resolved_base_specification", "contract_identity", "leaderboard",
             "gates", "recommendations", "attempt_history"},
        )
        leaderboard = inspect_experiment("leaderboard", payload["leaderboard"])
        if not leaderboard.executable:
            return leaderboard
        for gate in payload["gates"]:
            state = inspect_experiment("gate", gate)
            if not state.executable:
                return state
    return _executable(payload)


def _blocked(code: str, message: str) -> ContractDisposition:
    return ContractDisposition(CURRENT_BLOCKED, False, code, message)


def _executable(payload: Any) -> ContractDisposition:
    return ContractDisposition(
        CURRENT_EXECUTABLE,
        True,
        projection=deepcopy(canonical_payload(payload)),
    )


def _require_keys(payload: dict[str, Any], required: set[str]) -> None:
    missing = required.difference(payload)
    if missing:
        raise ValueError("persisted contract field is missing: " + sorted(missing)[0])
