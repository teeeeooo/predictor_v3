"""Shared Qt-free training result contract and application policies."""

from .contracts import (
    TRAINING_RESULT_SCHEMA_VERSION,
    TrainingAnalysisResult,
    load_training_analysis_payload,
)
from .service import TrainingResultService

__all__ = [
    "TRAINING_RESULT_SCHEMA_VERSION",
    "TrainingAnalysisResult",
    "TrainingResultService",
    "load_training_analysis_payload",
]
