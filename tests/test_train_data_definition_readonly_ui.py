"""Train Data Definition read-only UI tests."""

from __future__ import annotations

import inspect
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QAbstractItemView, QPushButton

from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
import apps.train.services.data_definition_service as data_definition_service_module
import apps.train.ui.data_definition_panel as data_definition_panel_module
from apps.train.ui.data_definition_panel import DataDefinitionPanel
from apps.train.ui.data_mapping_panel import DataMappingPanel
from apps.train.ui.shell import TrainShell
from core.data_definition import DataDefinitionReport


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_data_definition_service_returns_report_without_training_filename_default():
    service = DataDefinitionService()

    report = service.load_report()

    assert isinstance(report, DataDefinitionReport)
    assert report.ok
    assert "Practice_4.csv" not in inspect.getsource(data_definition_service_module)
    assert not any("Practice_4.csv" in check.message for check in report.readiness)


def test_data_definition_controller_returns_readonly_view_state():
    state = DataDefinitionController().refresh()

    assert state.status == "ready"
    assert ("Projected features", "28") in state.summary_rows
    assert ("Current catalog features", "28") in state.summary_rows
    assert ("Parity issues", "0") in state.summary_rows
    assert len(state.projected_feature_rows) == 28
    assert len(state.mapping_requirement_rows) == 8
    assert {row[1] for row in state.one_hot_rows} == {"refrigerant", "expansion_device"}
    assert {row[0] for row in state.readiness_rows} >= {
        "training_headers",
        "model_activation",
        "restart_impact",
    }
    assert all(len(row) == 4 for row in state.issue_rows)


def test_data_definition_panel_builds_readonly_tables_and_refreshes():
    app = _app()
    panel = DataDefinitionPanel()
    try:
        app.processEvents()

        assert panel.accessibleName() == "Data Definition"
        assert panel.summary_table.model().rowCount() >= 6
        assert panel.projected_features_table.model().rowCount() == 28
        assert panel.mapping_requirements_table.model().rowCount() == 8
        assert panel.one_hot_table.model().rowCount() == 2
        assert panel.readiness_table.model().rowCount() == 3
        assert panel.issues_table.model().rowCount() >= 1
        for table in data_definition_panel_module._tables(panel):
            assert table.editTriggers() == QAbstractItemView.NoEditTriggers
            assert not (table.model().flags(table.model().index(0, 0)) & Qt.ItemIsEditable)

        refresh_buttons = [
            child for child in panel.findChildren(QPushButton)
            if child.accessibleName() == "Refresh Data Definition"
        ]
        assert len(refresh_buttons) == 1
        refresh_buttons[0].click()
        app.processEvents()
        assert panel.status_label.text() == "No unsaved changes"
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_train_shell_registers_data_definition_tab_and_keeps_existing_tabs():
    app = _app()
    shell = TrainShell()
    try:
        app.processEvents()

        tab_names = [shell.tabs.tabText(index) for index in range(shell.tabs.count())]
        assert tab_names == [
            "Predict",
            "Train / Model",
            "Data Definition",
            "Data Mapping",
        ]
        assert isinstance(shell.tabs.widget(2), DataDefinitionPanel)
        assert isinstance(shell.tabs.widget(3), DataMappingPanel)
    finally:
        shell.close()
        shell.deleteLater()
        app.processEvents()
