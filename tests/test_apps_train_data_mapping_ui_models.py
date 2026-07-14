"""Train Data Mapping UI model foundation tests."""

import os
from pathlib import Path

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QApplication

from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_mapping_service import (
    DataMappingService,
    FoundationMappingCatalogProvider,
    RuntimeMappingCatalogProvider,
)
from apps.train.ui.data_mapping_models import EditableMappingTableModel, ReadOnlyMappingTableModel
from apps.train.ui.data_mapping_panel import (
    EXPORT_FILTERS,
    DataMappingPanel,
    _resolve_export_selection,
)
from apps.train.ui.data_mapping_view_models import (
    ATTRIBUTE_HEADERS,
    ENTITY_HEADERS,
    GROUP_HEADERS,
    VALIDATION_HEADERS,
    attribute_rows,
    entity_rows,
    group_rows,
    validation_rows,
    value_headers,
    value_rows,
)
from core.mapping.editor_projection import project_runtime_mapping_to_editor_draft


RUNTIME_FIXTURE = Path("tests/fixtures/mapping/mapping_runtime_equivalent.json")


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
    assert model.data(model.index(0, 0), Qt.ToolTipRole) == "x"
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


def test_group_navigation_rows_only_expose_label_and_row_count():
    state = _foundation_controller().refresh("odu_cond_specs")
    model = ReadOnlyMappingTableModel(GROUP_HEADERS, group_rows(state))

    assert model.columnCount() == 2
    assert model.cell_value(0, 0) == "IDU"
    assert model.cell_value(6, 0) == "ODU Cond Specs"
    assert model.cell_value(6, 1) == "1"


def test_validation_rows_represent_current_draft_state():
    state = _foundation_controller().refresh()
    validation_model = ReadOnlyMappingTableModel(
        VALIDATION_HEADERS,
        validation_rows(state),
    )

    assert validation_model.cell_value(0, 0) == "info"
    assert validation_model.cell_value(0, 4) == "Mapping draft projection OK."


