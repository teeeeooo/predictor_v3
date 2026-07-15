"""Inventory-first Data Definition Train/Admin panel."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QModelIndex, QSignalBlocker, Qt
from PySide6.QtGui import QResizeEvent, QShowEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.application.data_mapping import (
    DataMappingNavigationRequest,
    DataMappingNavigationResult,
)
from apps.train.controllers.data_definition_controller import (
    DataDefinitionController,
    DataDefinitionControllerState,
)
from apps.train.controllers.data_definition_detail_projection import DataDefinitionDetailState
from apps.train.controllers.data_definition_presentation import (
    DataDefinitionInventoryProjection,
    project_data_definition_inventory,
)
from apps.train.controllers.data_definition_impact_projection import (
    project_data_definition_impact,
)
from apps.train.controllers.data_definition_interaction import (
    project_data_definition_interaction,
)
from apps.train.ui.data_definition_diagnostics import (
    DataDefinitionDiagnostics,
    definition_table,
)
from apps.train.ui.data_definition_add_dialog import DataDefinitionAddDialog
from apps.train.ui.data_definition_edit_dialog import DataDefinitionEditDialog
from apps.train.ui.data_definition_models import DataDefinitionInventoryTableModel
from apps.train.ui.data_definition_impact_view import DataDefinitionImpactView
from apps.train.ui.data_definition import DataDefinitionHandoffPanel
from apps.train.ui.data_definition.workspace_behavior import (
    DataDefinitionWorkspaceBehavior,
)
from apps.train.ui.data_mapping_models import ReadOnlyMappingTableModel
from core.data_definition import AddDefinitionIntent, EditDefinitionIntent

DETAIL_HEADERS = ("Property", "Value")
INVENTORY_INITIAL_WIDTH = 760
DETAIL_INITIAL_WIDTH = 500


class DataDefinitionPanel(QWidget):
    """Inventory-first manager over the existing Data Definition lifecycle."""

    def __init__(
        self,
        parent: QWidget | None = None,
        controller: DataDefinitionController | None = None,
        on_open_data_mapping: (
            Callable[[DataMappingNavigationRequest], DataMappingNavigationResult] | None
        ) = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("DataDefinitionPanel")
        self.setAccessibleName("Data Definition")
        self._controller = controller or DataDefinitionController()
        self._state: DataDefinitionControllerState | None = None
        self._selected_identity: tuple[str, str] | None = None
        self._preferred_identity: tuple[str, str] | None = None
        self._last_projected_identity: tuple[str, str] | None = None

        self.status_label = QLabel("Data Definition pending.")
        self.status_label.setObjectName("PanelTitle")
        self.status_label.setAccessibleName("Data Definition application status")
        self.status_label.setWordWrap(True)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search label, key, or ML name")
        self.search_input.setAccessibleName("Search Data Definitions")
        self.category_filter = _filter_combo("Filter Data Definitions by category")
        self.source_filter = _filter_combo("Filter Data Definitions by value source")
        self.state_filter = _filter_combo("Filter Data Definitions by state")
        self.inventory_state_label = QLabel()
        self.inventory_state_label.setAccessibleName("Data Definition inventory state")
        self.inventory_table = definition_table("Data Definition Inventory")
        self.inventory_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.detail_state_label = QLabel()
        self.detail_state_label.setWordWrap(True)
        self.detail_state_label.setAccessibleName("Selected Data Definition state")
        self.detail_table = definition_table("Selected Data Definition Detail")
        self.impact_view = DataDefinitionImpactView(self)
        self.handoff_panel = DataDefinitionHandoffPanel(on_open_data_mapping)
        self.diagnostics = DataDefinitionDiagnostics(self._edit_draft_cell, self)
        self._publish_diagnostic_table_aliases()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self._build_command_bar())
        layout.addWidget(self._build_filter_bar())
        self.content_scroll = QScrollArea(self)
        self.content_scroll.setAccessibleName("Data Definition workspace viewport")
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setFrameShape(QScrollArea.NoFrame)
        self.content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget(self.content_scroll)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(style.spacing("space.sm"))
        content_layout.addWidget(self._build_workspace(), 1)
        content_layout.addWidget(self.impact_view)
        content_layout.addWidget(self.handoff_panel)
        content_layout.addWidget(self.diagnostics)
        self.content_scroll.setWidget(content)
        layout.addWidget(self.content_scroll, 1)
        self._behavior = DataDefinitionWorkspaceBehavior(self)
        self._connect_filters()
        self.refresh()

    def refresh(self) -> None:
        """Reload report and draft through the existing controller owner."""
        focus = self._behavior.workspace_focus()
        self._apply_state(self._controller.refresh())
        self._behavior.restore_workspace_focus(focus)

    def _build_command_bar(self) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("Panel")
        panel.setStyleSheet(style.panel_stylesheet())
        layout = QGridLayout(panel)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        self._command_layout = layout
        self.refresh_button = _button("Refresh", "Refresh Data Definition", self.refresh)
        self.reset_button = _button(
            "Reset Draft", "Reset Data Definition Draft", self._reset_draft
        )
        layout.addWidget(self.refresh_button, 0, 0)
        layout.addWidget(self.reset_button, 0, 1)
        self.add_definition_button = _button(
            "Add Definition", "Add Data Definition", self._add_definition
        )
        self.add_mapping_attribute_button = _button(
            "Add Mapping Attribute",
            "Add Data Definition Mapping Attribute",
            self._add_mapping_attribute,
        )
        self.edit_button = _button("Edit", "Edit Selected Data Definition", self._edit_definition)
        layout.addWidget(self.add_definition_button, 0, 2)
        layout.addWidget(self.add_mapping_attribute_button, 0, 3)
        layout.addWidget(self.edit_button, 0, 4)
        self.save_button = _button(
            "Save schema", "Save Data Definition Schema", self._save_schema
        )
        self.save_button.setObjectName("PrimaryButton")
        layout.addWidget(self.save_button, 0, 5)
        self.review_blockers_button = _button(
            "Review blockers",
            "Review Data Definition compatibility blockers",
            lambda: self._behavior.focus_blockers(),
        )
        layout.addWidget(self.review_blockers_button, 0, 6)
        layout.addWidget(self.status_label, 0, 7)
        layout.setColumnStretch(7, 1)
        return panel

    def _build_filter_bar(self) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("Panel")
        panel.setStyleSheet(style.panel_stylesheet())
        layout = QGridLayout(panel)
        self._filter_layout = layout
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self.search_input, 0, 0)
        layout.addWidget(self.category_filter, 0, 1)
        layout.addWidget(self.source_filter, 0, 2)
        layout.addWidget(self.state_filter, 0, 3)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        return panel

    def _build_workspace(self) -> QSplitter:
        splitter = QSplitter(self)
        self.workspace_splitter = splitter
        splitter.setAccessibleName("Definition inventory and focused detail")
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(
            self._panel("Definition Inventory", self.inventory_state_label, self.inventory_table)
        )
        splitter.addWidget(
            self._panel("Focused Detail", self.detail_state_label, self.detail_table)
        )
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes((INVENTORY_INITIAL_WIDTH, DETAIL_INITIAL_WIDTH))
        return splitter

    def _panel(self, title: str, state_label: QLabel, table: QTableView) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("Panel")
        panel.setAccessibleName(f"Data Definition {title}")
        panel.setStyleSheet(style.panel_stylesheet())
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
        )
        layout.setSpacing(style.spacing("space.xs"))
        heading = QLabel(title)
        heading.setObjectName("PanelTitle")
        heading.setFont(style.qfont("font.panel_title"))
        layout.addWidget(heading)
        layout.addWidget(state_label)
        layout.addWidget(table, 1)
        return panel

    def _connect_filters(self) -> None:
        self.search_input.textChanged.connect(self._apply_inventory)
        self.search_input.returnPressed.connect(self._behavior.focus_inventory)
        self.category_filter.currentIndexChanged.connect(self._apply_inventory)
        self.source_filter.currentIndexChanged.connect(self._apply_inventory)
        self.state_filter.currentIndexChanged.connect(self._apply_inventory)

    def _apply_state(self, state: DataDefinitionControllerState) -> None:
        self._state = state
        if state.focus_identity is not None:
            self._selected_identity = state.focus_identity
            self._preferred_identity = state.focus_identity
        elif (
            self._preferred_identity is not None
            and self._preferred_identity not in state.draft_row_identities
        ):
            self._preferred_identity = None
        self.diagnostics.apply_state(state)
        self.handoff_panel.apply_state(state)
        self._apply_inventory()

    def _apply_inventory(self) -> None:
        if self._state is None:
            return
        if (
            self._selected_identity is not None
            and self._selected_identity != self._last_projected_identity
        ):
            self._preferred_identity = self._selected_identity
        projection = project_data_definition_inventory(
            self._state,
            search=self.search_input.text(),
            category=str(self.category_filter.currentData() or ""),
            source_type=str(self.source_filter.currentData() or ""),
            lifecycle_state=str(self.state_filter.currentData() or ""),
            selected_identity=self._preferred_identity,
        )
        self._set_filter_options(projection)
        self._selected_identity = projection.selected_identity
        self._last_projected_identity = projection.selected_identity
        interaction = project_data_definition_interaction(self._state, projection)
        self.status_label.setText(interaction.status_text)
        self.status_label.setAccessibleDescription(self.status_label.text())
        self.inventory_state_label.setText(projection.view_message)
        model = DataDefinitionInventoryTableModel(projection.rows)
        self.inventory_table.setModel(model)
        self.inventory_table.resizeColumnsToContents()
        row_index = (
            model.row_for_identity(projection.selected_identity)
            if projection.selected_identity is not None
            else None
        )
        if row_index is not None:
            self.inventory_table.selectRow(row_index)
            self.inventory_table.setCurrentIndex(model.index(row_index, 0))
        else:
            self.inventory_table.clearSelection()
            self.inventory_table.setCurrentIndex(QModelIndex())
        self.inventory_table.selectionModel().currentRowChanged.connect(
            self._inventory_selection_changed
        )
        self._apply_detail(projection.detail)
        self.impact_view.apply_projection(
            project_data_definition_impact(self._state, projection.selected_identity)
        )
        _apply_action_state(self.save_button, interaction.save)
        _apply_action_state(self.edit_button, interaction.edit)
        _apply_action_state(self.review_blockers_button, interaction.review_blockers)
        self.inventory_table.setAccessibleDescription(projection.view_message)

    def _set_filter_options(self, projection: DataDefinitionInventoryProjection) -> None:
        _replace_options(
            self.category_filter,
            "All categories",
            projection.categories,
            projection.resolved_category,
        )
        _replace_options(
            self.source_filter,
            "All value sources",
            projection.source_types,
            projection.resolved_source_type,
        )
        _replace_options(
            self.state_filter,
            "All states",
            projection.lifecycle_states,
            projection.resolved_lifecycle_state,
        )

    def _inventory_selection_changed(
        self,
        current: QModelIndex,
        _previous: QModelIndex,
    ) -> None:
        model = self.inventory_table.model()
        if not isinstance(model, DataDefinitionInventoryTableModel):
            return
        identity = model.identity_at(current.row())
        if identity is None or self._state is None:
            return
        self._selected_identity = identity
        self._preferred_identity = identity
        self._last_projected_identity = identity
        projection = project_data_definition_inventory(
            self._state,
            search=self.search_input.text(),
            category=str(self.category_filter.currentData() or ""),
            source_type=str(self.source_filter.currentData() or ""),
            lifecycle_state=str(self.state_filter.currentData() or ""),
            selected_identity=identity,
        )
        self._apply_detail(projection.detail)
        self.impact_view.apply_projection(
            project_data_definition_impact(self._state, identity)
        )
        interaction = project_data_definition_interaction(self._state, projection)
        _apply_action_state(self.edit_button, interaction.edit)
        _apply_action_state(self.review_blockers_button, interaction.review_blockers)

    def _apply_detail(self, detail: DataDefinitionDetailState) -> None:
        self.detail_state_label.setText(
            f"{detail.title} — {detail.message}" if detail.message else detail.title
        )
        self.detail_table.setModel(ReadOnlyMappingTableModel(DETAIL_HEADERS, detail.rows))
        self.detail_table.resizeColumnsToContents()

    def _reset_draft(self) -> None:
        focus = self._behavior.workspace_focus()
        self._apply_state(self._controller.reset_draft())
        self._behavior.restore_workspace_focus(focus)

    def _add_definition(self) -> None:
        accepted = DataDefinitionAddDialog(self._apply_add_intent, parent=self).exec()
        self._behavior.restore_dialog_focus(bool(accepted), self.add_definition_button)

    def _add_mapping_attribute(self) -> None:
        accepted = DataDefinitionAddDialog(
            self._apply_add_intent,
            standalone_mapping_attribute=True,
            parent=self,
        ).exec()
        self._behavior.restore_dialog_focus(
            bool(accepted), self.add_mapping_attribute_button
        )

    def _edit_definition(self) -> None:
        values = self._selected_values()
        if values is None or self._selected_identity is None:
            return
        accepted = DataDefinitionEditDialog(
            self._selected_identity, values, self._apply_edit_intent, self,
        ).exec()
        self._behavior.restore_dialog_focus(bool(accepted), self.edit_button)

    def _apply_add_intent(self, intent: AddDefinitionIntent) -> tuple[bool, str]:
        state = self._controller.add_definition(intent)
        self._apply_state(state)
        return state.last_action_ok, state.message

    def _apply_edit_intent(self, intent: EditDefinitionIntent) -> tuple[bool, str]:
        state = self._controller.edit_definition(intent)
        self._apply_state(state)
        return state.last_action_ok, state.message

    def _selected_values(self) -> dict[str, str] | None:
        if self._state is None or self._selected_identity is None:
            return None
        try:
            index = self._state.draft_row_identities.index(self._selected_identity)
        except ValueError:
            return None
        return {cell.field_name: cell.value for cell in self._state.draft_rows[index]}

    def _save_schema(self) -> None:
        if not self.save_button.isEnabled():
            return
        self._apply_state(self._controller.save_schema())
        if self.review_blockers_button.isEnabled():
            self._behavior.restore_workspace_focus("blockers")
        else:
            self._behavior.restore_workspace_focus("inventory")

    def _edit_draft_cell(
        self,
        row_identity: tuple[str, str],
        field_name: str,
        value: object,
    ) -> bool:
        state = self._controller.edit_cell(row_identity, field_name, value)
        self._apply_state(state)
        return state.last_action_ok

    def _publish_diagnostic_table_aliases(self) -> None:
        for name in (
            "summary_table", "draft_table", "draft_changes_table", "save_plan_table",
            "save_blockers_table", "save_result_table", "projected_features_table",
            "mapping_requirements_table", "one_hot_table", "readiness_table", "issues_table",
        ):
            setattr(self, name, getattr(self.diagnostics, name))

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        self._behavior.show_default_focus()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._behavior.apply_width(event.size().width())


def _filter_combo(accessible_name: str) -> QComboBox:
    combo = QComboBox()
    combo.setAccessibleName(accessible_name)
    return combo


def _button(
    text: str,
    accessible_name: str,
    callback: Callable[[], None],
) -> QPushButton:
    button = QPushButton(text)
    button.setAccessibleName(accessible_name)
    button.clicked.connect(callback)
    return button


def _apply_action_state(button: QPushButton, presentation) -> None:  # noqa: ANN001
    button.setEnabled(presentation.enabled)
    button.setToolTip(presentation.reason)
    button.setAccessibleDescription(presentation.reason)


def _replace_options(
    combo: QComboBox,
    all_label: str,
    options: tuple[str, ...],
    selected: str,
) -> None:
    with QSignalBlocker(combo):
        combo.clear()
        combo.addItem(all_label, "")
        for option in options:
            combo.addItem(option, option)
        index = combo.findData(selected)
        combo.setCurrentIndex(index if index >= 0 else 0)


def _tables(panel: DataDefinitionPanel) -> tuple[QTableView, ...]:
    return panel.diagnostics.read_only_tables()
