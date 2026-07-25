"""Tabular projections derived from one training result contract."""

from __future__ import annotations

import json
from typing import Any

from apps.train.application.training_results import TrainingAnalysisResult


def result_tables(
    result: TrainingAnalysisResult,
) -> dict[str, list[dict[str, Any]]]:
    metrics: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    rfecv: list[dict[str, Any]] = []
    importance: list[dict[str, Any]] = []
    trials: list[dict[str, Any]] = []
    parameters: list[dict[str, Any]] = []
    for target in result.targets:
        identity = target.get("target_identity", "")
        metric = target.get("metrics", {})
        metrics.append({
            "target_identity": identity,
            "target_ml_name": target.get("target_ml_name", ""),
            "status": target.get("status", ""),
            "evaluation_scope": metric.get("evaluation_scope", ""),
            "sample_count": metric.get("sample_count", ""),
            "r2": metric.get("r2", ""),
            "mae": metric.get("mae", ""),
            "rmse": metric.get("rmse", ""),
            "fold_count": metric.get("fold_count", ""),
            "seed": metric.get("seed", ""),
            "r2_std": metric.get("r2_std", ""),
            "mae_std": metric.get("mae_std", ""),
            "rmse_std": metric.get("rmse_std", ""),
        })
        for item in target.get("rfecv", {}).get("features", []):
            row = {"target_identity": identity, **item}
            rfecv.append(row)
            if item.get("selected"):
                selected.append(row)
        for item in target.get("feature_importance", []):
            importance.append({"target_identity": identity, **item})
        optuna = target.get("optuna", {})
        for name, value in optuna.get("selected_parameters", {}).items():
            parameters.append({
                "target_identity": identity,
                "parameter": name,
                "value": value,
                "status": optuna.get("status", ""),
            })
        for item in optuna.get("trials", []):
            trials.append({
                "target_identity": identity,
                **item,
                "parameters": json.dumps(
                    item.get("parameters", {}), ensure_ascii=False, sort_keys=True
                ),
            })
    preprocessing = [
        {
            **item,
            "target_usage": "|".join(item.get("target_usage", ())),
        }
        for item in result.preprocessing.get("feature_data_quality", ())
    ]
    return {
        "target_metrics.csv": metrics,
        "selected_features.csv": selected,
        "rfecv_ranking.csv": rfecv,
        "feature_importance.csv": importance,
        "optuna_trials.csv": trials,
        "best_parameters.csv": parameters,
        "preprocessing_summary.csv": preprocessing,
    }


def workbook_tables(
    result: TrainingAnalysisResult,
    tables: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    summary = [{
        "run_id": result.run.get("run_id", ""),
        "candidate_id": result.run.get("candidate_id", ""),
        "status": result.run.get("status", ""),
        "promotion_eligible": result.promotion_eligibility.get("eligible", False),
        "baseline_type": result.baseline.get("type", ""),
        "baseline_identity": result.baseline.get("identity", ""),
        "baseline_comparable": result.baseline.get("comparable", False),
        "blocking_reasons": " | ".join(
            item["reason"] for item in result.blocking_reasons
        ),
    }]
    run_info = [{
        **result.run,
        "training_data_sha256": result.training_context.get(
            "training_data", {}
        ).get("sha256", ""),
        "training_sample_count": result.training_context.get(
            "training_data", {}
        ).get("sample_count", ""),
        "evaluation_context": json.dumps(
            result.training_context.get("evaluation", {}),
            ensure_ascii=False,
            sort_keys=True,
        ),
    }]
    return {
        "Summary": summary,
        "Target Metrics": tables["target_metrics.csv"],
        "Selected Features": tables["selected_features.csv"],
        "RFECV Ranking": tables["rfecv_ranking.csv"],
        "Feature Importance": tables["feature_importance.csv"],
        "Optuna Best Parameters": tables["best_parameters.csv"],
        "Optuna Trials": tables["optuna_trials.csv"],
        "Preprocessing": tables["preprocessing_summary.csv"],
        "Run Information": run_info,
    }
