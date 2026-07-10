"""Qt-free training execution controller."""

from __future__ import annotations

from collections.abc import Callable
from uuid import uuid4

from apps.train.ports.training_execution_port import (
    TrainingExecutionCallbacks,
    TrainingExecutionFactory,
    TrainingExecutionPort,
)
from apps.train.services.training_service import TrainingService
from apps.train.state.training_run_state import (
    TrainingLogEvent,
    TrainingProgress,
    TrainingRequest,
    TrainingResourceStatus,
    TrainingResult,
)
from core.ml.artifacts import MODEL_FILE, TRAIN_DATA_FILE


StatusCallback = Callable[[str], None]
LogCallback = Callable[[TrainingLogEvent], None]
ProgressCallback = Callable[[TrainingProgress], None]
ResultCallback = Callable[[TrainingResult], None]


class TrainController:
    """Coordinate validation and a runtime-neutral training execution port."""

    def __init__(
        self,
        service: TrainingService | None = None,
        execution: TrainingExecutionPort | None = None,
        execution_factory: TrainingExecutionFactory | None = None,
    ) -> None:
        self._service = service or TrainingService()
        self._execution = execution
        self._execution_factory = execution_factory
        self._is_running = False
        self._last_result: TrainingResult | None = None
        self._status_callback: StatusCallback | None = None
        self._log_callback: LogCallback | None = None
        self._progress_callback: ProgressCallback | None = None
        self._finished_callback: ResultCallback | None = None
        self._failed_callback: ResultCallback | None = None
        self._cancelled_callback: ResultCallback | None = None

    @property
    def is_running(self) -> bool:
        """Return whether a training run is active."""
        return self._is_running

    @property
    def last_result(self) -> TrainingResult | None:
        """Return the latest terminal training result."""
        return self._last_result

    def resource_status(
        self,
        data_path: str | None = None,
        model_output_path: str | None = None,
    ) -> TrainingResourceStatus:
        """Return data/model status through the service boundary."""
        return self._service.resource_status(data_path, model_output_path)

    def start(
        self,
        request: TrainingRequest | str | None = None,
        *,
        data_path: str | None = None,
        model_output_path: str | None = None,
        status_callback: StatusCallback | None = None,
        log_callback: LogCallback | None = None,
        progress_callback: ProgressCallback | None = None,
        finished_callback: ResultCallback | None = None,
        failed_callback: ResultCallback | None = None,
        cancelled_callback: ResultCallback | None = None,
    ) -> TrainingResult | None:
        """Validate and start a training run through the execution port."""
        if self._is_running:
            raise RuntimeError("Training run already in progress.")

        training_request = self._coerce_request(request, data_path, model_output_path)
        invalid = self._service.validate_request(training_request)
        if invalid is not None:
            self._last_result = invalid
            self._notify(status_callback, invalid.message)
            if failed_callback is not None:
                failed_callback(invalid)
            return invalid

        self._notify(status_callback, "Training run starting.")
        self._status_callback = status_callback
        self._log_callback = log_callback
        self._progress_callback = progress_callback
        self._finished_callback = finished_callback
        self._failed_callback = failed_callback
        self._cancelled_callback = cancelled_callback
        return self._start_execution(training_request)

    def cancel(self) -> bool:
        """Hard-cancel the active training runner when possible."""
        if self._execution is not None:
            return self._execution.cancel()
        return False

    def _coerce_request(
        self,
        request: TrainingRequest | str | None,
        data_path: str | None,
        model_output_path: str | None,
    ) -> TrainingRequest:
        if isinstance(request, TrainingRequest):
            return request
        resolved_data_path = data_path or request or TRAIN_DATA_FILE
        return TrainingRequest(
            run_id=f"train-{uuid4().hex}",
            data_path=str(resolved_data_path),
            model_output_path=str(model_output_path or MODEL_FILE),
        )

    def _start_execution(self, request: TrainingRequest) -> TrainingResult | None:
        execution = self._execution
        if execution is None and self._execution_factory is not None:
            execution = self._execution_factory()
            self._execution = execution
        if execution is None:
            result = TrainingResult(
                run_id=request.run_id,
                status="error",
                model_path=request.model_output_path,
                message="Training execution adapter is not configured.",
            )
            self._last_result = result
            self._notify(self._status_callback, result.message)
            if self._failed_callback is not None:
                self._failed_callback(result)
            self._clear_callbacks()
            return result

        self._is_running = True
        callbacks = TrainingExecutionCallbacks(
            log=self._handle_log,
            progress=self._handle_progress,
            finished=self._handle_finished,
            failed=self._handle_failed,
            cancelled=self._handle_cancelled,
        )
        try:
            execution.start(request, callbacks)
        except Exception as exc:
            result = TrainingResult(
                run_id=request.run_id,
                status="error",
                model_path=request.model_output_path,
                message=str(exc).splitlines()[0],
            )
            self._handle_failed(result)
            return result
        return None

    def _handle_log(self, event: TrainingLogEvent) -> None:
        if self._log_callback is not None:
            self._log_callback(event)

    def _handle_progress(self, progress: TrainingProgress) -> None:
        if self._progress_callback is not None:
            self._progress_callback(progress)
        if progress.message:
            self._notify(self._status_callback, progress.message)

    def _handle_finished(self, result: TrainingResult) -> None:
        self._is_running = False
        self._last_result = result
        self._notify(self._status_callback, "Training run finished.")
        if self._finished_callback is not None:
            self._finished_callback(result)
        self._clear_execution()

    def _handle_failed(self, result: TrainingResult) -> None:
        self._is_running = False
        self._last_result = result
        self._notify(self._status_callback, f"Training run failed: {result.message}")
        if self._failed_callback is not None:
            self._failed_callback(result)
        self._clear_execution()

    def _handle_cancelled(self, result: TrainingResult) -> None:
        self._is_running = False
        self._last_result = result
        self._notify(self._status_callback, "Training run cancelled.")
        if self._cancelled_callback is not None:
            self._cancelled_callback(result)
        self._clear_execution()

    def _notify(self, callback: StatusCallback | None, message: str) -> None:
        if callback is not None:
            callback(message)

    def _clear_execution(self) -> None:
        execution = self._execution
        self._execution = None
        if execution is not None:
            execution.dispose()
        self._clear_callbacks()

    def _clear_callbacks(self) -> None:
        self._status_callback = None
        self._log_callback = None
        self._progress_callback = None
        self._finished_callback = None
        self._failed_callback = None
        self._cancelled_callback = None
