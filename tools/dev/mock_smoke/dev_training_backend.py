"""DEV-only fast training backend for Train execution smoke."""

from __future__ import annotations

from pathlib import Path

import joblib

from apps.train.state.training_run_state import (
    TrainingLogCallback,
    TrainingLogEvent,
    TrainingProgress,
    TrainingProgressCallback,
    TrainingRequest,
    TrainingResult,
)
from tools.dev.mock_smoke.generators import (
    DEFAULT_ROWS,
    DEFAULT_SEED,
    build_mock_prediction_artifact,
)


class DevFastTrainingBackend:
    """Create an inference-compatible mock artifact without real training."""

    def __init__(
        self,
        *,
        rows: int = DEFAULT_ROWS,
        seed: int = DEFAULT_SEED,
        predict_delay_ms: int = 0,
    ) -> None:
        self.rows = rows
        self.seed = seed
        self.predict_delay_ms = predict_delay_ms
        self._cancel_requested = False

    def __call__(
        self,
        request: TrainingRequest,
        log_callback: TrainingLogCallback | None = None,
        progress_callback: TrainingProgressCallback | None = None,
    ) -> TrainingResult:
        """Run the deterministic DEV backend."""
        steps = (
            "Validate mock training input.",
            "Build mock model artifact.",
            "Write model artifact.",
        )
        self._emit_log(log_callback, request.run_id, "DEV fast training started.")
        for completed, message in enumerate(steps, start=1):
            if self._cancel_requested:
                return self._cancelled_result(request, message)
            self._emit_progress(progress_callback, request.run_id, completed - 1, len(steps), message)
            if message == "Build mock model artifact.":
                artifact = build_mock_prediction_artifact(
                    rows=max(self.rows, 5),
                    seed=self.seed,
                    predict_delay_ms=self.predict_delay_ms,
                )
            elif message == "Write model artifact.":
                model_path = Path(request.model_output_path)
                model_path.parent.mkdir(parents=True, exist_ok=True)
                joblib.dump(artifact, model_path)
            self._emit_log(log_callback, request.run_id, message)

        self._emit_progress(
            progress_callback,
            request.run_id,
            len(steps),
            len(steps),
            "DEV fast training finished.",
        )
        return TrainingResult(
            run_id=request.run_id,
            status="complete",
            summary="DEV fast training wrote an inference-compatible mock artifact.",
            model_path=request.model_output_path,
            message="DEV fast training completed.",
        )

    def cancel(self) -> None:
        """Request cooperative cancellation before the next DEV backend step."""
        self._cancel_requested = True

    def _cancelled_result(self, request: TrainingRequest, message: str) -> TrainingResult:
        return TrainingResult(
            run_id=request.run_id,
            status="cancelled",
            model_path=request.model_output_path,
            message=f"DEV fast training cancelled before: {message}",
        )

    def _emit_log(
        self,
        callback: TrainingLogCallback | None,
        run_id: str,
        message: str,
    ) -> None:
        if callback is not None:
            callback(TrainingLogEvent(run_id=run_id, message=message))

    def _emit_progress(
        self,
        callback: TrainingProgressCallback | None,
        run_id: str,
        completed: int,
        total: int,
        message: str,
    ) -> None:
        if callback is not None:
            callback(
                TrainingProgress(
                    run_id=run_id,
                    completed=completed,
                    total=total,
                    message=message,
                    indeterminate=False,
                )
            )
