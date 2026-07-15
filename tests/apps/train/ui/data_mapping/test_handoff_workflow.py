"""Offscreen Train shell Data Definition to Data Mapping workflow."""

from __future__ import annotations

import json
import os
import shutil

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.services.data_mapping_service import (
    DataDefinitionMappingRequirementProvider,
    DataMappingService,
    RuntimeMappingCatalogProvider,
)
from apps.train.ui.shell import TrainShell
from apps.train.application.data_mapping import DataMappingNavigationResult
from apps.train.ui.data_definition_panel import DataDefinitionPanel
from core.data_definition import AddDefinitionIntent, EditDefinitionIntent
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH, load_predict_schema_catalog_v2


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_cond_inner_area_saved_handoff_coverage_edit_save_reload(tmp_path):
    app = _app()
    schema_path = tmp_path / "schema.csv"
    shutil.copyfile(DEFAULT_SCHEMA_PATH, schema_path)
    mapping_path = _mapping_file(tmp_path)
    mapping_before = mapping_path.read_bytes()
    definition_controller = DataDefinitionController(
        DataDefinitionService(schema_path=schema_path)
    )
    mapping_controller = DataMappingController(
        DataMappingService(
            RuntimeMappingCatalogProvider(str(mapping_path)),
            DataDefinitionMappingRequirementProvider(schema_path),
        )
    )
    shell = TrainShell(
        data_definition_controller=definition_controller,
        data_mapping_controller=mapping_controller,
    )
    try:
        shell.resize(1440, 900)
        shell.show()
        app.processEvents()
        panel = shell.data_definition_panel
        before_projection = panel._state.projected_feature_rows

        accepted, _message = panel._apply_add_intent(_cond_intent())
        app.processEvents()

        assert accepted
        assert panel._state.draft_changed
        assert not panel.handoff_panel.open_button.isEnabled()
        assert "Save schema first" in panel.handoff_panel.detail.text()
        assert panel._state.projected_feature_rows == before_projection
        assert mapping_path.read_bytes() == mapping_before

        panel._save_schema()
        app.processEvents()

        assert not panel._state.draft_changed
        assert panel.handoff_panel.open_button.isEnabled()
        assert "Predict restart required" in panel.handoff_panel.detail.text()
        saved_row = next(
            row
            for row in load_predict_schema_catalog_v2(schema_path).rows
            if row.column_key == "cond_inner_area"
        )
        assert saved_row.mapping_entity == "cond_specs"
        assert saved_row.mapping_attribute == "Cond Inner Area"
        assert mapping_path.read_bytes() == mapping_before

        panel.handoff_panel.open_button.click()
        app.processEvents()

        mapping_panel = shell.data_mapping_panel
        state = mapping_panel._current_state
        assert shell.tabs.count() == 4
        assert shell.tabs.currentWidget() is mapping_panel
        assert state.selected_group_key == "odu_cond_specs"
        assert state.value_headers[-1] == "Cond Inner Area"
        assert [row.row_key for row in state.values] == [
            "ODU-A F&T 7 1",
            "ODU-A PFC 1",
        ]
        assert state.values[1].values[state.value_headers.index("Pi")] == ""
        coverage = _coverage(state)
        assert (coverage.ready_rows, coverage.missing_rows, coverage.invalid_rows) == (0, 2, 0)
        assert mapping_panel.row_table.currentIndex().row() == 0
        assert mapping_panel.row_table.currentIndex().column() == len(state.value_headers) - 1
        assert mapping_path.read_bytes() == mapping_before

        model = mapping_panel.row_table.model()
        dynamic_column = model.columnCount() - 1
        assert model.setData(model.index(0, dynamic_column), "not-a-number", Qt.EditRole)
        app.processEvents()
        assert (_coverage(mapping_panel._current_state).invalid_rows) == 1
        assert mapping_path.read_bytes() == mapping_before

        model = mapping_panel.row_table.model()
        assert model.setData(model.index(0, dynamic_column), "2.25", Qt.EditRole)
        app.processEvents()
        first_filled = _coverage(mapping_panel._current_state)
        assert (first_filled.ready_rows, first_filled.missing_rows, first_filled.invalid_rows) == (
            1,
            1,
            0,
        )
        mapping_panel.coverage_panel.go_button.click()
        app.processEvents()
        assert mapping_panel.row_table.currentIndex().row() == 1

        model = mapping_panel.row_table.model()
        assert model.setData(model.index(1, dynamic_column), "3.75", Qt.EditRole)
        app.processEvents()
        ready = _coverage(mapping_panel._current_state)
        assert ready.status == "ready"
        assert (ready.ready_rows, ready.missing_rows, ready.invalid_rows) == (2, 0, 0)
        assert "Coverage ready" in mapping_panel.coverage_panel.summary.text()
        assert mapping_panel._current_state.dirty
        assert _action_enabled(mapping_panel._current_state, "save_mapping_json")
        assert mapping_path.read_bytes() == mapping_before

        mapping_panel._save()
        app.processEvents()

        persisted = json.loads(mapping_path.read_text(encoding="utf-8"))
        assert persisted["cond_specs"]["ODU-A F&T 7 1"] == {
            "Cond Area": 3.5,
            "Cond Volume": 4.5,
            "Cond Inner Area": 2.25,
        }
        assert persisted["cond_specs"]["ODU-A PFC 1"] == {
            "Cond Area": 5.5,
            "Cond Volume": 6.5,
            "Cond Inner Area": 3.75,
        }
        assert persisted["idu"] == {"IDU-A": {"ID Volume": 1.25}}
        assert persisted["odu"] == {"ODU-A": {"OD Volume": 2.5}}
        assert not mapping_panel._current_state.dirty

        mapping_panel._apply_state(mapping_controller.reload("odu_cond_specs"))
        app.processEvents()
        reloaded = mapping_panel._current_state
        assert _coverage(reloaded).status == "ready"
        assert reloaded.values[0].values[-1] == "2.25"
        assert reloaded.values[1].values[-1] == "3.75"
        assert reloaded.values[0].values[4:6] == ("3.5", "4.5")
        assert reloaded.values[1].values[4:6] == ("5.5", "6.5")
    finally:
        shell.close()
        shell.deleteLater()
        app.processEvents()


