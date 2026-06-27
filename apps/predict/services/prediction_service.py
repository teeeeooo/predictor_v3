"""Qt-free service boundary for core prediction calls."""

from dataclasses import dataclass, field
from typing import Any

from core.ml.artifacts import MODEL_FILE
from core.ml.inference import load_model, predict_row

from apps.predict.adapters.row_to_ml_input_adapter import PredictionInputRequest


@dataclass(frozen=True)
class PredictionServiceResult:
    """Service result for one prediction request."""

    case_id: str
    status: str
    predictions: dict[str, float] = field(default_factory=dict)
    message: str = ""


class PredictionService:
    """Wrap existing core predictor route without changing core behavior."""

    def __init__(self, model_file: str = MODEL_FILE) -> None:
        self._model_file = model_file
        self._model_data: Any | None = None
        self._load_error: str = ""

    def predict_many(
        self,
        requests: list[PredictionInputRequest],
    ) -> list[PredictionServiceResult]:
        """Predict several rows, preserving row-level failure isolation."""
        model_data = self._load_model_data()
        if model_data is None:
            return [
                PredictionServiceResult(
                    case_id=request.case_id,
                    status="error",
                    message=self._load_error,
                )
                for request in requests
            ]
        return [self.predict_one(request) for request in requests]

    def predict_one(self, request: PredictionInputRequest) -> PredictionServiceResult:
        """Predict one row through the existing core predictor route."""
        model_data = self._load_model_data()
        if model_data is None:
            return PredictionServiceResult(
                case_id=request.case_id,
                status="error",
                message=self._load_error,
            )
        try:
            predictions = predict_row(model_data, request.row_input)
        except Exception as exc:
            return PredictionServiceResult(
                case_id=request.case_id,
                status="error",
                message=str(exc),
            )
        return PredictionServiceResult(
            case_id=request.case_id,
            status="complete",
            predictions=predictions,
        )

    def _load_model_data(self) -> Any | None:
        if self._model_data is not None:
            return self._model_data
        if self._load_error:
            return None
        try:
            self._model_data = load_model(self._model_file)
        except Exception as exc:
            self._load_error = str(exc)
            return None
        return self._model_data
