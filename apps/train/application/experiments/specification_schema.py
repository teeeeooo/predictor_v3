"""Closed Phase 5F Experiment Specification field catalog and defaults."""

from __future__ import annotations

from typing import Any

from .contracts import (
    EXPERIMENT_SPEC_VERSION,
    METRIC_CONTRACT_ID,
)

PROJECT_DEFAULTS: dict[str, Any] = {
    "schema_version": EXPERIMENT_SPEC_VERSION,
    "experiment": {"name": "training-run", "purpose": ""},
    "data": {"source_path": "", "snapshot_request": None},
    "targets": {
        "primary": [],
        "guardrail": [],
        "production_required": [],
    },
    "features": {
        "included": [],
        "excluded": [],
        "experimental_derived": [],
    },
    "preprocessing": {"contract_version": "v1.0"},
    "rfecv": {"mode": "registry"},
    "optuna": {
        "cv_folds": 5,
        "trials": 30,
        "n_estimators_min": 100,
        "n_estimators_max": 500,
        "n_jobs": -1,
        "sampler_seed": None,
    },
    "evaluation": {
        "metric_contract": METRIC_CONTRACT_ID,
        "splitter": "KFold",
        "shuffle": True,
        "seed": 42,
    },
    "campaign": {"max_iterations": 1, "experiments": []},
    "early_stopping": {
        "enabled": False,
        "policy_version": "phase5g-reserved.v1",
        "max_consecutive_non_improving": 0,
    },
    "retry": {"max_attempts": 1, "retryable_statuses": ["training_failure"]},
    "recommendation_thresholds": {},
}

SPECIFICATION_SHAPE = {
    "schema_version": None,
    "experiment": {"name": None, "purpose": None},
    "data": {"source_path": None, "snapshot_request": None},
    "targets": {"primary": None, "guardrail": None, "production_required": None},
    "features": {
        "included": None,
        "excluded": None,
        "experimental_derived": None,
    },
    "preprocessing": {"contract_version": None},
    "rfecv": {"mode": None},
    "optuna": {
        "cv_folds": None,
        "trials": None,
        "n_estimators_min": None,
        "n_estimators_max": None,
        "n_jobs": None,
        "sampler_seed": None,
    },
    "evaluation": {
        "metric_contract": None,
        "splitter": None,
        "shuffle": None,
        "seed": None,
    },
    "campaign": {"max_iterations": None, "experiments": None},
    "early_stopping": {
        "enabled": None,
        "policy_version": None,
        "max_consecutive_non_improving": None,
    },
    "retry": {"max_attempts": None, "retryable_statuses": None},
    "recommendation_thresholds": None,
}
