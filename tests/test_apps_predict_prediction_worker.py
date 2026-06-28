"""PredictionWorker headless behavior tests."""

from pathlib import Path

from PySide6.QtCore import QCoreApplication

from apps.predict.adapters.row_to_ml_input_adapter import PredictionInputRequest
from apps.predict.services.prediction_service import PredictionServiceResult
from apps.predict.state.predict_session import PredictSession
from apps.predict.workers.prediction_worker import PredictionJob, PredictionWorker


def _app() -> QCoreApplication:
    return QCoreApplication.instance() or QCoreApplication([])


def _request(case_id: str) -> PredictionInputRequest:
    return PredictionInputRequest(case_id=case_id, row_input={"Cooling Capa": 3500.0})


def _job(count: int = 2) -> PredictionJob:
    requests = tuple(_request(f"case-{index:04d}") for index in range(1, count + 1))
    return PredictionJob(run_id="run-1", requests=requests, total=len(requests))


class FakePredictionService:
    """Tiny service double for worker signal tests."""

    def __init__(self, statuses: tuple[str, ...] = ("complete",)) -> None:
        self.statuses = statuses
        self.calls: list[str] = []

    def predict_one(self, request: PredictionInputRequest) -> PredictionServiceResult:
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
            predictions={"Cooling Power": 1200.0},
        )


def test_worker_emits_row_results_progress_and_finished_summary():
    _app()
    service = FakePredictionService(("complete", "complete"))
    worker = PredictionWorker(_job(2), service=service)
    row_results = []
    progress = []
    finished = []

    worker.row_result.connect(row_results.append)
    worker.progress.connect(progress.append)
    worker.finished.connect(finished.append)

    worker.run()

    assert [result.case_id for result in row_results] == ["case-0001", "case-0002"]
    assert [item.completed for item in progress] == [1, 2]
    assert finished[0].complete == 2
    assert finished[0].error == 0


def test_worker_emits_row_error_and_continues():
    _app()
    service = FakePredictionService(("complete", "error", "complete"))
    worker = PredictionWorker(_job(3), service=service)
    row_results = []
    finished = []

    worker.row_result.connect(row_results.append)
    worker.finished.connect(finished.append)

    worker.run()

    assert [result.status for result in row_results] == ["complete", "error", "complete"]
    assert finished[0].complete == 2
    assert finished[0].error == 1


def test_worker_cancel_before_run_stops_before_remaining_rows():
    _app()
    service = FakePredictionService(("complete", "complete"))
    worker = PredictionWorker(_job(2), service=service)
    row_results = []
    cancelled = []
    finished = []

    worker.row_result.connect(row_results.append)
    worker.cancelled.connect(cancelled.append)
    worker.finished.connect(finished.append)
    worker.cancel()
    worker.run()

    assert row_results == []
    assert service.calls == []
    assert cancelled[0].cancelled == 2
    assert finished == []


def test_worker_cancel_after_row_stops_future_rows():
    _app()
    service = FakePredictionService(("complete", "complete", "complete"))
    worker = PredictionWorker(_job(3), service=service)
    row_results = []
    cancelled = []
    finished = []

    worker.row_result.connect(row_results.append)
    worker.row_result.connect(lambda _result: worker.cancel())
    worker.cancelled.connect(cancelled.append)
    worker.finished.connect(finished.append)

    worker.run()

    assert [result.case_id for result in row_results] == ["case-0001"]
    assert service.calls == ["case-0001"]
    assert cancelled[0].complete == 1
    assert cancelled[0].cancelled == 2
    assert cancelled[0].cancelled_case_ids == ("case-0002", "case-0003")
    assert finished == []


def test_worker_source_does_not_import_widgets_or_mutate_session():
    source = Path("apps/predict/workers/prediction_worker.py").read_text(
        encoding="utf-8"
    )

    assert "QtWidgets" not in source
    assert "PredictSession" not in source


def test_worker_does_not_mutate_predict_session():
    _app()
    session = PredictSession()
    session.case_store.append_empty_rows(1)
    before_results = dict(session.results_by_case_id)
    worker = PredictionWorker(_job(1), service=FakePredictionService(("complete",)))

    worker.run()

    assert session.results_by_case_id == before_results
