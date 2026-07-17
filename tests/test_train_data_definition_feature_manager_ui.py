"""Offscreen Basic Feature Manager command-flow and accessibility tests."""

from __future__ import annotations

import os

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QPushButton

from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.data_definition.command_preview_dialog import FeatureCommandPreviewDialog
from apps.train.ui.data_definition.feature_mutation_dialogs import (
    DuplicateFeatureDialog,
    RenameFeatureDialog,
)
from apps.train.ui.data_definition_add_dialog import DataDefinitionAddDialog
from apps.train.ui.data_definition_panel import DataDefinitionPanel
from core.data_definition import AddDefinitionIntent, RemoveDefinitionIntent, RenameDefinitionIntent
from core.data_definition.contract import bootstrap_manifest


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _panel(tmp_path):  # noqa: ANN001
    repository = DataDefinitionGenerationRepository(tmp_path / "definition-store")
    repository.publish(bootstrap_manifest())
    controller = DataDefinitionController(
        DataDefinitionService(generation_repository=repository)
    )
    return DataDefinitionPanel(controller=controller)


def _identity(panel, key):  # noqa: ANN001
    return next(
        identity
        for identity, cells in zip(
            panel._state.draft_row_identities,
            panel._state.draft_rows,
            strict=True,
        )
        if {cell.field_name: cell.value for cell in cells}["column_key"] == key
    )


def test_feature_manager_actions_remain_table_first_and_accessible(tmp_path):
    app = _app()
    panel = _panel(tmp_path)
    try:
        app.processEvents()
        assert panel.inventory_table.isVisible() is False  # panel itself is intentionally hidden
        assert panel.impact_preview_button.accessibleName() == "Preview selected Feature impact"
        assert panel.rename_action.statusTip() == "Manage the selected Basic Feature through controlled commands."
        assert panel.add_ml_only_action.toolTip() == "Add a hidden ordered ML input Feature"
        assert panel.move_predict_up_action.statusTip() == "Manage the selected Basic Feature through controlled commands."

        result_identity = _identity(panel, "cooling_power")
        result_row = panel._state.draft_row_identities.index(result_identity)
        panel.inventory_table.selectRow(result_row)
        app.processEvents()
        assert not panel.rename_action.isEnabled()
        assert "supported" in panel.rename_action.toolTip()
    finally:
        panel.close()


def test_rename_and_add_dialogs_collect_intent_without_exposing_identity_as_name(tmp_path):
    panel = _panel(tmp_path)
    identity = _identity(panel, "idu")
    values = panel._selected_values()
    rename = RenameFeatureDialog(identity, values, lambda _intent: (True, ""), panel)
    add = DataDefinitionAddDialog(lambda _intent: (True, ""), initial_intent="ml_only", parent=panel)
    try:
        rename.key_check.setChecked(True)
        rename.key_input.setText("indoor_unit")
        intent = rename.intent()
        assert intent.identity == identity
        assert intent.column_key == "indoor_unit"
        assert intent.label is None and intent.ml_name is None
        assert rename.key_check.accessibleName() == "Select Predict key for Rename"

        add.label_input.setText("Ambient Temperature")
        add.key_input.setText("ambient_temperature")
        add.ml_name_input.setText("Ambient Temperature")
        add_intent = add.intent()
        assert add_intent.kind == "ml_only"
        assert add_intent.model_input_enabled
        assert not add_intent.visible
        assert add_intent.ml_name == "Ambient Temperature"
    finally:
        rename.close()
        add.close()
        panel.close()


def test_duplicate_preview_flow_selects_new_stable_identity(tmp_path):
    app = _app()
    panel = _panel(tmp_path)
    panel.show()
    app.processEvents()
    original = _identity(panel, "idu")
    row = panel._state.draft_row_identities.index(original)
    panel.inventory_table.selectRow(row)
    app.processEvents()

    def complete_duplicate() -> None:
        dialog = app.activeModalWidget()
        assert isinstance(dialog, DuplicateFeatureDialog)
        dialog.label_input.setText("Indoor Unit Alternate")
        dialog.key_input.setText("idu_alternate")

        def accept_preview() -> None:
            preview = app.activeModalWidget()
            assert isinstance(preview, FeatureCommandPreviewDialog)
            assert preview.apply_button.accessibleName() == "Apply previewed command to Draft"
            preview.apply_button.click()

        QTimer.singleShot(0, accept_preview)
        dialog.findChildren(type(dialog.label_input))  # keep widgets alive for nested modal
        next(
            button for button in dialog.findChildren(QPushButton)
            if button.text() == "Preview and Duplicate"
        ).click()

    QTimer.singleShot(0, complete_duplicate)
    panel.duplicate_action.trigger()
    app.processEvents()

    try:
        assert panel._selected_values()["column_key"] == "idu_alternate"
        assert panel._selected_identity != original
        assert panel._selected_identity[1].startswith("ufm_feature_")
        assert panel._state.draft_changed
    finally:
        panel.close()


def test_blocked_rename_preserves_selection_and_remove_moves_to_neighbor(tmp_path):
    app = _app()
    panel = _panel(tmp_path)
    cooling = _identity(panel, "cooling_capa")
    cooling_row = panel._state.draft_row_identities.index(cooling)
    panel.inventory_table.selectRow(cooling_row)
    app.processEvents()
    accepted, _message = panel._feature_actions._preview_and_apply(
        RenameDefinitionIntent(cooling, ml_name="Cooling Capacity Renamed")
    )

    assert not accepted
    assert panel._selected_identity == cooling
    assert not panel._state.draft_changed
    assert panel._state.command_issue_rows

    first = panel._controller.add_definition(
        AddDefinitionIntent("predict_only", "First", "first_neighbor", "string")
    )
    panel._apply_state(first)
    first_identity = first.focus_identity
    second = panel._controller.add_definition(
        AddDefinitionIntent("predict_only", "Second", "second_neighbor", "string")
    )
    panel._apply_state(second)
    second_identity = second.focus_identity
    first_row = panel._state.draft_row_identities.index(first_identity)
    panel.inventory_table.selectRow(first_row)
    app.processEvents()

    QTimer.singleShot(0, lambda: app.activeModalWidget().accept())
    panel._feature_actions._preview_and_apply(RemoveDefinitionIntent(first_identity))
    app.processEvents()

    try:
        assert first_identity not in panel._state.draft_row_identities
        assert panel._selected_identity == second_identity
    finally:
        panel.close()
