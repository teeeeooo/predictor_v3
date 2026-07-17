"""Read-only command-specific impact preview and confirmation dialog."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from apps.common.ui import style
from core.data_definition import FeatureImpactPreview


class FeatureCommandPreviewDialog(QDialog):
    def __init__(self, preview: FeatureImpactPreview, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"{preview.action} Impact Preview")
        self.setAccessibleName(self.windowTitle())
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*([style.spacing("space.outer")] * 4))
        title = QLabel(self.windowTitle())
        title.setObjectName("PanelTitle")
        title.setFont(style.qfont("font.window_title"))
        layout.addWidget(title)
        summary = QLabel(preview.summary)
        summary.setAccessibleName("Feature command impact summary")
        summary.setWordWrap(True)
        layout.addWidget(summary)
        details = (
            f"Predict projection: {_changed(preview.predict_projection_changed)}\n"
            f"Ordered ML projection: {_changed(preview.ordered_ml_projection_changed)}\n"
            f"Mapping requirements: {_changed(preview.mapping_requirements_changed)}\n"
            f"Model compatibility: {_changed(preview.model_compatibility_changed)}\n"
            f"Retraining required: {'Yes' if preview.requires_retraining else 'No'}\n"
            f"Save possible: {'Yes' if preview.save_allowed else 'No'}"
        )
        evidence = QLabel(details)
        evidence.setAccessibleName("Feature command impact evidence")
        evidence.setWordWrap(True)
        layout.addWidget(evidence)
        blockers = QLabel("\n".join(
            f"• {item.message}" + (f" Next: {item.resolution}" if item.resolution else "")
            for item in preview.blockers
        ) or "No command or Save blockers.")
        blockers.setAccessibleName("Feature command blockers and resolutions")
        blockers.setWordWrap(True)
        layout.addWidget(blockers)
        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = QPushButton("Cancel")
        cancel.setAccessibleName("Cancel Feature command")
        cancel.clicked.connect(self.reject)
        self.apply_button = QPushButton("Apply to Draft")
        self.apply_button.setAccessibleName("Apply previewed command to Draft")
        self.apply_button.setEnabled(preview.command_accepted)
        self.apply_button.setDefault(preview.command_accepted)
        self.apply_button.clicked.connect(self.accept)
        actions.addWidget(cancel)
        actions.addWidget(self.apply_button)
        layout.addLayout(actions)


def _changed(value: bool) -> str:
    return "Changed" if value else "Unchanged"
