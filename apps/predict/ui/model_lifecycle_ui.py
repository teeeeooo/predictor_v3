"""Thin Predict UI adapter for application-owned loaded-model lifecycle state."""

from __future__ import annotations

import traceback


class PredictModelLifecycleUi:
    """Render lifecycle status and forward the explicit reload command."""

    def __init__(self, workspace) -> None:  # noqa: ANN001
        self._workspace = workspace
        workspace.command_bar.reload_model_button.clicked.connect(self.reload_active)

    def refresh(self) -> None:
        controller = self._workspace.prediction_controller
        status = controller.refresh_model_lifecycle()
        if status is None:
            self._workspace.command_bar.reload_model_button.setVisible(False)
            self._workspace._refresh_prediction_command_state()
            return
        if not controller.is_model_lifecycle_operation_current(status.operation_id):
            status = controller.current_model_lifecycle_status()
            if status is None:
                return
        self.render(status)

    def render(self, status, *, diagnostics=None) -> None:  # noqa: ANN001
        workspace = self._workspace
        workspace.command_bar.reload_model_button.setVisible(
            status.reload_required
            or status.status in {"active-unavailable", "reload-failed"}
        )
        loaded = status.loaded.candidate_id or "로드되지 않음"
        if status.status == "current":
            workspace.model_badge.set_status(f"{loaded} 사용 중", "ready")
        elif status.status == "reload-required":
            workspace.model_badge.set_status(
                f"{loaded} 사용 중 · 다시 불러오기 필요",
                "warning",
            )
        elif status.status == "reload-failed":
            workspace.model_badge.set_status(
                f"{loaded} 유지 · 다시 불러오기 실패",
                "error",
            )
        elif status.loaded.candidate_id:
            workspace.model_badge.set_status(
                f"{loaded} 유지 · Active 확인 불가",
                "warning",
            )
        else:
            workspace.model_badge.set_status("Active 모델 로드 실패", "error")
        workspace.status_label.setText(status.message)
        workspace.model_lifecycle_diagnostics = diagnostics or status
        workspace._refresh_prediction_command_state()

    def reload_active(self) -> None:
        workspace = self._workspace
        controller = workspace.prediction_controller
        button = workspace.command_bar.reload_model_button
        button.setEnabled(False)
        workspace.status_label.setText("새 Active 모델을 다시 불러오는 중...")
        try:
            outcome = controller.reload_active_model()
        except Exception:
            workspace.status_label.setText(
                "예상하지 못한 오류로 모델을 다시 불러오지 못했습니다. "
                "기존 모델은 유지됩니다. 진단 정보를 확인한 뒤 다시 시도하세요."
            )
            workspace.model_lifecycle_unexpected_traceback = traceback.format_exc()
            button.setEnabled(True)
            workspace._refresh_prediction_command_state()
            return
        if not controller.is_model_lifecycle_operation_current(outcome.operation_id):
            status = controller.current_model_lifecycle_status()
            if status is not None:
                self.render(status)
        elif outcome.applied_to_shared_state:
            self.render(outcome.model_status, diagnostics=outcome)
        button.setEnabled(not controller.is_running)
        workspace._refresh_prediction_command_state()
