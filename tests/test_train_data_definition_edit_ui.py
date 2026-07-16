"""Train Data Definition draft edit UI tests."""

from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QAbstractItemView

from apps.train.controllers.data_definition_controller import (
    DRAFT_FIELDS,
    DataDefinitionController,
)
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.data_definition_models import DataDefinitionDraftTableModel
from apps.train.ui.data_definition_panel import DataDefinitionPanel


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_data_definition_service_edits_in_memory_draft_and_previews_plan():
    service = DataDefinitionService()
    draft = service.load_draft()
    row = next(item for item in draft.rows if item.column_key == "idu")

    edited = service.edit_draft_cell(draft, row.identity, "label", "Indoor Unit")
    plan = service.preview_save_plan(edited.draft)
    blocked = service.edit_draft_cell(draft, row.identity, "column_key", "cooling_capacity")
    invalid_bool = service.edit_draft_cell(draft, row.identity, "visible", "maybe")

    assert edited.accepted
    assert edited.draft.is_changed
    assert plan.can_save_schema
    assert {change.field_name for change in plan.changed_fields} == {"label"}
    assert not blocked.accepted
    assert blocked.draft is draft
    assert not invalid_bool.accepted
    assert invalid_bool.message == "visible must be true or false."


def test_data_definition_controller_exposes_draft_rows_and_reset_state():
    controller = DataDefinitionController()

    state = controller.refresh()
    schema_row = ("schema_row", "idu")
    schema_index = state.draft_row_identities.index(schema_row)
    label_col = DRAFT_FIELDS.index("label")
    column_key_col = DRAFT_FIELDS.index("column_key")
    derived_index = next(
        index for index, identity in enumerate(state.draft_row_identities)
        if identity[0] == "derived_policy"
    )

    assert state.status == "ready"
    assert len(state.draft_rows) > 28
    assert state.draft_rows[0][label_col].editable
    assert not state.draft_rows[0][column_key_col].editable
    assert not state.draft_rows[derived_index][DRAFT_FIELDS.index("ml_name")].editable
    assert not state.draft_changed
    assert not state.can_save_schema

    edited = controller.edit_cell(schema_row, "label", "Indoor Unit")

    assert edited.status == "draft_changed"
    assert edited.draft_changed
    assert edited.can_save_schema
    assert any(row[2] == "label" for row in edited.draft_change_rows)
    assert edited.draft_rows[schema_index][label_col].changed

    reset = controller.reset_draft()

    assert reset.status == "ready"
    assert not reset.draft_changed
    assert not reset.can_save_schema


def test_data_definition_draft_table_model_enforces_field_editability():
    state = DataDefinitionController().refresh()
    accepted: list[tuple[tuple[str, str], str, object]] = []
    model = DataDefinitionDraftTableModel(
        state.draft_headers,
        state.draft_row_identities,
        state.draft_rows,
        on_cell_changed=lambda row_id, field, value: accepted.append((row_id, field, value)) or True,
    )
    label_col = DRAFT_FIELDS.index("label")
    column_key_col = DRAFT_FIELDS.index("column_key")

    assert model.flags(model.index(0, label_col)) & Qt.ItemIsEditable
    assert not (model.flags(model.index(0, column_key_col)) & Qt.ItemIsEditable)
    assert model.setData(model.index(0, label_col), "Cooling Capacity", Qt.EditRole)
    assert not model.setData(model.index(0, column_key_col), "cooling_capacity", Qt.EditRole)
    assert accepted == [(state.draft_row_identities[0], "label", "Cooling Capacity")]


def test_data_definition_panel_builds_editable_draft_workflow_and_reset():
    app = _app()
    panel = DataDefinitionPanel()
    try:
        app.processEvents()
        label_col = DRAFT_FIELDS.index("label")
        row_index = panel._state.draft_row_identities.index(("schema_row", "idu"))

        assert panel.draft_table.editTriggers() != QAbstractItemView.NoEditTriggers
        assert panel.draft_table.model().flags(
            panel.draft_table.model().index(0, label_col)
        ) & Qt.ItemIsEditable
        assert panel.draft_table.model().setData(
            panel.draft_table.model().index(row_index, label_col),
            "Indoor Unit",
            Qt.EditRole,
        )
        app.processEvents()
        assert panel.draft_table.model().is_changed_cell(row_index, label_col)
        assert panel.save_plan_table.model().cell_value(0, 1) == "planned"

        panel.reset_action.trigger()
        app.processEvents()

        assert not panel.draft_table.model().is_changed_cell(row_index, label_col)
        assert panel.save_plan_table.model().cell_value(0, 1) == "no_op"
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()
