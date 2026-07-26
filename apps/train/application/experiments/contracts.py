"""Strict declarative Experiment Specification contracts and resolution."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.ml.training_results import TrainingOptimizationConfig

EXPERIMENT_SPEC_VERSION = "predictor_v3.experiment.v1"
EXPERIMENT_OUTPUT_VERSION = "predictor_v3.experiment_output.v1"
CAMPAIGN_RECORD_VERSION = "predictor_v3.campaign.v1"
RUN_RECORD_VERSION = "predictor_v3.experiment_run.v1"
TRAINING_EXECUTION_ID = "training_lifecycle.v1"
METRIC_CONTRACT_ID = "core_training_evidence.v1"


class ExperimentContractError(ValueError):
    """Specification cannot be safely interpreted under the current contract."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ResolvedExperiment:
    payload: dict[str, Any]
    fingerprint: str

    def to_json(self) -> str:
        return json.dumps(
            self.payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )


def load_specification(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExperimentContractError(
            "specification_unreadable", f"Experiment specification is unreadable: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise ExperimentContractError(
            "specification_type_invalid", "Experiment specification must be an object."
        )
    return payload


def resolve_specification(
    explicit: dict[str, Any],
    *,
    campaign: dict[str, Any] | None = None,
) -> ResolvedExperiment:
    from .specification_schema import PROJECT_DEFAULTS, SPECIFICATION_SHAPE

    _reject_unknown(explicit, SPECIFICATION_SHAPE, "")
    if campaign is not None:
        _reject_unknown(campaign, SPECIFICATION_SHAPE, "")
    version = explicit.get(
        "schema_version",
        (campaign or {}).get("schema_version", EXPERIMENT_SPEC_VERSION),
    )
    if version != EXPERIMENT_SPEC_VERSION:
        raise ExperimentContractError(
            "unsupported_specification_version",
            f"Unsupported Experiment Specification version: {version!r}.",
        )
    resolved = _merge(PROJECT_DEFAULTS, campaign or {})
    resolved = _merge(resolved, explicit)
    resolved["schema_version"] = EXPERIMENT_SPEC_VERSION
    _validate_resolved(resolved)
    encoded = json.dumps(
        resolved, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return ResolvedExperiment(resolved, hashlib.sha256(encoded).hexdigest())


def optimization_config(payload: dict[str, Any]) -> TrainingOptimizationConfig:
    optuna = payload["optuna"]
    config = TrainingOptimizationConfig(
        cv_folds=optuna["cv_folds"],
        optuna_trials=optuna["trials"],
        n_estimators_min=optuna["n_estimators_min"],
        n_estimators_max=optuna["n_estimators_max"],
        n_jobs=optuna["n_jobs"],
        optuna_sampler_seed=optuna["sampler_seed"],
    )
    config.validate()
    return config


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for key, value in base.items():
        replacement = override.get(key, value)
        if isinstance(value, dict) and isinstance(replacement, dict):
            merged[key] = _merge(value, replacement)
        else:
            merged[key] = replacement
    return merged


def _reject_unknown(payload: Any, shape: Any, prefix: str) -> None:
    if not isinstance(payload, dict):
        raise ExperimentContractError(
            "specification_type_invalid", f"{prefix or 'specification'} must be an object."
        )
    unknown = sorted(set(payload).difference(shape))
    if unknown:
        field = f"{prefix}.{unknown[0]}" if prefix else unknown[0]
        raise ExperimentContractError(
            "unsupported_specification_field", f"Unsupported specification field: {field}."
        )
    for key, value in payload.items():
        if isinstance(shape[key], dict) and value is not None:
            _reject_unknown(value, shape[key], f"{prefix}.{key}".strip("."))


def _validate_resolved(payload: dict[str, Any]) -> None:
    experiment = payload["experiment"]
    if not isinstance(experiment["name"], str) or not experiment["name"].strip():
        raise ExperimentContractError(
            "experiment_name_invalid", "experiment.name must be a non-empty string."
        )
    source_path = payload["data"]["source_path"]
    if not isinstance(source_path, str) or not source_path:
        raise ExperimentContractError(
            "data_source_missing", "data.source_path must identify a training file."
        )
    if payload["data"]["snapshot_request"] is not None:
        raise ExperimentContractError(
            "snapshot_request_unsupported",
            "Data snapshot requests are reserved for Phase 5H; use source_path.",
        )
    for section, keys in (
        ("targets", ("primary", "guardrail", "production_required")),
        ("features", ("included", "excluded", "experimental_derived")),
    ):
        for key in keys:
            if not isinstance(payload[section][key], list):
                raise ExperimentContractError(
                    "specification_type_invalid", f"{section}.{key} must be an array."
                )
            if section == "targets" or key in {"included", "excluded"}:
                if any(type(item) is not str or not item for item in payload[section][key]):
                    raise ExperimentContractError(
                        "specification_type_invalid",
                        f"{section}.{key} must contain non-empty strings.",
                    )
    if set(payload["features"]["included"]) & set(payload["features"]["excluded"]):
        raise ExperimentContractError(
            "feature_policy_conflict", "A Feature cannot be both included and excluded."
        )
    if payload["preprocessing"]["contract_version"] != "v1.0":
        raise ExperimentContractError(
            "preprocessing_contract_unsupported",
            "Unsupported preprocessing contract version.",
        )
    if payload["rfecv"]["mode"] != "registry":
        raise ExperimentContractError(
            "rfecv_mode_unsupported", "rfecv.mode must be 'registry'."
        )
    if (
        payload["evaluation"]["metric_contract"] != METRIC_CONTRACT_ID
        or payload["evaluation"]["splitter"] != "KFold"
        or payload["evaluation"]["shuffle"] is not True
        or payload["evaluation"]["seed"] != 42
    ):
        raise ExperimentContractError(
            "evaluation_contract_unsupported",
            "Evaluation plan is not supported by the current training owner.",
        )
    optimization_config(payload)
    for section, key, minimum in (
        ("campaign", "max_iterations", 1),
        ("retry", "max_attempts", 1),
    ):
        value = payload[section][key]
        if type(value) is not int or value < minimum:
            raise ExperimentContractError(
                "budget_invalid", f"{section}.{key} must be at least {minimum}."
            )
    if payload["retry"]["max_attempts"] > 5:
        raise ExperimentContractError(
            "retry_policy_unbounded", "retry.max_attempts cannot exceed 5."
        )
    if payload["campaign"]["max_iterations"] > 100:
        raise ExperimentContractError(
            "campaign_budget_unbounded", "campaign.max_iterations cannot exceed 100."
        )
    if not isinstance(payload["campaign"]["experiments"], list):
        raise ExperimentContractError(
            "specification_type_invalid", "campaign.experiments must be an array."
        )
    if any(
        not isinstance(item, dict) for item in payload["campaign"]["experiments"]
    ):
        raise ExperimentContractError(
            "specification_type_invalid",
            "campaign.experiments must contain specification objects.",
        )
    retryable = payload["retry"]["retryable_statuses"]
    if (
        not isinstance(retryable, list)
        or any(item != "training_failure" for item in retryable)
    ):
        raise ExperimentContractError(
            "retry_policy_unsupported",
            "Only training_failure is a retryable Phase 5F status.",
        )
    early = payload["early_stopping"]
    if (
        type(early["enabled"]) is not bool
        or early["policy_version"] != "phase5g-reserved.v1"
        or type(early["max_consecutive_non_improving"]) is not int
        or early["max_consecutive_non_improving"] < 0
    ):
        raise ExperimentContractError(
            "early_stopping_policy_unsupported",
            "Early-stopping policy is reserved and must use the v1 declarative contract.",
        )
    if not isinstance(payload["recommendation_thresholds"], dict):
        raise ExperimentContractError(
            "specification_type_invalid",
            "recommendation_thresholds must be an object.",
        )
