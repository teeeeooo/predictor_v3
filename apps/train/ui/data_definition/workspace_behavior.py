"""Keyboard, focus, and responsive behavior for the Definition workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QPushButton

if TYPE_CHECKING:
    from apps.train.ui.data_definition_panel import DataDefinitionPanel


COMPACT_LAYOUT_WIDTH = 960


class DataDefinitionWorkspaceBehavior:
    """Own view-only interaction policy outside the panel composition owner."""

    def __init__(self, panel: DataDefinitionPanel) -> None:
        self.panel = panel
        self._compact_layout: bool | None = None
        self._install_shortcuts()
        self._configure_tab_order()
        self.apply_width(panel.width())

    def workspace_focus(self) -> str:
        focused = self.panel.window().focusWidget()
        if focused is self.panel.search_input:
            return "search"
        return "inventory"

    def restore_workspace_focus(self, target: str) -> None:
        def restore() -> None:
            if target == "search":
                self.panel.search_input.setFocus(Qt.OtherFocusReason)
            elif target == "blockers" and self.panel.review_blockers_button.isEnabled():
                self.focus_blockers()
            elif self.panel.inventory_table.currentIndex().isValid():
                self.panel.inventory_table.setFocus(Qt.OtherFocusReason)
            else:
                self.panel.search_input.setFocus(Qt.OtherFocusReason)

        QTimer.singleShot(0, restore)

    def restore_dialog_focus(self, accepted: bool, action: QPushButton) -> None:
        if accepted and self.panel.inventory_table.currentIndex().isValid():
            self.restore_workspace_focus("inventory")
        else:
            QTimer.singleShot(0, lambda: action.setFocus(Qt.OtherFocusReason))

    def show_default_focus(self) -> None:
        focused = self.panel.window().focusWidget()
        if focused is None or not self.panel.isAncestorOf(focused):
            self.restore_workspace_focus("search")

    def apply_width(self, width: int) -> None:
        compact = width < COMPACT_LAYOUT_WIDTH
        if compact == self._compact_layout:
            return
        self._compact_layout = compact
        self._apply_responsive_layout(compact)

    def focus_search(self) -> None:
        self.panel.search_input.setFocus(Qt.ShortcutFocusReason)
        self.panel.search_input.selectAll()

    def focus_inventory(self) -> None:
        if self.panel.inventory_table.currentIndex().isValid():
            self.panel.inventory_table.setFocus(Qt.TabFocusReason)

    def focus_blockers(self) -> None:
        self.panel.impact_view.focus_save_decision()

    def _clear_search_or_focus_inventory(self) -> None:
        if self.panel.search_input.text():
            self.panel.search_input.clear()
            self.panel.search_input.setFocus(Qt.ShortcutFocusReason)
        else:
            self.focus_inventory()

    def _edit_if_enabled(self) -> None:
        if self.panel.edit_button.isEnabled():
            self.panel._edit_definition()

    def _install_shortcuts(self) -> None:
        panel = self.panel
        panel.find_shortcut = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Find),
            panel,
        )
        panel.find_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        panel.find_shortcut.activated.connect(self.focus_search)
        panel.save_shortcut = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Save),
            panel,
        )
        panel.save_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        panel.save_shortcut.activated.connect(panel._save_schema)
        panel.clear_search_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), panel)
        panel.clear_search_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        panel.clear_search_shortcut.activated.connect(self._clear_search_or_focus_inventory)
        panel.inventory_table.activated.connect(lambda _index: self._edit_if_enabled())

    def _configure_tab_order(self) -> None:
        panel = self.panel
        order = (
            panel.refresh_button,
            panel.reset_button,
            panel.add_definition_button,
            panel.add_mapping_attribute_button,
            panel.edit_button,
            panel.save_button,
            panel.review_blockers_button,
            panel.search_input,
            panel.category_filter,
            panel.source_filter,
            panel.state_filter,
            panel.inventory_table,
            panel.detail_table,
            panel.handoff_panel.selector,
            panel.handoff_panel.open_button,
            panel.diagnostics.toggle_button,
        )
        for current, following in zip(order, order[1:]):
            panel.setTabOrder(current, following)

    def _apply_responsive_layout(self, compact: bool) -> None:
        panel = self.panel
        buttons = (
            panel.refresh_button,
            panel.reset_button,
            panel.add_definition_button,
            panel.add_mapping_attribute_button,
            panel.edit_button,
            panel.save_button,
            panel.review_blockers_button,
        )
        if compact:
            positions = ((1, 0), (1, 1), (0, 0), (0, 1), (0, 2), (0, 3), (1, 2))
            for button, (row, column) in zip(buttons, positions, strict=True):
                panel._command_layout.addWidget(button, row, column)
            panel._command_layout.addWidget(panel.status_label, 2, 0, 1, 4)
            panel._filter_layout.addWidget(panel.search_input, 0, 0, 1, 3)
            panel._filter_layout.addWidget(panel.category_filter, 1, 0)
            panel._filter_layout.addWidget(panel.source_filter, 1, 1)
            panel._filter_layout.addWidget(panel.state_filter, 1, 2)
            return
        for column, button in enumerate(buttons):
            panel._command_layout.addWidget(button, 0, column)
        panel._command_layout.addWidget(panel.status_label, 0, 7)
        panel._filter_layout.addWidget(panel.search_input, 0, 0)
        panel._filter_layout.addWidget(panel.category_filter, 0, 1)
        panel._filter_layout.addWidget(panel.source_filter, 0, 2)
        panel._filter_layout.addWidget(panel.state_filter, 0, 3)
