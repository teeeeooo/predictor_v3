"""Prediction execution controller foundation."""

from collections.abc import Callable
from apps.predict.adapters.pyside_prediction_runner import PySidePredictionRunner

from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter
from apps.predict.adapters.row_to_ml_input_adapter import RowToMlInputAdapter
from apps.predict.application.prediction_usecase import (
    PredictionRunSummary,
    PredictionUseCase,
)
from apps.predict.services.prediction_service import (
    PredictionModelStatus,
    PredictionServiceResult,
    PredictionService,
)
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow
from apps.predict.ports.prediction_execution_port import (
    PredictionProgress,
    PredictionWorkerSummary,
)


StatusCallback = Callable[[str], None]
ResultCallback = Callable[[ResultRow], None]
ProgressCallback = Callable[[PredictionProgress], None]
SummaryCallback = Callable[["PredictionRunSummary"], None]


class PredictionController:
    """Coordinate prediction inputs, service calls, and session updates."""

    def __init__(
        self,
        session: PredictSession,
        input_adapter: RowToMlInputAdapter | None = None,
        service: PredictionService | None = None,
        result_adapter: PredictionResultAdapter | None = None,
        runner: PySidePredictionRunner | None = None,
        runner_cls: type[PySidePredictionRunner] = PySidePredictionRunner,
    ) -> None:
        self._session = session
        self._service = service or PredictionService()
        self._usecase = PredictionUseCase(
            session=session,
            input_adapter=input_adapter,
            result_adapter=result_adapter,
        )
        self._runner = runner
        self._runner_cls = runner_cls
        self._is_running = False
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
        plan = self._usecase.prepare_run(case_ids, result_callback)
        if plan.job is None:
            self._notify(status_callback, "Prediction run finished.")
            if finished_callback is not None:
                finished_callback(plan.summary)
            return plan.summary

        self._start_worker(
            plan.job,
            invalid_count=plan.summary.invalid,
            status_callback=status_callback,
            result_callback=result_callback,
            progress_callback=progress_callback,
            finished_callback=finished_callback,
        )
        return plan.summary

    def cancel(self) -> None:
        """Request cancellation for the active runner, if any."""
        if self._runner is not None:
            self._runner.cancel()

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
            plan = self._usecase.prepare_run([case_id], result_callback)
            if plan.job is None:
                counts["invalid"] += 1
                continue
            valid_requests.extend(plan.job.requests)

        service_results = self._service.predict_many(
            [request for request in valid_requests if request is not None]
        )
        for service_result in service_results:
            self._usecase.apply_service_result(service_result, result_callback)
            result = self._session.result_for_case(service_result.case_id)
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

    def _notify(self, callback: StatusCallback | None, message: str) -> None:
        if callback is not None:
            callback(message)

    def _start_worker(
        self,
        job,
        invalid_count: int,
        status_callback: StatusCallback | None,
        result_callback: ResultCallback | None,
        progress_callback: ProgressCallback | None,
        finished_callback: SummaryCallback | None,
    ) -> None:
        self._is_running = True
        self._active_total = job.total + invalid_count
        self._active_invalid = invalid_count
        runner = self._runner or self._runner_cls(service=self._service)
        self._runner = runner
        runner.row_result.connect(
            lambda service_result: self._handle_worker_row_result(
                service_result,
                result_callback,
            )
        )
        runner.progress.connect(
            lambda progress: self._handle_worker_progress(
                progress,
                status_callback,
                progress_callback,
            )
        )
        runner.finished.connect(
            lambda summary: self._handle_worker_finished(
                summary,
                status_callback,
                finished_callback,
            )
        )
        runner.cancelled.connect(
            lambda summary: self._handle_worker_cancelled(
                summary,
                status_callback,
                result_callback,
                finished_callback,
            )
        )
        runner.failed.connect(
            lambda exc: self._handle_worker_failed(
                exc,
                status_callback,
                finished_callback,
            )
        )
        runner.finished.connect(self._clear_runner)
        runner.cancelled.connect(self._clear_runner)
        runner.failed.connect(self._clear_runner)
        runner.start(job)

    def _handle_worker_row_result(
        self,
        service_result: PredictionServiceResult,
        result_callback: ResultCallback | None,
    ) -> None:
        self._usecase.apply_service_result(service_result, result_callback)

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
        run_summary = self._usecase.summary_from_worker(summary, self._active_invalid)
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
        self._usecase.apply_cancelled_rows(summary.cancelled_case_ids, result_callback)
        run_summary = self._usecase.summary_from_worker(summary, self._active_invalid)
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

    def _clear_runner(self) -> None:
        if self._runner is not None:
            self._runner.deleteLater()
        self._runner = None
        self._active_total = 0
        self._active_invalid = 0
