"""Predict workspace bottom status presentation."""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QWidget

from apps.common.ui import style


def build_bottom_status(
    summary: QWidget,
    result_badge: QWidget,
    status: QWidget,
    parent: QWidget,
) -> QFrame:
    panel = QFrame(parent)
    panel.setObjectName("Panel")
    panel.setStyleSheet(style.panel_stylesheet())
    layout = QHBoxLayout(panel)
    layout.setContentsMargins(
        style.spacing("space.panel"),
        style.spacing("space.sm"),
        style.spacing("space.panel"),
        style.spacing("space.sm"),
    )
    layout.setSpacing(style.spacing("space.md"))
    layout.addWidget(summary)
    layout.addWidget(result_badge)
    layout.addStretch(1)
    layout.addWidget(status)
    return panel
