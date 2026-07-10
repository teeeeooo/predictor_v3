"""Prediction worker contract tests."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter
from apps.predict.application.models import PredictionInputRequest
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.ports.prediction_execution_port import (
    PredictionJob,
    PredictionProgress,
    PredictionWorkerSummary,
)


def _request(case_id: str = "case-0001") -> PredictionInputRequest:
    return PredictionInputRequest(case_id=case_id, row_input={"Cooling Capa": 3500.0})


def test_prediction_job_progress_and_summary_are_frozen_payloads():
    request = _request()
    job = PredictionJob(run_id="run-1", requests=(request,), total=1)
    progress = PredictionProgress(
        run_id="run-1",
        completed=1,
        total=1,
        current_case_id=request.case_id,
        message="1 / 1",
    )
    summary = PredictionWorkerSummary(run_id="run-1", total=1, complete=1)

    assert job.requests == (request,)
    assert progress.current_case_id == "case-0001"
    assert summary.cancelled == 0
    with pytest.raises(FrozenInstanceError):
        job.total = 2


def test_result_adapter_builds_running_invalid_and_cancelled_rows():
    adapter = PredictionResultAdapter()

    running = adapter.running_result("case-0001")
    invalid = adapter.invalid_result("case-0002", "bad\nsecond line")
    cancelled = adapter.cancelled_result("case-0003")

    assert running.status == "running"
    assert invalid.status == "invalid"
    assert invalid.message == "bad"
    assert cancelled.status == "cancelled"
    assert cancelled.message == "Prediction cancelled."


def test_service_adapter_contract_modules_do_not_import_pyside():
    paths = (
        "apps/predict/application/models.py",
        "apps/predict/ports/prediction_execution_port.py",
        "apps/predict/ports/prediction_workflow_ports.py",
        "apps/predict/services/prediction_service.py",
        "apps/predict/adapters/row_to_ml_input_adapter.py",
        "apps/predict/adapters/prediction_result_adapter.py",
    )

    for path in paths:
        assert "PySide6" not in Path(path).read_text(encoding="utf-8")


def test_worker_contract_module_does_not_import_widgets_or_session():
    source = Path("apps/predict/workers/prediction_worker.py").read_text(
        encoding="utf-8"
    )

    assert "QtWidgets" not in source
    assert "PredictSession" not in source


def test_application_and_ports_do_not_import_concrete_adapters():
    paths = (
        "apps/predict/application/prediction_usecase.py",
        "apps/predict/ports/prediction_execution_port.py",
        "apps/predict/ports/prediction_workflow_ports.py",
    )

    for path in paths:
        source = Path(path).read_text(encoding="utf-8")
        assert "apps.predict.adapters" not in source
        assert "apps.predict.services" not in source


def test_composition_owner_builds_predict_state_without_widgets():
    composition = build_predict_workspace_composition(initial_empty_rows=2)

    assert len(composition.session.case_order) == 2
    assert composition.prediction_controller.is_running is False
    assert composition.input_edit_controller is not None
