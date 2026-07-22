"""Task-oriented Data Definition Train/Admin panel."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QResizeEvent, QShowEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QPushButton,
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
from apps.train.controllers.data_definition_details_projection import (
    project_data_definition_details,
)
from apps.train.controllers.data_definition_presentation import (
    project_data_definition_inventory,
)
from apps.train.controllers.data_definition_impact_projection import (
    project_data_definition_impact,
)
from apps.train.controllers.data_definition_interaction import (
    project_data_definition_interaction,
)
from apps.train.controllers.data_definition_workspace_projection import (
    project_data_definition_workspace,
)
from apps.train.ui.data_definition_diagnostics import (
    DataDefinitionDiagnostics,
    definition_table,
)
from apps.train.ui.data_definition_add_dialog import DataDefinitionAddDialog
from apps.train.ui.data_definition_edit_dialog import DataDefinitionEditDialog
from apps.train.ui.data_definition_details_dialog import DataDefinitionDetailsDialog
from apps.train.ui.data_definition_models import DataDefinitionInventoryTableModel
from apps.train.ui.data_definition_impact_view import DataDefinitionImpactView
from apps.train.ui.data_definition import DataDefinitionHandoffPanel
from apps.train.ui.data_definition.filter_bar import DataDefinitionFilterBar
from apps.train.ui.data_definition.inventory_view import DataDefinitionInventoryView
from apps.train.ui.data_definition.task_header import DataDefinitionTaskHeader
from apps.train.ui.data_definition.workspace_behavior import (
    DataDefinitionWorkspaceBehavior,
)
from apps.train.ui.data_definition.feature_actions import FeatureManagerActions
from apps.train.ui.data_definition.derived_actions import (
    DefinitionManagerActions,
    DerivedManagerActions,
)
from apps.train.ui.data_definition.panel_compat import (
    publish_diagnostic_aliases,
    publish_workspace_aliases,
    read_only_tables as _tables,
    selected_values,
)
from apps.train.ui.data_definition.one_hot import OneHotManagerDialog
from apps.train.ui.data_definition.target_manager_dialog import TargetManagerDialog
from core.data_definition import AddDefinitionIntent, EditDefinitionIntent

class DataDefinitionPanel(QWidget):
    """Task-oriented manager over the existing Data Definition lifecycle."""

    def __init__(
        self,
        parent: QWidget | None = None,
        controller: DataDefinitionController | None = None,
        on_open_data_mapping: (
            Callable[[DataMappingNavigationRequest], DataMappingNavigationResult] | None
        ) = None,
        on_generation_persisted: Callable[[], None] | None = None,
    ) -> None:
        if controller is None:
            raise ValueError("DataDefinitionPanel requires an explicit controller")
        super().__init__(parent)
        self.setObjectName("DataDefinitionPanel")
        self.setAccessibleName("Data Definition")
        self._controller = controller
        self._on_generation_persisted = on_generation_persisted
        self._state: DataDefinitionControllerState | None = None
        self._selected_identity: tuple[str, str] | None = None
        self._preferred_identity: tuple[str, str] | None = None
        self._last_projected_identity: tuple[str, str] | None = None
        self._feature_actions = FeatureManagerActions(
            controller,
            self._selected_feature,
            self._apply_state,
            self,
        )
        self._derived_actions = DerivedManagerActions(
            controller,
            self._selected_feature,
            self._apply_state,
            self,
        )
        self._definition_actions = DefinitionManagerActions(
            self._feature_actions,
            self._derived_actions,
            self._selected_feature,
            self._edit_definition,
        )

        self.filter_bar = DataDefinitionFilterBar(
            self._apply_inventory,
            lambda: self._behavior.focus_inventory(),
            self,
        )
        self.search_input = self.filter_bar.search_input
        self.category_filter = self.filter_bar.category_filter
        self.source_filter = self.filter_bar.source_filter
        self.state_filter = self.filter_bar.state_filter
        self.inventory_table = definition_table("Data Definition Inventory")
        self.inventory_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.inventory_view = DataDefinitionInventoryView(
            self.inventory_table,
            self._clear_filters,
            self,
        )
        self.impact_view = DataDefinitionImpactView(self)
        self.impact_view.setVisible(False)
        self.handoff_panel = DataDefinitionHandoffPanel(on_open_data_mapping)
        self.handoff_panel.setVisible(False)
        self.diagnostics = DataDefinitionDiagnostics(self._edit_draft_cell, self)
        publish_diagnostic_aliases(self)
        self.task_header = DataDefinitionTaskHeader(
            on_add_manual=lambda: self._add_definition("manual_predict"),
            on_add_mapping=lambda: self._add_definition("mapping_predict"),
            on_add_attribute=self._add_mapping_attribute,
            on_add_predict_only=lambda: self._add_definition("predict_only"),
            on_add_ml_only=lambda: self._add_definition("ml_only"),
            on_add_helper=lambda: self._add_definition("helper_hidden"),
            on_add_derived=self._derived_actions.add,
            on_manage_one_hot=self._manage_one_hot,
            on_details=self._show_details,
            on_edit=self._definition_actions.edit,
            on_rename=self._definition_actions.rename,
            on_duplicate=self._definition_actions.duplicate,
            on_remove=self._definition_actions.remove,
            on_toggle_active=self._definition_actions.toggle_active,
            on_move_predict_up=lambda: self._feature_actions.move("predict", "up"),
            on_move_predict_down=lambda: self._feature_actions.move("predict", "down"),
            on_move_ml_up=lambda: self._feature_actions.move("ml", "up"),
            on_move_ml_down=lambda: self._feature_actions.move("ml", "down"),
            on_preview=self._review_current_state,
            on_save=self._save_schema,
            on_review=self._review_current_state,
            on_refresh=self.refresh,
            on_reset=self._reset_draft,
            on_diagnostics=self._toggle_diagnostics,
            parent=self,
        )
        self.diagnostics.toggle_button.toggled.connect(
            self.task_header.set_diagnostics_expanded
        )
        publish_workspace_aliases(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self.task_header)
        self.target_manager_button = QPushButton("Manage Result / Targets", self)
        self.target_manager_button.setAccessibleName("Manage Result and Targets")
        self.target_manager_button.setToolTip(
            "Manage atomic Result Feature and canonical Target registry lifecycle"
        )
        self.target_manager_button.clicked.connect(self._manage_targets)
        layout.addWidget(self.target_manager_button)
        layout.addWidget(self.filter_bar)
        layout.addWidget(self.inventory_view, 1)
        layout.addWidget(self.impact_view)
        layout.addWidget(self.handoff_panel)
        layout.addWidget(self.diagnostics)
        self._behavior = DataDefinitionWorkspaceBehavior(self)
        self.refresh()

    def refresh(self) -> None:
        """Reload report and draft through the existing controller owner."""
        focus = self._behavior.workspace_focus()
        self._apply_state(self._controller.refresh())
        self._behavior.restore_workspace_focus(focus)

    def apply_runtime_state(self, state: DataDefinitionControllerState) -> None:
        """Render one coordinator-committed controller state without reloading."""
        focus = self._behavior.workspace_focus()
        self._apply_state(state)
        self._behavior.restore_workspace_focus(focus)

    def _apply_state(self, state: DataDefinitionControllerState) -> None:
        previous_values = self._selected_values()
        previous_key = previous_values.get("column_key", "") if previous_values else ""
        self._state = state
        if state.focus_identity is not None:
            self._selected_identity = state.focus_identity
            self._preferred_identity = state.focus_identity
        elif (
            self._preferred_identity is not None
            and self._preferred_identity not in state.draft_row_identities
        ):
            self._preferred_identity = next(
                (
                    identity
                    for identity, cells in zip(
                        state.draft_row_identities,
                        state.draft_rows,
                        strict=True,
                    )
                    if previous_key
                    and {cell.field_name: cell.value for cell in cells}.get("column_key")
                    == previous_key
                ),
                None,
            )
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
        search, category, source_type, lifecycle_state = self.filter_bar.current_values()
        projection = project_data_definition_inventory(
            self._state,
            search=search,
            category=category,
            source_type=source_type,
            lifecycle_state=lifecycle_state,
            selected_identity=self._preferred_identity,
        )
        self.filter_bar.apply_projection(projection)
        self._selected_identity = projection.selected_identity
        self._last_projected_identity = projection.selected_identity
        interaction = project_data_definition_interaction(self._state, projection)
        model = DataDefinitionInventoryTableModel(projection.rows)
        self.inventory_table.setModel(model)
        self.inventory_view.refresh_column_policy()
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
        self._apply_workspace_projection(projection, interaction)
        self.inventory_table.setAccessibleDescription(projection.view_message)

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
        search, category, source_type, lifecycle_state = self.filter_bar.current_values()
        projection = project_data_definition_inventory(
            self._state,
            search=search,
            category=category,
            source_type=source_type,
            lifecycle_state=lifecycle_state,
            selected_identity=identity,
        )
        interaction = project_data_definition_interaction(self._state, projection)
        self._apply_workspace_projection(projection, interaction)

    def _apply_workspace_projection(self, projection, interaction) -> None:  # noqa: ANN001
        if self._state is None:
            return
        impact = project_data_definition_impact(
            self._state,
            projection.selected_identity,
        )
        workspace = project_data_definition_workspace(self._state, projection, impact)
        self.inventory_view.apply_state(
            projection.view_message,
            no_match=projection.view_state == "no_match",
        )
        self.impact_view.apply_projection(impact, workspace)
        self.impact_view.setVisible(workspace.show_impact_surface)
        self.task_header.apply_projection(workspace, interaction)
        selected = self._selected_values()
        if selected is not None:
            self.task_header.set_selected_active(
                selected.get("active", "false").casefold() == "true"
            )
            self.task_header.set_selected_kind(selected.get("source_kind", ""))
        self.handoff_panel.setVisible(workspace.show_saved_handoff)

    def _reset_draft(self) -> None:
        focus = self._behavior.workspace_focus()
        self._apply_state(self._controller.reset_draft())
        self._behavior.restore_workspace_focus(focus)

    def _add_definition(
        self,
        initial_intent: str | None = None,
    ) -> None:
        accepted = DataDefinitionAddDialog(
            self._apply_add_intent,
            initial_intent=initial_intent,
            parent=self,
        ).exec()
        self._behavior.restore_dialog_focus(bool(accepted), self.add_definition_button)

    def _add_mapping_attribute(self) -> None:
        accepted = DataDefinitionAddDialog(
            self._apply_add_intent,
            standalone_mapping_attribute=True,
            parent=self,
        ).exec()
        self._behavior.restore_dialog_focus(bool(accepted), self.add_definition_button)

    def _manage_one_hot(self) -> None:
        OneHotManagerDialog(self._controller, self._apply_state, self).exec()
        self._behavior.restore_workspace_focus("inventory")

    def _manage_targets(self) -> None:
        TargetManagerDialog(self._controller, self._apply_state, self).exec()
        self._behavior.restore_workspace_focus("inventory")

    def _review_current_state(self) -> None:
        self._behavior.focus_blockers()

    def _toggle_diagnostics(self) -> None:
        self.diagnostics.toggle_button.setChecked(
            not self.diagnostics.toggle_button.isChecked()
        )

    def _clear_filters(self) -> None:
        self.filter_bar.clear()
        self._apply_inventory()
        self._behavior.restore_workspace_focus("inventory")

    def _edit_definition(self) -> None:
        values = self._selected_values()
        if values is None or self._selected_identity is None:
            return
        accepted = DataDefinitionEditDialog(
            self._selected_identity, values, self._apply_edit_intent, self,
        ).exec()
        self._behavior.restore_dialog_focus(bool(accepted), self.edit_button)


    def _show_details(self) -> None:
        if self._state is None or self._selected_identity is None:
            return
        search, category, source_type, lifecycle_state = self.filter_bar.current_values()
        inventory = project_data_definition_inventory(
            self._state,
            search=search,
            category=category,
            source_type=source_type,
            lifecycle_state=lifecycle_state,
            selected_identity=self._selected_identity,
        )
        if inventory.selected_identity != self._selected_identity:
            return
        details = project_data_definition_details(self._state, inventory)
        if details.identity is None:
            return
        DataDefinitionDetailsDialog(details, self).exec()
        self._behavior.restore_workspace_focus("inventory")

    def _apply_add_intent(self, intent: AddDefinitionIntent) -> tuple[bool, str]:
        state = self._controller.add_definition(intent)
        self._apply_state(state)
        if QApplication.activeModalWidget() is None:
            self._behavior.restore_workspace_focus("inventory")
        return state.last_action_ok, state.message

    def _apply_edit_intent(self, intent: EditDefinitionIntent) -> tuple[bool, str]:
        state = self._controller.edit_definition(intent)
        self._apply_state(state)
        if QApplication.activeModalWidget() is None:
            self._behavior.restore_workspace_focus("inventory")
        return state.last_action_ok, state.message

    def _selected_values(self) -> dict[str, str] | None:
        return selected_values(self._state, self._selected_identity)

    def _selected_feature(self):  # noqa: ANN202
        values = self._selected_values()
        if values is None or self._selected_identity is None:
            return None
        return self._selected_identity, values

    def _save_schema(self) -> None:
        if not self.save_button.isEnabled():
            return
        state = self._controller.save_schema()
        self._apply_state(state)
        if state.status == "saved" and self._on_generation_persisted is not None:
            self._on_generation_persisted()
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

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        self._behavior.show_default_focus()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._behavior.apply_width(event.size().width())