def test_data_mapping_panel_builds_editable_manager_surface():
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
        assert panel.entity_table.parentWidget().minimumWidth() >= 180
        assert panel.entity_table.parentWidget().maximumWidth() <= 300
        assert panel.entity_table.currentIndex().isValid()
        assert panel._buttons["add_row"].isEnabled()
        assert not panel._buttons["duplicate_row"].isEnabled()
        assert not panel._buttons["delete_row"].isEnabled()
        assert panel._buttons["export_csv_v2"].isEnabled()
        assert not panel._buttons["save_mapping_json"].isEnabled()
        assert panel._buttons["reload_runtime"].isEnabled()
        panel.row_table.setCurrentIndex(panel.row_table.model().index(0, 0))
        app.processEvents()
        assert panel._buttons["duplicate_row"].isEnabled()
        assert panel._buttons["delete_row"].isEnabled()
        assert "read-only review snapshot" in panel._buttons["export_csv_v2"].toolTip()
        assert [button.text() for button in panel._buttons.values()] == [
            "Add",
            "Duplicate",
            "Delete",
            "Export",
            "Save",
            "Reload",
        ]
        assert panel.status_label.text() == "Ready."
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_mapping_panel_populated_fixture_navigation_updates_primary_table():
    app = _app()
    controller = DataMappingController(
        DataMappingService(RuntimeMappingCatalogProvider(str(RUNTIME_FIXTURE)))
    )
    panel = DataMappingPanel(controller=controller)
    try:
        panel.resize(1280, 760)
        panel.show()
        app.processEvents()

        group_model = panel.entity_table.model()
        assert [group_model.cell_value(row, 0) for row in range(7)] == [
            "IDU",
            "Evap Index",
            "ODU",
            "Compressor",
            "Refrigerant",
            "Expansion",
            "ODU Cond Specs",
        ]
        assert [group_model.cell_value(row, 1) for row in range(7)] == [
            "9", "13", "5", "3", "2", "2", "22"
        ]

        panel.entity_table.setCurrentIndex(group_model.index(6, 0))
        app.processEvents()

        assert panel._selected_group_key == "odu_cond_specs"
        assert panel.row_table.model().rowCount() == 22
        assert panel.row_table.model().headerData(0, Qt.Horizontal) == "ODU"
        assert panel.primary_title.text() == "ODU Cond Specs Mapping Rows"
        assert panel.workspace_stack.currentWidget() is panel.primary_panel
        assert panel.content_splitter.sizes()[0] > panel.content_splitter.sizes()[1]
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_mapping_panel_group_refresh_preserves_selection_and_draft():
    app = _app()
    panel = DataMappingPanel(controller=_foundation_controller())
    try:
        panel.show()
        app.processEvents()
        group_model = panel.entity_table.model()
        panel.entity_table.setCurrentIndex(group_model.index(6, 0))
        app.processEvents()
        value_model = panel.row_table.model()
        assert value_model.setData(value_model.index(0, 4), "4.25", Qt.EditRole)

        panel.refresh()
        app.processEvents()

        assert panel._selected_group_key == "odu_cond_specs"
        assert panel.entity_table.currentIndex().row() == 6
        assert panel.row_table.model().cell_value(0, 4) == "4.25"
        assert panel._dirty
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_mapping_panel_empty_group_is_not_load_error():
    class EmptyGroupProvider:
        source_label = "Empty group fixture"

        def load_draft(self):
            return project_runtime_mapping_to_editor_draft(
                {
                    "idu": {},
                    "evap_index": {"EVAP-A": {"Evap Area": 8.2, "Evap Volume": 2.1}},
                    "odu": {"ODU-A": {"OD Volume": 2.5}},
                    "compressor": {"CMP-A": {"Comp EER": 3.2, "Comp cc": 11}},
                    "ref_type": {"R32": {}},
                    "exp_type": {"EEV": {}},
                },
                source_label=self.source_label,
            )

    app = _app()
    panel = DataMappingPanel(
        controller=DataMappingController(DataMappingService(EmptyGroupProvider()))
    )
    try:
        app.processEvents()

        assert panel._selected_group_key == "idu"
        assert panel.status_label.text() == "Ready."
        assert panel.state_title.text() == "IDU has no rows"
        assert "available but empty" in panel.state_message.text()
        assert panel.workspace_stack.currentWidget() is panel.state_panel
        assert panel._buttons["add_row"].isEnabled()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_mapping_panel_existing_malformed_source_is_load_error(tmp_path):
    app = _app()
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text("{not-json", encoding="utf-8")
    panel = DataMappingPanel(
        controller=DataMappingController(
            DataMappingService(RuntimeMappingCatalogProvider(str(mapping_file)))
        )
    )
    try:
        app.processEvents()

        assert panel.status_label.text() == "Unable to load mapping data."
        assert panel.state_title.text() == "Mapping data could not be loaded"
        assert panel.workspace_stack.currentWidget() is panel.state_panel
        assert panel.validation_table.model().cell_value(0, 0) == "error"
        assert panel._buttons["reload_runtime"].isEnabled()
        assert not panel._buttons["add_row"].isEnabled()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_mapping_panel_secondary_details_can_collapse():
    app = _app()
    panel = DataMappingPanel(controller=_foundation_controller())
    try:
        panel.show()
        app.processEvents()

        assert panel.details_panel.isVisible()
        panel.details_toggle.click()
        app.processEvents()
        assert not panel.details_panel.isVisible()
        assert panel.details_toggle.text() == "Show details"

        panel.details_toggle.click()
        app.processEvents()
        assert panel.details_panel.isVisible()
        assert panel.details_toggle.text() == "Hide details"
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_mapping_panel_keeps_primary_workspace_at_compact_window_size():
    app = _app()
    panel = DataMappingPanel(controller=_foundation_controller())
    try:
        panel.resize(900, 600)
        panel.show()
        app.processEvents()

        assert panel.width() == 900
        assert panel.entity_table.parentWidget().width() <= 280
        assert panel.row_table.viewport().width() > panel.entity_table.viewport().width()
        before = panel.row_table.viewport().height()
        panel.details_toggle.click()
        app.processEvents()
        assert panel.row_table.viewport().height() > before
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_mapping_export_selection_resolves_json_and_xlsx_extensions():
    assert EXPORT_FILTERS == "JSON Files (*.json);;Excel Workbook (*.xlsx)"
    assert _resolve_export_selection("/tmp/snapshot", "JSON Files (*.json)") == (
        "/tmp/snapshot.json",
        "json",
    )
    assert _resolve_export_selection("/tmp/snapshot", "Excel Workbook (*.xlsx)") == (
        "/tmp/snapshot.xlsx",
        "xlsx",
    )
    assert _resolve_export_selection(
        "/tmp/data_mapping_review_snapshot.json",
        "Excel Workbook (*.xlsx)",
    ) == (
        "/tmp/data_mapping_review_snapshot.xlsx",
        "xlsx",
    )
    assert _resolve_export_selection("/tmp/snapshot.xlsx", "JSON Files (*.json)") == (
        "/tmp/snapshot.xlsx",
        "xlsx",
    )


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


