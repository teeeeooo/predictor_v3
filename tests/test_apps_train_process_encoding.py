"""Locale-independent shared training child transport regressions."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEventLoop, QTimer

from apps.train.adapters.qprocess_training_runner import QProcessTrainingRunner
from apps.train.adapters.subprocess_training_runner import SubprocessTrainingRunner
from apps.train.adapters.training_process_events import parse_training_event
from apps.train.ports.training_execution_port import TrainingExecutionCallbacks
from apps.train.state.training_run_state import TrainingRequest
from tools.dev.mock_smoke.generators import write_mock_training_data

UNICODE_RUN_ID = "train-📦-✅"
UNICODE_LOG = "📦 데이터 로드 및 전처리 시작... 목표 ✅ / 실패 ❌"


def _request(tmp_path: Path) -> TrainingRequest:
    data_path = write_mock_training_data(output_dir=tmp_path, rows=8)
    return TrainingRequest(
        run_id=UNICODE_RUN_ID,
        data_path=str(data_path),
        model_output_path=str(tmp_path / "model-✅.pkl"),
    )


def _callbacks(logs, progress, started, terminal):  # noqa: ANN001
    return TrainingExecutionCallbacks(
        started=started.append,
        log=logs.append,
        progress=progress.append,
        finished=lambda result: terminal.append(("finished", result)),
        failed=lambda result: terminal.append(("failed", result)),
        cancelled=lambda result: terminal.append(("cancelled", result)),
    )


def test_child_event_round_trip_is_utf8_under_cp949_environment(tmp_path):
    request = _request(tmp_path)
    code = (
        "import sys;"
        "from apps.train.jobs.train_job import "
        "_configure_process_stdio_utf8,emit_log;"
        "_configure_process_stdio_utf8();"
        f"emit_log({UNICODE_RUN_ID!r},{UNICODE_LOG!r});"
        "sys.stderr.write('진단 ❌\\n');sys.stderr.flush()"
    )
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp949"

    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    line = completed.stdout.decode("utf-8").strip()
    event_type, event = parse_training_event(line, request)

    assert completed.stderr.decode("utf-8") == "진단 ❌\n"
    assert event_type == "log"
    assert event.run_id == UNICODE_RUN_ID
    assert event.message == UNICODE_LOG
    assert event.level == "info"


def test_subprocess_runner_consumes_utf8_child_events_under_cp949(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("PYTHONIOENCODING", "cp949")
    request = _request(tmp_path)
    logs, progress, started, terminal = [], [], [], []
    runner = SubprocessTrainingRunner(
        extra_args=("--dev-fast", "--dev-rows", "8")
    )

    runner.start(request, _callbacks(logs, progress, started, terminal))

    assert started == [request]
    assert len(terminal) == 1
    assert terminal[0][0] == "finished"
    assert terminal[0][1].status == "complete"
    assert terminal[0][1].model_path == request.model_output_path
    assert progress[-1].completed == progress[-1].total
    assert logs and all(event.run_id == UNICODE_RUN_ID for event in logs)
    assert Path(request.model_output_path).exists()


def test_qprocess_runner_consumes_utf8_child_events_under_cp949(
    tmp_path, monkeypatch, qprocess_app
):
    monkeypatch.setenv("PYTHONIOENCODING", "cp949")
    request = _request(tmp_path)
    logs, progress, started, terminal = [], [], [], []
    runner = QProcessTrainingRunner(
        extra_args=("--dev-fast", "--dev-rows", "8")
    )
    loop = QEventLoop()
    timeout = QTimer()
    timeout.setSingleShot(True)
    callbacks = _callbacks(logs, progress, started, terminal)

    runner.finished.connect(loop.quit)
    runner.failed.connect(loop.quit)
    runner.cancelled.connect(loop.quit)
    timeout.timeout.connect(loop.quit)
    runner.start(request, callbacks)
    timeout.start(20000)
    loop.exec()
    timeout.stop()
    qprocess_app.processEvents()

    assert started == [request]
    assert len(terminal) == 1
    assert terminal[0][0] == "finished"
    assert terminal[0][1].status == "complete"
    assert terminal[0][1].model_path == request.model_output_path
    assert progress[-1].completed == progress[-1].total
    assert logs and all(event.run_id == UNICODE_RUN_ID for event in logs)
    assert Path(request.model_output_path).exists()
    assert not runner.is_running
    runner.dispose()
    qprocess_app.processEvents()


def test_non_protocol_diagnostic_fallback_remains_log(tmp_path):
    request = _request(tmp_path)
    diagnostic = "진단 라인 ❌"

    event_type, event = parse_training_event(diagnostic, request)

    assert event_type == "log"
    assert event.run_id == request.run_id
    assert event.message == diagnostic


def test_malformed_structured_progress_remains_rejected(tmp_path):
    request = _request(tmp_path)
    malformed = json.dumps(
        {"type": "progress", "run_id": request.run_id, "completed": "invalid"}
    )

    with pytest.raises(ValueError):
        parse_training_event(malformed, request)
