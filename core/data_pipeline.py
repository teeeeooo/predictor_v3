"""Compatibility wrapper for ML preprocessing.

Actual implementation lives in `core.ml.preprocessing`.
"""

from core.ml.preprocessing import calculate_derived_features, load_and_preprocess, prepare_pipeline

__all__ = [
    "calculate_derived_features",
    "prepare_pipeline",
    "load_and_preprocess",
]
