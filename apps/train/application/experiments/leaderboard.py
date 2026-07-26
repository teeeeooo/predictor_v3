"""Deterministic Phase 5G leaderboard and incumbent reconstruction."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .agent_contracts import LEADERBOARD_VERSION


def rebuild_leaderboard(
    gates: list[dict[str, Any]],
    *,
    policy: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any]:
    entries = [_entry(item, policy) for item in gates]
    entries.sort(key=lambda item: _ranking_key(item, policy))
    for rank, item in enumerate(entries, start=1):
        item["rank"] = rank if item["gate_pass"] else None
        item["ranking_reason"] = _ranking_reason(item, policy)
        item["tie_break_basis"] = (
            "candidate_id lexical order after identical persisted ranking evidence"
            if item["gate_pass"] else "hard-gate failure; not ranked"
        )
    valid = [item for item in entries if item["gate_pass"]]
    incumbent = valid[0]["candidate_id"] if valid else None
    return {
        "schema_version": LEADERBOARD_VERSION,
        "baseline": deepcopy(baseline),
        "entries": entries,
        "incumbent_candidate_id": incumbent,
        "deterministic_order": [
            "primary_target_improvement",
            "guardrail_target_behavior",
            "cv_seed_stability",
            "feature_count_and_complexity",
            "physical_plausibility_and_explainability",
            "training_cost_and_reproducibility",
            "candidate_identity_tie_break",
        ],
    }


def _entry(gate: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    primary = gate["primary_target_evidence"]
    direction = policy["ranking"]["direction"]
    value = primary["value"]
    improvement = primary["delta"]
    if improvement is not None and direction == "lower":
        improvement = -improvement
    absolute_preference = (
        (-float(value) if direction == "lower" else float(value))
        if isinstance(value, (int, float)) else None
    )
    return {
        "candidate_id": gate["candidate_id"],
        "run_id": gate["run_id"],
        "gate_pass": gate["gate_pass"],
        "blocking_reasons": deepcopy(gate["blocking_reasons"]),
        "production_eligible": gate["production_eligible"],
        "exploratory_eligible": gate["exploratory_eligible"],
        "target_metrics": deepcopy(gate["target_metrics"]),
        "target_metric_changes": deepcopy(gate["target_metric_changes"]),
        "primary_target_change": deepcopy(primary),
        "primary_improvement_preference": improvement,
        "primary_absolute_preference": absolute_preference,
        "guardrail": deepcopy(gate["guardrail_evidence"]),
        "stability": deepcopy(gate["stability_evidence"]),
        "complexity": deepcopy(gate["complexity_evidence"]),
        "physical_plausibility": deepcopy(
            gate["physical_plausibility_evidence"]
        ),
        "explainability": deepcopy(gate["explainability_evidence"]),
        "training_cost": deepcopy(gate["execution_cost_evidence"]),
        "experimental": gate["experimental"],
    }


def _ranking_key(entry: dict[str, Any], policy: dict[str, Any]) -> tuple[Any, ...]:
    if not entry["gate_pass"]:
        return (1, str(entry["run_id"]))
    primary = entry["primary_improvement_preference"]
    if primary is None:
        primary = entry["primary_absolute_preference"]
    stability = entry["stability"].get("aggregate_std")
    feature_count = entry["complexity"].get("feature_count")
    duration = entry["training_cost"].get("duration_seconds")
    guardrail = entry["guardrail"]
    guardrail_degradation = max(
        (
            float(item["degradation"])
            for item in guardrail["entries"]
            if isinstance(item.get("degradation"), (int, float))
        ),
        default=0.0,
    )
    return (
        0,
        _descending(primary),
        guardrail_degradation,
        _ascending(stability),
        _ascending(feature_count),
        _review_order(entry["physical_plausibility"]["status"]),
        _review_order(entry["explainability"]["status"]),
        _ascending(duration),
        str(entry["candidate_id"]),
    )


def _ranking_reason(entry: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    if not entry["gate_pass"]:
        return {
            "status": "excluded",
            "blocking_reason_codes": [
                item["code"] for item in entry["blocking_reasons"]
            ],
        }
    return {
        "status": "ranked",
        "primary_metric": policy["ranking"]["primary_metric"],
        "direction": policy["ranking"]["direction"],
        "primary_change": entry["primary_target_change"],
        "guardrail_status": (
            entry["guardrail"]["status"]
        ),
        "stability_status": (
            entry["stability"]["status"]
        ),
        "physical_plausibility": entry["physical_plausibility"]["status"],
        "explainability": entry["explainability"]["status"],
    }


def _descending(value: Any) -> tuple[int, float]:
    return (0, -float(value)) if isinstance(value, (int, float)) else (1, 0.0)


def _ascending(value: Any) -> tuple[int, float]:
    return (0, float(value)) if isinstance(value, (int, float)) else (1, 0.0)


def _review_order(status: str) -> int:
    return {"available": 0, "review_required": 1, "unresolved": 2}.get(status, 3)
