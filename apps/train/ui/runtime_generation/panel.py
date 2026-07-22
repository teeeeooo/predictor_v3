"""Concise runtime generation status and recovery actions."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from apps.common.runtime_generation import GenerationTransitionStatus
from apps.common.ui import style


class RuntimeGenerationPanel(QFrame):
    def __init__(
        self,
        *,
        on_retry: Callable[[], None],
        on_review_mapping: Callable[[], None],
        on_save_mapping: Callable[[], None],
        on_discard_mapping: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setStyleSheet(style.panel_stylesheet())
        layout = QHBoxLayout(self)
        self.status_label = QLabel("Up to date", self)
        self.status_label.setAccessibleName("Runtime generation status")
        layout.addWidget(self.status_label)
        layout.addStretch(1)
        self.retry_button = _button("Retry Apply", on_retry, self)
        self.review_button = _button("Review Update", on_review_mapping, self)
        self.save_mapping_button = _button("Save Mapping", on_save_mapping, self)
        self.discard_button = _button("Discard and Reload", on_discard_mapping, self)
        for button in (
            self.retry_button, self.review_button,
            self.save_mapping_button, self.discard_button,
        ):
            layout.addWidget(button)

    def apply_status(self, status: GenerationTransitionStatus) -> None:
        self.status_label.setText(status.message)
        mapping_review = status.blocker_code == "mapping_reconciliation_required"
        self.retry_button.setVisible(bool(status.pending_generation) and not mapping_review)
        self.review_button.setVisible(mapping_review)
        self.save_mapping_button.setVisible(mapping_review)
        self.discard_button.setVisible(mapping_review)
        self.setToolTip(
            "\n".join(item for item in (
                f"Persisted: {status.persisted_generation}",
                f"Process active: {status.active_generation}",
                f"Pending: {status.pending_generation}" if status.pending_generation else "",
                f"Blocker: {status.blocker_code}" if status.blocker_code else "",
                f"Action: {status.recommended_action}" if status.recommended_action else "",
                f"Model: {status.model_compatibility}" if status.model_compatibility else "",
                *(f"{item.participant}: active={item.active_generation}, prepared={item.prepared_generation or '-'}" for item in status.participants),
                *(f"Mapping: {item}" for item in status.mapping_conflicts[:8]),
            ) if item)
        )


def _button(label: str, callback: Callable[[], None], parent: QWidget) -> QPushButton:
    button = QPushButton(label, parent)
    button.clicked.connect(callback)
    button.setVisible(False)
    return button
