"""Small status widgets for the Predict workspace."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from apps.common.ui import style


class StatusBadge(QLabel):
    """Non-clickable status badge using semantic visual roles."""

    def __init__(
        self,
        label: str,
        value: str,
        kind: str = "neutral",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._label = label
        self.setObjectName("StatusBadge")
        self.setAlignment(Qt.AlignCenter)
        self.set_status(value, kind)

    def set_status(self, value: str, kind: str = "neutral") -> None:
        """Update badge text and visual status kind."""
        self.setText(f"{self._label}: {value}")
        self.setStyleSheet(style.status_badge_stylesheet(kind))


class StatusStrip(QFrame):
    """Horizontal strip for high-level Predict environment status."""

    def __init__(
        self,
        badges: tuple[StatusBadge, ...],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setStyleSheet(style.panel_stylesheet())
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        for badge in badges:
            layout.addWidget(badge)
        layout.addStretch(1)
