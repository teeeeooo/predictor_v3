"""Offscreen UI tests for the Slice 3A Data Definition workspace."""

from __future__ import annotations

from dataclasses import replace
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QAbstractItemView, QPushButton

from apps.train.controllers.data_definition_controller import (
    DRAFT_FIELDS,
    DataDefinitionController,
)
from apps.train.controllers.data_definition_presentation import (
    project_data_definition_inventory,
)
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.data_definition_panel import DataDefinitionPanel


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_inventory_panel_wires_search_selection_and_advanced_diagnostics():
    app = _app()
    panel = DataDefinitionPanel()
    try:
        app.processEvents()
        assert panel.inventory_table.model().rowCount() == len(panel._state.draft_rows)
        assert panel.diagnostics.tabs.isHidden()
        assert panel.diagnostics.tabs.count() == 11
        assert panel.diagnostics.tabs.tabText(0) == "Raw Draft"

        panel.search_input.setText("  cooling_capa ")
        app.processEvents()
        model = panel.inventory_table.model()
        assert model.rowCount() == 1
        assert model.identity_at(0) == ("schema_row", "cooling_capa")
        assert "cooling_capa" in panel.detail_state_label.text()

        panel.search_input.clear()
        app.processEvents()
        panel.inventory_table.selectRow(1)
        app.processEvents()
        selected_identity = panel.inventory_table.model().identity_at(1)
        assert panel._selected_identity == selected_identity
        panel.refresh()
        app.processEvents()
        assert panel._selected_identity == selected_identity

        panel.diagnostics.toggle_button.click()
        app.processEvents()
        assert not panel.diagnostics.tabs.isHidden()
        assert panel.draft_table.editTriggers() != QAbstractItemView.NoEditTriggers
        future_actions = [
            button for button in panel.findChildren(QPushButton)
            if button.accessibleName().startswith("Future Data Definition action:")
        ]
        assert len(future_actions) == 3
        assert all(not button.isEnabled() for button in future_actions)
        assert all("next Phase 3" in button.toolTip() for button in future_actions)
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_inventory_panel_save_enablement_tracks_clean_dirty_blocked_and_reset():
    app = _app()
    panel = DataDefinitionPanel()
    try:
        app.processEvents()
        assert not panel.save_button.isEnabled()
        label_column = DRAFT_FIELDS.index("label")
        assert panel.draft_table.model().setData(
            panel.draft_table.model().index(0, label_column),
            "Cooling Capacity",
            Qt.EditRole,
        )
        app.processEvents()
        assert panel.save_button.isEnabled()
        assert panel.status_label.text().startswith("Unsaved / dirty:")

        _find_button(panel, "Reset Data Definition Draft").click()
        app.processEvents()
        assert not panel.save_button.isEnabled()
        assert panel.status_label.text().startswith("Clean:")

        ml_name_column = DRAFT_FIELDS.index("ml_name")
        assert panel.draft_table.model().setData(
            panel.draft_table.model().index(0, ml_name_column),
            "Cooling Capacity Renamed",
            Qt.EditRole,
        )
        app.processEvents()
        assert not panel.save_button.isEnabled()
        assert panel.status_label.text().startswith("Blocked:")
        selected = project_data_definition_inventory(
            panel._state,
            selected_identity=("schema_row", "cooling_capa"),
        )
        assert selected.rows[0].lifecycle_state == "Blocked"
        assert "compatibility projection writer" in dict(selected.detail.rows)["ML compatibility"]
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_inventory_panel_renders_no_match_and_load_error_messages():
    app = _app()
    panel = DataDefinitionPanel(controller=_FailingController())
    try:
        app.processEvents()
        assert panel.inventory_table.model().rowCount() == 0
        assert "failed" in panel.inventory_state_label.text().lower()
        assert "No definition selected" in panel.detail_state_label.text()
        assert not panel.save_button.isEnabled()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()

    panel = DataDefinitionPanel(controller=_EmptyController())
    try:
        app.processEvents()
        assert panel.inventory_table.model().rowCount() == 0
        assert "No definitions are available" in panel.inventory_state_label.text()
        assert "No definition selected" in panel.detail_state_label.text()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()

    panel = DataDefinitionPanel()
    try:
        panel.search_input.setText("definitely-not-present")
        app.processEvents()
        assert panel.inventory_table.model().rowCount() == 0
        assert "No definitions match" in panel.inventory_state_label.text()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


class _FailingService(DataDefinitionService):
    def refresh_report(self, *, training_data_path=None):  # noqa: ANN001
        raise RuntimeError("fixture load failed")


class _FailingController(DataDefinitionController):
    def __init__(self) -> None:
        super().__init__(_FailingService())


class _EmptyController:
    def refresh(self):  # noqa: ANN201
        state = DataDefinitionController().refresh()
        return replace(state, draft_rows=(), draft_row_identities=())


def _find_button(panel: DataDefinitionPanel, accessible_name: str) -> QPushButton:
    return next(
        button
        for button in panel.findChildren(QPushButton)
        if button.accessibleName() == accessible_name
    )
