"""Compatibility wrapper for ML inference.

Actual implementation lives in `core.ml.inference`.
"""

from core.ml.inference import CURRENT_PREPROCESS_VERSION, build_input_df, load_model, predict_row

__all__ = [
    "CURRENT_PREPROCESS_VERSION",
    "load_model",
    "build_input_df",
    "predict_row",
]
