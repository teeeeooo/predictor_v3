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
