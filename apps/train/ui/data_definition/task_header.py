"""Current-state and action hierarchy for the Definition workspace."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QMenu, QPushButton, QWidget

from apps.common.ui import style
from apps.train.controllers.data_definition_interaction import (
    DataDefinitionInteractionPresentation,
    DefinitionActionPresentation,
)
from apps.train.controllers.data_definition_workspace_projection import (
    DataDefinitionWorkspaceProjection,
)


class DataDefinitionTaskHeader(QFrame):
    """Render primary, contextual, and secondary actions as distinct groups."""

    def __init__(
        self,
        *,
        on_add_manual: Callable[[], None],
        on_add_mapping: Callable[[], None],
        on_add_attribute: Callable[[], None],
        on_edit: Callable[[], None],
        on_save: Callable[[], None],
        on_review: Callable[[], None],
        on_refresh: Callable[[], None],
        on_reset: Callable[[], None],
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
        self.status_label.setWordWrap(True)
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
        self.add_button.setMenu(self.add_menu)

        self.edit_button = _button(
            "Edit", "Edit Selected Data Definition", on_edit, primary=True
        )
        self.review_button = _button(
            "Review changes", "Review Data Definition changes", on_review
        )
        self.save_button = _button(
            "Save schema", "Save Data Definition Schema", on_save, primary=True
        )
        self.refresh_button = _button(
            "Refresh", "Refresh Data Definition", on_refresh
        )
        self.reset_button = _button(
            "Reset Draft", "Reset Data Definition Draft", on_reset
        )
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
        self.review_button.setVisible(workspace.review_enabled)
        self.refresh_button.setVisible(workspace.show_refresh)
        self.reset_button.setVisible(workspace.show_reset)
        self.reset_button.setEnabled(workspace.show_reset)
        self._arrange()

    def apply_compact(self, compact: bool) -> None:
        if compact == self._compact:
            return
        self._compact = compact
        self._arrange()

    def _arrange(self) -> None:
        widgets = (
            self.status_label,
            self.detail_label,
            self.add_button,
            self.edit_button,
            self.review_button,
            self.save_button,
            self.refresh_button,
            self.reset_button,
        )
        for widget in widgets:
            self.layout_grid.removeWidget(widget)
        for column in range(6):
            self.layout_grid.setColumnStretch(column, 0)
        if self._compact:
            self.layout_grid.addWidget(self.status_label, 0, 0, 1, 4)
            self.layout_grid.addWidget(self.detail_label, 1, 0, 1, 4)
            primary = tuple(
                button
                for button in (
                    self.add_button,
                    self.edit_button,
                    self.review_button,
                    self.save_button,
                )
                if not button.isHidden()
            )
            secondary = tuple(
                button
                for button in (self.refresh_button, self.reset_button)
                if not button.isHidden()
            )
            for column, button in enumerate(primary):
                self.layout_grid.addWidget(button, 2, column)
                self.layout_grid.setColumnStretch(column, 1)
            start = max(0, len(primary) - len(secondary))
            for offset, button in enumerate(secondary):
                self.layout_grid.addWidget(button, 3, start + offset)
        else:
            self.layout_grid.addWidget(self.status_label, 0, 0)
            self.layout_grid.addWidget(self.detail_label, 0, 1)
            self.layout_grid.addWidget(self.add_button, 0, 2)
            self.layout_grid.addWidget(self.edit_button, 0, 3)
            self.layout_grid.addWidget(self.review_button, 0, 4)
            self.layout_grid.addWidget(self.save_button, 0, 5)
            self.layout_grid.addWidget(self.refresh_button, 1, 4)
            self.layout_grid.addWidget(self.reset_button, 1, 5)
            self.layout_grid.setColumnStretch(1, 1)


def _button(
    text: str,
    accessible_name: str,
    callback: Callable[[], None],
    *,
    primary: bool = False,
) -> QPushButton:
    button = QPushButton(text)
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
    button: QPushButton,
    presentation: DefinitionActionPresentation,
) -> None:
    button.setEnabled(presentation.enabled)
    button.setToolTip(presentation.reason)
    button.setAccessibleDescription(presentation.reason)
