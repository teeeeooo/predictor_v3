"""Data Mapping toolbar composition and action-state binding."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget

from apps.common.ui import style
from apps.train.controllers.data_mapping_controller import DataMappingControllerState

_ACTION_LABELS = (
    ("add_row", "Add"),
    ("duplicate_row", "Duplicate"),
    ("delete_row", "Delete"),
    ("export_csv_v2", "Export"),
    ("save_mapping_json", "Save"),
    ("refresh_view", "Refresh"),
    ("reload_runtime", "Reload"),
)


class DataMappingToolbar(QFrame):
    """Compact action composition owned outside the panel."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        callbacks: dict[str, Callable[[], None]] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setStyleSheet(style.panel_stylesheet())
        self.buttons: dict[str, QPushButton] = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        for key, label in _ACTION_LABELS:
            button = QPushButton(label)
            button.setAccessibleName(label)
            button.setEnabled(False)
            callback = (callbacks or {}).get(key)
            if callback is not None:
                button.clicked.connect(callback)
            self.buttons[key] = button
            layout.addWidget(button)
        layout.addStretch(1)
        self.buttons["refresh_view"].setToolTip(
            "Refresh validation and rendered state without reading the source file."
        )
        self.buttons["refresh_view"].setAccessibleDescription(
            "Refresh the current in-memory draft without reading the mapping source."
        )
        self.buttons["reload_runtime"].setAccessibleDescription(
            "Read the mapping source again; unsaved changes may be discarded."
        )

    def bind_state(self, state: DataMappingControllerState, *, has_row: bool) -> None:
        """Apply controller action and row-selection availability."""
        actions = {action.key: action for action in state.actions}
        for key, button in self.buttons.items():
            if key == "refresh_view":
                button.setEnabled(True)
                continue
            if key == "add_row":
                button.setEnabled(bool(state.selected_group_key))
                button.setToolTip("")
                continue
            if key in {"duplicate_row", "delete_row"}:
                enabled = bool(state.selected_group_key and has_row)
                button.setEnabled(enabled)
                button.setToolTip("" if enabled else "Select a mapping row first.")
                continue
            action = actions.get(key)
            button.setEnabled(bool(action and action.enabled))
            if action is not None:
                button.setToolTip(action.reason)
