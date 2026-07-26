"""Immutable Phase 5G recommendation artifact projection."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .agent_contracts import RECOMMENDATION_VERSION


def build_recommendation(
    campaign: dict[str, Any],
    *,
    recommendation_id: str,
    created_at: str,
) -> dict[str, Any]:
    leaderboard = campaign["leaderboard"]
    ranked = [
        item for item in leaderboard["entries"]
        if item["gate_pass"] and item.get("rank") is not None
    ]
    ranked.sort(key=lambda item: item["rank"])
    top = ranked[0] if ranked else None
    runner_up = ranked[1] if len(ranked) > 1 else None
    baseline = campaign["baseline"]
    recommended, conclusion = _selection(top, baseline, campaign["policy"])
    iteration = _candidate_iteration(campaign, recommended)
    feature_changes = _feature_changes(iteration)
    rejected = [
        {
            "candidate_id": item["candidate_id"],
            "run_id": item["run_id"],
            "reason_codes": [
                reason["code"] for reason in item["blocking_reasons"]
            ],
        }
        for item in leaderboard["entries"] if not item["gate_pass"]
    ]
    artifact = {
        "schema_version": RECOMMENDATION_VERSION,
        "recommendation_contract_version": RECOMMENDATION_VERSION,
        "recommendation_id": recommendation_id,
        "campaign_id": campaign["campaign_id"],
        "created_at": created_at,
        "recommended_candidate": (
            _candidate_summary(recommended) if recommended else None
        ),
        "runner_up": _candidate_summary(runner_up) if runner_up else None,
        "current_active_or_campaign_baseline": deepcopy(baseline),
        "target_level_metric_changes": (
            deepcopy(recommended["target_metric_changes"]) if recommended else None
        ),
        "stability_change": (
            deepcopy(recommended["stability"]) if recommended else None
        ),
        "feature_count_change": (
            deepcopy(recommended["complexity"]) if recommended else None
        ),
        "feature_additions": feature_changes["included"],
        "feature_exclusions": feature_changes["excluded"],
        "experimental_derived_feature_proposal": feature_changes["derived"],
        "rejected_candidates": rejected,
        "hard_gate_results": [
            {
                "candidate_id": item["candidate_id"],
                "run_id": item["run_id"],
                "gate_pass": item["gate_pass"],
                "blocking_reasons": deepcopy(item["blocking_reasons"]),
                "guardrail_evidence": deepcopy(item["guardrail"]),
                "stability_evidence": deepcopy(item["stability"]),
            }
            for item in leaderboard["entries"]
        ],
        "uncertainty_and_limitations": _limitations(campaign, top),
        "additional_experiment_or_budget_extension": _next_action(campaign, top),
        "final_confirmation_required": True,
        "approval_required": True,
        "production_ready": False,
        "conclusion": conclusion,
    }
    artifact["human_summary"] = _human_summary(artifact)
    return artifact


def _selection(top, baseline, policy):  # noqa: ANN001, ANN202
    if top is None:
        return None, "no_recommendation"
    mode = baseline["mode"]
    if mode == "unbenchmarked_active":
        return None, "keep_current_active"
    if mode == "comparable_active":
        change = top["primary_target_change"]
        delta = change.get("delta")
        direction = policy["ranking"]["direction"]
        improvement = (
            -float(delta) if direction == "lower" and delta is not None
            else float(delta) if delta is not None else None
        )
        if improvement is None or improvement <= float(policy["ranking"]["tolerance"]):
            return None, "keep_current_active"
    return top, "candidate_recommended_for_phase5h_confirmation"


def _candidate_summary(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": entry["candidate_id"],
        "run_id": entry["run_id"],
        "rank": entry["rank"],
        "production_eligible": entry["production_eligible"],
        "experimental": entry["experimental"],
    }


def _candidate_iteration(campaign, entry):  # noqa: ANN001, ANN202
    if entry is None:
        return None
    return next(
        (
            item for item in campaign["iterations"]
            if item.get("candidate_id") == entry["candidate_id"]
        ),
        None,
    )


def _feature_changes(iteration):  # noqa: ANN001, ANN202
    if not iteration:
        return {"included": [], "excluded": [], "derived": []}
    after = iteration["resolved_specification_after"]["features"]
    before = iteration["resolved_specification_before"]["features"]
    return {
        "included": sorted(set(after["included"]) - set(before["included"])),
        "excluded": sorted(set(after["excluded"]) - set(before["excluded"])),
        "derived": deepcopy(after["experimental_derived"]),
    }


def _limitations(campaign, top):  # noqa: ANN001, ANN202
    values = [
        "Phase 5H independent final confirmation and optional locked final test remain required.",
        "Recommendation does not promote, publish a Definition, or replace deployment.",
    ]
    if campaign["baseline"]["mode"] == "unbenchmarked_active":
        values.append(
            "The current Active is unbenchmarked; no improvement over Active is claimed."
        )
    if campaign["baseline"]["mode"] == "no_active":
        values.append(
            "Bootstrap ranking does not establish production readiness."
        )
    if top and (
        top["physical_plausibility"]["status"] != "available"
        or top["explainability"]["status"] != "available"
    ):
        values.append(
            "Physical plausibility or explainability evidence requires human review."
        )
    return values


def _next_action(campaign, top):  # noqa: ANN001, ANN202
    remaining = campaign["budget"]["remaining_iterations"]
    if top is None and remaining:
        return {"action": "additional_experiment", "budget_extension_suggested": False}
    if top is None and not remaining:
        return {"action": "operator_review", "budget_extension_suggested": True}
    return {"action": "phase5h_confirmation", "budget_extension_suggested": False}


def _human_summary(artifact: dict[str, Any]) -> str:
    candidate = artifact["recommended_candidate"]
    if candidate is None:
        return (
            "No Candidate is recommended. Keep the current Active when one exists. "
            "Approval and operator review are required."
        )
    return (
        f"Candidate {candidate['candidate_id']} is recommended only for Phase 5H "
        "confirmation. Approval is required; no production mutation was performed."
    )
