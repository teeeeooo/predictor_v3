"""Offscreen Qt impact preview and guarded Save workflow tests."""

from __future__ import annotations

import os
import shutil

from PySide6.QtWidgets import QApplication

from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.controllers.data_definition_impact_projection import (
    project_data_definition_impact,
)
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.data_definition_panel import DataDefinitionPanel
from core.data_definition import AddDefinitionIntent, EditDefinitionIntent
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH, load_predict_schema_catalog_v2


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_impact_view_updates_through_add_save_reload_and_preserves_selection(tmp_path):
    app = _app()
    schema_path = _copy_schema(tmp_path)
    panel = DataDefinitionPanel(controller=_controller(schema_path))
    identity = ("schema_row", "fan_diameter")
    try:
        assert panel.impact_view.isVisibleTo(panel)
        assert panel.impact_view.change_label.text() == "No unsaved definition changes."
        assert not panel.save_button.isEnabled()

        accepted, _message = panel._apply_add_intent(
            AddDefinitionIntent("manual_predict", "Fan Diameter", "fan_diameter", "number")
        )
        app.processEvents()

        assert accepted
        assert panel._selected_identity == identity
        assert panel.impact_view.status_label.text() == "Dirty — Schema write: Ready"
        assert "Add Fan Diameter" in panel.impact_view.change_label.text()
        assert "Predict restart: required" in panel.impact_view.runtime_label.text()
        assert "ML compatibility fingerprint: unchanged" in panel.impact_view.runtime_label.text()
        assert panel.save_button.isEnabled()

        panel.save_button.click()
        app.processEvents()

        assert panel._selected_identity == identity
        assert panel.impact_view.status_label.text() == "Clean — Schema write: No changes"
        assert "Status: written" in panel.impact_view.result_label.text()
        assert "Backup path:" in panel.impact_view.result_label.text()
        assert not panel.save_button.isEnabled()
        loaded = load_predict_schema_catalog_v2(schema_path)
        assert next(row for row in loaded.rows if row.column_key == "fan_diameter").display_order == 420
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_impact_view_shows_mapping_owner_and_ml_blocker_then_reset_clears_stale_state(
    tmp_path,
):
    app = _app()
    panel = DataDefinitionPanel(controller=_controller(_copy_schema(tmp_path)))
    try:
        accepted, _message = panel._apply_add_intent(AddDefinitionIntent(
            "mapping_attribute",
            "Cond Inner Area",
            "cond_inner_area",
            "number",
            mapping_entity="cond_specs",
            mapping_attribute="Cond Inner Area",
            trigger_column="odu",
            rule_id="cond_specs_lookup",
        ))
        app.processEvents()

        assert accepted
        assert "Cond Inner Area in cond_specs" in panel.impact_view.mapping_label.text()
        assert "Data Mapping-owned" in panel.impact_view.mapping_label.text()

        panel._selected_identity = ("schema_row", "cooling_capa")
        accepted, _message = panel._apply_edit_intent(EditDefinitionIntent(
            panel._selected_identity,
            (("ml_name", "Cooling Capacity Renamed"),),
        ))
        app.processEvents()
        assert accepted
        assert panel.impact_view.status_label.text() == "Blocked — Schema write: Blocked"
        assert "Direct" in panel.impact_view.save_label.text()
        assert "(ml_compatibility_projection_write_required)" in (
            panel.impact_view.save_label.text()
        )
        assert not panel.save_button.isEnabled()

        panel._reset_draft()
        app.processEvents()
        assert panel.impact_view.change_label.text() == "No unsaved definition changes."
        assert panel.impact_view.result_label.text() == "No save attempted."
        assert "Mapping Requirement impact" in panel.impact_view.mapping_label.text()
        assert not panel.save_button.isEnabled()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_no_match_search_preserves_blocker_evidence_and_reprojects_relevance(tmp_path):
    app = _app()
    schema_path = _copy_schema(tmp_path)
    panel = DataDefinitionPanel(controller=_controller(schema_path))
    identity = ("schema_row", "cooling_capa")
    try:
        panel._selected_identity = identity
        accepted, _message = panel._apply_edit_intent(EditDefinitionIntent(
            identity,
            (("ml_name", "Cooling Capacity Renamed"),),
        ))
        app.processEvents()
        assert accepted
        state_before = panel._state
        schema_before = schema_path.read_bytes()
        selected = project_data_definition_impact(state_before, identity)
        evidence = tuple(
            (
                item.code,
                item.target,
                item.message,
                item.related_row_identity,
                item.related_field,
            )
            for item in selected.blockers
        )
        assert {item.relevance for item in selected.blockers} == {"direct"}

        panel.search_input.setText("definitely-no-definition-matches")
        app.processEvents()

        assert panel.inventory_table.model().rowCount() == 0
        assert panel._selected_identity is None
        assert panel._state is state_before
        assert panel._state.draft_changed
        assert not panel.save_button.isEnabled()
        no_selection = project_data_definition_impact(panel._state, None)
        assert tuple(
            (
                item.code,
                item.target,
                item.message,
                item.related_row_identity,
                item.related_field,
            )
            for item in no_selection.blockers
        ) == evidence
        assert {item.relevance for item in no_selection.blockers} == {
            "selection_unavailable"
        }
        assert "Selection Unavailable" in panel.impact_view.save_label.text()
        assert "(ml_compatibility_projection_write_required)" in (
            panel.impact_view.save_label.text()
        )
        assert "definition: cooling_capa" in panel.impact_view.save_label.text()
        assert "field: ml_name" in panel.impact_view.save_label.text()
        assert "target: schema_csv" in panel.impact_view.save_label.text()
        assert schema_path.read_bytes() == schema_before

        panel.search_input.clear()
        app.processEvents()
        restored = project_data_definition_impact(
            panel._state,
            panel._selected_identity,
        )
        assert panel._selected_identity == identity
        assert tuple(
            (
                item.code,
                item.target,
                item.message,
                item.related_row_identity,
                item.related_field,
            )
            for item in restored.blockers
        ) == evidence
        assert {item.relevance for item in restored.blockers} == {"direct"}
        assert "selection_unavailable" not in panel.impact_view.save_label.text()
        assert "definition: cooling_capa" not in panel.impact_view.save_label.text()
        assert schema_path.read_bytes() == schema_before
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def _copy_schema(tmp_path):
    schema_path = tmp_path / "schema.csv"
    shutil.copyfile(DEFAULT_SCHEMA_PATH, schema_path)
    return schema_path


def _controller(schema_path):
    return DataDefinitionController(DataDefinitionService(schema_path=schema_path))
