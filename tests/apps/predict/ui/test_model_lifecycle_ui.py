"""Predict UI projection for explicit Active-model reload state."""

from __future__ import annotations

import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QPushButton  # noqa: E402

from apps.predict.application.model_lifecycle import (  # noqa: E402
    LoadedModelIdentity,
    ModelReloadOutcome,
    PredictModelLifecycleStatus,
)
from apps.predict.ui.model_lifecycle_ui import PredictModelLifecycleUi  # noqa: E402
from apps.predict.ui.status_widgets import StatusBadge  # noqa: E402


def _app():
    return QApplication.instance() or QApplication([])


class FakeController:
    def __init__(self, status):
        self.status = status
        self.is_running = False
        self.reload_calls = 0
        self.outcome = None

    def refresh_model_lifecycle(self):
        return self.status

    def reload_active_model(self):
        self.reload_calls += 1
        return self.outcome or ModelReloadOutcome(
            "failed",
            self.status,
            self.status.message,
            operation_id=self.status.operation_id,
        )

    def is_model_reload_operation_current(self, operation_id):
        return operation_id == self.status.operation_id


def _workspace(status):
    _app()
    return SimpleNamespace(
        prediction_controller=FakeController(status),
        command_bar=SimpleNamespace(reload_model_button=QPushButton()),
        model_badge=StatusBadge("모델 상태", "준비"),
        status_label=QLabel(),
    )


def test_reload_required_shows_old_loaded_model_and_explicit_action():
    status = PredictModelLifecycleStatus(
        "reload-required",
        LoadedModelIdentity("candidate-a", 1, "generation-1"),
        "candidate-b",
        2,
        "새 모델이 있습니다.",
    )
    workspace = _workspace(status)
    adapter = PredictModelLifecycleUi(workspace)

    adapter.refresh()

    assert not workspace.command_bar.reload_model_button.isHidden()
    assert "candidate-a" in workspace.model_badge.text()
    assert "다시 불러오기 필요" in workspace.model_badge.text()
    assert workspace.status_label.text() == "새 모델이 있습니다."


def test_reload_failed_and_running_block_preserve_user_facing_state():
    status = PredictModelLifecycleStatus(
        "reload-failed",
        LoadedModelIdentity("candidate-a", 1, "generation-1"),
        "candidate-b",
        2,
        "새 모델을 불러오지 못해 기존 모델을 계속 사용합니다.",
        "hash mismatch",
    )
    workspace = _workspace(status)
    adapter = PredictModelLifecycleUi(workspace)

    adapter.reload_active()

    assert workspace.prediction_controller.reload_calls == 1
    assert "candidate-a" in workspace.model_badge.text()
    assert "다시 불러오기 실패" in workspace.model_badge.text()
    assert "기존 모델" in workspace.status_label.text()

    workspace.prediction_controller.is_running = True
    adapter.reload_active()

    assert workspace.prediction_controller.reload_calls == 1
    assert "현재 예측" in workspace.status_label.text()


def test_stale_reload_completion_does_not_replace_newer_ui_state():
    current = PredictModelLifecycleStatus(
        "current",
        LoadedModelIdentity("candidate-c", 3, "generation-1"),
        "candidate-c",
        3,
        "현재 Active 모델을 사용 중입니다.",
        operation_id=2,
    )
    stale_failure = PredictModelLifecycleStatus(
        "reload-failed",
        LoadedModelIdentity("candidate-a", 1, "generation-1"),
        "candidate-c",
        3,
        "secret stale failure",
        operation_id=1,
    )
    workspace = _workspace(current)
    workspace.prediction_controller.outcome = ModelReloadOutcome(
        "failed",
        stale_failure,
        stale_failure.message,
        reason_code="stale_active_revision",
        operation_id=1,
        applied_to_shared_state=False,
    )
    adapter = PredictModelLifecycleUi(workspace)

    adapter.reload_active()

    assert "candidate-c" in workspace.model_badge.text()
    assert "다시 불러오기 실패" not in workspace.model_badge.text()
    assert workspace.status_label.text() == current.message


def test_unexpected_ui_exception_is_redacted_and_traceback_is_preserved():
    status = PredictModelLifecycleStatus(
        "current",
        LoadedModelIdentity("candidate-a", 1, "generation-1"),
        "candidate-a",
        1,
        operation_id=1,
    )
    workspace = _workspace(status)
    workspace.prediction_controller.reload_active_model = (
        lambda: (_ for _ in ()).throw(
            RuntimeError("secret /tmp/model.pkl fingerprint")
        )
    )
    adapter = PredictModelLifecycleUi(workspace)

    adapter.reload_active()

    assert "secret" not in workspace.status_label.text()
    assert "/tmp" not in workspace.status_label.text()
    assert "RuntimeError" not in workspace.status_label.text()
    assert "secret /tmp/model.pkl fingerprint" in (
        workspace.model_lifecycle_unexpected_traceback
    )
