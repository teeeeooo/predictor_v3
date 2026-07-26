"""Pure Phase 5G Candidate hard-gate projection from persisted evidence."""

from __future__ import annotations

from typing import Any

from .agent_contracts import GATE_VERSION
from .gate_thresholds import guardrail_evidence, stability_evidence
from .gate_metrics import (
    mean_feature_count,
    primary_metric_summary,
    target_metric_changes,
)

_BLOCKING_CODE_MAP = {
    "required_targets_incomplete": "production_required_target_failure",
    "core_training_blocked": "production_required_target_failure",
    "target_leakage": "target_leakage",
    "unreproducible_predict_feature": "predict_feature_unreproducible",
    "invalid_derived_feature_output": "invalid_derived_feature_output",
    "unpublished_experimental_features": "unpublished_experimental_feature",
    "candidate_publication_failed": "incomplete_artifact",
    "terminal_artifact_fallback": "incomplete_artifact",
}


def evaluate_candidate(
    analysis: dict[str, Any] | None,
    *,
    run_record: dict[str, Any],
    policy: dict[str, Any],
    baseline_analysis: dict[str, Any] | None,
    artifact_integrity: dict[str, Any],
) -> dict[str, Any]:
    specification = run_record["resolved_specification"]
    result = run_record.get("result") or {}
    run_id = run_record["run_id"]
    candidate_id = result.get("candidate_reference")
    evidence_reference = result.get("evidence_reference")
    blockers: list[dict[str, Any]] = []
    if analysis is None:
        blockers.append(_reason(
            "incomplete_artifact",
            evidence_reference,
            "Structured training analysis is unavailable.",
        ))
        targets: list[dict[str, Any]] = []
        analysis_run: dict[str, Any] = {}
        analysis_blocking: list[dict[str, Any]] = []
    else:
        targets = list(analysis.get("targets", ()))
        analysis_run = analysis.get("run", {})
        analysis_blocking = list(analysis.get("blocking_reasons", ()))

    completed = {
        str(item.get("target_identity")): item
        for item in targets
        if item.get("status") == "complete"
    }
    production_required = set(specification["targets"]["production_required"])
    if production_required and not production_required <= set(completed):
        blockers.append(_reason(
            "production_required_target_failure",
            evidence_reference,
            "One or more production-required Targets are absent or failed.",
        ))
    if (
        run_record["status"] != "success"
        or analysis_run.get("status") not in {"valid_completed", None}
    ):
        blockers.append(_reason(
            "incomplete_result",
            evidence_reference,
            "Partial, failed, or incomplete results are not production eligible.",
        ))
    for item in analysis_blocking:
        source_code = str(item.get("code", "lifecycle_compatibility_failure"))
        blockers.append(_reason(
            _BLOCKING_CODE_MAP.get(source_code, "lifecycle_compatibility_failure"),
            evidence_reference,
            str(item.get("reason", source_code)),
        ))
    if not artifact_integrity.get("valid", False):
        blockers.append(_reason(
            str(artifact_integrity.get("code", "lifecycle_integrity_failure")),
            artifact_integrity.get("evidence_reference"),
            str(artifact_integrity.get("reason", "Candidate integrity is invalid.")),
        ))
    if specification["features"]["experimental_derived"]:
        blockers.append(_reason(
            "unpublished_experimental_feature",
            evidence_reference,
            "Experimental unpublished Features cannot enter a production recommendation.",
        ))
    if _target_scoped(specification):
        blockers.append(_reason(
            "target_scoped_exploration",
            evidence_reference,
            "Target-scoped exploratory results cannot enter a production recommendation.",
        ))

    baseline_targets = _target_map(baseline_analysis)
    primary = primary_metric_summary(
        completed,
        specification["targets"]["primary"],
        policy["ranking"]["primary_metric"],
        baseline_targets,
    )
    if primary["value"] is None:
        blockers.append(_reason(
            "primary_metric_unavailable",
            evidence_reference,
            "Configured primary metric evidence is unavailable.",
        ))
    guardrail = guardrail_evidence(
        completed, baseline_targets, policy["ranking"]["guardrail_thresholds"]
    )
    if guardrail["violation"]:
        blockers.append(_reason(
            "guardrail_violation",
            evidence_reference,
            "A configured guardrail degradation threshold was exceeded.",
        ))
    stability = stability_evidence(
        completed, policy["ranking"]["instability_thresholds"]
    )
    if stability["violation"]:
        blockers.append(_reason(
            "excessive_instability",
            evidence_reference,
            "A configured instability threshold was exceeded.",
        ))

    blockers = _deduplicate(blockers)
    exploratory_blockers = {
        "target_scoped_exploration",
        "unpublished_experimental_feature",
        "production_required_target_failure",
        "incomplete_result",
        "incomplete_artifact",
        "guardrail_violation",
        "excessive_instability",
    }
    if (
        specification["features"]["included"]
        or specification["features"]["excluded"]
    ):
        exploratory_blockers.add("lifecycle_compatibility_failure")
    exploratory_eligible = bool(completed) and all(
        item["code"] in exploratory_blockers for item in blockers
    )
    feature_count = mean_feature_count(completed)
    baseline_feature_count = mean_feature_count(baseline_targets)
    duration = analysis_run.get("duration_seconds")
    return {
        "schema_version": GATE_VERSION,
        "run_id": run_id,
        "candidate_id": candidate_id,
        "gate_pass": not blockers and bool(candidate_id),
        "blocking_reasons": blockers,
        "evidence_reference": evidence_reference,
        "production_eligible": not blockers and bool(candidate_id),
        "exploratory_eligible": exploratory_eligible,
        "target_metrics": {
            identity: dict(item.get("metrics", {}))
            for identity, item in sorted(completed.items())
        },
        "target_metric_changes": target_metric_changes(
            completed, baseline_targets
        ),
        "primary_target_evidence": primary,
        "guardrail_evidence": guardrail,
        "stability_evidence": stability,
        "complexity_evidence": {
            "feature_count": feature_count,
            "baseline_feature_count": baseline_feature_count,
            "delta": (
                feature_count - baseline_feature_count
                if feature_count is not None and baseline_feature_count is not None
                else None
            ),
            "status": "available" if feature_count is not None else "unresolved",
        },
        "physical_plausibility_evidence": {
            "status": "review_required",
            "score": None,
        },
        "explainability_evidence": {
            "status": "review_required",
            "score": None,
        },
        "execution_cost_evidence": {
            "duration_seconds": duration if isinstance(duration, (int, float)) else None,
            "reproducible_contract": True,
        },
        "experimental": bool(
            specification["features"]["experimental_derived"]
            or _target_scoped(specification)
        ),
    }


def _target_map(analysis):  # noqa: ANN001, ANN202
    if not analysis:
        return {}
    return {
        str(item.get("target_identity")): item
        for item in analysis.get("targets", ())
        if item.get("status") == "complete"
    }


def _target_scoped(specification: dict[str, Any]) -> bool:
    selected = set(specification["targets"]["primary"]) | set(
        specification["targets"]["guardrail"]
    )
    required = set(specification["targets"]["production_required"])
    return bool(selected and required and selected != required)


def _reason(code: str, reference: Any, message: str) -> dict[str, Any]:
    return {"code": code, "evidence_reference": reference, "message": message}


def _deduplicate(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return list({item["code"]: item for item in values}.values())
