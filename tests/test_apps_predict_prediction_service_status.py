"""Prediction service model status tests."""

from apps.predict.adapters.row_to_ml_input_adapter import PredictionInputRequest
from apps.predict.controllers.prediction_controller import PredictionController
from apps.predict.services import prediction_service as prediction_service_module
from apps.predict.services.prediction_service import PredictionService
from apps.predict.state.predict_session import PredictSession


def test_prediction_service_model_status_reports_missing_path(tmp_path):
    missing_path = tmp_path / "model.pkl"
    service = PredictionService(model_file=str(missing_path))

    status = service.model_status()

    assert status.model_path == str(missing_path)
    assert status.status == "missing"
    assert status.message == "Model artifact is missing."


def test_prediction_service_model_status_does_not_eagerly_load_model(
    tmp_path,
    monkeypatch,
):
    model_path = tmp_path / "model.pkl"
    model_path.write_bytes(b"placeholder")
    calls = []

    def _load_model(_path):
        calls.append(_path)
        raise AssertionError("model_status must not load the model")

    monkeypatch.setattr(prediction_service_module, "load_model", _load_model)
    service = PredictionService(model_file=str(model_path))

    status = service.model_status()

    assert status.status == "exists"
    assert calls == []


def test_prediction_service_model_status_reports_load_error(tmp_path, monkeypatch):
    model_path = tmp_path / "model.pkl"
    model_path.write_bytes(b"placeholder")

    def _load_model(_path):
        raise RuntimeError("cannot load model")

    monkeypatch.setattr(prediction_service_module, "load_model", _load_model)
    service = PredictionService(model_file=str(model_path))
    result = service.predict_one(
        PredictionInputRequest(case_id="case-0001", row_input={"Cooling Capa": 3500.0})
    )

    status = service.model_status()

    assert result.status == "error"
    assert status.status == "load-error"
    assert status.message == "cannot load model"


def test_controller_model_status_delegates_without_mutating_session(tmp_path):
    session = PredictSession()
    session.case_store.append_empty_rows(1)
    service = PredictionService(model_file=str(tmp_path / "missing.pkl"))
    controller = PredictionController(session=session, service=service)
    before_order = session.case_order
    before_results = dict(session.results_by_case_id)

    status = controller.model_status()

    assert status.status == "missing"
    assert session.case_order == before_order
    assert session.results_by_case_id == before_results
