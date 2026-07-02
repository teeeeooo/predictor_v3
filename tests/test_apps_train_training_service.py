"""TrainingService contract tests."""

from pathlib import Path

from apps.train.state.training_run_state import (
    TrainingRequest,
    TrainingResult,
)
from apps.train.services.training_service import (
    TrainingService,
)
from core.ml.inference import load_model
from core.ml.catalog_fingerprint import CATALOG_FINGERPRINT_KEY
from tools.dev.mock_smoke.dev_training_backend import DevFastTrainingBackend
from tools.dev.mock_smoke.dev_training_runner import run_dev_training_backend
from tools.dev.mock_smoke.generators import write_mock_training_data


def test_training_service_missing_data_path_returns_validation_error(tmp_path):
    service = TrainingService()
    request = TrainingRequest(
        run_id="run-missing",
        data_path=str(tmp_path / "missing.csv"),
        model_output_path=str(tmp_path / "model.pkl"),
    )

    result = service.validate_request(request)

    assert result is not None
    assert result.status == "error"
    assert "Training data is missing" in result.message


def test_training_service_accepts_valid_mock_csv_contract(tmp_path):
    data_path = write_mock_training_data(output_dir=tmp_path, rows=8)
    service = TrainingService()
    request = TrainingRequest(
        run_id="run-valid",
        data_path=str(data_path),
        model_output_path=str(tmp_path / "model.pkl"),
    )

    assert service.validate_request(request) is None
    status = service.resource_status(request.data_path, request.model_output_path)
    assert status.data_status == "exists"
    assert status.model_status == "missing"


def test_training_service_source_imports_no_pyside6():
    source = Path("apps/train/services/training_service.py").read_text(encoding="utf-8")

    assert "PySide6" not in source
    assert "QtWidgets" not in source


def test_dev_fast_training_backend_creates_inference_compatible_artifact(tmp_path):
    data_path = write_mock_training_data(output_dir=tmp_path, rows=8)
    model_path = tmp_path / "model.pkl"
    backend = DevFastTrainingBackend(rows=8)
    logs = []
    progress = []

    result = run_dev_training_backend(
        TrainingRequest(
            run_id="run-dev",
            data_path=str(data_path),
            model_output_path=str(model_path),
        ),
        backend,
        log_callback=logs.append,
        progress_callback=progress.append,
    )

    assert result.status == "complete"
    assert model_path.exists()
    assert load_model(model_path)["preprocess_version"] == "v1.0"
    assert CATALOG_FINGERPRINT_KEY in load_model(model_path)
    assert any("DEV fast training" in event.message for event in logs)
    assert progress[-1].completed == progress[-1].total


def test_training_service_has_no_direct_train_method(tmp_path):
    data_path = write_mock_training_data(output_dir=tmp_path, rows=8)
    model_path = tmp_path / "model.pkl"
    service = TrainingService()
    request = TrainingRequest(
        run_id="run-default",
        data_path=str(data_path),
        model_output_path=str(model_path),
    )

    assert service.validate_request(request) is None
    assert not hasattr(service, "train")
    assert not model_path.exists()
