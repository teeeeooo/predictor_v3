"""PredictionController worker orchestration tests."""

import pytest
from PySide6.QtCore import QCoreApplication, QEventLoop, QObject, QTimer, Signal

from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter
from apps.predict.adapters.row_to_ml_input_adapter import RowToMlInputAdapter
from apps.predict.application.model_lifecycle import LoadedModelIdentity
from apps.predict.application.models import (
    PredictionModelStatus,
    PredictionServiceResult,
)
from apps.predict.application.prediction_usecase import PredictionUseCase
from apps.predict.controllers.prediction_controller import PredictionController
from apps.predict.ports.prediction_execution_port import (
    PredictionProgress,
    PredictionWorkerSummary,
)
from apps.predict.state.predict_session import PredictSession
from core.ml.features import TARGETS


def _app() -> QCoreApplication:
    return QCoreApplication.instance() or QCoreApplication([])


def _wait_until(predicate, timeout_ms: int = 1500) -> None:  # noqa: ANN001
    app = _app()
    if predicate():
        app.processEvents()
        return
    loop = QEventLoop()
    poll = QTimer()
    poll.setInterval(10)
    timeout = QTimer()
    timeout.setSingleShot(True)
    poll.timeout.connect(lambda: loop.quit() if predicate() else None)
    timeout.timeout.connect(loop.quit)
    poll.start()
    timeout.start(timeout_ms)
    loop.exec()
    poll.stop()
    timeout.stop()
    app.processEvents()
    assert predicate()


def _session_with_cases(*cooling_values: str) -> PredictSession:
    session = PredictSession()
    rows = session.case_store.append_empty_rows(len(cooling_values))
    for row, value in zip(rows, cooling_values, strict=True):
        if value:
            row.set_input_value("cooling_capa", value)
    return session


class FakePredictionService:
    """Fast service double for controller orchestration tests."""

    def __init__(self, statuses: tuple[str, ...] = ("complete",)) -> None:
        self.statuses = statuses
        self.calls: list[str] = []

    def model_status(self):
        return PredictionModelStatus("fake", "loaded")

    def predict_one(self, request):
        self.calls.append(request.case_id)
        status = self.statuses[min(len(self.calls) - 1, len(self.statuses) - 1)]
        if status == "error":
            return PredictionServiceResult(
                case_id=request.case_id,
                status="error",
                message="row failed",
                context=request.context,
            )
        return PredictionServiceResult(
            case_id=request.case_id,
            status="complete",
            predictions={target: 1200.0 for target in TARGETS},
            context=request.context,
        )


class MissingModelService(FakePredictionService):
    def model_status(self):
        return PredictionModelStatus("missing", "missing")

    def predict_one(self, request):
        self.calls.append(request.case_id)
        return PredictionServiceResult(
            case_id=request.case_id,
            status="error",
            message="모델 파일을 찾을 수 없습니다",
            context=request.context,
        )


class FakePredictionRunner(QObject):
    """Runner double used through the controller factory boundary."""

    progress = Signal(object)
    row_result = Signal(object)
    finished = Signal(object)
    cancelled = Signal(object)
    failed = Signal(object)

    def __init__(self, service, *, auto_finish: bool = True):  # noqa: ANN001
        super().__init__()
        self._service = service
        self.auto_finish = auto_finish
        self.job = None
        self.cancel_called = False
        self.is_running = False
        self.disposed = False

    def start(self, job) -> None:  # noqa: ANN001
        self.job = job
        self.is_running = True
        if self.auto_finish:
            QTimer.singleShot(0, self.complete)

    def cancel(self) -> None:
        self.cancel_called = True
        if self.job is None:
            return
        first = self.job.requests[0]
        result = self._service.predict_one(first)
        self.row_result.emit(result)
        self.progress.emit(
            PredictionProgress(
                run_id=self.job.run_id,
                completed=1,
                total=self.job.total,
                current_case_id=first.case_id,
                message=f"1 / {self.job.total}",
            )
        )
        self.is_running = False
        self.cancelled.emit(
            PredictionWorkerSummary(
                run_id=self.job.run_id,
                total=self.job.total,
                complete=1 if result.status == "complete" else 0,
                error=1 if result.status == "error" else 0,
                cancelled=max(self.job.total - 1, 0),
                cancelled_case_ids=tuple(
                    request.case_id for request in self.job.requests[1:]
                ),
            )
        )

    def complete(self) -> None:
        complete = 0
        error = 0
        for index, request in enumerate(self.job.requests, start=1):
            result = self._service.predict_one(request)
            self.row_result.emit(result)
            if result.status == "complete":
                complete += 1
            elif result.status == "error":
                error += 1
            self.progress.emit(
                PredictionProgress(
                    run_id=self.job.run_id,
                    completed=index,
                    total=self.job.total,
                    current_case_id=request.case_id,
                    message=f"{index} / {self.job.total}",
                )
            )
        self.is_running = False
        self.finished.emit(
            PredictionWorkerSummary(
                run_id=self.job.run_id,
                total=self.job.total,
                complete=complete,
                error=error,
            )
        )

    def fail(self, *, completed_rows: int = 0, message: str = "runner exploded") -> None:
        for request in self.job.requests[:completed_rows]:
            self.row_result.emit(self._service.predict_one(request))
        self.is_running = False
        self.failed.emit(RuntimeError(message))

    def dispose(self) -> None:
        self.disposed = True