def test_saved_requirement_optional_remove_readd_preserves_unsaved_mapping_session(tmp_path):
    app = _app()
    schema_path = tmp_path / "schema.csv"
    shutil.copyfile(DEFAULT_SCHEMA_PATH, schema_path)
    mapping_path = _mapping_file(tmp_path)
    mapping_before = mapping_path.read_bytes()
    mapping_service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_path)),
        DataDefinitionMappingRequirementProvider(schema_path),
    )
    definition_controller = DataDefinitionController(
        DataDefinitionService(schema_path=schema_path)
    )
    mapping_controller = DataMappingController(mapping_service)
    shell = TrainShell(
        data_definition_controller=definition_controller,
        data_mapping_controller=mapping_controller,
    )
    try:
        shell.show()
        panel = shell.data_definition_panel
        accepted, _message = panel._apply_add_intent(_cond_intent())
        assert accepted
        panel._save_schema()
        panel.handoff_panel.open_button.click()
        app.processEvents()

        mapping_panel = shell.data_mapping_panel
        model = mapping_panel.row_table.model()
        dynamic_column = model.columnCount() - 1
        assert model.setData(model.index(0, dynamic_column), "2.25", Qt.EditRole)
        app.processEvents()
        mapping_controller.edit_cell("idu", 0, "ID Volume", "9.5")
        initial_request = panel._state.saved_mapping_handoffs[0]
        assert mapping_path.read_bytes() == mapping_before

        accepted, _message = panel._apply_edit_intent(
            EditDefinitionIntent(
                ("schema_row", "cond_inner_area"),
                (("required", False),),
            )
        )
        assert accepted
        panel._save_schema()
        panel.handoff_panel.open_button.click()
        app.processEvents()

        optional = mapping_panel._current_state
        optional_coverage = _coverage(optional)
        assert optional.dirty
        assert not optional_coverage.required
        assert (optional_coverage.ready_rows, optional_coverage.missing_rows) == (1, 1)
        assert optional.values[0].values[-1] == "2.25"
        assert _action_enabled(optional, "save_mapping_json")
        assert not any(
            issue.code == "required_mapping_value_missing"
            and issue.field == "Cond Inner Area"
            for issue in optional.validation_rows
        )
        assert mapping_path.read_bytes() == mapping_before

        accepted, _message = panel._apply_edit_intent(
            EditDefinitionIntent(
                ("schema_row", "cond_inner_area"),
                (("active", False),),
            )
        )
        assert accepted
        panel._save_schema()
        assert not panel.handoff_panel.open_button.isEnabled()

        stale = shell.open_data_mapping(initial_request)
        app.processEvents()
        removed = mapping_panel._current_state
        backing_group = mapping_service.current_snapshot().draft.group("odu_cond_specs")
        assert stale.status == "requirement_not_saved"
        assert "Cond Inner Area" not in removed.value_headers
        assert not any(
            item.definition_column_key == "cond_inner_area"
            for item in removed.coverage_items
        )
        assert backing_group.rows[0].value_for("Cond Inner Area") == 2.25
        assert "Cond Inner Area" not in backing_group.notes
        assert mapping_path.read_bytes() == mapping_before

        accepted, _message = panel._apply_edit_intent(
            EditDefinitionIntent(
                ("schema_row", "cond_inner_area"),
                (("active", True),),
            )
        )
        assert accepted
        panel._save_schema()
        panel.handoff_panel.open_button.click()
        app.processEvents()

        restored = mapping_panel._current_state
        restored_coverage = _coverage(restored)
        assert restored.value_headers[-1] == "Cond Inner Area"
        assert restored.values[0].values[-1] == "2.25"
        assert (restored_coverage.ready_rows, restored_coverage.missing_rows) == (1, 1)
        assert not restored_coverage.required
        assert restored.dirty
        assert mapping_path.read_bytes() == mapping_before
    finally:
        shell.close()
        shell.deleteLater()
        app.processEvents()


