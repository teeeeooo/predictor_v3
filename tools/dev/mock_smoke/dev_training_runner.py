"""DEV/test-only training backend runner helpers."""

from __future__ import annotations

from apps.train.services.training_service import TrainingService
from apps.train.state.training_run_state import (
    TrainingLogCallback,
    TrainingLogEvent,
    TrainingProgress,
    TrainingProgressCallback,
    TrainingRequest,
    TrainingResult,
)


def run_dev_training_backend(
    request: TrainingRequest,
    backend,  # noqa: ANN001
    log_callback: TrainingLogCallback | None = None,
    progress_callback: TrainingProgressCallback | None = None,
) -> TrainingResult:
    """Run an explicitly supplied DEV/test backend after resource validation."""
    invalid = TrainingService().validate_request(request)
    if invalid is not None:
        _emit_log(log_callback, request.run_id, invalid.message, "error")
        return invalid
    try:
        _emit_progress(
            progress_callback,
            TrainingProgress(
                run_id=request.run_id,
                completed=0,
                total=0,
                message="DEV/test training started.",
                indeterminate=True,
            ),
        )
        return backend(request, log_callback, progress_callback)
    except Exception as exc:  # pragma: no cover - defensive dev helper boundary
        message = str(exc).splitlines()[0]
        _emit_log(log_callback, request.run_id, message, "error")
        return TrainingResult(
            run_id=request.run_id,
            status="error",
            model_path=request.model_output_path,
            message=message,
        )


def _emit_log(
    callback: TrainingLogCallback | None,
    run_id: str,
    message: str,
    level: str = "info",
) -> None:
    if callback is not None:
        callback(TrainingLogEvent(run_id=run_id, message=message, level=level))


def _emit_progress(
    callback: TrainingProgressCallback | None,
    progress: TrainingProgress,
) -> None:
    if callback is not None:
        callback(progress)
