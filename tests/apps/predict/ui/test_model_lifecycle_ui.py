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

    def refresh_model_lifecycle(self):
        return self.status

    def reload_active_model(self):
        self.reload_calls += 1
        return ModelReloadOutcome("failed", self.status, self.status.message)


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
