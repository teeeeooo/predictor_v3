"""Train Data Mapping UI model foundation tests."""

import os

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QApplication

from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_mapping_service import (
    DataMappingService,
    FoundationMappingCatalogProvider,
    RuntimeMappingCatalogProvider,
)
from apps.train.ui.data_mapping_models import EditableMappingTableModel, ReadOnlyMappingTableModel
from apps.train.ui.data_mapping_panel import DataMappingPanel
from apps.train.ui.data_mapping_view_models import (
    ATTRIBUTE_HEADERS,
    ENTITY_HEADERS,
    VALIDATION_HEADERS,
    attribute_rows,
    entity_rows,
    validation_rows,
    value_headers,
    value_rows,
)


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _foundation_controller() -> DataMappingController:
    return DataMappingController(DataMappingService(FoundationMappingCatalogProvider()))


def test_read_only_mapping_table_model_exposes_headers_rows_and_flags():
    state = _foundation_controller().refresh()
    model = ReadOnlyMappingTableModel(ENTITY_HEADERS, entity_rows(state))

    assert model.rowCount() == 7
    assert model.columnCount() == len(ENTITY_HEADERS)
    assert model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == "Group"
    assert model.headerData(0, Qt.Vertical, Qt.DisplayRole) == 1
    assert model.data(model.index(0, 0), Qt.DisplayRole) == "idu"
    assert model.data(model.index(0, 0), Qt.EditRole) == "idu"
    assert not (model.flags(model.index(0, 0)) & Qt.ItemIsEditable)


def test_read_only_mapping_table_model_guards_invalid_ax_access():
    model = ReadOnlyMappingTableModel(("A", "B"), (("x", "y"),))

    assert model.data(QModelIndex(), Qt.DisplayRole) is None
    assert model.data(model.createIndex(99, 0), Qt.DisplayRole) is None
    assert model.data(model.createIndex(0, 99), Qt.DisplayRole) is None
    assert model.data(model.index(0, 0), Qt.ToolTipRole) is None
    assert model.headerData(-1, Qt.Horizontal, Qt.DisplayRole) is None
    assert model.headerData(99, Qt.Horizontal, Qt.DisplayRole) is None
    assert model.headerData(99, Qt.Vertical, Qt.DisplayRole) is None
    assert model.headerData(0, Qt.Horizontal, Qt.ToolTipRole) is None
    assert model.headerData(0, 999, Qt.DisplayRole) is None
    assert model.flags(QModelIndex()) == Qt.NoItemFlags
    assert model.flags(model.createIndex(99, 0)) == Qt.NoItemFlags
    assert model.cell_value(-1, 0) is None
    assert model.cell_value(0, -1) is None
    assert model.cell_value(99, 99) is None


def test_read_only_mapping_table_model_guards_short_rows():
    model = ReadOnlyMappingTableModel(("A", "B"), (("x",),))

    assert model.columnCount() == 2
    assert model.data(model.createIndex(0, 1), Qt.DisplayRole) is None
    assert model.cell_value(0, 1) is None
    assert model.flags(model.createIndex(0, 1)) == Qt.NoItemFlags


def test_editable_mapping_table_model_updates_cell_through_callback():
    calls = []
    model = EditableMappingTableModel(
        ("IDU", "ID Volume"),
        (("IDU-A", "1.25"),),
        on_cell_changed=lambda row, column, value: calls.append((row, column, value)) or True,
    )

    index = model.index(0, 1)

    assert model.flags(index) & Qt.ItemIsEditable
    assert model.setData(index, "2.5", Qt.EditRole)
    assert calls == [(0, "ID Volume", "2.5")]


def test_attribute_and_value_view_models_are_table_ready():
    state = _foundation_controller().refresh("evap_index")
    attribute_model = ReadOnlyMappingTableModel(ATTRIBUTE_HEADERS, attribute_rows(state))
    value_model = ReadOnlyMappingTableModel(value_headers(state), value_rows(state))

    assert attribute_model.cell_value(2, 0) == "Evap Area"
    assert attribute_model.cell_value(2, 3) == "false"
    assert value_model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == "Evap Index"
    assert value_model.headerData(1, Qt.Horizontal, Qt.DisplayRole) == "Size"
    assert value_model.headerData(2, Qt.Horizontal, Qt.DisplayRole) == "Evap Area"
    assert value_model.cell_value(0, 0) == "EVAP-A"
    assert value_model.cell_value(0, 1) == "S1"
    assert value_model.cell_value(0, 2) == "8.2"


def test_validation_rows_represent_read_only_foundation_state():
    state = _foundation_controller().refresh()
    validation_model = ReadOnlyMappingTableModel(
        VALIDATION_HEADERS,
        validation_rows(state),
    )

    assert validation_model.cell_value(0, 0) == "info"
    assert validation_model.cell_value(0, 4) == "Mapping draft projection OK."


def test_data_mapping_panel_builds_read_only_foundation_surface():
    app = _app()
    panel = DataMappingPanel(controller=_foundation_controller())
    try:
        app.processEvents()

        assert panel.entity_table.model().rowCount() == 7
        assert panel.attribute_table.model().rowCount() > 0
        assert panel.row_table.model().rowCount() > 0
        assert panel.accessibleName() == "Data Mapping Manager"
        assert panel.entity_table.accessibleName() == "Groups"
        assert not hasattr(panel, "actions_table")
        assert panel.entity_table.minimumWidth() >= 380
        assert not panel.entity_table.currentIndex().isValid()
        assert panel._buttons["add_row"].isEnabled()
        assert panel._buttons["duplicate_row"].isEnabled()
        assert panel._buttons["delete_row"].isEnabled()
        assert not panel._buttons["save_mapping_json"].isEnabled()
        assert panel._buttons["reload_runtime"].isEnabled()
        assert not panel._buttons["import_csv_v2"].isEnabled()
        assert [button.text() for button in panel._buttons.values()] == [
            "Add Row",
            "Duplicate",
            "Delete",
            "Import",
            "Export",
            "Save",
            "Reload",
        ]
        assert panel.status_label.text() == "Ready."
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_mapping_panel_programmatic_edit_marks_dirty():
    app = _app()
    panel = DataMappingPanel(controller=_foundation_controller())
    try:
        app.processEvents()
        model = panel.row_table.model()

        assert model.setData(model.index(0, 1), "2.5", Qt.EditRole)

        assert panel.status_label.text() == "Unsaved changes."
        assert not panel.row_table.currentIndex().isValid()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_mapping_panel_shows_runtime_source_on_load_error(tmp_path):
    app = _app()
    missing_mapping = tmp_path / "missing.json"
    controller = DataMappingController(
        DataMappingService(RuntimeMappingCatalogProvider(str(missing_mapping)))
    )
    panel = DataMappingPanel(controller=controller)
    try:
        app.processEvents()

        assert panel.entity_table.model().rowCount() == 0
        assert str(missing_mapping) in panel.source_label.text()
        assert "runtime" not in panel.source_label.text().lower()
        assert "repository" not in panel.source_label.text().lower()
        assert panel.status_label.text() == "Unable to load data."
        assert panel.validation_table.model().cell_value(0, 4) == "Data load failed: runtime mapping data is empty or unavailable: " + str(missing_mapping)
        assert not panel.entity_table.currentIndex().isValid()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()
