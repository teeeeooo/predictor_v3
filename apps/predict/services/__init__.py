"""Qt-free Predict services."""

from apps.predict.services.prediction_service import (
    PredictionService,
    PredictionServiceResult,
)

__all__ = [
    "PredictionService",
    "PredictionServiceResult",
]
