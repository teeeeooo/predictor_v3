"""Data Mapping toolbar composition and action-state binding."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QFrame, QHBoxLayout, QMenu, QPushButton, QToolButton, QWidget

from apps.common.ui import style
from apps.train.controllers.data_mapping_controller import DataMappingControllerState

_ACTION_LABELS = (
    ("add_row", "Add"),
    ("duplicate_row", "Duplicate"),
    ("delete_row", "Delete"),
    ("export_csv_v2", "Export"),
    ("import_mapping_bundle", "Import"),
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
        self.buttons: dict[str, QPushButton | QToolButton] = {}
        self._export_menu_actions = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.xs"))
        for key, label in _ACTION_LABELS:
            if key == "export_csv_v2":
                button = self._build_export_button(callbacks or {})
                self.buttons[key] = button
                layout.addWidget(button)
                continue
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

    def _build_export_button(self, callbacks: dict[str, Callable[[], None]]) -> QToolButton:
        button = QToolButton(self)
        button.setText("Export")
        button.setAccessibleName("Export")
        button.setToolTip(
            "Choose a read-only review snapshot or mapping exchange package export."
        )
        button.setEnabled(False)
        button.setPopupMode(QToolButton.InstantPopup)
        menu = QMenu(button)
        exchange_action = menu.addAction("Mapping Exchange Package…")
        review_action = menu.addAction("Review Snapshot…")
        exchange_callback = callbacks.get("export_mapping_exchange")
        review_callback = callbacks.get("export_csv_v2")
        if exchange_callback is not None:
            exchange_action.triggered.connect(exchange_callback)
        if review_callback is not None:
            review_action.triggered.connect(review_callback)
        button.setMenu(menu)
        self._export_menu_actions = {
            "exchange": exchange_action,
            "review": review_action,
        }
        return button

    def bind_state(self, state: DataMappingControllerState, *, has_row: bool) -> None:
        """Apply controller action and row-selection availability."""
        actions = {action.key: action for action in state.actions}
        for key, button in self.buttons.items():
            if key == "export_csv_v2":
                review_action = actions.get("export_csv_v2")
                exchange_action = actions.get("export_mapping_exchange")
                self._export_menu_actions["review"].setEnabled(
                    bool(review_action and review_action.enabled)
                )
                self._export_menu_actions["exchange"].setEnabled(
                    bool(exchange_action and exchange_action.enabled)
                )
                button.setEnabled(bool(review_action and review_action.enabled))
                continue
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
