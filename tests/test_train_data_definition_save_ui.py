"""Train Data Definition guarded save UI tests."""

from __future__ import annotations

import hashlib
import os
import shutil

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QPushButton

from apps.train.controllers.data_definition_controller import DRAFT_FIELDS, DataDefinitionController
from apps.train.controllers.data_definition_detail_projection import project_blockers
from apps.train.controllers.data_definition_presentation import (
    project_data_definition_inventory,
)
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.data_definition_panel import DataDefinitionPanel
import core.data_definition.schema_writer as schema_writer_module
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH, load_predict_schema_catalog_v2


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_data_definition_service_saves_schema_draft_to_explicit_tmp_path(tmp_path):
    before_hash = _file_hash(DEFAULT_SCHEMA_PATH)
    schema_path = _copy_schema(tmp_path)
    service = DataDefinitionService(schema_path=schema_path)
    draft = service.load_draft()
    row = next(item for item in draft.rows if item.column_key == "idu")
    edited = service.edit_draft_cell(draft, row.identity, "label", "Indoor Unit")

    result = service.save_schema_draft(edited.draft)

    assert result.success
    assert result.status == "written"
    assert result.backup_path is not None
    assert result.backup_path.exists()
    loaded = load_predict_schema_catalog_v2(schema_path)
    assert next(item for item in loaded.rows if item.column_key == "idu").label == (
        "Indoor Unit"
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
    row_identity = ("schema_row", "idu")
    row_index = state.draft_row_identities.index(row_identity)

    edited = controller.edit_cell(row_identity, "label", "Indoor Unit")
    saved = controller.save_schema()
    noop = controller.save_schema()

    assert edited.can_save_schema
    assert saved.status == "saved"
    assert ("Status", "written") in saved.save_result_rows
    assert not saved.draft_changed
    assert saved.save_plan_rows[0][1] == "no_op"
    assert saved.draft_rows[row_index][DRAFT_FIELDS.index("label")].value == "Indoor Unit"
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
    assert saved.can_save_schema
    assert not saved.save_action_enabled
    assert saved.save_result_issue_rows == (
        (
            "error",
            "candidate_schema_validation_failed",
            "schema_csv",
            "line 2 column_key=cooling_capa: invalid data_type 'invalid_type'",
        ),
    )
    candidate = next(
        item
        for item in saved.blocker_items
        if item.code == "candidate_schema_validation_failed"
    )
    assert candidate.related_row_identity == ("schema_row", "cooling_capa")
    assert candidate.related_field == "data_type"
    assert candidate.source == "last_save_result"
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


def test_candidate_blocker_is_other_for_valid_changed_row_and_direct_for_invalid_row(
    tmp_path,
):
    schema_path = _copy_schema(tmp_path)
    original = schema_path.read_text(encoding="utf-8")
    controller = DataDefinitionController(DataDefinitionService(schema_path=schema_path))
    controller.refresh()
    valid_identity = ("schema_row", "idu")
    invalid_identity = ("schema_row", "cooling_capa")
    controller.edit_cell(valid_identity, "label", "Indoor Unit Label")
    controller.edit_cell(invalid_identity, "data_type", "invalid_type")

    saved = controller.save_schema()
    valid_blockers = project_blockers(saved, valid_identity)
    invalid_blockers = project_blockers(saved, invalid_identity)
    valid_summary = dict(
        project_data_definition_inventory(
            saved,
            selected_identity=valid_identity,
        ).detail.rows
    )["Save blockers"]
    invalid_summary = dict(
        project_data_definition_inventory(
            saved,
            selected_identity=invalid_identity,
        ).detail.rows
    )["Save blockers"]

    assert saved.status == "blocked"
    assert not saved.save_action_enabled
    assert [item.relevance for item in valid_blockers] == ["other_definition"]
    assert [item.relevance for item in invalid_blockers] == ["direct"]
    assert valid_summary.startswith("No direct blocker for this definition.")
    assert "cooling_capa" in valid_summary
    assert invalid_summary.startswith("Direct blockers")
    assert "candidate_schema_validation_failed" in invalid_summary
    assert "invalid data_type 'invalid_type'" in invalid_summary
    assert schema_path.read_text(encoding="utf-8") == original


def test_distinct_candidate_issues_with_same_code_keep_row_and_field_attribution(
    tmp_path,
):
    schema_path = _copy_schema(tmp_path)
    original = schema_path.read_text(encoding="utf-8")
    controller = DataDefinitionController(DataDefinitionService(schema_path=schema_path))
    controller.refresh()
    cooling_identity = ("schema_row", "cooling_capa")
    heating_identity = ("schema_row", "heating_capa")
    controller.edit_cell(cooling_identity, "data_type", "invalid_type")
    controller.edit_cell(heating_identity, "editor", "invalid_editor")

    saved = controller.save_schema()
    result_candidates = tuple(
        item
        for item in saved.blocker_items
        if item.source == "last_save_result"
        and item.code == "candidate_schema_validation_failed"
    )
    cooling_blockers = project_blockers(saved, cooling_identity)
    heating_blockers = project_blockers(saved, heating_identity)

    assert len(saved.save_result_issue_rows) == 2
    assert len(result_candidates) == 2
    assert [item.related_row_identity for item in result_candidates] == [
        cooling_identity,
        heating_identity,
    ]
    assert [item.related_field for item in result_candidates] == ["data_type", "editor"]
    assert [item.relevance for item in cooling_blockers] == ["direct", "other_definition"]
    assert [item.relevance for item in heating_blockers] == ["direct", "other_definition"]
    assert cooling_blockers[0].related_row_identity == cooling_identity
    assert heating_blockers[0].related_row_identity == heating_identity
    assert "invalid data_type" in saved.save_result_issue_rows[0][3]
    assert "invalid editor" in saved.save_result_issue_rows[1][3]
    assert schema_path.read_text(encoding="utf-8") == original

    controller.edit_cell(cooling_identity, "data_type", "number")
    remaining = controller.save_schema()
    remaining_candidates = tuple(
        item
        for item in remaining.blocker_items
        if item.code == "candidate_schema_validation_failed"
    )

    assert len(remaining_candidates) == 1
    assert remaining_candidates[0].related_row_identity == heating_identity
    assert remaining_candidates[0].related_field == "editor"
    assert "invalid editor" in remaining_candidates[0].message
    assert schema_path.read_text(encoding="utf-8") == original


def test_data_definition_panel_save_button_displays_guarded_result(tmp_path):
    app = _app()
    schema_path = _copy_schema(tmp_path)
    controller = DataDefinitionController(DataDefinitionService(schema_path=schema_path))
    panel = DataDefinitionPanel(controller=controller)
    try:
        app.processEvents()
        panel.search_input.setText("idu")
        app.processEvents()
        assert panel._selected_identity == ("schema_row", "idu")
        label_col = DRAFT_FIELDS.index("label")
        row_index = panel._state.draft_row_identities.index(("schema_row", "idu"))
        assert panel.draft_table.model().setData(
            panel.draft_table.model().index(row_index, label_col),
            "Indoor Unit",
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
        assert not panel.draft_table.model().is_changed_cell(row_index, label_col)
        assert not panel.save_button.isEnabled()
        assert panel.status_label.text() == "Schema saved"
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

        assert panel.status_label.text() == "Save blocked"
        assert not panel.save_button.isEnabled()
        assert panel._state.draft_changed
        assert panel._state.can_save_schema
        assert not panel._state.save_action_enabled
        blockers = dict(
            project_data_definition_inventory(
                panel._state,
                selected_identity=("schema_row", "cooling_capa"),
            ).detail.rows
        )["Save blockers"]
        assert "candidate_schema_validation_failed" in blockers
        assert "invalid data_type 'invalid_type'" in blockers
        assert blockers != "None"
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_data_definition_panel_retries_recoverable_schema_write_error(
    tmp_path,
    monkeypatch,
):
    app = _app()
    schema_path = _copy_schema(tmp_path)
    original = schema_path.read_text(encoding="utf-8")
    real_replace = schema_writer_module.os.replace
    attempts = 0

    def fail_once(source, destination):  # noqa: ANN001, ANN202
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise OSError("temporary replace failure")
        return real_replace(source, destination)

    monkeypatch.setattr(schema_writer_module.os, "replace", fail_once)
    panel = DataDefinitionPanel(
        controller=DataDefinitionController(DataDefinitionService(schema_path=schema_path))
    )
    try:
        app.processEvents()
        panel.search_input.setText("idu")
        app.processEvents()
        assert panel._selected_identity == ("schema_row", "idu")
        label_col = DRAFT_FIELDS.index("label")
        row_index = panel._state.draft_row_identities.index(("schema_row", "idu"))
        assert not panel.save_button.isEnabled()
        assert panel.draft_table.model().setData(
            panel.draft_table.model().index(row_index, label_col),
            "Indoor Unit",
            Qt.EditRole,
        )
        assert panel.save_button.isEnabled()

        panel.save_button.click()
        app.processEvents()

        assert dict(panel._state.save_result_rows)["Status"] == "error"
        assert schema_path.read_text(encoding="utf-8") == original
        assert panel._state.draft_changed
        assert panel._state.can_save_schema
        assert panel._state.save_action_enabled
        assert panel.save_plan_table.model().cell_value(0, 1) == "planned"
        assert panel.save_button.isEnabled()
        assert panel.status_label.text() == "Schema save failed"
        assert panel.save_button.text() == "Retry Save"
        assert "temporary replace failure" in panel.impact_view.concise_label.text()
        assert panel.search_input.text() == "idu"
        assert panel._selected_identity == ("schema_row", "idu")

        panel.save_button.click()
        app.processEvents()

        assert attempts == 2
        assert dict(panel._state.save_result_rows)["Status"] == "written"
        assert not panel._state.draft_changed
        assert not panel._state.can_save_schema
        assert not panel._state.save_action_enabled
        assert not panel.save_button.isEnabled()
        assert panel.status_label.text() == "Schema saved"
        assert panel.search_input.text() == "idu"
        assert panel._selected_identity == ("schema_row", "idu")
        loaded = load_predict_schema_catalog_v2(schema_path)
        assert next(row for row in loaded.rows if row.column_key == "idu").label == (
            "Indoor Unit"
        )
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