def _controller(
    session,
    service,
    *,
    auto_finish: bool = True,
    model_lifecycle=None,
):  # noqa: ANN001
    runners = []

    def _factory(factory_service):  # noqa: ANN001
        runner = FakePredictionRunner(factory_service, auto_finish=auto_finish)
        runners.append(runner)
        return runner

    usecase = PredictionUseCase(
        session,
        input_mapper=RowToMlInputAdapter(),
        result_mapper=PredictionResultAdapter(),
    )
    return PredictionController(
        session=session,
        usecase=usecase,
        service=service,
        runner_factory=_factory,
        model_lifecycle=model_lifecycle,
    ), runners


def test_controller_worker_run_updates_session_rows():
    _app()
    session = _session_with_cases("3500", "3600")
    service = FakePredictionService(("complete", "complete"))
    controller, runners = _controller(session, service)
    summaries = []
    progress = []

    controller.start_all(
        progress_callback=progress.append,
        finished_callback=summaries.append,
    )
    _wait_until(lambda: summaries and controller._runner is None)

    assert [item.completed for item in progress] == [1, 2]
    assert summaries[0].complete == 2
    assert runners[0].disposed
    assert service.calls == list(session.case_order)
    for case_id in session.case_order:
        assert session.result_for_case(case_id).status == "complete"


def test_controller_rejects_double_start_while_running():
    _app()
    session = _session_with_cases("3500")
    service = FakePredictionService()
    controller, runners = _controller(session, service, auto_finish=False)
    summaries = []

    controller.start_all(finished_callback=summaries.append)
    assert runners[0].is_running
    assert controller.is_running
    with pytest.raises(RuntimeError, match="already in progress"):
        controller.start_all()

    runners[0].complete()
    _wait_until(lambda: summaries and controller._runner is None)


def test_late_terminal_event_for_another_run_cannot_finish_active_run():
    _app()
    session = _session_with_cases("3500")
    controller, runners = _controller(
        session, FakePredictionService(), auto_finish=False
    )
    summaries = []
    controller.start_all(finished_callback=summaries.append)

    runners[0].finished.emit(PredictionWorkerSummary("superseded-run", total=1))
    _app().processEvents()

    assert controller.is_running
    assert controller._runner is runners[0]
    assert summaries == []
    runners[0].complete()
    _wait_until(lambda: summaries and controller._runner is None)


def test_controller_applies_invalid_rows_without_worker_call():
    _app()
    session = _session_with_cases("")
    service = FakePredictionService()
    controller, _runners = _controller(session, service)
    summaries = []

    initial = controller.start_all(finished_callback=summaries.append)

    case_id = session.case_order[0]
    assert initial.invalid == 1
    assert summaries[0].invalid == 1
    assert session.result_for_case(case_id).status == "invalid"
    assert service.calls == []
    assert not controller.is_running


def test_controller_cancel_requests_worker_cancel():
    _app()
    session = _session_with_cases("3500", "3600")
    service = FakePredictionService()
    controller, runners = _controller(session, service, auto_finish=False)
    summaries = []

    controller.start_all(finished_callback=summaries.append)
    assert runners[0].is_running
    controller.cancel()
    _wait_until(lambda: summaries and controller._runner is None)

    assert runners[0].cancel_called
    assert runners[0].disposed
    assert summaries[0].complete == 1
    assert summaries[0].cancelled == 1
    assert service.calls == [session.case_order[0]]
    assert session.result_for_case(session.case_order[1]).status == "cancelled"


def test_controller_worker_error_result_continues_to_summary():
    _app()
    session = _session_with_cases("3500", "3600")
    service = FakePredictionService(("error", "complete"))
    controller, _runners = _controller(session, service)
    summaries = []

    controller.start_all(finished_callback=summaries.append)
    _wait_until(lambda: summaries and controller._runner is None)

    first, second = session.case_order
    assert session.result_for_case(first).status == "error"
    assert session.result_for_case(second).status == "complete"
    assert summaries[0].error == 1
    assert summaries[0].complete == 1


