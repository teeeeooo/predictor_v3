"""Training execution controller foundation."""

from __future__ import annotations

from collections.abc import Callable
from uuid import uuid4

from PySide6.QtCore import QObject, Slot

from apps.train.adapters.qprocess_training_runner import QProcessTrainingRunner
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


class TrainController(QObject):
    """Coordinate Train service, worker, and thread lifecycle."""

    def __init__(
        self,
        service: TrainingService | None = None,
        runner: QProcessTrainingRunner | None = None,
        runner_cls: type[QProcessTrainingRunner] = QProcessTrainingRunner,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service or TrainingService()
        self._runner = runner
        self._runner_cls = runner_cls
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
        """Start a worker-backed training run."""
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
        self._start_worker(training_request)
        return None

    def cancel(self) -> bool:
        """Hard-cancel the active training runner when possible."""
        if self._runner is not None:
            return self._runner.cancel()
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

    def _start_worker(self, request: TrainingRequest) -> None:
        self._is_running = True
        runner = self._runner or self._runner_cls()
        self._runner = runner
        runner.log_event.connect(self._handle_log)
        runner.progress.connect(self._handle_progress)
        runner.finished.connect(self._handle_finished)
        runner.failed.connect(self._handle_failed)
        runner.cancelled.connect(self._handle_cancelled)
        runner.finished.connect(self._clear_runner)
        runner.failed.connect(self._clear_runner)
        runner.cancelled.connect(self._clear_runner)
        runner.start(request)

    @Slot(object)
    def _handle_log(self, event: TrainingLogEvent) -> None:
        if self._log_callback is not None:
            self._log_callback(event)

    @Slot(object)
    def _handle_progress(self, progress: TrainingProgress) -> None:
        if self._progress_callback is not None:
            self._progress_callback(progress)
        if progress.message:
            self._notify(self._status_callback, progress.message)

    @Slot(object)
    def _handle_finished(self, result: TrainingResult) -> None:
        self._is_running = False
        self._last_result = result
        self._notify(self._status_callback, "Training run finished.")
        if self._finished_callback is not None:
            self._finished_callback(result)

    @Slot(object)
    def _handle_failed(self, result: TrainingResult) -> None:
        self._is_running = False
        self._last_result = result
        self._notify(self._status_callback, f"Training run failed: {result.message}")
        if self._failed_callback is not None:
            self._failed_callback(result)

    @Slot(object)
    def _handle_cancelled(self, result: TrainingResult) -> None:
        self._is_running = False
        self._last_result = result
        self._notify(self._status_callback, "Training run cancelled.")
        if self._cancelled_callback is not None:
            self._cancelled_callback(result)

    def _notify(self, callback: StatusCallback | None, message: str) -> None:
        if callback is not None:
            callback(message)

    def _clear_runner(self) -> None:
        if self._runner is not None:
            self._runner.deleteLater()
        self._runner = None
        self._clear_callbacks()

    def _clear_callbacks(self) -> None:
        self._status_callback = None
        self._log_callback = None
        self._progress_callback = None
        self._finished_callback = None
        self._failed_callback = None
        self._cancelled_callback = None
