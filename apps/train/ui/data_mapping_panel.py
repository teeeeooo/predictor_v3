"""Data Mapping Manager panel."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QModelIndex, QSignalBlocker
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QFileDialog,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.controllers.data_mapping_controller import (
    DataMappingController,
    DataMappingControllerState,
)
from apps.train.ui.data_mapping_models import EditableMappingTableModel, ReadOnlyMappingTableModel
from apps.train.ui.data_mapping_view_models import (
    ATTRIBUTE_HEADERS,
    ENTITY_HEADERS,
    VALIDATION_HEADERS,
    attribute_rows,
    entity_rows,
    validation_rows,
    value_headers,
    value_rows,
)

ENTITY_PANEL_MIN_WIDTH = 420
DETAIL_PANEL_INITIAL_WIDTH = 980
EXPORT_FILTERS = "JSON Files (*.json);;Excel Workbook (*.xlsx)"


class DataMappingPanel(QWidget):
    """Editable Data Mapping Manager admin surface."""

    def __init__(
        self,
        parent: QWidget | None = None,
        controller: DataMappingController | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("DataMappingPanel")
        self.setAccessibleName("Data Mapping Manager")
        self._controller = controller or DataMappingController()
        self._selected_group_key = ""
        self._dirty = False

        self.status_label = QLabel()
        self.status_label.setAccessibleName("Data Mapping validation status")
        self.source_label = QLabel()
        self.source_label.setAccessibleName("Data Mapping source")
        self.entity_table = _table("Groups")
        self.attribute_table = _table("Fields")
        self.row_table = _table("Data")
        self.validation_table = _table("Issues")
        self._buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self._build_command_bar())
        layout.addWidget(self._build_body(), 1)

        self.refresh()

    def refresh(self) -> None:
        """Reload state through the controller."""
        self._apply_state(self._controller.refresh(self._selected_group_key))

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
        layout.setSpacing(style.spacing("space.sm"))
        refresh_button = QPushButton("Refresh")
        refresh_button.setAccessibleName("Refresh")
        refresh_button.clicked.connect(self.refresh)
        layout.addWidget(refresh_button)
        for key, label in (
            ("add_row", "Add Row"),
            ("duplicate_row", "Duplicate"),
            ("delete_row", "Delete"),
            ("import_csv_v2", "Import"),
            ("export_csv_v2", "Export"),
            ("save_mapping_json", "Save"),
            ("reload_runtime", "Reload"),
        ):
            button = QPushButton(label)
            button.setAccessibleName(label)
            button.setEnabled(False)
            self._buttons[key] = button
            layout.addWidget(button)
        self._buttons["add_row"].clicked.connect(self._add_row)
        self._buttons["duplicate_row"].clicked.connect(self._duplicate_row)
        self._buttons["delete_row"].clicked.connect(self._delete_row)
        self._buttons["export_csv_v2"].clicked.connect(self._export)
        self._buttons["save_mapping_json"].clicked.connect(self._save)
        self._buttons["reload_runtime"].clicked.connect(self._reload)
        layout.addStretch(1)
        return panel

    def _build_body(self) -> QSplitter:
        splitter = QSplitter(self)
        splitter.setObjectName("DataMappingSplitter")
        splitter.setAccessibleName("Data Mapping split view")
        splitter.setChildrenCollapsible(False)
        entity_panel = self._panel("Groups", self.entity_table)
        entity_panel.setMinimumWidth(ENTITY_PANEL_MIN_WIDTH)
        self.entity_table.setMinimumWidth(ENTITY_PANEL_MIN_WIDTH - style.spacing("space.panel") * 2)
        splitter.addWidget(entity_panel)
        details = QWidget(splitter)
        layout = QVBoxLayout(details)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(style.spacing("space.sm"))
        self.status_label.setObjectName("PanelTitle")
        layout.addWidget(self.status_label)
        layout.addWidget(self.source_label)
        fields_panel = self._panel("Fields", self.attribute_table)
        fields_panel.setMaximumHeight(140)
        layout.addWidget(fields_panel, 0)
        layout.addWidget(self._panel("Data", self.row_table), 2)
        layout.addWidget(self._panel("Issues", self.validation_table), 1)
        splitter.addWidget(details)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes((ENTITY_PANEL_MIN_WIDTH, DETAIL_PANEL_INITIAL_WIDTH))
        return splitter

    def _panel(self, title: str, table: QTableView) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("Panel")
        panel.setAccessibleName(f"Data Mapping {title}")
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
        layout.addWidget(table, 1)
        return panel

    def _apply_state(self, state: DataMappingControllerState) -> None:
        self.setUpdatesEnabled(False)
        blockers = tuple(QSignalBlocker(table) for table in _data_tables(self))
        try:
            self._selected_group_key = state.selected_group_key
            self._dirty = state.dirty
            self.status_label.setText(state.message)
            self.source_label.setText(state.source_label)
            self.entity_table.setModel(
                ReadOnlyMappingTableModel(ENTITY_HEADERS, entity_rows(state))
            )
            self.attribute_table.setModel(
                ReadOnlyMappingTableModel(ATTRIBUTE_HEADERS, attribute_rows(state))
            )
            self.row_table.setModel(
                EditableMappingTableModel(
                    value_headers(state),
                    value_rows(state),
                    on_cell_changed=self._edit_cell,
                )
            )
            self.validation_table.setModel(
                ReadOnlyMappingTableModel(VALIDATION_HEADERS, validation_rows(state))
            )
            self._sync_action_buttons(state)
            self._bind_entity_selection(state)
        finally:
            del blockers
            self.setUpdatesEnabled(True)
            self.update()

    def _bind_entity_selection(self, state: DataMappingControllerState) -> None:
        selection_model = self.entity_table.selectionModel()
        if selection_model is None:
            return
        selection_model.currentRowChanged.connect(self._on_entity_row_changed)

    def _on_entity_row_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if not current.isValid():
            return
        model = self.entity_table.model()
        key = model.data(model.index(current.row(), 0)) if model is not None else ""
        if key and key != self._selected_group_key:
            self._selected_group_key = str(key)
            self.refresh()

    def _sync_action_buttons(self, state: DataMappingControllerState) -> None:
        actions = {action.key: action for action in state.actions}
        for key, button in self._buttons.items():
            if key in {"add_row", "duplicate_row", "delete_row"}:
                button.setEnabled(bool(state.selected_group_key))
                button.setToolTip("")
                continue
            action = actions.get(key)
            button.setEnabled(bool(action and action.enabled))
            if action is not None:
                button.setToolTip(action.reason)

    def _edit_cell(self, row: int, column: str, value: object) -> bool:
        if not self._selected_group_key:
            return False
        self._apply_state(
            self._controller.edit_cell(self._selected_group_key, row, column, value)
        )
        return True

    def _add_row(self) -> None:
        if self._selected_group_key:
            self._apply_state(self._controller.add_row(self._selected_group_key))

    def _duplicate_row(self) -> None:
        row = self._selected_row()
        if self._selected_group_key and row is not None:
            self._apply_state(self._controller.duplicate_row(self._selected_group_key, row))

    def _delete_row(self) -> None:
        row = self._selected_row()
        if self._selected_group_key and row is not None:
            self._apply_state(self._controller.delete_row(self._selected_group_key, row))

    def _reload(self) -> None:
        if self._dirty and not self._confirm_reload_discard():
            return
        self._apply_state(self._controller.reload())

    def _confirm_reload_discard(self) -> bool:
        return (
            QMessageBox.question(
                self,
                "Reload Data Mapping",
                "Unsaved changes will be discarded. Reload from file?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            == QMessageBox.Yes
        )

    def _save(self) -> None:
        self._apply_state(self._controller.save())

    def _export(self) -> None:
        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Data Mapping Review Snapshot",
            "data_mapping_review_snapshot.json",
            EXPORT_FILTERS,
        )
        if path:
            destination, export_format = _resolve_export_selection(path, selected_filter)
            self._apply_state(self._controller.export_snapshot(destination, export_format))

    def _selected_row(self) -> int | None:
        index = self.row_table.currentIndex()
        if not index.isValid():
            return None
        return index.row()


def _data_tables(panel: DataMappingPanel) -> tuple[QTableView, ...]:
    return (
        panel.entity_table,
        panel.attribute_table,
        panel.row_table,
        panel.validation_table,
    )


def _table(accessible_name: str) -> QTableView:
    table = QTableView()
    table.setObjectName(accessible_name.replace(" ", ""))
    table.setAccessibleName(accessible_name)
    table.setEditTriggers(
        QAbstractItemView.DoubleClicked
        | QAbstractItemView.EditKeyPressed
        | QAbstractItemView.AnyKeyPressed
    )
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    return table


def _resolve_export_selection(path: str, selected_filter: str) -> tuple[str, str]:
    suffix = Path(path).suffix.lower()
    if "*.xlsx" in selected_filter:
        if suffix == ".xlsx":
            return path, "xlsx"
        if suffix == ".json":
            return str(Path(path).with_suffix(".xlsx")), "xlsx"
        return f"{path}.xlsx", "xlsx"
    if suffix == ".xlsx":
        return path, "xlsx"
    if suffix == ".json":
        return path, "json"
    return f"{path}.json", "json"
