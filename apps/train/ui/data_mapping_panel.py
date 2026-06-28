"""Data Mapping visual panel."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from core.mapping.paths import MAPPING_JSON_FILE


class DataMappingPanel(QWidget):
    """Visual Data Mapping admin surface without execution wiring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DataMappingPanel")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self._build_mapping_source_panel(), 1)
        layout.addWidget(self._build_mapping_status_panel(), 2)

    def _build_mapping_source_panel(self) -> QFrame:
        panel, body = _panel("Data Mapping")
        mapping_path = QLineEdit(MAPPING_JSON_FILE)
        mapping_path.setReadOnly(True)
        update_button = QPushButton("매핑 업데이트")
        update_button.setObjectName("PrimaryButton")
        update_button.setEnabled(False)
        update_button.setToolTip("mapping Excel update execution은 후속 Arc에서 구현됩니다.")
        reload_button = QPushButton("상태 새로고침")
        reload_button.setEnabled(False)

        body.addWidget(QLabel("mapping.json 경로"))
        body.addWidget(mapping_path)
        body.addWidget(_status_line("mapping 파일", "found" if Path(MAPPING_JSON_FILE).exists() else "missing", "ready" if Path(MAPPING_JSON_FILE).exists() else "missing"))
        actions = QHBoxLayout()
        actions.addWidget(update_button)
        actions.addWidget(reload_button)
        actions.addStretch(1)
        body.addLayout(actions)
        body.addStretch(1)
        return panel

    def _build_mapping_status_panel(self) -> QFrame:
        panel, body = _panel("Mapping Status / Log")
        log = QTextEdit()
        log.setObjectName("MappingLog")
        log.setReadOnly(True)
        log.setPlainText(
            "Mapping update execution is intentionally deferred.\n"
            "Predict dropdown/autofill uses the current core mapping owner."
        )
        body.addWidget(log)
        return panel


def _panel(title: str) -> tuple[QFrame, QVBoxLayout]:
    panel = QFrame()
    panel.setObjectName("Panel")
    panel.setStyleSheet(style.panel_stylesheet())
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(
        style.spacing("space.panel"),
        style.spacing("space.panel"),
        style.spacing("space.panel"),
        style.spacing("space.panel"),
    )
    layout.setSpacing(style.spacing("space.sm"))
    heading = QLabel(title)
    heading.setObjectName("PanelTitle")
    heading.setFont(style.qfont("font.panel_title"))
    layout.addWidget(heading)
    return panel, layout


def _status_line(label: str, value: str, kind: str) -> QLabel:
    item = QLabel(f"{label}: {value}")
    item.setStyleSheet(style.status_badge_stylesheet(kind))
    return item
