"""PredictionController worker orchestration tests."""

from threading import Event

import pytest
from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer

from apps.predict.controllers.prediction_controller import PredictionController
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


class BlockingPredictionService(FakePredictionService):
    """Service double that lets tests observe the running state."""

    def __init__(self) -> None:
        super().__init__(("complete",))
        self.started = Event()
        self.release = Event()

    def predict_one(self, request):
        self.started.set()
        assert self.release.wait(1)
        return super().predict_one(request)


def test_controller_worker_run_updates_session_rows():
    _app()
    session = _session_with_cases("3500", "3600")
    service = FakePredictionService(("complete", "complete"))
    controller = PredictionController(session=session, service=service)
    summaries = []
    progress = []

    controller.start_all(
        progress_callback=progress.append,
        finished_callback=summaries.append,
    )
    _wait_until(lambda: summaries and controller._thread is None)

    assert [item.completed for item in progress] == [1, 2]
    assert summaries[0].complete == 2
    assert service.calls == list(session.case_order)
    for case_id in session.case_order:
        assert session.result_for_case(case_id).status == "complete"


def test_controller_rejects_double_start_while_running():
    _app()
    session = _session_with_cases("3500")
    service = BlockingPredictionService()
    controller = PredictionController(session=session, service=service)
    summaries = []

    controller.start_all(finished_callback=summaries.append)
    assert service.started.wait(1)
    assert controller.is_running
    with pytest.raises(RuntimeError, match="already in progress"):
        controller.start_all()

    service.release.set()
    _wait_until(lambda: summaries and controller._thread is None)


def test_controller_applies_invalid_rows_without_worker_call():
    _app()
    session = _session_with_cases("")
    service = FakePredictionService()
    controller = PredictionController(session=session, service=service)
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
    service = BlockingPredictionService()
    controller = PredictionController(session=session, service=service)
    summaries = []

    controller.start_all(finished_callback=summaries.append)
    assert service.started.wait(1)
    controller.cancel()
    service.release.set()
    _wait_until(lambda: summaries and controller._thread is None)

    assert summaries[0].complete == 1
    assert summaries[0].cancelled == 1
    assert service.calls == [session.case_order[0]]


def test_controller_worker_error_result_continues_to_summary():
    _app()
    session = _session_with_cases("3500", "3600")
    service = FakePredictionService(("error", "complete"))
    controller = PredictionController(session=session, service=service)
    summaries = []

    controller.start_all(finished_callback=summaries.append)
    _wait_until(lambda: summaries and controller._thread is None)

    first, second = session.case_order
    assert session.result_for_case(first).status == "error"
    assert session.result_for_case(second).status == "complete"
    assert summaries[0].error == 1
    assert summaries[0].complete == 1
