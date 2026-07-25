"""Thin Predict UI adapter for application-owned loaded-model lifecycle state."""

from __future__ import annotations


class PredictModelLifecycleUi:
    """Render lifecycle status and forward the explicit reload command."""

    def __init__(self, workspace) -> None:  # noqa: ANN001
        self._workspace = workspace
        workspace.command_bar.reload_model_button.clicked.connect(self.reload_active)

    def refresh(self) -> None:
        status = self._workspace.prediction_controller.refresh_model_lifecycle()
        if status is None:
            self._workspace.command_bar.reload_model_button.setVisible(False)
            return
        self.render(status)

    def render(self, status) -> None:  # noqa: ANN001
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
        workspace.model_lifecycle_diagnostics = status

    def reload_active(self) -> None:
        workspace = self._workspace
        controller = workspace.prediction_controller
        if controller.is_running:
            workspace.status_label.setText(
                "현재 예측 때문에 모델을 다시 불러올 수 없습니다."
            )
            return
        button = workspace.command_bar.reload_model_button
        button.setEnabled(False)
        workspace.status_label.setText("새 Active 모델을 다시 불러오는 중...")
        try:
            outcome = controller.reload_active_model()
        except Exception as exc:
            workspace.status_label.setText(
                f"모델 다시 불러오기 오류: {str(exc).splitlines()[0]}"
            )
            button.setEnabled(True)
            return
        self.render(outcome.model_status)
        button.setEnabled(not controller.is_running)