def test_controller_model_missing_blocks_before_worker_and_preserves_rows():
    _app()
    session = _session_with_cases("3500", "3600")
    service = MissingModelService()
    controller, runners = _controller(session, service)
    summaries = []
    before = tuple(session.result_for_case(case_id) for case_id in session.case_order)

    assert not controller.can_start_prediction
    with pytest.raises(RuntimeError, match="No usable prediction service"):
        controller.start_all(finished_callback=summaries.append)

    assert runners == []
    assert summaries == []
    assert service.calls == []
    assert tuple(
        session.result_for_case(case_id) for case_id in session.case_order
    ) == before


@pytest.mark.parametrize(
    "lifecycle_status",
    ("current", "reload-required", "reload-failed", "active-unavailable"),
)
def test_preserved_loaded_identity_keeps_prediction_eligible(lifecycle_status):
    session = _session_with_cases("3500")
    lifecycle = type(
        "LifecycleStub",
        (),
        {
            "loaded": LoadedModelIdentity("candidate-a", 1, "generation-1"),
            "status_name": lifecycle_status,
        },
    )()
    controller, _runners = _controller(
        session,
        FakePredictionService(),
        model_lifecycle=lifecycle,
    )

    assert controller.has_usable_prediction_service
    assert controller.can_start_prediction

    controller._is_running = True
    assert not controller.can_start_prediction


def test_lifecycle_without_loaded_identity_blocks_even_if_service_artifact_exists():
    session = _session_with_cases("3500")
    service = FakePredictionService()
    service.model_status = lambda: PredictionModelStatus("fake", "exists")
    lifecycle = type(
        "LifecycleStub",
        (),
        {"loaded": LoadedModelIdentity(), "status_name": "startup-failed"},
    )()
    controller, runners = _controller(
        session,
        service,
        model_lifecycle=lifecycle,
    )

    assert not controller.has_usable_prediction_service
    with pytest.raises(RuntimeError, match="No usable prediction service"):
        controller.start_all()

    assert runners == []
    assert session.result_for_case(session.case_order[0]).status == "pending"


def test_controller_runner_failure_preserves_terminal_rows_and_summarizes_session():
    _app()
    session = _session_with_cases("3500", "", "3600")
    service = FakePredictionService()
    controller, runners = _controller(session, service, auto_finish=False)
    summaries = []
    results = []

    controller.start_all(
        result_callback=results.append,
        finished_callback=summaries.append,
    )
    runners[0].fail(completed_rows=1, message="execution adapter exploded\ntrace")
    _wait_until(lambda: summaries and controller._runner is None)

    first, invalid, remaining = session.case_order
    assert session.result_for_case(first).status == "complete"
    assert session.result_for_case(invalid).status == "invalid"
    assert session.result_for_case(remaining).status == "error"
    assert "execution adapter exploded" not in session.result_for_case(remaining).message
    assert "다시 실행" in session.result_for_case(remaining).message
    assert "입력" not in session.result_for_case(remaining).message
    assert (summaries[0].total, summaries[0].complete) == (3, 1)
    assert (summaries[0].error, summaries[0].invalid) == (1, 1)
    assert not controller.is_running
    assert runners[0].disposed
    assert results[-1].case_id == remaining


def test_controller_immediate_runner_failure_errors_all_rows_and_allows_retry():
    _app()
    session = _session_with_cases("3500", "3600")
    service = FakePredictionService()
    controller, runners = _controller(session, service, auto_finish=False)
    summaries = []

    controller.start_all(finished_callback=summaries.append)
    runners[0].fail(message="runner failed immediately")
    _wait_until(lambda: len(summaries) == 1 and controller._runner is None)

    assert all(
        session.result_for_case(case_id).status == "error"
        for case_id in session.case_order
    )
    assert (summaries[0].complete, summaries[0].error, summaries[0].invalid) == (0, 2, 0)
    assert runners[0].disposed
    assert not controller.is_running

    controller.start_all(finished_callback=summaries.append)
    assert len(runners) == 2
    runners[1].complete()
    _wait_until(lambda: len(summaries) == 2 and controller._runner is None)

    assert summaries[1].complete == 2
    assert summaries[1].error == 0
    assert runners[1].disposed
    assert not controller.is_running


def test_controller_source_does_not_import_pyside_runner_concrete():
    source = open("apps/predict/controllers/prediction_controller.py", encoding="utf-8").read()

    assert "PySidePredictionRunner" not in source
    assert "pyside_prediction_runner" not in source
