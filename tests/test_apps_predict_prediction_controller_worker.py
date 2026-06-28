"""PredictionController worker orchestration tests."""

import pytest
from PySide6.QtCore import QCoreApplication, QEventLoop, QObject, QTimer, Signal

from apps.predict.controllers.prediction_controller import PredictionController
from apps.predict.ports.prediction_execution_port import (
    PredictionProgress,
    PredictionWorkerSummary,
)
from apps.predict.services.prediction_service import PredictionServiceResult
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

    def predict_one(self, request):
        self.calls.append(request.case_id)
        status = self.statuses[min(len(self.calls) - 1, len(self.statuses) - 1)]
        if status == "error":
            return PredictionServiceResult(
                case_id=request.case_id,
                status="error",
                message="row failed",
            )
        return PredictionServiceResult(
            case_id=request.case_id,
            status="complete",
            predictions={target: 1200.0 for target in TARGETS},
        )


class MissingModelService(FakePredictionService):
    def predict_one(self, request):
        self.calls.append(request.case_id)
        return PredictionServiceResult(
            case_id=request.case_id,
            status="error",
            message="모델 파일을 찾을 수 없습니다",
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


def _controller(session, service, *, auto_finish: bool = True):  # noqa: ANN001
    runners = []

    def _factory(factory_service):  # noqa: ANN001
        runner = FakePredictionRunner(factory_service, auto_finish=auto_finish)
        runners.append(runner)
        return runner

    return PredictionController(
        session=session,
        service=service,
        runner_factory=_factory,
    ), runners


def test_controller_worker_run_updates_session_rows():
    _app()
    session = _session_with_cases("3500", "3600")
    service = FakePredictionService(("complete", "complete"))
    controller, _runners = _controller(session, service)
    summaries = []
    progress = []

    controller.start_all(
        progress_callback=progress.append,
        finished_callback=summaries.append,
    )
    _wait_until(lambda: summaries and controller._runner is None)

    assert [item.completed for item in progress] == [1, 2]
    assert summaries[0].complete == 2
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


def test_controller_model_missing_becomes_controlled_row_errors():
    _app()
    session = _session_with_cases("3500", "3600")
    service = MissingModelService()
    controller, _runners = _controller(session, service)
    summaries = []

    controller.start_all(finished_callback=summaries.append)
    _wait_until(lambda: summaries and controller._runner is None)

    assert summaries[0].error == 2
    for case_id in session.case_order:
        assert session.result_for_case(case_id).status == "error"
        assert "모델 파일" in session.result_for_case(case_id).message


def test_controller_source_does_not_import_pyside_runner_concrete():
    source = open("apps/predict/controllers/prediction_controller.py", encoding="utf-8").read()

    assert "PySidePredictionRunner" not in source
    assert "pyside_prediction_runner" not in source
