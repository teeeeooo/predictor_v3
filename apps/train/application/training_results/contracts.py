"""Compatibility imports for the shared lifecycle-readable result contract."""

from apps.common.model_lifecycle.training_result_contracts import (  # noqa: F401
    TRAINING_RESULT_SCHEMA_VERSION,
    TrainingAnalysisResult,
    load_training_analysis_payload,
)

__all__ = [
    "TRAINING_RESULT_SCHEMA_VERSION",
    "TrainingAnalysisResult",
    "load_training_analysis_payload",
]
