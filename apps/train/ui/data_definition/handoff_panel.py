"""Post-save Mapping Requirement handoff surface."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from apps.common.ui import style
from apps.train.application.data_mapping import (
    DataMappingNavigationRequest,
    DataMappingNavigationResult,
)
from apps.train.controllers.data_definition_state_builder import DataDefinitionControllerState


class DataDefinitionHandoffPanel(QFrame):
    """Show latest successful saved-schema handoff evidence and action."""

    def __init__(
        self,
        on_open: Callable[[DataMappingNavigationRequest], DataMappingNavigationResult] | None,
    ) -> None:
        super().__init__()
        self.setObjectName("Panel")
        self.setAccessibleName("Saved Mapping Requirement handoff")
        self.setStyleSheet(style.panel_stylesheet())
        self._on_open = on_open
        self._requests: tuple[DataMappingNavigationRequest, ...] = ()
        self.selector = QComboBox(self)
        self.selector.setAccessibleName("Saved Mapping Requirement")
        self.selector.currentIndexChanged.connect(self._sync_detail)
        self.detail = QLabel(self)
        self.detail.setWordWrap(True)
        self.detail.setAccessibleName("Saved Mapping Requirement details")
        self.open_button = QPushButton("Open Data Mapping", self)
        self.open_button.setAccessibleName("Open Data Mapping")
        self.open_button.clicked.connect(self._open)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        heading = QHBoxLayout()
        title = QLabel("Next step: Data Mapping", self)
        title.setObjectName("PanelTitle")
        title.setFont(style.qfont("font.panel_title"))
        heading.addWidget(title)
        heading.addWidget(self.selector, 1)
        heading.addWidget(self.open_button)
        layout.addLayout(heading)
        layout.addWidget(self.detail)

    def apply_state(self, state: DataDefinitionControllerState) -> None:
        """Render only latest successful save evidence, never draft metadata."""
        self._requests = state.saved_mapping_handoffs
        with QSignalBlocker(self.selector):
            self.selector.clear()
            for request in self._requests:
                self.selector.addItem(
                    f"{request.definition_label} ({request.definition_column_key})",
                    request.definition_column_key,
                )
        has_multiple_requests = len(self._requests) >= 2
        self.selector.setVisible(has_multiple_requests)
        self.selector.setEnabled(has_multiple_requests)
        self.selector.setToolTip("")
        self.selector.setAccessibleDescription("")
        self.open_button.setEnabled(bool(self._requests and self._on_open is not None))
        if self._requests:
            if has_multiple_requests:
                self.selector.setToolTip("Choose a saved Mapping Requirement.")
                self.selector.setAccessibleDescription(
                    "Choose a Mapping Requirement from the latest successful schema save."
                )
            self.open_button.setToolTip("Open the exact requirement in Data Mapping.")
            self.open_button.setAccessibleDescription(
                "Open the selected saved Mapping Requirement in Data Mapping."
            )
            self.selector.setCurrentIndex(0)
            self._sync_detail()
        elif state.draft_changed and state.mapping_requirement_rows:
            reason = (
                "Save schema first. Unsaved Mapping Requirement metadata is not active in Data Mapping."
            )
            self.detail.setText(reason)
            self._set_disabled_reason(reason)
        else:
            reason = "No Mapping Requirement handoff from the latest successful save."
            self.detail.setText(reason)
            self._set_disabled_reason(reason)

    def _sync_detail(self) -> None:
        request = self._selected_request()
        if request is None:
            return
        intent = "Required" if request.required else "Optional"
        group_label = request.resolved_group_key.replace("_", " ").title()
        next_step = (
            f"Mapping values are required for {request.definition_label}."
            if request.required
            else f"Mapping values can be supplied for {request.definition_label}."
        )
        self.detail.setText(
            f"{next_step} {request.definition_label} [{request.definition_column_key}] — Saved · "
            f"Data Mapping group: {group_label} ({request.resolved_group_key}) · "
            f"{request.mapping_attribute} · {intent} · {request.data_type}. "
            "Concrete values are managed in Data Mapping. Predict restart required."
        )

    def _open(self) -> None:
        request = self._selected_request()
        if request is None or self._on_open is None:
            return
        result = self._on_open(request)
        self.detail.setText(result.message)

    def _selected_request(self) -> DataMappingNavigationRequest | None:
        if len(self._requests) == 1:
            return self._requests[0]
        if len(self._requests) < 2:
            return None
        index = self.selector.currentIndex()
        if not 0 <= index < len(self._requests):
            return None
        return self._requests[index]

    def _set_disabled_reason(self, reason: str) -> None:
        self.selector.setToolTip(reason)
        self.selector.setAccessibleDescription(reason)
        self.open_button.setToolTip(reason)
        self.open_button.setAccessibleDescription(reason)
