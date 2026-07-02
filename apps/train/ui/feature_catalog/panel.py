"""Feature Catalog Train/Admin panel."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.controllers.feature_catalog_controller import (
    FeatureCatalogController,
    FeatureCatalogControllerState,
)
from apps.train.ui.feature_catalog.table_model import FeatureCatalogTableModel


class FeatureCatalogPanel(QWidget):
    """Read-only Feature Catalog viewer and validation surface."""

    def __init__(
        self,
        parent: QWidget | None = None,
        controller: FeatureCatalogController | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("FeatureCatalogPanel")
        self.controller = controller or FeatureCatalogController()
        self.table_model = FeatureCatalogTableModel()

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
        content.addWidget(self._build_summary_panel(), 1)
        content.addWidget(self._build_table_panel(), 3)
        layout.addLayout(content, 1)
        self.refresh()

    def refresh(self) -> None:
        """Reload the Feature Catalog and update the read-only view."""
        self._apply_state(self.controller.refresh())

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
        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.clicked.connect(self.refresh)
        layout.addWidget(self.refresh_button)
        layout.addStretch(1)
        return panel

    def _build_summary_panel(self) -> QFrame:
        panel, body = _panel("Feature Catalog")
        grid = QGridLayout()
        grid.setSpacing(style.spacing("space.sm"))
        self.path_value = QLabel("-")
        self.row_count_value = QLabel("0")
        self.active_count_value = QLabel("0")
        self.validation_value = QLabel("Validation pending")
        self.validation_value.setStyleSheet(style.status_badge_stylesheet("neutral"))
        for row, (label, widget) in enumerate(
            (
                ("Catalog path", self.path_value),
                ("Rows", self.row_count_value),
                ("Active rows", self.active_count_value),
                ("Validation", self.validation_value),
            )
        ):
            grid.addWidget(QLabel(label), row, 0)
            grid.addWidget(widget, row, 1)
        body.addLayout(grid)
        self.messages = QTextEdit()
        self.messages.setObjectName("FeatureCatalogValidationMessages")
        self.messages.setReadOnly(True)
        self.messages.setMinimumHeight(160)
        body.addWidget(QLabel("Validation Messages"))
        body.addWidget(self.messages, 1)
        return panel

    def _build_table_panel(self) -> QFrame:
        panel, body = _panel("Catalog Rows")
        table = QTableView()
        table.setObjectName("FeatureCatalogTable")
        table.setModel(self.table_model)
        table.verticalHeader().setVisible(True)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnsToContents()
        self.table = table
        body.addWidget(table, 1)
        return panel

    def _apply_state(self, state: FeatureCatalogControllerState) -> None:
        snapshot = state.snapshot
        self.table_model.set_snapshot(snapshot)
        if snapshot is None:
            self.path_value.setText("-")
            self.row_count_value.setText("0")
            self.active_count_value.setText("0")
            self._set_validation_status(state.message, "error")
            self.messages.setPlainText(state.message)
            return

        self.path_value.setText(str(snapshot.path))
        self.row_count_value.setText(str(snapshot.row_count))
        self.active_count_value.setText(str(snapshot.active_count))
        self._set_validation_status(state.message, state.status)
        self.messages.setPlainText("\n".join(snapshot.validation_messages()))
        self.table.resizeColumnsToContents()

    def _set_validation_status(self, message: str, status: str) -> None:
        kind = "ready" if status == "ready" else "error"
        self.validation_value.setText(message)
        self.validation_value.setStyleSheet(style.status_badge_stylesheet(kind))


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
