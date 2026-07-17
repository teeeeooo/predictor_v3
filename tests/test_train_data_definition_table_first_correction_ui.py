"""Focused offscreen checks for the Slice 3F table-first correction."""

from __future__ import annotations

import os

from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLineEdit, QScrollArea

from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.data_definition_details_dialog import DataDefinitionDetailsDialog
from apps.train.ui.data_definition_edit_dialog import DataDefinitionEditDialog
from apps.train.ui.data_definition_panel import DataDefinitionPanel
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _panel() -> DataDefinitionPanel:
    controller = DataDefinitionController(
        DataDefinitionService(schema_path=DEFAULT_SCHEMA_PATH)
    )
    return DataDefinitionPanel(controller=controller)


def _close_active_modal(observed: dict[str, object]) -> None:
    dialog = QApplication.activeModalWidget()
    observed["dialog"] = dialog
    if dialog is not None:
        dialog.reject()


def test_details_is_read_only_snapshot_with_one_outer_scroll_and_focus_restore():
    app = _app()
    panel = _panel()
    panel.resize(900, 640)
    panel.show()
    app.processEvents()
    panel.inventory_table.setFocus()
    before_rows = panel._state.draft_rows
    before_filter = panel.search_input.text()
    before_identity = panel._selected_identity
    observed: dict[str, object] = {}

    def inspect() -> None:
        dialog = QApplication.activeModalWidget()
        observed["dialog"] = dialog
        try:
            assert isinstance(dialog, DataDefinitionDetailsDialog)
            assert dialog.isModal()
            assert dialog.findChildren(QScrollArea) == [dialog.scroll_area]
            assert dialog.scroll_area.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
            assert not dialog.findChildren(QLineEdit)
            assert dialog.key_label.text() == "Internal key: cooling_capa"
            assert dialog.technical_toggle.isVisible()
            assert dialog.technical_table.wordWrap()
            dialog.technical_toggle.click()
            app.processEvents()
            observed["technical_visible"] = dialog.technical_table.isVisible()
            observed["outer_scroll_max"] = dialog.scroll_area.verticalScrollBar().maximum()
            observed["table_scroll_max"] = dialog.technical_table.verticalScrollBar().maximum()
            dialog.close_button.click()
        except Exception as error:  # pragma: no cover - reported below
            observed["error"] = repr(error)
            if dialog is not None:
                dialog.reject()

    QTimer.singleShot(0, inspect)
    panel.details_action.trigger()
    app.processEvents()
    QTest.qWait(10)

    try:
        assert observed.get("error") is None, observed.get("error")
        assert isinstance(observed.get("dialog"), DataDefinitionDetailsDialog)
        assert observed["technical_visible"] is True
        assert int(observed["outer_scroll_max"]) > 0
        assert observed["table_scroll_max"] == 0
        assert panel._state.draft_rows == before_rows
        assert panel.search_input.text() == before_filter
        assert panel._selected_identity == before_identity
        assert panel.inventory_table.hasFocus()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_enter_routes_edit_and_read_only_rows_to_separate_modal_workflows():
    app = _app()
    panel = _panel()
    panel.show()
    app.processEvents()

    def open_with_enter(identity: tuple[str, str]) -> object:
        row = panel.inventory_table.model().row_for_identity(identity)
        assert row is not None
        panel.inventory_table.selectRow(row)
        panel.activateWindow()
        panel.inventory_table.setFocus()
        app.processEvents()
        observed: dict[str, object] = {}
        QTimer.singleShot(0, lambda: _close_active_modal(observed))
        QTest.keyClick(panel.inventory_table, Qt.Key_Return)
        app.processEvents()
        QTest.qWait(5)
        return observed.get("dialog")

    try:
        editable = open_with_enter(("schema_row", "cooling_capa"))
        assert isinstance(editable, DataDefinitionEditDialog)
        readonly_identity = next(
            identity
            for identity in (
                panel.inventory_table.model().identity_at(row)
                for row in range(panel.inventory_table.model().rowCount())
            )
            if identity is not None and identity[0] != "schema_row"
        )
        readonly = open_with_enter(readonly_identity)
        assert isinstance(readonly, DataDefinitionDetailsDialog)
        assert panel._selected_identity == readonly_identity
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_details_escape_is_non_mutating_and_restores_inventory_focus():
    app = _app()
    panel = _panel()
    panel.show()
    app.processEvents()
    before_rows = panel._state.draft_rows
    before_identity = panel._selected_identity
    observed: dict[str, object] = {}

    def inspect() -> None:
        dialog = QApplication.activeModalWidget()
        observed["dialog"] = dialog
        if dialog is not None:
            dialog.close_button.setFocus()
            app.processEvents()
            QTest.keyClick(dialog.close_button, Qt.Key_Escape)

    QTimer.singleShot(0, inspect)
    panel.details_action.trigger()
    app.processEvents()
    QTest.qWait(10)
    try:
        assert isinstance(observed.get("dialog"), DataDefinitionDetailsDialog)
        assert panel._state.draft_rows == before_rows
        assert panel._selected_identity == before_identity
        assert panel.inventory_table.hasFocus()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_double_click_uses_the_same_controlled_open_path_for_selected_row():
    app = _app()
    panel = _panel()
    panel.show()
    app.processEvents()
    panel.inventory_table.setFocus()
    index = panel.inventory_table.model().index(0, 0)
    observed: dict[str, object] = {}
    QTimer.singleShot(0, lambda: _close_active_modal(observed))
    panel.inventory_table.doubleClicked.emit(index)
    app.processEvents()
    QTest.qWait(5)
    try:
        assert isinstance(observed.get("dialog"), DataDefinitionEditDialog)
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()
