"""Training execution controller foundation."""

from __future__ import annotations

from collections.abc import Callable
from uuid import uuid4

from PySide6.QtCore import QThread, QTimer

from apps.train.services.training_service import TrainingService
from apps.train.state.training_run_state import (
    TrainingLogEvent,
    TrainingProgress,
    TrainingRequest,
    TrainingResourceStatus,
    TrainingResult,
)
from apps.train.workers.train_worker import TrainWorker
from core.ml.artifacts import MODEL_FILE, TRAIN_DATA_FILE


StatusCallback = Callable[[str], None]
LogCallback = Callable[[TrainingLogEvent], None]
ProgressCallback = Callable[[TrainingProgress], None]
ResultCallback = Callable[[TrainingResult], None]


class TrainController:
    """Coordinate Train service, worker, and thread lifecycle."""

    def __init__(
        self,
        service: TrainingService | None = None,
        worker_cls: type[TrainWorker] = TrainWorker,
    ) -> None:
        self._service = service or TrainingService()
        self._worker_cls = worker_cls
        self._is_running = False
        self._thread: QThread | None = None
        self._worker: TrainWorker | None = None
        self._last_result: TrainingResult | None = None

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
        self._start_worker(
            training_request,
            status_callback=status_callback,
            log_callback=log_callback,
            progress_callback=progress_callback,
            finished_callback=finished_callback,
            failed_callback=failed_callback,
            cancelled_callback=cancelled_callback,
        )
        return None

    def cancel(self) -> bool:
        """Request cooperative cancellation for the active worker."""
        if self._worker is None:
            return False
        self._worker.cancel()
        return True

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

    def _start_worker(
        self,
        request: TrainingRequest,
        *,
        status_callback: StatusCallback | None,
        log_callback: LogCallback | None,
        progress_callback: ProgressCallback | None,
        finished_callback: ResultCallback | None,
        failed_callback: ResultCallback | None,
        cancelled_callback: ResultCallback | None,
    ) -> None:
        self._is_running = True
        self._thread = QThread()
        self._worker = self._worker_cls(request, service=self._service)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.log_event.connect(lambda event: self._handle_log(event, log_callback))
        self._worker.progress.connect(
            lambda progress: self._handle_progress(
                progress,
                status_callback,
                progress_callback,
            )
        )
        self._worker.finished.connect(
            lambda result: self._handle_finished(
                result,
                status_callback,
                finished_callback,
            )
        )
        self._worker.failed.connect(
            lambda result: self._handle_failed(
                result,
                status_callback,
                failed_callback,
            )
        )
        self._worker.cancelled.connect(
            lambda result: self._handle_cancelled(
                result,
                status_callback,
                cancelled_callback,
            )
        )
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._worker.cancelled.connect(self._thread.quit)
        self._thread.finished.connect(lambda: QTimer.singleShot(0, self._clear_worker_thread))
        self._thread.start()

    def _handle_log(
        self,
        event: TrainingLogEvent,
        log_callback: LogCallback | None,
    ) -> None:
        if log_callback is not None:
            log_callback(event)

    def _handle_progress(
        self,
        progress: TrainingProgress,
        status_callback: StatusCallback | None,
        progress_callback: ProgressCallback | None,
    ) -> None:
        if progress_callback is not None:
            progress_callback(progress)
        if progress.message:
            self._notify(status_callback, progress.message)

    def _handle_finished(
        self,
        result: TrainingResult,
        status_callback: StatusCallback | None,
        finished_callback: ResultCallback | None,
    ) -> None:
        self._is_running = False
        self._last_result = result
        self._notify(status_callback, "Training run finished.")
        if finished_callback is not None:
            finished_callback(result)

    def _handle_failed(
        self,
        result: TrainingResult,
        status_callback: StatusCallback | None,
        failed_callback: ResultCallback | None,
    ) -> None:
        self._is_running = False
        self._last_result = result
        self._notify(status_callback, f"Training run failed: {result.message}")
        if failed_callback is not None:
            failed_callback(result)

    def _handle_cancelled(
        self,
        result: TrainingResult,
        status_callback: StatusCallback | None,
        cancelled_callback: ResultCallback | None,
    ) -> None:
        self._is_running = False
        self._last_result = result
        self._notify(status_callback, "Training run cancelled.")
        if cancelled_callback is not None:
            cancelled_callback(result)

    def _notify(self, callback: StatusCallback | None, message: str) -> None:
        if callback is not None:
            callback(message)

    def _clear_worker_thread(self) -> None:
        self._thread = None
        self._worker = None
