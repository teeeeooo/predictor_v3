"""Train Data Definition guarded save UI tests."""

from __future__ import annotations

import hashlib
import os
import shutil

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QPushButton

from apps.train.controllers.data_definition_controller import DRAFT_FIELDS, DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.data_definition_panel import DataDefinitionPanel
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH, load_predict_schema_catalog_v2


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_data_definition_service_saves_schema_draft_to_explicit_tmp_path(tmp_path):
    before_hash = _file_hash(DEFAULT_SCHEMA_PATH)
    schema_path = _copy_schema(tmp_path)
    service = DataDefinitionService(schema_path=schema_path)
    draft = service.load_draft()
    row = next(item for item in draft.rows if item.column_key == "cooling_capa")
    edited = service.edit_draft_cell(draft, row.identity, "label", "Cooling Capacity")

    result = service.save_schema_draft(edited.draft)

    assert result.success
    assert result.status == "written"
    assert result.backup_path is not None
    assert result.backup_path.exists()
    loaded = load_predict_schema_catalog_v2(schema_path)
    assert next(item for item in loaded.rows if item.column_key == "cooling_capa").label == (
        "Cooling Capacity"
    )
    assert _file_hash(DEFAULT_SCHEMA_PATH) == before_hash


def test_data_definition_controller_save_reports_noop_for_unchanged_draft(tmp_path):
    schema_path = _copy_schema(tmp_path)
    controller = DataDefinitionController(DataDefinitionService(schema_path=schema_path))
    controller.refresh()

    state = controller.save_schema()

    assert state.status == "ready"
    assert ("Status", "noop") in state.save_result_rows
    assert ("Rows written", "0") in state.save_result_rows
    assert not state.draft_changed


def test_data_definition_controller_save_reloads_after_success(tmp_path):
    schema_path = _copy_schema(tmp_path)
    controller = DataDefinitionController(DataDefinitionService(schema_path=schema_path))
    state = controller.refresh()
    row_identity = state.draft_row_identities[0]

    edited = controller.edit_cell(row_identity, "label", "Cooling Capacity")
    saved = controller.save_schema()
    noop = controller.save_schema()

    assert edited.can_save_schema
    assert saved.status == "saved"
    assert ("Status", "written") in saved.save_result_rows
    assert not saved.draft_changed
    assert saved.save_plan_rows[0][1] == "no_op"
    assert saved.draft_rows[0][DRAFT_FIELDS.index("label")].value == "Cooling Capacity"
    assert noop.status == "ready"
    assert ("Status", "noop") in noop.save_result_rows


def test_data_definition_controller_surfaces_blocked_candidate_validation(tmp_path):
    schema_path = _copy_schema(tmp_path)
    original = schema_path.read_text(encoding="utf-8")
    controller = DataDefinitionController(DataDefinitionService(schema_path=schema_path))
    state = controller.refresh()

    edited = controller.edit_cell(state.draft_row_identities[0], "data_type", "invalid_type")
    saved = controller.save_schema()

    assert edited.can_save_schema
    assert saved.status == "blocked"
    assert ("Status", "blocked") in saved.save_result_rows
    assert "candidate_schema_validation_failed" in dict(saved.save_result_rows)["Issues"]
    assert saved.draft_changed
    assert not saved.can_save_schema
    assert schema_path.read_text(encoding="utf-8") == original
    assert not (tmp_path / "backups").exists()


def test_data_definition_controller_blocks_ml_projection_change_without_write(tmp_path):
    schema_path = _copy_schema(tmp_path)
    original = schema_path.read_text(encoding="utf-8")
    controller = DataDefinitionController(DataDefinitionService(schema_path=schema_path))
    state = controller.refresh()
    row_index = next(
        index
        for index, identity in enumerate(state.draft_row_identities)
        if identity == ("schema_row", "cooling_capa")
    )

    edited = controller.edit_cell(
        state.draft_row_identities[row_index],
        "ml_name",
        "Cooling Capacity Renamed",
    )
    saved = controller.save_schema()

    blocker = next(
        row
        for row in edited.save_blocker_rows
        if row[1] == "ml_compatibility_projection_write_required"
    )
    assert not edited.can_save_schema
    assert blocker[:3] == ("error", "ml_compatibility_projection_write_required", "schema_csv")
    assert saved.status == "blocked"
    assert "ml_compatibility_projection_write_required" in dict(saved.save_result_rows)["Issues"]
    assert schema_path.read_text(encoding="utf-8") == original
    assert not (tmp_path / "backups").exists()


def test_data_definition_panel_save_button_displays_guarded_result(tmp_path):
    app = _app()
    schema_path = _copy_schema(tmp_path)
    controller = DataDefinitionController(DataDefinitionService(schema_path=schema_path))
    panel = DataDefinitionPanel(controller=controller)
    try:
        app.processEvents()
        label_col = DRAFT_FIELDS.index("label")
        assert panel.draft_table.model().setData(
            panel.draft_table.model().index(0, label_col),
            "Cooling Capacity",
            Qt.EditRole,
        )
        app.processEvents()

        save_buttons = [
            child for child in panel.findChildren(QPushButton)
            if child.accessibleName() == "Save Data Definition Schema"
        ]
        assert len(save_buttons) == 1
        save_buttons[0].click()
        app.processEvents()

        result_model = panel.save_result_table.model()
        result_rows = {
            result_model.cell_value(row, 0): result_model.cell_value(row, 1)
            for row in range(result_model.rowCount())
        }
        assert result_rows["Status"] == "written"
        assert result_rows["Success"] == "true"
        assert panel.save_plan_table.model().cell_value(0, 1) == "no_op"
        assert not panel.draft_table.model().is_changed_cell(0, label_col)
        assert not panel.save_button.isEnabled()
        assert panel.status_label.text().startswith("Saved:")
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_definition_panel_failed_save_reprojects_blocked_action_state(tmp_path):
    app = _app()
    schema_path = _copy_schema(tmp_path)
    panel = DataDefinitionPanel(
        controller=DataDefinitionController(DataDefinitionService(schema_path=schema_path))
    )
    try:
        app.processEvents()
        data_type_col = DRAFT_FIELDS.index("data_type")
        assert panel.draft_table.model().setData(
            panel.draft_table.model().index(0, data_type_col),
            "invalid_type",
            Qt.EditRole,
        )
        assert panel.save_button.isEnabled()

        panel.save_button.click()
        app.processEvents()

        assert panel.status_label.text().startswith("Blocked:")
        assert not panel.save_button.isEnabled()
        assert panel._state.draft_changed
        assert not panel._state.can_save_schema
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def _copy_schema(tmp_path):
    schema_path = tmp_path / "schema.csv"
    shutil.copyfile(DEFAULT_SCHEMA_PATH, schema_path)
    return schema_path


def _file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
