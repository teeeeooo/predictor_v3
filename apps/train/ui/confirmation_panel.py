"""Minimal Train GUI projection over shared Phase 5H persisted evidence."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.ui.models.static_table_model import StaticTableModel


class ConfirmationPanel(QFrame):
    def __init__(
        self,
        controller,
        parent: QWidget | None = None,
        *,
        confirm: Callable[[str, str], bool] | None = None,
        notify: Callable[[str, str, bool], None] | None = None,
    ) -> None:  # noqa: ANN001
        super().__init__(parent)
        self._controller = controller
        self._confirm = confirm or self._confirm_dialog
        self._notify = notify or self._notify_dialog
        self._confirmation = None
        self._active_revision = 0
        self._build()
        self.refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
        )
        heading = QHBoxLayout()
        title = QLabel("최종 확인")
        title.setFont(style.qfont("font.panel_title"))
        heading.addWidget(title)
        heading.addStretch(1)
        refresh = QPushButton("새로고침")
        refresh.clicked.connect(self.refresh)
        heading.addWidget(refresh)
        layout.addLayout(heading)
        self.snapshot_label = QLabel()
        self.snapshot_label.setWordWrap(True)
        self.confirmation_label = QLabel()
        self.confirmation_label.setWordWrap(True)
        self.compatibility_label = QLabel()
        self.compatibility_label.setWordWrap(True)
        layout.addWidget(self.snapshot_label)
        layout.addWidget(self.confirmation_label)
        layout.addWidget(self.compatibility_label)
        self.targets = QTableView()
        self.targets.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.targets.setSelectionMode(QAbstractItemView.NoSelection)
        self.targets.verticalHeader().setVisible(False)
        layout.addWidget(self.targets)
        actions = QHBoxLayout()
        actions.addStretch(1)
        self.reject_button = QPushButton("최종 확인 거절")
        self.reject_button.clicked.connect(lambda: self._decide(False))
        actions.addWidget(self.reject_button)
        self.approve_button = QPushButton("확인 후 이 모델 사용")
        self.approve_button.setObjectName("PrimaryButton")
        self.approve_button.clicked.connect(lambda: self._decide(True))
        actions.addWidget(self.approve_button)
        layout.addLayout(actions)

    def refresh(self) -> None:
        inspect = getattr(self._controller, "inspect_lifecycle_closeout", None)
        value = inspect() if inspect is not None else None
        snapshot = (value or {}).get("snapshot")
        confirmation = (value or {}).get("confirmation")
        self._confirmation = confirmation
        inspect_models = getattr(self._controller, "inspect_models", None)
        models = inspect_models() if inspect_models is not None else None
        self._active_revision = models.active_revision if models else 0
        self.snapshot_label.setText(
            "Snapshot: "
            + (
                f"{snapshot['snapshot_id']} · {snapshot['status']}"
                if snapshot else "없음"
            )
        )
        locked = (confirmation or {}).get("locked_final_test") or {}
        self.confirmation_label.setText(
            "Confirmation: "
            + (
                f"{confirmation['confirmation_id']} · {confirmation['status']} "
                f"· locked final-test {locked.get('status', 'not_configured')}"
                if confirmation else "없음"
            )
        )
        blockers = [
            item.get("code", "")
            for item in (confirmation or {}).get("blocking_reasons", ())
        ]
        if (value or {}).get("blocked_reason"):
            blockers.append(value["blocked_reason"])
        self.compatibility_label.setText(
            "호환성/차단: " + (", ".join(blockers) if blockers else "차단 없음")
        )
        rows = tuple(
            (
                item.get("target_identity", ""),
                item.get("status", ""),
                _metric(item, "rmse"),
                _metric(item, "mae"),
                _metric(item, "r2"),
            )
            for item in (confirmation or {}).get("target_results", ())
        )
        self.targets.setModel(StaticTableModel(
            ("Target", "상태", "RMSE", "MAE", "R²"),
            rows,
        ))
        self.targets.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ready = bool(
            confirmation
            and confirmation.get("status") == "awaiting_user_decision"
        )
        self.approve_button.setEnabled(ready)
        self.reject_button.setEnabled(ready)

    def _decide(self, approve: bool) -> None:
        if not self._confirmation:
            return
        action = "승인하고 현재 사용 모델로 변경" if approve else "거절"
        if not self._confirm(
            "최종 확인",
            f"{self._confirmation['confirmation_id']} evidence를 {action}하시겠습니까?",
        ):
            return
        try:
            outcome = self._controller.decide_final_confirmation(
                self._confirmation["confirmation_id"],
                approve=approve,
                expected_active_revision=self._active_revision,
                reason="Train GUI explicit final decision.",
            )
        except Exception as exc:
            self._notify("최종 확인 실패", str(exc).splitlines()[0], True)
            return
        message = outcome.status
        if outcome.promotion is not None:
            message += f" · promotion {outcome.promotion.status}"
        self._notify("최종 확인", message, outcome.status == "stale")
        self.refresh()

    def _confirm_dialog(self, title: str, message: str) -> bool:
        return QMessageBox.question(self, title, message) == QMessageBox.Yes

    def _notify_dialog(self, title: str, message: str, error: bool) -> None:
        method = QMessageBox.warning if error else QMessageBox.information
        method(self, title, message)


def _metric(item: dict, name: str) -> str:
    value = item.get("metrics", {}).get(name)
    return "" if value is None else str(value)