def test_data_mapping_panel_reload_skips_confirm_when_clean(monkeypatch):
    app = _app()
    panel = DataMappingPanel(controller=_foundation_controller())
    calls = []
    try:
        app.processEvents()
        monkeypatch.setattr(panel, "_confirm_reload_discard", lambda: calls.append("confirm") or True)
        original_reload = panel._controller.reload
        monkeypatch.setattr(
            panel._controller,
            "reload",
            lambda selected="": calls.append("reload") or original_reload(selected),
        )

        panel._reload()

        assert calls == ["reload"]
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_mapping_panel_reload_cancel_preserves_dirty(monkeypatch):
    app = _app()
    panel = DataMappingPanel(controller=_foundation_controller())
    calls = []
    try:
        app.processEvents()
        model = panel.row_table.model()
        assert model.setData(model.index(0, 1), "2.5", Qt.EditRole)
        monkeypatch.setattr(panel, "_confirm_reload_discard", lambda: calls.append("confirm") or False)
        monkeypatch.setattr(panel._controller, "reload", lambda: calls.append("reload"))

        panel._reload()

        assert calls == ["confirm"]
        assert panel.status_label.text() == "Unsaved changes."
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_mapping_panel_reload_confirm_discards_dirty(monkeypatch):
    app = _app()
    panel = DataMappingPanel(controller=_foundation_controller())
    calls = []
    try:
        app.processEvents()
        model = panel.row_table.model()
        assert model.setData(model.index(0, 1), "2.5", Qt.EditRole)
        monkeypatch.setattr(panel, "_confirm_reload_discard", lambda: calls.append("confirm") or True)
        original_reload = panel._controller.reload
        monkeypatch.setattr(
            panel._controller,
            "reload",
            lambda selected="": calls.append("reload") or original_reload(selected),
        )

        panel._reload()

        assert calls == ["confirm", "reload"]
        assert panel.status_label.text() == "Ready."
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_mapping_panel_shows_missing_runtime_source_state(tmp_path):
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
        assert panel.status_label.text() == "Mapping resource not found."
        assert panel.state_title.text() == "Mapping resource unavailable"
        assert panel.workspace_stack.currentWidget() is panel.state_panel
        assert panel.validation_table.model().cell_value(0, 4) == "The configured mapping file does not exist."
        assert not panel._buttons["add_row"].isEnabled()
        assert not panel._buttons["export_csv_v2"].isEnabled()
        assert panel._buttons["reload_runtime"].isEnabled()
        assert not panel.entity_table.currentIndex().isValid()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()
