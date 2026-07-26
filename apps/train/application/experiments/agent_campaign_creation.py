"""Creation and baseline classification for one Phase 5G campaign."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from .agent_contracts import AGENT_CAMPAIGN_VERSION, validate_campaign_definition
from .contracts import ExperimentContractError
from .leaderboard import rebuild_leaderboard
from .records import utc_now


def create_agent_campaign(
    experiments,  # noqa: ANN001
    evidence,  # noqa: ANN001
    definition: dict[str, Any],
    *,
    campaign_id: str | None,
) -> dict[str, Any]:
    validated = validate_campaign_definition(definition)
    resolved = experiments.validate(validated["base_specification"])
    if resolved.payload["campaign"]["experiments"]:
        raise ExperimentContractError(
            "agent_campaign_explicit_runs_forbidden",
            "Agent-assisted campaigns accept one external proposal at a time.",
        )
    targets = resolved.payload["targets"]
    if not targets["primary"] or not targets["production_required"]:
        raise ExperimentContractError(
            "agent_target_roles_required",
            "Agent campaigns require explicit primary and production-required Targets.",
        )
    configured_guardrails = {
        item["target"]
        for item in validated["policy"]["ranking"]["guardrail_thresholds"]
    }
    missing_guardrails = set(targets["guardrail"]).difference(configured_guardrails)
    if missing_guardrails:
        raise ExperimentContractError(
            "guardrail_policy_incomplete",
            "Every guardrail Target requires a configured metric threshold.",
        )
    experiments.preflight(resolved)
    baseline = _baseline(experiments, evidence, validated["policy"], resolved)
    experiments.ensure_runtime_initialized()
    identity = campaign_id or f"campaign-{uuid4().hex}"
    maximum = validated["policy"]["max_iterations"]
    record = {
        "schema_version": AGENT_CAMPAIGN_VERSION,
        "campaign_id": identity,
        "mode": "agent_assisted",
        "status": "awaiting_proposal",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "policy": validated["policy"],
        "resolved_base_specification": resolved.payload,
        "contract_identity": experiments.execution_identity(resolved),
        "baseline": baseline,
        "budget": {
            "max_iterations": maximum,
            "consumed_iterations": 0,
            "remaining_iterations": maximum,
        },
        "current": None,
        "current_proposal_id": None,
        "pending_execution": None,
        "proposals": [],
        "iterations": [],
        "attempt_history": [],
        "completed_runs": [],
        "gates": [],
        "leaderboard": rebuild_leaderboard(
            [], policy=validated["policy"], baseline=baseline
        ),
        "incumbent_candidate_id": None,
        "incumbent_specification": None,
        "recommendations": [],
        "recommendation_status": "not_requested",
        "approval_required": True,
        "pause_requested": False,
        "cancel_requested": False,
        "failure": None,
    }
    experiments.store.create_campaign(identity, record)
    return record


def comparison_analysis(evidence, record):  # noqa: ANN001, ANN202
    evidence_id = record["baseline"].get("evidence_candidate_id")
    if not evidence_id:
        return None
    return evidence.candidate_analysis(evidence_id)[0]


def _baseline(experiments, evidence, policy, resolved):  # noqa: ANN001, ANN202
    configured = policy["baseline"]
    active = evidence.active_reference()
    mode = configured["mode"]
    expected_id = active["candidate_id"] if active else None
    if mode == "no_active" and active is not None:
        raise ExperimentContractError(
            "baseline_mode_conflict", "An Active Candidate exists."
        )
    if mode != "no_active" and (
        active is None or configured["active_candidate_id"] != expected_id
    ):
        raise ExperimentContractError(
            "baseline_reference_invalid", "Configured Active reference is stale."
        )
    comparable = False
    evidence_reference = None
    if mode == "comparable_active":
        evidence_id = configured["evidence_candidate_id"]
        if evidence_id != expected_id:
            raise ExperimentContractError(
                "baseline_evidence_invalid",
                "Comparable Active evidence must identify the current Active.",
            )
        analysis, integrity = evidence.candidate_analysis(evidence_id)
        comparable = bool(
            integrity["valid"]
            and analysis
            and analysis.get("training_context", {}).get("training_data", {}).get(
                "sha256"
            )
            == experiments.execution_identity(resolved)["data_sha256"]
            and analysis.get("training_context", {}).get("evaluation")
            == _evaluation_context(resolved.payload)
        )
        if not comparable:
            raise ExperimentContractError(
                "baseline_not_comparable",
                "Active evidence is not comparable under this campaign contract.",
            )
        evidence_reference = f"candidates/{evidence_id}/training_result.json"
    return {
        "mode": mode,
        "active_candidate_id": expected_id,
        "evidence_candidate_id": configured["evidence_candidate_id"],
        "evidence_reference": evidence_reference,
        "comparable": comparable,
        "improvement_claim_allowed": comparable,
        "bootstrap": mode == "no_active",
    }


def _evaluation_context(payload: dict[str, Any]) -> dict[str, Any]:
    evaluation = payload["evaluation"]
    return {
        "scope": f"shuffled_{payload['optuna']['cv_folds']}_fold_cross_validation",
        "fold_count": payload["optuna"]["cv_folds"],
        "seed": evaluation["seed"],
        "splitter": evaluation["splitter"],
    }
