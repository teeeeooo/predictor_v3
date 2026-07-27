"""Qt-free Train run contract payloads."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from core.ml.artifacts import MODEL_FILE, TRAIN_DATA_FILE


DEFAULT_PREPROCESS_VERSION = "v1.0"


@dataclass(frozen=True)
class TrainingRequest:
    """Immutable inputs for one training run."""

    run_id: str
    data_path: str = TRAIN_DATA_FILE
    model_output_path: str = MODEL_FILE
    preprocess_version: str = DEFAULT_PREPROCESS_VERSION
    generation_id: str = ""
    registry_fingerprint: str = ""
    ordered_ml_fingerprint: str = ""
    derived_semantics_fingerprint: str = ""
    one_hot_fingerprint: str = ""
    registry_payload_json: str = ""
    candidate_id: str = ""
    optimization_config_json: str = ""
    derived_evaluation_json: str = ""
    resolved_experiment_json: str = ""
    experiment_contract_fingerprint: str = ""
    production_required_target_ids_json: str = ""
    contains_unpublished_features: bool = False
    exploratory_feature_policy: bool = False
    target_scoped_exploratory: bool = False
    execution_owner: str = "gui"
    campaign_id: str = ""
    publication_source: str = "training"
    confirmation_fixed_parameters_json: str = ""
    confirmation_fixed_features_json: str = ""


@dataclass(frozen=True)
class TrainingLogEvent:
    """One training log line emitted by the service/backend boundary."""

    run_id: str
    message: str
    level: str = "info"


@dataclass(frozen=True)
class TrainingProgress:
    """Training progress payload suitable for worker/controller forwarding."""

    run_id: str
    completed: int = 0
    total: int = 0
    message: str = ""
    indeterminate: bool = True


@dataclass(frozen=True)
class TrainingResult:
    """Structured final result for one training run."""

    run_id: str
    status: str
    summary: str = ""
    model_path: str = ""
    log_path: str = ""
    message: str = ""
    generation_id: str = ""
    registry_fingerprint: str = ""
    candidate_id: str = ""
    publication_outcome: str = ""
    evidence_path: str = ""


@dataclass(frozen=True)
class TrainingResourceStatus:
    """Qt-free training data and model artifact status."""

    data_path: str
    model_path: str
    data_status: str
    model_status: str
    message: str = ""


TrainingLogCallback = Callable[[TrainingLogEvent], None]
TrainingProgressCallback = Callable[[TrainingProgress], None]
