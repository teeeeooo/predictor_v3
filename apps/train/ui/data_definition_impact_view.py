"""Concise default impact surface for Data Definition."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from apps.common.ui import style
from apps.train.controllers.data_definition_impact_projection import (
    DataDefinitionImpactProjection,
)
from apps.train.controllers.data_definition_workspace_projection import (
    DataDefinitionWorkspaceProjection,
)


class DataDefinitionImpactView(QFrame):
    """Render the pure impact projection without policy recomputation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setAccessibleName("Data Definition change and next step")
        self.setStyleSheet(style.panel_stylesheet())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*([style.spacing("space.panel")] * 4))
        layout.setSpacing(style.spacing("space.xs"))
        self.status_label = QLabel("Current state unavailable.")
        self.status_label.setObjectName("PanelTitle")
        self.status_label.setFont(style.qfont("font.panel_title"))
        self.status_label.setAccessibleName("Data Definition current workflow state")
        layout.addWidget(self.status_label)
        self.concise_label = QLabel(self)
        self.concise_label.setAccessibleName("Data Definition current state guidance")
        self.concise_label.setWordWrap(True)
        layout.addWidget(self.concise_label)
        self.details_container = QWidget(self)
        details_layout = QVBoxLayout(self.details_container)
        details_layout.setContentsMargins(0, style.spacing("space.xs"), 0, 0)
        details_layout.setSpacing(style.spacing("space.xs"))
        self.change_label = _section(details_layout, "What will change", "Impact changes")
        self.save_label = _section(details_layout, "Save decision", "Impact save decision")
        self.runtime_label = _section(
            details_layout, "Runtime and compatibility", "Impact runtime"
        )
        self.mapping_label = _section(details_layout, "Mapping impact", "Impact mapping")
        self.result_label = _section(details_layout, "Save result", "Impact save result")
        self.details_container.setVisible(False)
        layout.addWidget(self.details_container)

    def apply_projection(
        self,
        projection: DataDefinitionImpactProjection,
        workspace: DataDefinitionWorkspaceProjection,
    ) -> None:
        self.status_label.setText(workspace.surface_title)
        self.status_label.setStyleSheet(style.status_badge_stylesheet(workspace.status_kind))
        self.concise_label.setText(workspace.surface_message)
        self.concise_label.setAccessibleDescription(workspace.surface_message)
        self.change_label.setText(projection.change_text)
        self.save_label.setText(projection.save_text)
        self.runtime_label.setText(projection.runtime_text)
        self.mapping_label.setText(projection.mapping_text)
        self.result_label.setText(projection.result_text)
        if not workspace.review_enabled:
            self.set_details_visible(False)

    def set_details_visible(self, visible: bool) -> None:
        self.details_container.setVisible(visible)
        self.save_label.setFocusPolicy(Qt.StrongFocus if visible else Qt.NoFocus)

    def focus_save_decision(self) -> None:
        """Expose the current save/blocker summary to keyboard users."""
        self.set_details_visible(True)
        self.save_label.setAccessibleDescription(self.save_label.text())
        self.save_label.setFocus(Qt.OtherFocusReason)


def _section(layout: QVBoxLayout, title: str, accessible_name: str) -> QLabel:
    heading = QLabel(title)
    heading.setFont(style.qfont("font.panel_title"))
    layout.addWidget(heading)
    label = QLabel()
    label.setAccessibleName(accessible_name)
    label.setWordWrap(True)
    layout.addWidget(label)
    return label
