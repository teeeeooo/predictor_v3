"""Compatibility wrapper for ML training.

Actual implementation lives in `core.ml.training`.
"""

from core.ml.training import optimize_and_train, train_all_models

__all__ = [
    "optimize_and_train",
    "train_all_models",
]
