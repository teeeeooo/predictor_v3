"""Application policy for baseline comparison and promotion snapshots."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from core.ml.training_results import CoreTrainingEvidence

from .contracts import TrainingAnalysisResult


REQUIRED_ARTIFACTS = (
    "training_result.json",
    "analysis/target_metrics.csv",
    "analysis/selected_features.csv",
    "analysis/rfecv_ranking.csv",
    "analysis/feature_importance.csv",
    "analysis/optuna_trials.csv",
    "analysis/best_parameters.csv",
    "analysis/preprocessing_summary.csv",
    "training_report.xlsx",
)


class TrainingResultService:
    """Build one result without redefining core ML metric semantics."""

    def build(
        self,
        *,
        run_id: str,
        candidate_id: str,
        evidence: CoreTrainingEvidence,
        required_target_identities: tuple[str, ...],
        baseline: TrainingAnalysisResult | None = None,
        baseline_identity: str = "",
        baseline_unavailable_reason: str = "",
        contains_unpublished_features: bool = False,
        publication_outcome: str = "pending",
    ) -> TrainingAnalysisResult:
        targets = tuple(dict(item) for item in evidence.targets)
        target_ids = {
            str(item.get("target_identity", "")) for item in targets
            if item.get("status") == "complete"
        }
        missing = tuple(
            identity for identity in required_target_identities
            if identity not in target_ids
        )
        blocking = [
            {"code": "core_training_blocked", "reason": reason}
            for reason in evidence.blocking_reasons
        ]
        if missing:
            blocking.append({
                "code": "required_targets_incomplete",
                "reason": "Missing required target(s): " + ", ".join(missing),
            })
        if contains_unpublished_features:
            blocking.append({
                "code": "unpublished_experimental_features",
                "reason": "Result uses unpublished experimental Features.",
            })
        status = (
            "valid_completed"
            if evidence.status == "complete" and not missing
            else evidence.status
        )
        comparison = _compare_baseline(
            evidence,
            targets,
            baseline,
            baseline_identity=baseline_identity,
            baseline_unavailable_reason=baseline_unavailable_reason,
        )
        eligible = (
            status == "valid_completed"
            and not blocking
            and publication_outcome not in {"failed", "artifact_generation_failed"}
        )
        return TrainingAnalysisResult(
            run={
                "run_id": run_id,
                "candidate_id": candidate_id,
                "status": status,
                "started_at": evidence.started_at,
                "finished_at": evidence.finished_at,
                "duration_seconds": evidence.duration_seconds,
                "publication_outcome": publication_outcome,
            },
            training_context={
                "training_data": {
                    "sha256": evidence.training_data_sha256,
                    "sample_count": evidence.training_data_rows,
                },
                "evaluation": evidence.evaluation_context,
            },
            targets=tuple(_with_delta(item, comparison) for item in targets),
            baseline=comparison["summary"],
            preprocessing=evidence.preprocessing,
            artifacts=tuple(
                {"category": _artifact_category(path), "path": path, "required": True}
                for path in REQUIRED_ARTIFACTS
            ),
            promotion_eligibility={
                "eligible": eligible,
                "snapshot_only": True,
                "promotion_time_revalidation_required": True,
                "evaluated_conditions": [
                    "production_required_target_completeness",
                    "canonical_feature_publication",
                    "required_analysis_artifacts",
                ],
            },
            blocking_reasons=tuple(blocking),
        )

    @staticmethod
    def with_publication(
        result: TrainingAnalysisResult,
        outcome: str,
    ) -> TrainingAnalysisResult:
        run = dict(result.run)
        run["publication_outcome"] = outcome
        eligibility = dict(result.promotion_eligibility)
        if outcome != "published":
            eligibility["eligible"] = False
        return replace(result, run=run, promotion_eligibility=eligibility)


def _compare_baseline(
    evidence: CoreTrainingEvidence,
    targets: tuple[dict[str, Any], ...],
    baseline: TrainingAnalysisResult | None,
    *,
    baseline_identity: str = "",
    baseline_unavailable_reason: str = "",
) -> dict[str, Any]:
    if baseline is None:
        has_identified_baseline = bool(baseline_identity)
        return {
            "summary": {
                "type": (
                    "active_candidate" if has_identified_baseline else "none"
                ),
                "identity": baseline_identity,
                "comparable": False,
                "unavailable_reason": (
                    baseline_unavailable_reason
                    or "No comparable baseline is available (Bootstrap is valid)."
                ),
            },
            "metrics": {},
        }
    same_data = (
        baseline.training_context.get("training_data", {}).get("sha256")
        == evidence.training_data_sha256
    )
    same_evaluation = (
        baseline.training_context.get("evaluation") == evidence.evaluation_context
    )
    if not same_data or not same_evaluation:
        reason = (
            "Training data context differs."
            if not same_data else "Evaluation context differs."
        )
        return {
            "summary": {
                "type": "active_candidate",
                "identity": baseline.run.get("candidate_id", ""),
                "comparable": False,
                "unavailable_reason": reason,
            },
            "metrics": {},
        }
    metrics = {
        str(item["target_identity"]): item["metrics"]
        for item in baseline.targets if item.get("status") == "complete"
    }
    return {
        "summary": {
            "type": "active_candidate",
            "identity": baseline.run.get("candidate_id", ""),
            "comparable": True,
            "unavailable_reason": "",
        },
        "metrics": metrics,
    }


def _with_delta(
    target: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    copied = dict(target)
    baseline_metrics = comparison["metrics"].get(str(target.get("target_identity")))
    if baseline_metrics is None or target.get("status") != "complete":
        copied["baseline_comparison"] = {
            "comparable": False,
            "unavailable_reason": comparison["summary"]["unavailable_reason"]
            or "Target is unavailable in the baseline.",
        }
        return copied
    current = target["metrics"]
    numeric_keys = ("r2", "mae", "rmse")
    if any(
        not isinstance(current.get(key), (int, float))
        or not isinstance(baseline_metrics.get(key), (int, float))
        for key in numeric_keys
    ):
        copied["baseline_comparison"] = {
            "comparable": False,
            "unavailable_reason": "Target metrics are unavailable for numeric comparison.",
        }
        return copied
    copied["baseline_comparison"] = {
        "comparable": True,
        "absolute": dict(current),
        "delta": {
            key: float(current[key]) - float(baseline_metrics[key])
            for key in numeric_keys
        },
    }
    return copied


def _artifact_category(path: str) -> str:
    return path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