def test_data_definition_multiple_handoffs_are_selectable_and_deterministic(tmp_path):
    app = _app()
    schema_path = tmp_path / "schema.csv"
    shutil.copyfile(DEFAULT_SCHEMA_PATH, schema_path)
    opened = []

    def open_request(request):  # noqa: ANN001, ANN202
        opened.append(request)
        return DataMappingNavigationResult("opened", "Opened.", request)

    panel = DataDefinitionPanel(
        controller=DataDefinitionController(DataDefinitionService(schema_path=schema_path)),
        on_open_data_mapping=open_request,
    )
    try:
        panel._apply_add_intent(_cond_intent())
        panel._apply_add_intent(
            AddDefinitionIntent(
                kind="mapping_attribute",
                label="Fan Diameter",
                column_key="fan_diameter",
                data_type="number",
                required=False,
                mapping_entity="idu",
                mapping_attribute="Fan Diameter",
                trigger_column="idu",
            )
        )
        panel._save_schema()
        app.processEvents()

        assert panel.handoff_panel.selector.count() == 2
        assert [
            panel.handoff_panel.selector.itemData(index) for index in range(2)
        ] == ["cond_inner_area", "fan_diameter"]
        panel.handoff_panel.selector.setCurrentIndex(1)
        panel.handoff_panel.open_button.click()

        assert len(opened) == 1
        assert opened[0].definition_column_key == "fan_diameter"
        assert opened[0].resolved_group_key == "idu"
        assert not opened[0].required
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def _coverage(state):  # noqa: ANN001, ANN202
    return next(
        item
        for item in state.coverage_items
        if item.definition_column_key == "cond_inner_area"
    )


def _action_enabled(state, key):  # noqa: ANN001, ANN202
    return next(action.enabled for action in state.actions if action.key == key)


def _cond_intent() -> AddDefinitionIntent:
    return AddDefinitionIntent(
        kind="mapping_attribute",
        label="Cond Inner Area",
        column_key="cond_inner_area",
        data_type="number",
        required=True,
        mapping_entity="cond_specs",
        mapping_attribute="Cond Inner Area",
        trigger_column="odu",
        rule_id="cond_specs_lookup",
        notes="Supported condenser lookup",
    )


def _mapping_file(tmp_path):  # noqa: ANN001, ANN201
    path = tmp_path / "mapping.json"
    path.write_text(
        json.dumps(
            {
                "idu": {"IDU-A": {"ID Volume": 1.25}},
                "odu": {"ODU-A": {"OD Volume": 2.5}},
                "odu_cascade": {
                    "ODU-A": {
                        "Available_Fins": ["F&T", "PFC"],
                        "Available_Pis": ["7"],
                        "Available_Rows": ["1"],
                    }
                },
                "cond_specs": {
                    "ODU-A F&T 7 1": {"Cond Area": 3.5, "Cond Volume": 4.5},
                    "ODU-A PFC 1": {"Cond Area": 5.5, "Cond Volume": 6.5},
                },
                "ref_type": {"R32": {}},
                "exp_type": {"EEV": {}},
            }
        ),
        encoding="utf-8",
    )
    return path
