"""Core-owned training optimization and evaluation evidence."""

from .contracts import CoreTrainingEvidence, CoreTrainingOutput
from .optimization import (
    TrainingOptimizationConfig,
    optimize_and_train,
    summarize_fold_metrics,
)

__all__ = [
    "CoreTrainingEvidence",
    "CoreTrainingOutput",
    "TrainingOptimizationConfig",
    "optimize_and_train",
    "summarize_fold_metrics",
]
