"""Keyboard, focus, and responsive behavior for the Definition workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QPushButton

if TYPE_CHECKING:
    from apps.train.ui.data_definition_panel import DataDefinitionPanel


COMPACT_LAYOUT_WIDTH = 960


class DataDefinitionWorkspaceBehavior:
    """Own view-only interaction policy outside the panel composition owner."""

    def __init__(self, panel: DataDefinitionPanel) -> None:
        self.panel = panel
        self._compact_layout: bool | None = None
        self._tab_order_configured = False
        self._install_shortcuts()
        self.apply_width(panel.width())

    def workspace_focus(self) -> str:
        focused = self.panel.window().focusWidget()
        if focused is self.panel.search_input:
            return "search"
        return "inventory"

    def restore_workspace_focus(self, target: str) -> None:
        def restore() -> None:
            modal = QApplication.activeModalWidget()
            if modal is not None and modal is not self.panel:
                return
            window = self.panel.window()
            if window.isVisible():
                window.activateWindow()
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
            QTimer.singleShot(1, lambda: self.restore_workspace_focus("inventory"))
        else:
            QTimer.singleShot(1, lambda: action.setFocus(Qt.OtherFocusReason))

    def show_default_focus(self) -> None:
        if not self._tab_order_configured:
            self._configure_tab_order()
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
        window = self.panel.window()
        if window.isVisible():
            window.activateWindow()
        self.panel.impact_view.focus_save_decision()

    def _clear_search_or_focus_inventory(self) -> None:
        if self.panel.search_input.text():
            self.panel.search_input.clear()
            self.panel.search_input.setFocus(Qt.ShortcutFocusReason)
        else:
            self.focus_inventory()

    def _open_selected_definition(self) -> None:
        if self.panel.edit_button.isEnabled():
            self.panel._edit_definition()
        elif self.panel.details_action.isEnabled():
            self.panel._show_details()

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
        panel.inventory_table.doubleClicked.connect(
            lambda _index: self._open_selected_definition()
        )
        for name, key in (
            ("inventory_return_shortcut", Qt.Key_Return),
            ("inventory_enter_shortcut", Qt.Key_Enter),
        ):
            shortcut = QShortcut(QKeySequence(key), panel.inventory_table)
            shortcut.setContext(Qt.WidgetShortcut)
            shortcut.activated.connect(self._open_selected_definition)
            setattr(panel, name, shortcut)

    def _configure_tab_order(self) -> None:
        if self._tab_order_configured:
            return
        panel = self.panel
        order = (
            panel.add_definition_button,
            panel.edit_button,
            panel.impact_preview_button,
            panel.review_blockers_button,
            panel.save_button,
            panel.more_button,
            panel.search_input,
            panel.category_filter,
            panel.source_filter,
            panel.state_filter,
            panel.inventory_table,
            panel.handoff_panel.selector,
            panel.handoff_panel.open_button,
            panel.diagnostics.toggle_button,
        )
        for current, following in zip(order, order[1:]):
            panel.setTabOrder(current, following)
        self._tab_order_configured = True

    def _apply_responsive_layout(self, compact: bool) -> None:
        panel = self.panel
        panel.task_header.apply_compact(compact)
        panel.filter_bar.apply_compact(compact)
        panel.inventory_view.apply_compact(compact)
