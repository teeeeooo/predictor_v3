"""TrainWorker headless behavior tests."""

import os
from pathlib import Path

from PySide6.QtWidgets import QApplication

from apps.train.services.training_service import TrainingService
from apps.train.state.training_run_state import TrainingRequest
from apps.train.workers.train_worker import TrainWorker
from tools.dev.mock_smoke.dev_training_backend import DevFastTrainingBackend
from tools.dev.mock_smoke.generators import write_mock_training_data


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _request(tmp_path, run_id: str = "run-worker") -> TrainingRequest:  # noqa: ANN001
    data_path = write_mock_training_data(output_dir=tmp_path, rows=8)
    return TrainingRequest(
        run_id=run_id,
        data_path=str(data_path),
        model_output_path=str(tmp_path / f"{run_id}.pkl"),
    )


def test_train_worker_emits_logs_progress_and_finished_with_dev_service(tmp_path):
    _app()
    service = TrainingService(backend=DevFastTrainingBackend(rows=8))
    worker = TrainWorker(_request(tmp_path), service=service)
    logs = []
    progress = []
    finished = []

    worker.log_event.connect(logs.append)
    worker.progress.connect(progress.append)
    worker.finished.connect(finished.append)

    worker.run()

    assert logs
    assert [item.completed for item in progress][-1] == progress[-1].total
    assert finished[0].status == "complete"
    assert Path(finished[0].model_path).exists()


def test_train_worker_emits_failed_for_service_error(tmp_path):
    _app()
    request = TrainingRequest(
        run_id="run-error",
        data_path=str(tmp_path / "missing.csv"),
        model_output_path=str(tmp_path / "model.pkl"),
    )
    worker = TrainWorker(request)
    failed = []

    worker.failed.connect(failed.append)
    worker.run()

    assert failed[0].status == "error"
    assert "Training data is missing" in failed[0].message


def test_train_worker_cancel_before_run_emits_cancelled(tmp_path):
    _app()
    worker = TrainWorker(_request(tmp_path), service=TrainingService(backend=DevFastTrainingBackend(rows=8)))
    cancelled = []
    finished = []

    worker.cancelled.connect(cancelled.append)
    worker.finished.connect(finished.append)
    worker.cancel()
    worker.run()

    assert cancelled[0].status == "cancelled"
    assert finished == []


def test_train_worker_cooperative_cancel_with_dev_backend(tmp_path):
    _app()
    backend = DevFastTrainingBackend(rows=8)
    worker = TrainWorker(_request(tmp_path), service=TrainingService(backend=backend))
    cancelled = []
    finished = []

    worker.progress.connect(lambda _progress: worker.cancel())
    worker.cancelled.connect(cancelled.append)
    worker.finished.connect(finished.append)

    worker.run()

    assert cancelled[0].status == "cancelled"
    assert finished == []


def test_train_worker_source_does_not_import_widgets_or_mutate_panel():
    source = Path("apps/train/workers/train_worker.py").read_text(encoding="utf-8")

    assert "QtWidgets" not in source
    assert "TrainModelPanel" not in source
    assert "QTextEdit" not in source
