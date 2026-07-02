"""Feature Catalog Train/Admin panel."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)

from apps.common.ui import style
from apps.train.controllers.feature_catalog_controller import (
    FeatureCatalogController,
    FeatureCatalogControllerState,
    FeatureCatalogExportState,
    FeatureCatalogSaveState,
)
from apps.train.ui.feature_catalog.delegates import FeatureCatalogDropdownDelegate
from apps.train.ui.feature_catalog.help_dialog import FeatureCatalogHelpDialog
from apps.train.ui.feature_catalog.table_model import FeatureCatalogTableModel
from apps.train.ui.feature_catalog.table_view import FeatureCatalogTableView


class FeatureCatalogPanel(QWidget):
    """Feature Catalog manager and validation surface."""

    def __init__(
        self,
        parent: QWidget | None = None,
        controller: FeatureCatalogController | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("FeatureCatalogPanel")
        self.controller = controller or FeatureCatalogController()
        self.table_model = FeatureCatalogTableModel()
        self._snapshot = None
        self.table_model.dirty_changed.connect(self._set_dirty_state)

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
        self.export_button = QPushButton("CSV 내보내기")
        self.save_button = QPushButton("저장")
        self.revert_button = QPushButton("되돌리기/다시 불러오기")
        self.help_button = QPushButton("도움말")
        self.refresh_button.clicked.connect(self.refresh)
        self.export_button.clicked.connect(self._export_csv)
        self.save_button.clicked.connect(self._save_catalog)
        self.revert_button.clicked.connect(self.refresh)
        self.help_button.clicked.connect(self._show_help)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.export_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.revert_button)
        layout.addWidget(self.help_button)
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
        self.export_value = QLabel("No export yet")
        self.validation_value.setStyleSheet(style.status_badge_stylesheet("neutral"))
        self.export_value.setStyleSheet(style.status_badge_stylesheet("neutral"))
        for row, (label, widget) in enumerate(
            (
                ("Catalog path", self.path_value),
                ("Rows", self.row_count_value),
                ("Active rows", self.active_count_value),
                ("Validation", self.validation_value),
                ("Export", self.export_value),
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
        table = FeatureCatalogTableView()
        table.setObjectName("FeatureCatalogTable")
        table.setModel(self.table_model)
        table.setItemDelegate(FeatureCatalogDropdownDelegate(table))
        table.verticalHeader().setVisible(True)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnsToContents()
        self.table = table
        body.addWidget(table, 1)
        return panel

    def _apply_state(self, state: FeatureCatalogControllerState) -> None:
        snapshot = state.snapshot
        self._snapshot = snapshot
        self.table_model.set_snapshot(snapshot)
        self.table.clear_undo_history()
        self.export_button.setEnabled(snapshot is not None)
        self._set_dirty_state(False)
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

    def _save_catalog(self) -> None:
        state = self.controller.save_records(self.table_model.records())
        self._apply_save_state(state)

    def _export_csv(self) -> None:
        if self._snapshot is None:
            self._set_export_status("Load the Feature Catalog before export.", "error")
            return
        path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Feature Catalog CSV",
            "feature_catalog_export.csv",
            "CSV files (*.csv);;All files (*.*)",
        )
        if not path:
            self._set_export_status("Export cancelled.", "neutral")
            return
        self._apply_export_state(
            self.controller.export_records(self.table_model.records(), self._snapshot, path)
        )

    def _show_help(self) -> None:
        dialog = FeatureCatalogHelpDialog(self)
        dialog.exec()

    def _set_validation_status(self, message: str, status: str) -> None:
        kind = "ready" if status == "ready" else "error"
        self.validation_value.setText(message)
        self.validation_value.setStyleSheet(style.status_badge_stylesheet(kind))

    def _apply_export_state(self, state: FeatureCatalogExportState) -> None:
        self._set_export_status(state.message, state.status)

    def _set_export_status(self, message: str, status: str) -> None:
        kind = "ready" if status == "ready" else "error" if status == "error" else "neutral"
        self.export_value.setText(message)
        self.export_value.setStyleSheet(style.status_badge_stylesheet(kind))

    def _apply_save_state(self, state: FeatureCatalogSaveState) -> None:
        result = state.result
        if state.status == "ready" and result is not None and result.snapshot is not None:
            self._apply_state(
                FeatureCatalogControllerState(
                    snapshot=result.snapshot,
                    status="ready",
                    message=state.message,
                )
            )
            self.messages.setPlainText("\n".join(result.snapshot.validation_messages()))
            return
        self._set_validation_status(state.message, "error")
        if result is not None and result.errors:
            self.messages.setPlainText("\n".join(result.errors))
        else:
            self.messages.setPlainText(state.message)

    def _set_dirty_state(self, dirty: bool) -> None:
        self.save_button.setEnabled(dirty)
        self.revert_button.setEnabled(dirty)


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
