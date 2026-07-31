"""Qt-free service adapter for core prediction calls."""

from pathlib import Path
from typing import Any

from apps.predict.application.models import (
    PredictionInputRequest,
    PredictionModelStatus,
    PredictionServiceResult,
)
from core.ml.artifacts import MODEL_FILE
from core.ml.inference import load_model, predict_row
from apps.predict.application.runtime_snapshot import PredictRuntimeSnapshot


class PredictionService:
    """Wrap existing core predictor route without changing core behavior."""

    def __init__(
        self,
        model_file: str = MODEL_FILE,
        *,
        runtime_snapshot: PredictRuntimeSnapshot | None = None,
    ) -> None:
        self._model_file = model_file
        self._runtime_snapshot = runtime_snapshot
        self._model_data: Any | None = None
        self._load_error: str = ""

    @property
    def generation_id(self) -> str:
        return self._runtime_snapshot.generation_id if self._runtime_snapshot else "legacy"

    def model_status(self) -> PredictionModelStatus:
        """Return model artifact status without loading the model."""
        model_path = Path(self._model_file)
        path_text = str(model_path)
        if self._model_data is not None:
            return PredictionModelStatus(
                model_path=path_text,
                status="loaded",
                message="Model is loaded.",
            )
        if self._load_error:
            return PredictionModelStatus(
                model_path=path_text,
                status="load-error",
                message=self._load_error,
            )
        if not model_path.exists():
            return PredictionModelStatus(
                model_path=path_text,
                status="missing",
                message="Model artifact is missing.",
            )
        return PredictionModelStatus(
            model_path=path_text,
            status="exists",
            message="Model artifact exists.",
        )

    def prepare_model(self) -> None:
        """Eagerly load and validate a replacement before runtime installation."""
        if self._load_model_data() is None:
            raise ValueError(self._load_error or "Model could not be loaded.")

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
                    context=request.context,
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
                context=request.context,
            )
        try:
            runtime = self._runtime_snapshot
            predictions = predict_row(
                model_data,
                request.row_input,
                targets=runtime.active_targets if runtime is not None else None,
                derived_snapshot=runtime.derived if runtime is not None else None,
                zero_fill_policies=(
                    runtime.zero_fill_policy_by_ml_name if runtime is not None else None
                ),
                ordered_input_features=(
                    runtime.ordered_input_ml_names if runtime is not None else None
                ),
            )
        except Exception as exc:
            return PredictionServiceResult(
                case_id=request.case_id,
                status="error",
                message=str(exc),
                context=request.context,
            )
        return PredictionServiceResult(
            case_id=request.case_id,
            status="complete",
            predictions=predictions,
            context=request.context,
        )

    def _load_model_data(self) -> Any | None:
        if self._model_data is not None:
            return self._model_data
        if self._load_error:
            return None
        try:
            runtime = self._runtime_snapshot
            model_data = (
                load_model(
                    self._model_file,
                    preprocess_version=runtime.preprocessing_version,
                    validate_static_catalog=False,
                )
                if runtime is not None
                else load_model(self._model_file)
            )
            if runtime is not None:
                self._validate_runtime_contract(model_data, runtime)
            self._model_data = model_data
        except Exception as exc:
            self._load_error = str(exc)
            return None
        return self._model_data

    @staticmethod
    def _validate_runtime_contract(
        model_data: Any,
        runtime: PredictRuntimeSnapshot,
    ) -> None:
        contract = model_data.get("training_contract") if isinstance(model_data, dict) else None
        if not isinstance(contract, dict):
            raise ValueError(
                "Active model metadata cannot prove runtime generation compatibility."
            )
        mismatched = tuple(
            key
            for key, expected in runtime.expected_model_contract.items()
            if contract.get(key) != expected
        )
        if mismatched:
            raise ValueError(
                "Active model runtime contract differs: " + ", ".join(mismatched)
            )
