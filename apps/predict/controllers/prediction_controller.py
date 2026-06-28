"""Prediction execution controller foundation."""

from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

from PySide6.QtCore import QThread, QTimer

from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter
from apps.predict.adapters.row_to_ml_input_adapter import (
    PredictionInputRequest,
    RowToMlInputAdapter,
)
from apps.predict.services.prediction_service import (
    PredictionModelStatus,
    PredictionServiceResult,
    PredictionService,
)
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow
from apps.predict.workers.prediction_worker import (
    PredictionJob,
    PredictionProgress,
    PredictionWorker,
    PredictionWorkerSummary,
)


StatusCallback = Callable[[str], None]
ResultCallback = Callable[[ResultRow], None]
ProgressCallback = Callable[[PredictionProgress], None]
SummaryCallback = Callable[["PredictionRunSummary"], None]


@dataclass(frozen=True)
class PredictionRunSummary:
    """Batch prediction run counts."""

    total: int
    complete: int
    error: int
    invalid: int
    cancelled: int = 0


class PredictionController:
    """Coordinate prediction inputs, service calls, and session updates."""

    def __init__(
        self,
        session: PredictSession,
        input_adapter: RowToMlInputAdapter | None = None,
        service: PredictionService | None = None,
        result_adapter: PredictionResultAdapter | None = None,
    ) -> None:
        self._session = session
        self._input_adapter = input_adapter or RowToMlInputAdapter()
        self._service = service or PredictionService()
        self._result_adapter = result_adapter or PredictionResultAdapter()
        self._is_running = False
        self._thread: QThread | None = None
        self._worker: PredictionWorker | None = None
        self._active_total = 0
        self._active_invalid = 0

    @property
    def is_running(self) -> bool:
        """Return whether a prediction run is active."""
        return self._is_running

    def model_status(self) -> PredictionModelStatus:
        """Return Qt-free model status through the service boundary."""
        return self._service.model_status()

    def start_all(
        self,
        status_callback: StatusCallback | None = None,
        result_callback: ResultCallback | None = None,
        progress_callback: ProgressCallback | None = None,
        finished_callback: SummaryCallback | None = None,
    ) -> PredictionRunSummary:
        """Start asynchronous prediction for every current case row."""
        return self.start_case_ids(
            list(self._session.case_order),
            status_callback=status_callback,
            result_callback=result_callback,
            progress_callback=progress_callback,
            finished_callback=finished_callback,
        )

    def start_case_ids(
        self,
        case_ids: list[str],
        status_callback: StatusCallback | None = None,
        result_callback: ResultCallback | None = None,
        progress_callback: ProgressCallback | None = None,
        finished_callback: SummaryCallback | None = None,
    ) -> PredictionRunSummary:
        """Start worker-backed prediction for selected case ids."""
        if self._is_running:
            raise RuntimeError("Prediction run already in progress.")

        total = len(case_ids)
        self._notify(status_callback, f"Starting prediction for {total} rows.")
        valid_requests: list[PredictionInputRequest] = []
        invalid_count = 0
        for case_id in case_ids:
            case = self._session.case_store.get_case(case_id)
            outcome = self._input_adapter.build_request(case)
            if not outcome.is_valid:
                result = self._result_adapter.invalid_result(
                    case_id=case_id,
                    message="; ".join(outcome.errors),
                )
                self._record_result(result, result_callback)
                invalid_count += 1
                continue
            if outcome.request is None:
                continue
            self._record_result(
                self._result_adapter.running_result(case_id),
                result_callback,
            )
            valid_requests.append(outcome.request)

        initial_summary = PredictionRunSummary(
            total=total,
            complete=0,
            error=0,
            invalid=invalid_count,
        )
        if not valid_requests:
            self._notify(status_callback, "Prediction run finished.")
            if finished_callback is not None:
                finished_callback(initial_summary)
            return initial_summary

        self._start_worker(
            valid_requests,
            total=total,
            invalid_count=invalid_count,
            status_callback=status_callback,
            result_callback=result_callback,
            progress_callback=progress_callback,
            finished_callback=finished_callback,
        )
        return initial_summary

    def cancel(self) -> None:
        """Request cancellation for the active worker, if any."""
        if self._worker is not None:
            self._worker.cancel()

    def run_all(
        self,
        status_callback: StatusCallback | None = None,
        result_callback: ResultCallback | None = None,
    ) -> PredictionRunSummary:
        """Run prediction for every current case row."""
        return self.run_case_ids(
            list(self._session.case_order),
            status_callback=status_callback,
            result_callback=result_callback,
        )

    def run_case_ids(
        self,
        case_ids: list[str],
        status_callback: StatusCallback | None = None,
        result_callback: ResultCallback | None = None,
    ) -> PredictionRunSummary:
        """Run prediction for selected case ids."""
        total = len(case_ids)
        self._notify(status_callback, f"Starting prediction for {total} rows.")

        valid_requests = []
        counts = {"complete": 0, "error": 0, "invalid": 0}
        for case_id in case_ids:
            case = self._session.case_store.get_case(case_id)
            outcome = self._input_adapter.build_request(case)
            if not outcome.is_valid:
                result = self._result_adapter.invalid_result(
                    case_id=case_id,
                    message="; ".join(outcome.errors),
                )
                self._record_result(result, result_callback)
                counts["invalid"] += 1
                continue
            running = self._result_adapter.running_result(case_id)
            self._record_result(running, result_callback)
            valid_requests.append(outcome.request)

        service_results = self._service.predict_many(
            [request for request in valid_requests if request is not None]
        )
        for service_result in service_results:
            result = self._result_adapter.from_service_result(service_result)
            self._record_result(result, result_callback)
            if result.status == "complete":
                counts["complete"] += 1
            elif result.status == "error":
                counts["error"] += 1

        self._notify(status_callback, "Prediction run finished.")
        return PredictionRunSummary(
            total=total,
            complete=counts["complete"],
            error=counts["error"],
            invalid=counts["invalid"],
        )

    def _record_result(
        self,
        result: ResultRow,
        result_callback: ResultCallback | None,
    ) -> None:
        self._session.set_result(result)
        if result_callback is not None:
            result_callback(result)

    def _notify(self, callback: StatusCallback | None, message: str) -> None:
        if callback is not None:
            callback(message)

    def _start_worker(
        self,
        requests: list[PredictionInputRequest],
        total: int,
        invalid_count: int,
        status_callback: StatusCallback | None,
        result_callback: ResultCallback | None,
        progress_callback: ProgressCallback | None,
        finished_callback: SummaryCallback | None,
    ) -> None:
        self._is_running = True
        self._active_total = total
        self._active_invalid = invalid_count
        self._thread = QThread()
        self._worker = PredictionWorker(
            PredictionJob(
                run_id=f"predict-{uuid4().hex}",
                requests=tuple(requests),
                total=len(requests),
            ),
            service=self._service,
        )
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.row_result.connect(
            lambda service_result: self._handle_worker_row_result(
                service_result,
                result_callback,
            )
        )
        self._worker.progress.connect(
            lambda progress: self._handle_worker_progress(
                progress,
                status_callback,
                progress_callback,
            )
        )
        self._worker.finished.connect(
            lambda summary: self._handle_worker_finished(
                summary,
                status_callback,
                finished_callback,
            )
        )
        self._worker.cancelled.connect(
            lambda summary: self._handle_worker_cancelled(
                summary,
                status_callback,
                result_callback,
                finished_callback,
            )
        )
        self._worker.failed.connect(
            lambda exc: self._handle_worker_failed(
                exc,
                status_callback,
                finished_callback,
            )
        )
        self._worker.finished.connect(self._thread.quit)
        self._worker.cancelled.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(lambda: QTimer.singleShot(0, self._clear_worker_thread))
        self._thread.start()

    def _handle_worker_row_result(
        self,
        service_result: PredictionServiceResult,
        result_callback: ResultCallback | None,
    ) -> None:
        self._record_result(
            self._result_adapter.from_service_result(service_result),
            result_callback,
        )

    def _handle_worker_progress(
        self,
        progress: PredictionProgress,
        status_callback: StatusCallback | None,
        progress_callback: ProgressCallback | None,
    ) -> None:
        if progress_callback is not None:
            progress_callback(progress)
        self._notify(status_callback, progress.message)

    def _handle_worker_finished(
        self,
        summary: PredictionWorkerSummary,
        status_callback: StatusCallback | None,
        finished_callback: SummaryCallback | None,
    ) -> None:
        run_summary = self._run_summary_from_worker(summary)
        self._is_running = False
        self._notify(status_callback, "Prediction run finished.")
        if finished_callback is not None:
            finished_callback(run_summary)

    def _handle_worker_cancelled(
        self,
        summary: PredictionWorkerSummary,
        status_callback: StatusCallback | None,
        result_callback: ResultCallback | None,
        finished_callback: SummaryCallback | None,
    ) -> None:
        for case_id in summary.cancelled_case_ids:
            self._record_result(
                self._result_adapter.cancelled_result(case_id),
                result_callback,
            )
        run_summary = self._run_summary_from_worker(summary)
        self._is_running = False
        self._notify(status_callback, "Prediction run cancelled.")
        if finished_callback is not None:
            finished_callback(run_summary)

    def _handle_worker_failed(
        self,
        exc: object,
        status_callback: StatusCallback | None,
        finished_callback: SummaryCallback | None,
    ) -> None:
        self._is_running = False
        summary = PredictionRunSummary(
            total=self._active_total,
            complete=0,
            error=0,
            invalid=self._active_invalid,
        )
        self._notify(
            status_callback,
            f"Prediction worker failed: {str(exc).splitlines()[0]}",
        )
        if finished_callback is not None:
            finished_callback(summary)

    def _run_summary_from_worker(
        self,
        summary: PredictionWorkerSummary,
    ) -> PredictionRunSummary:
        return PredictionRunSummary(
            total=self._active_total,
            complete=summary.complete,
            error=summary.error,
            invalid=self._active_invalid,
            cancelled=summary.cancelled,
        )

    def _clear_worker_thread(self) -> None:
        self._thread = None
        self._worker = None
        self._active_total = 0
        self._active_invalid = 0
