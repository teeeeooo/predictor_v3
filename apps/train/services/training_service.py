"""Qt-free service boundary for model training execution."""

from __future__ import annotations

from pathlib import Path

from core.ml.artifacts import MODEL_FILE, TRAIN_DATA_FILE
from apps.train.state.training_run_state import (
    TrainingLogCallback,
    TrainingLogEvent,
    TrainingProgress,
    TrainingProgressCallback,
    TrainingRequest,
    TrainingResourceStatus,
    TrainingResult,
)


class TrainingService:
    """Validate Train resources and host explicitly injected test backends."""

    def __init__(self, backend=None) -> None:  # noqa: ANN001
        self._backend = backend

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

    def train(
        self,
        request: TrainingRequest,
        log_callback: TrainingLogCallback | None = None,
        progress_callback: TrainingProgressCallback | None = None,
    ) -> TrainingResult:
        """Run an explicitly injected backend for tests/dev helpers only."""
        invalid = self.validate_request(request)
        if invalid is not None:
            self._emit_log(log_callback, request.run_id, invalid.message, "error")
            return invalid
        if self._backend is None:
            message = (
                "Direct TrainingService.train execution is disabled; use "
                "QProcessTrainingRunner for production UI training."
            )
            self._emit_log(log_callback, request.run_id, message, "error")
            return TrainingResult(
                run_id=request.run_id,
                status="error",
                model_path=request.model_output_path,
                message=message,
            )
        try:
            self._emit_progress(
                progress_callback,
                TrainingProgress(
                    run_id=request.run_id,
                    completed=0,
                    total=0,
                    message="Training started.",
                    indeterminate=True,
                ),
            )
            return self._backend(request, log_callback, progress_callback)
        except Exception as exc:  # pragma: no cover - defensive service boundary
            message = str(exc).splitlines()[0]
            self._emit_log(log_callback, request.run_id, message, "error")
            return TrainingResult(
                run_id=request.run_id,
                status="error",
                model_path=request.model_output_path,
                message=message,
            )

    def cancel(self) -> bool:
        """Request cooperative backend cancellation when supported."""
        cancel = getattr(self._backend, "cancel", None)
        if not callable(cancel):
            return False
        cancel()
        return True

    def _emit_log(
        self,
        callback: TrainingLogCallback | None,
        run_id: str,
        message: str,
        level: str = "info",
    ) -> None:
        if callback is not None:
            callback(TrainingLogEvent(run_id=run_id, message=message, level=level))

    def _emit_progress(
        self,
        callback: TrainingProgressCallback | None,
        progress: TrainingProgress,
    ) -> None:
        if callback is not None:
            callback(progress)
