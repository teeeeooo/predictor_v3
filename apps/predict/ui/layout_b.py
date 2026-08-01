"""Cached full-surface Layout B composition for the Predict workspace."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.predict.application.workspace_state import WorkspaceSurface
from apps.predict.schema.case_table_schema_adapter import UnifiedCaseColumn
from apps.predict.ui.tables.group_header import TableLinkedGroupHeader


class PredictLayoutBSurfaces(QWidget):
    """Keep Input and Result widgets alive while showing one full surface."""

    def __init__(
        self,
        input_table: QWidget,
        result_table: QWidget,
        input_columns: tuple[UnifiedCaseColumn, ...],
        on_surface_requested: Callable[[WorkspaceSurface], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_surface_requested = on_surface_requested
        self.input_button = QPushButton("입력 작성", self)
        self.result_button = QPushButton("결과 검토", self)
        self.input_button.setCheckable(True)
        self.result_button.setCheckable(True)
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._button_group.addButton(self.input_button)
        self._button_group.addButton(self.result_button)
        self.input_button.clicked.connect(
            lambda: self._on_surface_requested(WorkspaceSurface.INPUT)
        )
        self.result_button.clicked.connect(
            lambda: self._on_surface_requested(WorkspaceSurface.RESULT)
        )

        controls = QHBoxLayout()
        controls.setSpacing(style.spacing("space.sm"))
        controls.addWidget(QLabel("작업 화면"))
        controls.addWidget(self.input_button)
        controls.addWidget(self.result_button)
        controls.addStretch(1)

        input_panel = self._panel("예측 케이스")
        input_layout = input_panel.layout()
        self.group_header = TableLinkedGroupHeader(
            input_table,
            input_columns,
            input_panel,
        )
        input_layout.addWidget(self.group_header)
        input_layout.addWidget(input_table)

        result_panel = self._panel("결과 검토")
        result_panel.layout().addWidget(result_table)

        self.stack = QStackedWidget(self)
        self.stack.addWidget(input_panel)
        self.stack.addWidget(result_panel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(style.spacing("space.sm"))
        layout.addLayout(controls)
        layout.addWidget(self.stack, 1)
        self.show_surface(WorkspaceSurface.INPUT)

    def show_surface(self, surface: WorkspaceSurface) -> None:
        """Present one cached page without changing either table's local state."""
        resolved = WorkspaceSurface(surface)
        is_input = resolved is WorkspaceSurface.INPUT
        self.input_button.setChecked(is_input)
        self.result_button.setChecked(not is_input)
        self.stack.setCurrentIndex(0 if is_input else 1)

    def _panel(self, title: str) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("Panel")
        panel.setStyleSheet(style.panel_stylesheet())
        label = QLabel(title, panel)
        label.setObjectName("PanelTitle")
        label.setFont(style.qfont("font.panel_title"))
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(label)
        return panel
