"""Data Mapping Manager panel."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QModelIndex, QSignalBlocker, Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QFileDialog,
    QSplitter,
    QStackedWidget,
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
from apps.train.ui.data_mapping import DataMappingTableView, DataMappingToolbar
from apps.train.ui.data_mapping_table_sizing import (
    apply_group_navigation_sizing,
    apply_primary_table_sizing,
    apply_secondary_table_sizing,
    configure_table_defaults,
)
from apps.train.ui.data_mapping_view_models import (
    ATTRIBUTE_HEADERS,
    GROUP_HEADERS,
    VALIDATION_HEADERS,
    attribute_rows,
    group_rows,
    status_kind,
    status_summary,
    validation_rows,
    value_headers,
    value_rows,
    workspace_state_copy,
)

GROUP_NAV_MIN_WIDTH = 190
GROUP_NAV_MAX_WIDTH = 280
GROUP_NAV_INITIAL_WIDTH = 230
WORKSPACE_INITIAL_WIDTH = 1050
DETAILS_INITIAL_HEIGHT = 210
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
        self._group_keys: tuple[str, ...] = ()

        self.status_label = QLabel()
        self.status_label.setAccessibleName("Data Mapping validation status")
        self.source_label = QLabel()
        self.source_label.setAccessibleName("Data Mapping source")
        self.source_label.setMinimumWidth(0)
        self.source_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.summary_label = QLabel()
        self.summary_label.setAccessibleName("Data Mapping summary")
        self.entity_table = _table("Groups")
        self.attribute_table = _table("Fields")
        self.row_table = DataMappingTableView()
        _configure_table(self.row_table, "Data")
        self.row_table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.row_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.row_table.setEditTriggers(
            QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed
        )
        self.validation_table = _table("Issues")
        self.row_table.bind_interactions(
            batch_edit=self._edit_cells,
            undo=self._undo,
        )
        self.toolbar = DataMappingToolbar(
            self,
            callbacks={
                "add_row": self._add_row,
                "duplicate_row": self._duplicate_row,
                "delete_row": self._delete_row,
                "export_csv_v2": self._export,
                "save_mapping_json": self._save,
                "refresh_view": self.refresh,
                "reload_runtime": self._reload,
            },
        )
        self._buttons = self.toolbar.buttons
        self.details_toggle = QPushButton("Hide details")
        self.details_toggle.setAccessibleName("Toggle field and issue details")
        self.details_toggle.clicked.connect(self._toggle_details)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self._build_body(), 1)

        self.refresh()

    def refresh(self) -> None:
        """Reload state through the controller."""
        self._apply_state(self._controller.refresh(self._selected_group_key))

    def _build_body(self) -> QSplitter:
        splitter = QSplitter(self)
        splitter.setObjectName("DataMappingSplitter")
        splitter.setAccessibleName("Data Mapping split view")
        splitter.setChildrenCollapsible(False)
        group_panel = self._panel("Mapping Groups", self.entity_table)
        group_panel.setMinimumWidth(GROUP_NAV_MIN_WIDTH)
        group_panel.setMaximumWidth(GROUP_NAV_MAX_WIDTH)
        splitter.addWidget(group_panel)

        workspace = QWidget(splitter)
        layout = QVBoxLayout(workspace)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self._build_status_strip())
        layout.addWidget(self.toolbar)

        self.workspace_stack = QStackedWidget(workspace)
        self.primary_panel = self._panel("Mapping Rows", self.row_table)
        self.primary_title = self.primary_panel.findChild(QLabel, "PanelTitle")
        self.state_panel = self._build_workspace_state()
        self.workspace_stack.addWidget(self.primary_panel)
        self.workspace_stack.addWidget(self.state_panel)

        self.details_panel = self._build_details_panel()
        self.content_splitter = QSplitter(Qt.Vertical, workspace)
        self.content_splitter.setAccessibleName("Mapping rows and secondary details")
        self.content_splitter.addWidget(self.workspace_stack)
        self.content_splitter.addWidget(self.details_panel)
        self.content_splitter.setStretchFactor(0, 4)
        self.content_splitter.setStretchFactor(1, 1)
        self.content_splitter.setCollapsible(0, False)
        self.content_splitter.setCollapsible(1, True)
        self.content_splitter.setSizes((620, DETAILS_INITIAL_HEIGHT))
        layout.addWidget(self.content_splitter, 1)

        splitter.addWidget(workspace)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes((GROUP_NAV_INITIAL_WIDTH, WORKSPACE_INITIAL_WIDTH))
        return splitter

    def _build_status_strip(self) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("Panel")
        panel.setStyleSheet(style.panel_stylesheet())
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.xs"))
        self.status_label.setFont(style.qfont("font.panel_title"))
        heading = QHBoxLayout()
        heading.setSpacing(style.spacing("space.sm"))
        heading.addWidget(self.status_label)
        heading.addStretch(1)
        heading.addWidget(self.details_toggle)
        layout.addLayout(heading)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.source_label)
        return panel

    def _build_details_panel(self) -> QFrame:
        panel = QFrame(self)
        panel.setAccessibleName("Data Mapping secondary details")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self._panel("Field Definitions", self.attribute_table), 1)
        layout.addWidget(self._panel("Validation & Issues", self.validation_table), 2)
        return panel

    def _build_workspace_state(self) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("Panel")
        panel.setStyleSheet(style.panel_stylesheet())
        body = QVBoxLayout(panel)
        body.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
        )
        body.addStretch(1)
        self.state_title = QLabel()
        self.state_title.setObjectName("PanelTitle")
        self.state_title.setFont(style.qfont("font.window_title"))
        self.state_title.setAlignment(Qt.AlignCenter)
        self.state_message = QLabel()
        self.state_message.setAlignment(Qt.AlignCenter)
        self.state_message.setWordWrap(True)
        body.addWidget(self.state_title)
        body.addWidget(self.state_message)
        body.addStretch(1)
        return panel

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
        selected_cell = self._selected_cell()
        self._current_state = state
        self.setUpdatesEnabled(False)
        blockers = tuple(QSignalBlocker(table) for table in _data_tables(self))
        try:
            self._selected_group_key = state.selected_group_key
            self._dirty = state.dirty
            self._group_keys = tuple(entity.entity_key for entity in state.entities)
            self._sync_status(state)
            self.source_label.setText(f"Source: {state.source_label or 'Not available'}")
            self.source_label.setToolTip(state.source_label)
            self.entity_table.setModel(
                ReadOnlyMappingTableModel(GROUP_HEADERS, group_rows(state))
            )
            self.attribute_table.setModel(
                ReadOnlyMappingTableModel(ATTRIBUTE_HEADERS, attribute_rows(state))
            )
            self.row_table.setModel(
                EditableMappingTableModel(
                    value_headers(state),
                    value_rows(state),
                    on_cell_changed=self._edit_cell,
                    read_only_cells=state.read_only_cells,
                )
            )
            self.validation_table.setModel(
                ReadOnlyMappingTableModel(VALIDATION_HEADERS, validation_rows(state))
            )
            apply_group_navigation_sizing(self.entity_table)
            apply_primary_table_sizing(self.row_table)
            apply_secondary_table_sizing(
                self.attribute_table,
                description_header="Notes",
            )
            apply_secondary_table_sizing(
                self.validation_table,
                description_header="Message",
            )
            self._bind_group_selection(state)
            self._bind_row_selection(selected_cell)
            self.toolbar.bind_state(state, has_row=self._selected_row() is not None)
            self._sync_workspace_state(state)
        finally:
            del blockers
            self.setUpdatesEnabled(True)
            self.update()

    def _bind_group_selection(self, state: DataMappingControllerState) -> None:
        selection_model = self.entity_table.selectionModel()
        if selection_model is None:
            return
        selection_model.currentRowChanged.connect(self._on_entity_row_changed)
        if state.selected_group_key in self._group_keys:
            row = self._group_keys.index(state.selected_group_key)
            blocker = QSignalBlocker(selection_model)
            self.entity_table.setCurrentIndex(self.entity_table.model().index(row, 0))
            del blocker

    def _bind_row_selection(self, selected_cell: tuple[int, int] | None) -> None:
        selection_model = self.row_table.selectionModel()
        if selection_model is None:
            return
        selection_model.currentRowChanged.connect(self._on_value_row_changed)
        row_count = self.row_table.model().rowCount()
        if selected_cell is not None and row_count:
            row = min(selected_cell[0], row_count - 1)
            column = min(selected_cell[1], max(0, self.row_table.model().columnCount() - 1))
            self.row_table.setCurrentIndex(self.row_table.model().index(row, column))
        self._sync_row_actions()

    def _on_entity_row_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if not current.isValid():
            return
        key = self._group_keys[current.row()] if current.row() < len(self._group_keys) else ""
        if key and key != self._selected_group_key:
            self._selected_group_key = str(key)
            self.refresh()

    def _on_value_row_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None:
        self._sync_row_actions()

    def _sync_row_actions(self) -> None:
        state = getattr(self, "_current_state", None)
        if state is not None:
            self.toolbar.bind_state(state, has_row=self._selected_row() is not None)

    def _sync_status(self, state: DataMappingControllerState) -> None:
        self.status_label.setText(state.message)
        self.status_label.setStyleSheet(
            style.status_badge_stylesheet(status_kind(state))
        )
        self.summary_label.setText(status_summary(state))

    def _sync_workspace_state(self, state: DataMappingControllerState) -> None:
        entity = next(
            (item for item in state.entities if item.entity_key == state.selected_group_key),
            None,
        )
        title, message = workspace_state_copy(state)
        if title:
            self.state_title.setText(title)
            self.state_message.setText(message)
            self.workspace_stack.setCurrentWidget(self.state_panel)
        else:
            if self.primary_title is not None:
                self.primary_title.setText(f"{entity.label} Mapping Rows")
            self.workspace_stack.setCurrentWidget(self.primary_panel)

    def _toggle_details(self) -> None:
        visible = not self.details_panel.isVisible()
        self.details_panel.setVisible(visible)
        self.details_toggle.setText("Hide details" if visible else "Show details")
        if visible:
            self.content_splitter.setSizes((620, DETAILS_INITIAL_HEIGHT))

    def _edit_cell(self, row: int, column: str, value: object) -> bool:
        if not self._selected_group_key:
            return False
        state = self._controller.edit_cell(self._selected_group_key, row, column, value)
        self._dirty = state.dirty
        self._sync_status(state)
        self._current_state = state
        self.toolbar.bind_state(state, has_row=self._selected_row() is not None)
        QTimer.singleShot(0, self.refresh)
        return True

    def _edit_cells(self, edits) -> DataMappingControllerState:  # noqa: ANN001
        state = self._controller.edit_cells(self._selected_group_key, edits)
        self._apply_state(state)
        return state

    def _undo(self) -> DataMappingControllerState:
        state = self._controller.undo(self._selected_group_key)
        self._apply_state(state)
        return state

    def _add_row(self) -> None:
        if self._selected_group_key:
            state = self._controller.add_row(self._selected_group_key)
            self._apply_state(state)
            self._select_row(max(0, len(state.values) - 1))

    def _duplicate_row(self) -> None:
        row = self._selected_row()
        if self._selected_group_key and row is not None:
            self._apply_state(self._controller.duplicate_row(self._selected_group_key, row))
            self._select_row(row + 1)

    def _delete_row(self) -> None:
        row = self._selected_row()
        if self._selected_group_key and row is not None:
            self._apply_state(self._controller.delete_row(self._selected_group_key, row))
            self._select_row(row)

    def _reload(self) -> None:
        if self._dirty and not self._confirm_reload_discard():
            return
        self._apply_state(self._controller.reload(self._selected_group_key))

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
        self._apply_state(self._controller.save(self._selected_group_key))

    def _export(self) -> None:
        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Data Mapping Review Snapshot",
            "data_mapping_review_snapshot.json",
            EXPORT_FILTERS,
        )
        if path:
            destination, export_format = _resolve_export_selection(path, selected_filter)
            self._apply_state(
                self._controller.export_snapshot(
                    destination,
                    export_format,
                    self._selected_group_key,
                )
            )

    def _selected_row(self) -> int | None:
        index = self.row_table.currentIndex()
        if not index.isValid():
            return None
        return index.row()

    def _selected_cell(self) -> tuple[int, int] | None:
        index = self.row_table.currentIndex()
        if not index.isValid():
            return None
        return index.row(), index.column()

    def _select_row(self, row: int) -> None:
        model = self.row_table.model()
        if model is None or not model.rowCount() or not model.columnCount():
            return
        index = model.index(min(row, model.rowCount() - 1), 0)
        self.row_table.setCurrentIndex(index)
        self.row_table.scrollTo(index)


def _data_tables(panel: DataMappingPanel) -> tuple[QTableView, ...]:
    return (
        panel.entity_table,
        panel.attribute_table,
        panel.row_table,
        panel.validation_table,
    )


def _table(accessible_name: str) -> QTableView:
    table = QTableView()
    _configure_table(table, accessible_name)
    return table


def _configure_table(table: QTableView, accessible_name: str) -> None:
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
    table.setAlternatingRowColors(True)
    configure_table_defaults(table)


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
