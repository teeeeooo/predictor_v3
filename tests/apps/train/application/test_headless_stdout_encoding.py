"""Locale-independent machine-readable stdout regressions for headless Experiment."""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys

from apps.common.model_lifecycle import default_model_lifecycle_root
from apps.train.application.experiments.store import ExperimentStore
from apps.train.composition.experiments import PROJECT_ROOT
from apps.train.interfaces.headless import (
    agent_commands,
    closeout_commands,
    command_contract,
)
from apps.train.interfaces.headless import cli as headless_cli
from apps.train.interfaces.headless.command_contract import (
    EXIT_INTERNAL,
    EXIT_SUCCESS,
    EXIT_VALIDATION,
)


def _run_cp949(*args: str, state_home) -> subprocess.CompletedProcess:  # noqa: ANN001
    environment = os.environ.copy()
    environment["XDG_STATE_HOME"] = str(state_home)
    environment["PYTHONIOENCODING"] = "cp949:strict"
    return subprocess.run(
        [sys.executable, "-B", str(PROJECT_ROOT / "app_experiment.py"), *args],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        check=False,
    )


def _single_json_stdout(completed: subprocess.CompletedProcess) -> dict:
    assert not completed.stdout.startswith(b"\xef\xbb\xbf")
    lines = completed.stdout.splitlines()
    assert len(lines) == 1
    return json.loads(lines[0])


def test_cp949_stdout_preserves_unicode_success_and_machine_contract(tmp_path):
    specification = {
        "schema_version": "predictor_v3.experiment.v1",
        "experiment": {"name": "실험-🧪", "purpose": "검증-🧪"},
        "data": {"source_path": str(tmp_path / "입력-🧪.csv")},
    }
    path = tmp_path / "spec.json"
    path.write_text(json.dumps(specification, ensure_ascii=False), encoding="utf-8")

    completed = _run_cp949("validate", str(path), state_home=tmp_path / "state")
    output = _single_json_stdout(completed)
    assert completed.returncode == EXIT_SUCCESS
    assert b"UnicodeEncodeError" not in completed.stderr
    assert set(output) == {
        "schema_version",
        "command",
        "outcome",
        "message",
        "diagnostics",
        "data",
    }
    assert output["schema_version"] == "predictor_v3.experiment_output.v1"
    assert output["command"] == "validate"
    assert output["outcome"] == "success"
    resolved = output["data"]["resolved_specification"]
    assert resolved["experiment"] == {"name": "실험-🧪", "purpose": "검증-🧪"}
    assert resolved["data"]["source_path"].endswith("입력-🧪.csv")


def test_cp949_stdout_preserves_unicode_validation_diagnostic_and_exit(tmp_path):
    missing = tmp_path / "없는-🧪.json"

    completed = _run_cp949("validate", str(missing), state_home=tmp_path / "state")
    output = _single_json_stdout(completed)

    assert completed.returncode == EXIT_VALIDATION
    assert b"UnicodeEncodeError" not in completed.stderr
    assert output["schema_version"] == "predictor_v3.experiment_output.v1"
    assert output["outcome"] == "validation_failure"
    assert output["diagnostics"] == {"code": "specification_unreadable"}
    assert "없는-🧪.json" in output["message"]


def test_cp949_stdout_preserves_unicode_internal_failure_diagnostic(monkeypatch):
    def fail_dispatch(_args):  # noqa: ANN001
        raise RuntimeError("내부-🧪")

    buffer = io.BytesIO()
    stdout = io.TextIOWrapper(
        buffer,
        encoding="cp949",
        errors="strict",
        write_through=True,
    )
    monkeypatch.setattr(headless_cli, "_dispatch", fail_dispatch)
    monkeypatch.setattr(sys, "stdout", stdout)

    status = headless_cli.main(["lock-status"])
    lines = buffer.getvalue().splitlines()

    assert status == EXIT_INTERNAL
    assert len(lines) == 1
    output = json.loads(lines[0])
    assert output["schema_version"] == "predictor_v3.experiment_output.v1"
    assert output["outcome"] == "internal_failure"
    assert output["diagnostics"] == {"type": "RuntimeError", "detail": "내부-🧪"}


def test_cp949_stdout_preserves_unicode_run_log_event_data(tmp_path):
    state_home = tmp_path / "state"
    lifecycle_root = default_model_lifecycle_root(
        environment={"XDG_STATE_HOME": str(state_home)}
    )
    store = ExperimentStore(lifecycle_root)
    store.write_run(
        "unicode-log-run",
        {
            "schema_version": "predictor_v3.experiment_run.v1",
            "run_id": "unicode-log-run",
            "status": "success",
            "result": {
                "log_reference": "로그-🧪",
                "evidence_reference": "증거-🧪",
            },
        },
    )
    store.append_run_event(
        "unicode-log-run",
        {"event": "진행-🧪", "message": "학습 로그-🧪"},
    )

    completed = _run_cp949(
        "run-logs", "unicode-log-run", state_home=state_home
    )
    output = _single_json_stdout(completed)

    assert completed.returncode == EXIT_SUCCESS
    assert output["outcome"] == "success"
    assert output["data"]["log_reference"] == "로그-🧪"
    assert output["data"]["evidence_reference"] == "증거-🧪"
    assert output["data"]["events"] == [
        {"event": "진행-🧪", "message": "학습 로그-🧪"}
    ]


def test_headless_command_families_share_one_output_owner():
    assert headless_cli.emit is command_contract.emit
    assert agent_commands.emit is command_contract.emit
    assert closeout_commands.emit is command_contract.emit
