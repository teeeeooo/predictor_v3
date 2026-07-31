"""Prediction execution controller foundation."""

from collections.abc import Callable

from apps.predict.application.model_lifecycle import (
    ModelReloadOutcome,
    PredictModelLifecycleService,
    PredictModelLifecycleStatus,
)
from apps.predict.application.models import (
    PredictionModelStatus,
    PredictionServiceResult,
)
from apps.predict.application.result_contract import (
    PredictionModelIdentity,
)
from apps.predict.application.prediction_usecase import (
    PredictionRunSummary,
    PredictionUseCase,
)
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow
from apps.predict.ports.prediction_execution_port import (
    PredictionExecutionPort,
    PredictionProgress,
    PredictionWorkerSummary,
)
from apps.predict.ports.prediction_workflow_ports import PredictionServicePort


StatusCallback = Callable[[str], None]
ResultCallback = Callable[[ResultRow], None]
ProgressCallback = Callable[[PredictionProgress], None]
SummaryCallback = Callable[["PredictionRunSummary"], None]
PredictionRunnerFactory = Callable[[PredictionServicePort], PredictionExecutionPort]


class PredictionController:
    """Coordinate prediction inputs, service calls, and session updates."""

    def __init__(
        self,
        session: PredictSession,
        usecase: PredictionUseCase,
        service: PredictionServicePort,
        runner: PredictionExecutionPort | None = None,
        runner_factory: PredictionRunnerFactory | None = None,
        model_lifecycle: PredictModelLifecycleService | None = None,
    ) -> None:
        self._session = session
        self._service = service
        self._usecase = usecase
        self._runner = runner
        self._runner_factory = runner_factory
        self._model_lifecycle = model_lifecycle
        self._is_running = False
        self._active_case_ids: tuple[str, ...] = ()
        self._active_run_id = ""

    @property
    def is_running(self) -> bool:
        """Return whether a prediction run is active."""
        return self._is_running

    @property
    def has_usable_prediction_service(self) -> bool:
        """Return whether the current process can execute predictions."""
        service_status = self._service.model_status().status
        if service_status not in {"loaded", "exists"}:
            return False
        if self._model_lifecycle is None:
            return True
        return bool(self._model_lifecycle.loaded.candidate_id)

    @property
    def can_start_prediction(self) -> bool:
        """Return current command eligibility for starting prediction."""
        return not self._is_running and self.has_usable_prediction_service

    def model_status(self) -> PredictionModelStatus:
        """Return Qt-free model status through the service boundary."""
        return self._service.model_status()

    @property
    def model_lifecycle(self) -> PredictModelLifecycleService | None:
        return self._model_lifecycle

    def refresh_model_lifecycle(self) -> PredictModelLifecycleStatus | None:
        if self._model_lifecycle is None:
            return None
        return self._model_lifecycle.refresh()

    def current_model_lifecycle_status(self) -> PredictModelLifecycleStatus | None:
        if self._model_lifecycle is None:
            return None
        return self._model_lifecycle.status

    def reload_active_model(self) -> ModelReloadOutcome:
        if self._model_lifecycle is None:
            raise RuntimeError("Model lifecycle reload is unavailable.")
        outcome = self._model_lifecycle.reload(
            prediction_running=self._is_running,
            swap_service=self._replace_service,
        )
        if outcome.status == "reloaded" and outcome.applied_to_shared_state:
            semantics, _old_model = self._usecase.execution_environment
            loaded = self._model_lifecycle.loaded
            model = PredictionModelIdentity(
                loaded.candidate_id, loaded.active_revision, loaded.generation_id
            )
            self._usecase.update_execution_environment(semantics, model)
            self._session.reconcile_result_currentness(semantics, model)
        return outcome

    def is_model_reload_operation_current(self, operation_id: int) -> bool:
        return self.is_model_lifecycle_operation_current(operation_id)

    def is_model_lifecycle_operation_current(self, operation_id: int) -> bool:
        if self._model_lifecycle is None:
            return False
        return self._model_lifecycle.is_operation_current(operation_id)

    def runtime_dependencies(
        self,
    ) -> tuple[PredictionServicePort, PredictionRunnerFactory | None]:
        """Expose immutable composition dependencies for staged generation rebuilds."""
        return self._service, self._runner_factory

    def reconcile_session_currentness(self) -> None:
        semantics, model = self._usecase.execution_environment
        self._session.reconcile_result_currentness(semantics, model)

    @property
    def execution_environment(self):  # noqa: ANN201
        return self._usecase.execution_environment

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
        if not self.has_usable_prediction_service:
            raise RuntimeError("No usable prediction service is loaded.")

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
            case_ids=tuple(case_ids),
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
        if not self.has_usable_prediction_service:
            raise RuntimeError("No usable prediction service is loaded.")
        total = len(case_ids)
        self._notify(status_callback, f"Starting prediction for {total} rows.")

        valid_requests = []
        counts = {"complete": 0, "partial": 0, "error": 0, "invalid": 0}
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
            elif result.status == "partial":
                counts["partial"] += 1
            elif result.status == "error":
                counts["error"] += 1

        self._notify(status_callback, "Prediction run finished.")
        return PredictionRunSummary(
            total=total,
            complete=counts["complete"],
            error=counts["error"],
            invalid=counts["invalid"],
            partial=counts["partial"],
        )

    def _notify(self, callback: StatusCallback | None, message: str) -> None:
        if callback is not None:
            callback(message)

    def _replace_service(self, service: PredictionServicePort) -> None:
        if self._is_running:
            raise RuntimeError("Prediction started during model reload.")
        self._service = service

    def _start_worker(
        self,
        job,
        case_ids: tuple[str, ...],
        status_callback: StatusCallback | None,
        result_callback: ResultCallback | None,
        progress_callback: ProgressCallback | None,
        finished_callback: SummaryCallback | None,
    ) -> None:
        self._is_running = True
        self._active_case_ids = case_ids
        self._active_run_id = job.run_id
        runner = self._runner
        if runner is None:
            if self._runner_factory is None:
                raise RuntimeError("Prediction runner factory is not configured.")
            runner = self._runner_factory(self._service)
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
                job.run_id,
                status_callback,
                result_callback,
                finished_callback,
            )
        )
        runner.finished.connect(lambda summary: self._clear_runner(summary.run_id))
        runner.cancelled.connect(lambda summary: self._clear_runner(summary.run_id))
        runner.failed.connect(lambda _exc: self._clear_runner(job.run_id))
        runner.start(job)

    def _handle_worker_row_result(
        self,
        service_result: PredictionServiceResult,
        result_callback: ResultCallback | None,
    ) -> None:
        context = service_result.context
        if context is None or context.run_id != self._active_run_id:
            return
        self._usecase.apply_service_result(service_result, result_callback)

    def _handle_worker_progress(
        self,
        progress: PredictionProgress,
        status_callback: StatusCallback | None,
        progress_callback: ProgressCallback | None,
    ) -> None:
        if progress.run_id != self._active_run_id:
            return
        if progress_callback is not None:
            progress_callback(progress)
        self._notify(status_callback, progress.message)

    def _handle_worker_finished(
        self,
        summary: PredictionWorkerSummary,
        status_callback: StatusCallback | None,
        finished_callback: SummaryCallback | None,
    ) -> None:
        if summary.run_id != self._active_run_id:
            return
        run_summary = self._usecase.summary_from_case_ids(self._active_case_ids)
        self._session.revoke_run(summary.run_id)
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
        if summary.run_id != self._active_run_id:
            return
        self._usecase.apply_cancelled_rows(
            summary.cancelled_case_ids, result_callback, run_id=summary.run_id
        )
        run_summary = self._usecase.summary_from_case_ids(self._active_case_ids)
        self._is_running = False
        self._notify(status_callback, "Prediction run cancelled.")
        if finished_callback is not None:
            finished_callback(run_summary)

    def _handle_worker_failed(
        self,
        exc: object,
        run_id: str,
        status_callback: StatusCallback | None,
        result_callback: ResultCallback | None,
        finished_callback: SummaryCallback | None,
    ) -> None:
        if run_id != self._active_run_id:
            return
        failure_message = f"Prediction worker failed: {str(exc).splitlines()[0]}"
        summary = self._usecase.apply_infrastructure_failure(
            self._active_case_ids,
            failure_message,
            result_callback,
            run_id=run_id,
        )
        self._is_running = False
        self._notify(status_callback, failure_message)
        if finished_callback is not None:
            finished_callback(summary)

    def _clear_runner(self, run_id: str) -> None:
        if self._active_run_id != run_id:
            return
        runner = self._runner
        self._runner = None
        self._active_case_ids = ()
        self._active_run_id = ""
        if runner is not None:
            runner.dispose()
