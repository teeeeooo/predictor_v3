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
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH
from core.data_definition import RenameDefinitionIntent


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _controller() -> DataDefinitionController:
    return DataDefinitionController(
        DataDefinitionService(schema_path=DEFAULT_SCHEMA_PATH)
    )


def _panel() -> DataDefinitionPanel:
    return DataDefinitionPanel(controller=_controller())


def test_inventory_panel_wires_search_selection_and_advanced_diagnostics():
    app = _app()
    panel = _panel()
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
        assert panel.details_action.isEnabled()
        assert not hasattr(panel, "summary_card")

        panel.search_input.clear()
        app.processEvents()
        panel.inventory_table.selectRow(1)
        app.processEvents()
        selected_identity = panel.inventory_table.model().identity_at(1)
        assert panel._selected_identity == selected_identity
        panel.refresh()
        app.processEvents()
        assert panel._selected_identity == selected_identity

        assert panel.details_action.isEnabled()
        assert [
            action.text()
            for action in panel.task_header.more_menu.actions()
            if not action.isSeparator()
        ] == [
            "Rename Feature", "Duplicate Feature", "Remove Feature", "Disable Feature",
            "Move Up — Predict Order", "Move Down — Predict Order",
            "Move Up — ML Order", "Move Down — ML Order",
            "Details", "Export Training Header Template", "Export Definition Reference",
            "Refresh", "Reset Draft", "Advanced Diagnostics",
        ]

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
            "Predict-only Feature",
            "ML-only Feature",
            "Helper / Hidden Feature",
            "Derived Feature",
            "One-hot Group / Category",
        ]
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_task_workspace_normal_and_compact_geometry_has_no_horizontal_split_or_scroll():
    app = _app()
    panel = _panel()
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
            assert panel.inventory_view.width() >= panel.width() - 48
            assert panel.inventory_view.height() > panel.height() // 2
            assert panel.inventory_table.horizontalScrollBar().maximum() == 0
            assert not header.stretchLastSection()
            visible = {
                column
                for column in range(model.columnCount())
                if not panel.inventory_table.isColumnHidden(column)
            }
            expected_visible = set(range(model.columnCount())) if not compact else {
                0, 1, 2, 3, 4, 7,
            }
            assert visible == expected_visible
            assert all(
                header.sectionResizeMode(column) == QHeaderView.Interactive
                for column in visible
            )
            assert all(
                header.sectionResizeMode(column) != QHeaderView.Stretch
                for column in visible
            )
            assert panel.diagnostics.tabs.isHidden()
            assert panel.impact_view.isHidden()
            assert panel.handoff_panel.isHidden()
            assert panel.add_definition_button.isVisibleTo(panel)
            assert panel.edit_button.isVisibleTo(panel)
            assert panel.save_button.isVisibleTo(panel)
            assert panel.more_button.isVisibleTo(panel)
            assert panel.details_action.isEnabled()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()

def test_inventory_panel_save_enablement_tracks_clean_dirty_blocked_and_reset():
    app = _app()
    panel = _panel()
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

        panel.reset_action.trigger()
        app.processEvents()
        assert not panel.save_button.isEnabled()
        assert panel.status_label.text() == "No unsaved changes"

        ml_name_column = DRAFT_FIELDS.index("ml_name")
        assert not panel.draft_table.model().setData(
            panel.draft_table.model().index(0, ml_name_column),
            "Cooling Capacity Renamed",
            Qt.EditRole,
        )
        panel._apply_state(panel._controller.rename_definition(RenameDefinitionIntent(
            ("schema_row", "cooling_capa"),
            ml_name="Cooling Capacity Renamed",
        )))
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
        assert not panel.details_action.isEnabled()
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
        assert not panel.details_action.isEnabled()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()

    panel = _panel()
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
    panel = _panel()
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
        assert panel._selected_identity == ("schema_row", "cooling_capa")
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
        super().__init__(_FailingService(schema_path=DEFAULT_SCHEMA_PATH))


class _EmptyController:
    def refresh(self):  # noqa: ANN201
        state = _controller().refresh()
        return replace(state, draft_rows=(), draft_row_identities=())
