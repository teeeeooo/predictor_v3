"""Qt-free status and validation boundary for Train resources."""

from __future__ import annotations

from pathlib import Path

from core.ml.artifacts import MODEL_FILE, TRAIN_DATA_FILE
from apps.train.state.training_run_state import (
    TrainingRequest,
    TrainingResourceStatus,
    TrainingResult,
)


class TrainingService:
    """Expose Train resource status and request validation only."""

    def resource_status(
        self,
        data_path: str | None = None,
        model_output_path: str | None = None,
    ) -> TrainingResourceStatus:
        """Return lightweight data/model status for controller/UI display."""
        data = Path(data_path or TRAIN_DATA_FILE)
        model = Path(model_output_path or MODEL_FILE)
        data_status = "exists" if data.exists() else "missing"
        model_status = "exists" if model.exists() else "missing"
        messages = []
        if data_status == "missing":
            messages.append(f"Training data is missing: {data}")
        if model_status == "missing":
            messages.append(f"Model artifact is missing: {model}")
        return TrainingResourceStatus(
            data_path=str(data),
            model_path=str(model),
            data_status=data_status,
            model_status=model_status,
            message="; ".join(messages),
        )

    def validate_request(self, request: TrainingRequest) -> TrainingResult | None:
        """Return an error result when request resources are not runnable."""
        data_path = Path(request.data_path)
        if not data_path.exists():
            return TrainingResult(
                run_id=request.run_id,
                status="error",
                model_path=request.model_output_path,
                message=f"Training data is missing: {data_path}",
            )
        if not data_path.is_file():
            return TrainingResult(
                run_id=request.run_id,
                status="error",
                model_path=request.model_output_path,
                message=f"Training data is not a file: {data_path}",
            )
        return None
