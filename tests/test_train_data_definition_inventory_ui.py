"""Offscreen UI tests for the Slice 3A Data Definition workspace."""

from __future__ import annotations

from dataclasses import replace
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QHeaderView,
    QPushButton,
    QSplitter,
)

from apps.train.controllers.data_definition_controller import (
    DRAFT_FIELDS,
    DataDefinitionController,
)
from apps.train.controllers.data_definition_presentation import (
    project_data_definition_inventory,
)
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.data_definition_panel import DataDefinitionPanel
from apps.train.ui.data_definition_models import INVENTORY_HEADERS
import apps.train.ui.data_definition_panel as data_definition_panel_module


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
        assert panel.summary_card.key_label.text() == "cooling_capa"

        panel.search_input.clear()
        app.processEvents()
        panel.inventory_table.selectRow(1)
        app.processEvents()
        selected_identity = panel.inventory_table.model().identity_at(1)
        assert panel._selected_identity == selected_identity
        panel.refresh()
        app.processEvents()
        assert panel._selected_identity == selected_identity

        assert panel.detail_table.isHidden()
        assert panel.detail_table.focusPolicy() == Qt.NoFocus
        panel.summary_card.technical_toggle.click()
        app.processEvents()
        assert not panel.detail_table.isHidden()
        assert panel.detail_table.model().rowCount() >= 20
        assert panel.detail_table.focusPolicy() == Qt.StrongFocus
        panel.summary_card.technical_toggle.click()
        assert panel.detail_table.isHidden()

        panel.diagnostics.toggle_button.click()
        app.processEvents()
        assert not panel.diagnostics.tabs.isHidden()
        assert panel.draft_table.editTriggers() != QAbstractItemView.NoEditTriggers
        controlled_actions = [
            button for button in panel.findChildren(QPushButton)
            if button.accessibleName() in {
                "Add Data Definition",
                "Edit Selected Data Definition",
            }
        ]
        assert len(controlled_actions) == 2
        assert all(button.isEnabled() for button in controlled_actions)
        assert [action.text() for action in panel.task_header.add_menu.actions()] == [
            "Manual Predict input",
            "Mapping-backed Predict input",
            "Data Mapping attribute",
        ]
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_task_workspace_normal_and_compact_geometry_has_no_horizontal_split_or_scroll():
    app = _app()
    panel = DataDefinitionPanel()
    try:
        for size, compact in (((1280, 820), False), ((900, 640), True)):
            panel.resize(*size)
            panel.show()
            app.processEvents()
            header = panel.inventory_table.horizontalHeader()
            model = panel.inventory_table.model()
            assert tuple(
                model.headerData(column, Qt.Horizontal)
                for column in range(model.columnCount())
            ) == INVENTORY_HEADERS
            assert panel.findChildren(QSplitter) == []
            assert panel.inventory_view.width() == panel.summary_card.width()
            assert panel.summary_card.y() > panel.inventory_view.y()
            assert panel.inventory_table.horizontalScrollBar().maximum() == 0
            assert panel.content_scroll.horizontalScrollBar().maximum() == 0
            assert not header.stretchLastSection()
            assert header.sectionResizeMode(0) == QHeaderView.Stretch
            assert header.sectionResizeMode(5) == QHeaderView.Fixed
            assert panel.diagnostics.tabs.isHidden()
            assert panel.impact_view.details_container.isHidden()
            assert panel.detail_table.isHidden()
            assert panel.add_definition_button.isVisibleTo(panel)
            assert panel.save_button.isVisibleTo(panel)
            fact_names = [name for name, _value in panel.summary_card._fact_labels]
            if compact:
                assert all(
                    current.y() < following.y()
                    for current, following in zip(fact_names, fact_names[1:])
                )
            else:
                assert fact_names[0].y() == fact_names[1].y()
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
        idu_row = panel._state.draft_row_identities.index(("schema_row", "idu"))
        assert panel.draft_table.model().setData(
            panel.draft_table.model().index(idu_row, label_column),
            "Indoor Unit",
            Qt.EditRole,
        )
        app.processEvents()
        assert panel.save_button.isEnabled()
        assert panel.status_label.text() == "1 unsaved change"

        _find_button(panel, "Reset Data Definition Draft").click()
        app.processEvents()
        assert not panel.save_button.isEnabled()
        assert panel.status_label.text() == "No unsaved changes"

        ml_name_column = DRAFT_FIELDS.index("ml_name")
        assert panel.draft_table.model().setData(
            panel.draft_table.model().index(0, ml_name_column),
            "Cooling Capacity Renamed",
            Qt.EditRole,
        )
        app.processEvents()
        assert not panel.save_button.isEnabled()
        assert panel.status_label.text() == "Save blocked"
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


def test_inventory_panel_reconciles_removed_filter_option_without_signal_recursion(
    monkeypatch,
):
    app = _app()
    panel = DataDefinitionPanel()
    try:
        app.processEvents()
        label_col = DRAFT_FIELDS.index("label")
        for identity, label in (
            (("schema_row", "fin_type"), "Fin Type"),
            (("schema_row", "pi"), "Pi Type"),
        ):
            row = panel._state.draft_row_identities.index(identity)
            assert panel.draft_table.model().setData(
                panel.draft_table.model().index(row, label_col),
                label,
                Qt.EditRole,
            )
        changed_index = panel.state_filter.findData("Changed")
        assert changed_index >= 0
        panel.state_filter.setCurrentIndex(changed_index)
        app.processEvents()
        assert panel.inventory_table.model().rowCount() == 2
        assert panel._selected_identity == ("schema_row", "fin_type")

        row = panel._state.draft_row_identities.index(("schema_row", "fin_type"))
        assert panel.draft_table.model().setData(
            panel.draft_table.model().index(row, label_col),
            "FIN종류",
            Qt.EditRole,
        )

        project_calls = 0
        real_project = data_definition_panel_module.project_data_definition_inventory

        def counted_project(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            nonlocal project_calls
            project_calls += 1
            return real_project(*args, **kwargs)

        monkeypatch.setattr(
            data_definition_panel_module,
            "project_data_definition_inventory",
            counted_project,
        )
        row = panel._state.draft_row_identities.index(("schema_row", "pi"))
        assert panel.draft_table.model().setData(
            panel.draft_table.model().index(row, label_col),
            "PI",
            Qt.EditRole,
        )
        app.processEvents()

        assert project_calls == 1
        assert panel.state_filter.currentText() == "All states"
        assert panel.state_filter.currentData() == ""
        model = panel.inventory_table.model()
        assert model.rowCount() == len(panel._state.draft_rows)
        assert tuple(model.identity_at(index) for index in range(model.rowCount())) == (
            panel._state.draft_row_identities
        )
        assert "No definitions match" not in panel.inventory_state_label.text()
        assert panel._selected_identity == ("schema_row", "cooling_capa")
        assert panel.summary_card.key_label.text() == "cooling_capa"
        assert not panel._state.draft_changed
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
