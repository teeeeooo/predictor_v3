"""Qt-free Predict adapters."""

from apps.predict.adapters.row_to_ml_input_adapter import (
    RowToMlInputAdapter,
)
from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter

__all__ = [
    "PredictionResultAdapter",
    "RowToMlInputAdapter",
]
