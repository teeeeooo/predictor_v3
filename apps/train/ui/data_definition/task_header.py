"""Compact current-state and action hierarchy for the Definition workspace."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSignalBlocker
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QMenu,
    QPushButton,
    QWidget,
)

from apps.common.ui import style
from apps.train.controllers.data_definition_interaction import (
    DataDefinitionInteractionPresentation,
    DefinitionActionPresentation,
)
from apps.train.controllers.data_definition_workspace_projection import (
    DataDefinitionWorkspaceProjection,
)


class DataDefinitionTaskHeader(QFrame):
    """Render feature-management actions with a compact secondary menu."""

    def __init__(
        self,
        *,
        on_add_manual: Callable[[], None],
        on_add_mapping: Callable[[], None],
        on_add_attribute: Callable[[], None],
        on_add_predict_only: Callable[[], None],
        on_add_ml_only: Callable[[], None],
        on_add_helper: Callable[[], None],
        on_add_derived: Callable[[], None],
        on_details: Callable[[], None],
        on_edit: Callable[[], None],
        on_rename: Callable[[], None],
        on_duplicate: Callable[[], None],
        on_remove: Callable[[], None],
        on_toggle_active: Callable[[], None],
        on_move_predict_up: Callable[[], None],
        on_move_predict_down: Callable[[], None],
        on_move_ml_up: Callable[[], None],
        on_move_ml_down: Callable[[], None],
        on_preview: Callable[[], None],
        on_save: Callable[[], None],
        on_review: Callable[[], None],
        on_refresh: Callable[[], None],
        on_reset: Callable[[], None],
        on_diagnostics: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setAccessibleName("Data Definition current state and actions")
        self.setStyleSheet(style.panel_stylesheet())
        self._compact = False
        self.layout_grid = QGridLayout(self)
        self.layout_grid.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        self.layout_grid.setSpacing(style.spacing("space.xs"))

        self.status_label = QLabel("Data Definition pending.", self)
        self.status_label.setAccessibleName("Data Definition application status")
        self.status_label.setFont(style.qfont("font.panel_title"))
        self.status_label.setWordWrap(False)
        self.detail_label = QLabel(self)
        self.detail_label.setAccessibleName("Data Definition current state guidance")
        self.detail_label.setWordWrap(True)

        self.add_button = QPushButton("Add", self)
        self.add_button.setObjectName("PrimaryButton")
        self.add_button.setAccessibleName("Add Data Definition")
        self.add_menu = QMenu(self.add_button)
        self.add_menu.setAccessibleName("Choose Data Definition purpose")
        self.add_manual_action = _menu_action(
            self.add_menu,
            "Manual Predict input",
            "Add a manual Predict input",
            on_add_manual,
        )
        self.add_mapping_action = _menu_action(
            self.add_menu,
            "Mapping-backed Predict input",
            "Add a Predict input supplied by Data Mapping",
            on_add_mapping,
        )
        self.add_attribute_action = _menu_action(
            self.add_menu,
            "Data Mapping attribute",
            "Add a Data Mapping attribute without a visible Predict input",
            on_add_attribute,
        )
        self.add_predict_only_action = _menu_action(
            self.add_menu,
            "Predict-only Feature",
            "Add a Feature displayed in Predict but excluded from ML",
            on_add_predict_only,
        )
        self.add_ml_only_action = _menu_action(
            self.add_menu,
            "ML-only Feature",
            "Add a hidden ordered ML input Feature",
            on_add_ml_only,
        )
        self.add_helper_action = _menu_action(
            self.add_menu,
            "Helper / Hidden Feature",
            "Add a projection-neutral Helper or Hidden Feature",
            on_add_helper,
        )
        self.add_derived_action = _menu_action(
            self.add_menu,
            "Derived Feature",
            "Add an inactive restricted safe_ratio Derived definition",
            on_add_derived,
        )
        self.add_button.setMenu(self.add_menu)

        self.edit_button = _button(
            "Edit", "Edit Selected Data Definition", on_edit, primary=True, parent=self
        )
        self.preview_button = _button(
            "Impact Preview", "Preview selected Feature impact", on_preview, parent=self
        )
        self.review_button = _button(
            "Review changes", "Review Data Definition changes", on_review, parent=self
        )
        self.save_button = _button(
            "Save schema", "Save Data Definition Schema", on_save, primary=True, parent=self
        )

        self.more_button = QPushButton("More", self)
        self.more_button.setAccessibleName("More Data Definition actions")
        self.more_menu = QMenu(self.more_button)
        self.more_menu.setAccessibleName("More Data Definition actions")
        self.rename_action = _menu_action(
            self.more_menu, "Rename Feature", "Rename Predict key or ML name", on_rename,
        )
        self.duplicate_action = _menu_action(
            self.more_menu, "Duplicate Feature", "Duplicate the selected Basic Feature", on_duplicate,
        )
        self.remove_action = _menu_action(
            self.more_menu, "Remove Feature", "Remove the selected Basic Feature", on_remove,
        )
        self.toggle_active_action = _menu_action(
            self.more_menu, "Disable Feature", "Enable or disable the selected Feature", on_toggle_active,
        )
        self.more_menu.addSeparator()
        self.move_predict_up_action = _menu_action(
            self.more_menu, "Move Up — Predict Order", "Move in Predict display order only", on_move_predict_up,
        )
        self.move_predict_down_action = _menu_action(
            self.more_menu, "Move Down — Predict Order", "Move in Predict display order only", on_move_predict_down,
        )
        self.move_ml_up_action = _menu_action(
            self.more_menu, "Move Up — ML Order", "Move in ordered ML contract only", on_move_ml_up,
        )
        self.move_ml_down_action = _menu_action(
            self.more_menu, "Move Down — ML Order", "Move in ordered ML contract only", on_move_ml_down,
        )
        self.more_menu.addSeparator()
        self.details_action = _menu_action(
            self.more_menu,
            "Details",
            "Open read-only Details for the selected Definition",
            on_details,
        )
        self.refresh_action = _menu_action(
            self.more_menu,
            "Refresh",
            "Reload Data Definition state",
            on_refresh,
        )
        self.reset_action = _menu_action(
            self.more_menu,
            "Reset Draft",
            "Discard the current Data Definition draft",
            on_reset,
        )
        self.more_menu.addSeparator()
        self.diagnostics_action = self.more_menu.addAction("Advanced Diagnostics")
        self.diagnostics_action.setObjectName("AdvancedDiagnostics")
        self.diagnostics_action.setCheckable(True)
        self.diagnostics_action.setToolTip("Show or hide Advanced Diagnostics")
        self.diagnostics_action.setStatusTip(self.diagnostics_action.toolTip())
        self.diagnostics_action.triggered.connect(
            lambda _checked=False: on_diagnostics()
        )
        self.more_button.setMenu(self.more_menu)
        self._arrange()

    def apply_projection(
        self,
        workspace: DataDefinitionWorkspaceProjection,
        interaction: DataDefinitionInteractionPresentation,
    ) -> None:
        self.status_label.setText(workspace.headline)
        self.status_label.setStyleSheet(style.status_badge_stylesheet(workspace.status_kind))
        self.status_label.setAccessibleDescription(workspace.headline)
        self.detail_label.setText(workspace.headline_detail)
        self.detail_label.setAccessibleDescription(workspace.headline_detail)
        _apply_action_state(self.save_button, interaction.save)
        _apply_action_state(self.edit_button, interaction.edit)
        _apply_action_state(self.preview_button, interaction.preview)
        for action in (
            self.rename_action,
            self.duplicate_action,
            self.remove_action,
            self.toggle_active_action,
            self.move_predict_up_action,
            self.move_predict_down_action,
            self.move_ml_up_action,
            self.move_ml_down_action,
        ):
            _apply_action_state(action, interaction.manage)
        _apply_action_state(self.details_action, interaction.details)
        self.save_button.setText(workspace.save_label)
        self.review_button.setText(workspace.review_label)
        self.review_button.setAccessibleName(
            "Review Data Definition blocker"
            if workspace.review_label == "Review blocker"
            else "Review Data Definition changes"
        )
        self.review_button.setEnabled(workspace.review_enabled)
        self.review_button.setToolTip(
            "Show the preserved structured impact and blocker evidence."
        )
        self.review_button.setAccessibleDescription(self.review_button.toolTip())

        self.add_button.setVisible(workspace.show_add_edit)
        self.edit_button.setVisible(workspace.show_add_edit)
        self.preview_button.setVisible(workspace.show_add_edit)
        self.save_button.setVisible(True)
        self.review_button.setVisible(workspace.review_enabled)
        self.more_button.setVisible(True)
        self.refresh_action.setEnabled(workspace.show_refresh)
        self.reset_action.setEnabled(workspace.show_reset)
        self.reset_action.setToolTip(
            "Discard the current Data Definition draft."
            if workspace.show_reset
            else "No unsaved Data Definition draft to reset."
        )
        self._arrange()

    def apply_compact(self, compact: bool) -> None:
        if compact == self._compact:
            return
        self._compact = compact
        self._arrange()

    def set_diagnostics_expanded(self, expanded: bool) -> None:
        """Keep the More menu check state aligned with the diagnostics toggle."""
        with QSignalBlocker(self.diagnostics_action):
            self.diagnostics_action.setChecked(expanded)

    def _arrange(self) -> None:
        widgets = (
            self.status_label,
            self.detail_label,
            self.add_button,
            self.edit_button,
            self.preview_button,
            self.review_button,
            self.save_button,
            self.more_button,
        )
        for widget in widgets:
            self.layout_grid.removeWidget(widget)
        for column in range(8):
            self.layout_grid.setColumnStretch(column, 0)

        actions = tuple(
            button
            for button in (
                self.add_button,
                self.edit_button,
                self.preview_button,
                self.review_button,
                self.save_button,
                self.more_button,
            )
            if not button.isHidden()
        )
        if self._compact:
            self.layout_grid.addWidget(self.status_label, 0, 0, 1, 6)
            self.layout_grid.addWidget(self.detail_label, 1, 0, 1, 6)
            for column, button in enumerate(actions):
                self.layout_grid.addWidget(button, 2, column)
            self.layout_grid.setColumnStretch(5, 1)
        else:
            self.layout_grid.addWidget(self.status_label, 0, 0)
            self.layout_grid.addWidget(self.detail_label, 0, 1)
            for column, button in enumerate(actions, start=2):
                self.layout_grid.addWidget(button, 0, column)
            self.layout_grid.setColumnStretch(1, 1)

    def set_selected_active(self, active: bool) -> None:
        """Keep the active-state command label aligned with selection."""
        self.toggle_active_action.setText("Disable Feature" if active else "Enable Feature")
        self.toggle_active_action.setStatusTip(
            "Disable selected Feature" if active else "Enable selected Feature"
        )

    def set_selected_kind(self, source_kind: str) -> None:
        """Adapt labels and remove manual ordering for Derived selection."""
        derived = source_kind == "derived_policy"
        self.rename_action.setText("Rename Derived" if derived else "Rename Feature")
        self.duplicate_action.setText("Duplicate Derived" if derived else "Duplicate Feature")
        self.remove_action.setText("Remove Derived" if derived else "Remove Feature")
        active = self.toggle_active_action.text().startswith("Disable")
        self.toggle_active_action.setText(
            ("Disable" if active else "Enable") + (" Derived" if derived else " Feature")
        )
        for action in (
            self.move_predict_up_action,
            self.move_predict_down_action,
            self.move_ml_up_action,
            self.move_ml_down_action,
        ):
            action.setEnabled(action.isEnabled() and not derived)


def _button(
    text: str,
    accessible_name: str,
    callback: Callable[[], None],
    *,
    primary: bool = False,
    parent: QWidget | None = None,
) -> QPushButton:
    button = QPushButton(text, parent)
    button.setAccessibleName(accessible_name)
    if primary:
        button.setObjectName("PrimaryButton")
    button.clicked.connect(callback)
    return button


def _menu_action(
    menu: QMenu,
    text: str,
    description: str,
    callback: Callable[[], None],
) -> QAction:
    action = menu.addAction(text)
    action.setObjectName(text.replace(" ", ""))
    action.setToolTip(description)
    action.setStatusTip(description)
    action.triggered.connect(lambda _checked=False: callback())
    return action


def _apply_action_state(
    control: QPushButton | QAction,
    presentation: DefinitionActionPresentation,
) -> None:
    control.setEnabled(presentation.enabled)
    control.setToolTip(presentation.reason)
    if isinstance(control, QPushButton):
        control.setAccessibleDescription(presentation.reason)
    else:
        control.setStatusTip(presentation.reason)
