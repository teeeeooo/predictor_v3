"""Data Mapping visual panel."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.ui.models.static_table_model import StaticTableModel
from core.mapping.paths import MAPPING_JSON_FILE


class DataMappingPanel(QWidget):
    """Visual Data Mapping admin surface without execution wiring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DataMappingPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self._build_command_bar())

        content = QHBoxLayout()
        content.setSpacing(style.spacing("space.sm"))
        content.addWidget(self._build_mapping_source_panel(), 1)
        content.addWidget(self._build_mapping_status_panel(), 2)
        layout.addLayout(content, 1)

    def _build_command_bar(self) -> QFrame:
        panel = QFrame(self)
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
        for button in (
            _disabled_button("매핑 Excel 선택"),
            _disabled_button("매핑 업데이트", primary=True),
            _disabled_button("상태 새로고침"),
        ):
            layout.addWidget(button)
        layout.addStretch(1)
        return panel

    def _build_mapping_source_panel(self) -> QFrame:
        panel, body = _panel("Data Mapping")
        body.addWidget(QLabel("mapping.json 경로"))
        body.addWidget(_readonly_line(MAPPING_JSON_FILE))
        body.addWidget(QLabel("Excel source"))
        body.addWidget(_readonly_line("후속 Arc에서 선택"))
        body.addWidget(QLabel("Predict dropdown owner"))
        body.addWidget(_readonly_line("current core mapping owner"))
        body.addStretch(1)
        return panel

    def _build_mapping_status_panel(self) -> QFrame:
        panel, body = _panel("Mapping Status / Log")
        body.addWidget(_mapping_table())
        log = QTextEdit()
        log.setObjectName("MappingLog")
        log.setReadOnly(True)
        log.setPlainText(
            "Mapping update execution is intentionally deferred.\n"
            "Predict dropdown/autofill uses the current core mapping owner."
        )
        body.addWidget(log, 1)
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


def _readonly_line(value: str) -> QLineEdit:
    line = QLineEdit(value)
    line.setReadOnly(True)
    return line


def _disabled_button(text: str, primary: bool = False) -> QPushButton:
    button = QPushButton(text)
    if primary:
        button.setObjectName("PrimaryButton")
    button.setEnabled(False)
    button.setToolTip("mapping Excel update execution은 후속 Arc에서 구현됩니다.")
    return button


def _mapping_table() -> QTableView:
    exists = Path(MAPPING_JSON_FILE).exists()
    rows = (
        ("mapping.json", "found" if exists else "missing", "현재 JSON read-only 사용"),
        ("Excel update", "deferred", "실행 foundation은 후속 Arc"),
        ("Per-row dropdown", "active owner", "Predict mapping repository 사용"),
    )
    table = QTableView()
    table.setModel(StaticTableModel(("Item", "Status", "Notes"), rows))
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setMinimumHeight(180)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    return table
