"""Concise default impact surface for Data Definition."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from apps.common.ui import style
from apps.train.controllers.data_definition_impact_projection import (
    DataDefinitionImpactProjection,
)


class DataDefinitionImpactView(QFrame):
    """Render the pure impact projection without policy recomputation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setAccessibleName("Data Definition Impact Preview")
        self.setStyleSheet(style.panel_stylesheet())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*([style.spacing("space.panel")] * 4))
        layout.setSpacing(style.spacing("space.xs"))
        heading = QLabel("Impact Preview")
        heading.setObjectName("PanelTitle")
        heading.setFont(style.qfont("font.panel_title"))
        layout.addWidget(heading)
        self.status_label = QLabel("Impact unavailable.")
        self.status_label.setAccessibleName("Impact status")
        layout.addWidget(self.status_label)
        self.change_label = _section(layout, "What will change", "Impact changes")
        self.save_label = _section(layout, "Save decision", "Impact save decision")
        self.runtime_label = _section(layout, "Runtime and compatibility", "Impact runtime")
        self.mapping_label = _section(layout, "Mapping impact", "Impact mapping")
        self.result_label = _section(layout, "Save result", "Impact save result")

    def apply_projection(self, projection: DataDefinitionImpactProjection) -> None:
        self.status_label.setText(
            f"{projection.status.title()} — schema write {projection.schema_write_status}"
        )
        self.change_label.setText(projection.change_text)
        self.save_label.setText(projection.save_text)
        self.runtime_label.setText(projection.runtime_text)
        self.mapping_label.setText(projection.mapping_text)
        self.result_label.setText(projection.result_text)


def _section(layout: QVBoxLayout, title: str, accessible_name: str) -> QLabel:
    heading = QLabel(title)
    heading.setFont(style.qfont("font.panel_title"))
    layout.addWidget(heading)
    label = QLabel()
    label.setAccessibleName(accessible_name)
    label.setWordWrap(True)
    layout.addWidget(label)
    return label
