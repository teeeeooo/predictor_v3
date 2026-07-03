"""Train Data Mapping UI model foundation tests."""

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.ui.data_mapping_models import ReadOnlyMappingTableModel
from apps.train.ui.data_mapping_panel import DataMappingPanel
from apps.train.ui.data_mapping_view_models import (
    ATTRIBUTE_HEADERS,
    ENTITY_HEADERS,
    VALIDATION_HEADERS,
    action_rows,
    attribute_rows,
    entity_rows,
    validation_rows,
    value_headers,
    value_rows,
)


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_read_only_mapping_table_model_exposes_headers_rows_and_flags():
    state = DataMappingController().refresh()
    model = ReadOnlyMappingTableModel(ENTITY_HEADERS, entity_rows(state))

    assert model.rowCount() == 2
    assert model.columnCount() == len(ENTITY_HEADERS)
    assert model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == "Entity"
    assert model.headerData(0, Qt.Vertical, Qt.DisplayRole) == 1
    assert model.data(model.index(0, 0), Qt.DisplayRole) == "fan_motor"
    assert model.data(model.index(0, 0), Qt.EditRole) == "fan_motor"
    assert model.cell_value(99, 99) == ""
    assert not (model.flags(model.index(0, 0)) & Qt.ItemIsEditable)


def test_attribute_and_value_view_models_are_table_ready():
    state = DataMappingController().refresh("evap_index")
    attribute_model = ReadOnlyMappingTableModel(ATTRIBUTE_HEADERS, attribute_rows(state))
    value_model = ReadOnlyMappingTableModel(value_headers(state), value_rows(state))

    assert attribute_model.cell_value(2, 0) == "Inner Surface Area"
    assert attribute_model.cell_value(2, 4) == "false"
    assert value_model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == "Row Key"
    assert value_model.headerData(2, Qt.Horizontal, Qt.DisplayRole) == "Size"
    assert value_model.cell_value(0, 0) == "S1-2"
    assert value_model.cell_value(0, 3) == "8.2"


def test_validation_and_action_rows_represent_read_only_foundation_state():
    state = DataMappingController().refresh()
    validation_model = ReadOnlyMappingTableModel(
        VALIDATION_HEADERS,
        validation_rows(state),
    )
    action_model = ReadOnlyMappingTableModel(
        ("Action", "Label", "Enabled", "Reason"),
        action_rows(state),
    )

    assert validation_model.cell_value(0, 0) == "info"
    assert validation_model.cell_value(0, 1) == "ok"
    assert action_model.rowCount() == 4
    assert action_model.cell_value(0, 2) == "false"
    assert "future Arc 14B" in action_model.cell_value(0, 3)


def test_data_mapping_panel_builds_read_only_foundation_surface():
    app = _app()
    panel = DataMappingPanel()
    try:
        app.processEvents()

        assert panel.entity_table.model().rowCount() == 2
        assert panel.attribute_table.model().rowCount() > 0
        assert panel.row_table.model().rowCount() > 0
        assert panel.accessibleName() == "Data Mapping Manager"
        assert panel.entity_table.accessibleName() == "Data Mapping Entities"
        assert panel.entity_table.minimumWidth() >= 380
        assert all(not button.isEnabled() for button in panel._buttons.values())
        assert "validation OK" in panel.status_label.text()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()
