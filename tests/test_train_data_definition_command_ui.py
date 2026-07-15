"""Offscreen Qt controlled Add/Edit workflow tests."""

from __future__ import annotations

import os
import shutil

from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog

from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.data_definition_add_dialog import DataDefinitionAddDialog
from apps.train.ui.data_definition_edit_dialog import DataDefinitionEditDialog
from apps.train.ui.data_definition_panel import DataDefinitionPanel
import apps.train.ui.data_definition_panel as data_definition_panel_module
from core.data_definition import AddDefinitionIntent, EditDefinitionIntent
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_add_dialog_keeps_invalid_command_open_and_cancel_is_noop(tmp_path):
    app = _app()
    controller = _controller(tmp_path)
    before = controller.refresh()
    applied = []

    def apply(intent):  # noqa: ANN001, ANN202
        applied.append(intent)
        state = controller.add_definition(intent)
        return state.last_action_ok, state.message

    dialog = DataDefinitionAddDialog(apply)
    try:
        dialog.label_input.setText("Duplicate")
        dialog.key_input.setText("cooling_capa")
        dialog.apply_button.click()
        app.processEvents()

        assert dialog.result() != QDialog.Accepted
        assert "already exists" in dialog.error_label.text()
        assert len(applied) == 1
        after_invalid = controller.edit_cell(("schema_row", "idu"), "label", "실내기")
        assert after_invalid.draft_row_identities == before.draft_row_identities
        assert not after_invalid.draft_changed

        dialog.reject()
        assert len(applied) == 1
    finally:
        dialog.deleteLater()
        app.processEvents()


def test_add_dialog_and_panel_select_complete_new_definition(tmp_path):
    app = _app()
    panel = DataDefinitionPanel(controller=_controller(tmp_path))
    dialog = DataDefinitionAddDialog(
        panel._apply_add_intent,
        initial_intent="manual_predict",
        parent=panel,
    )
    try:
        dialog.label_input.setText("Fan Diameter")
        dialog.key_input.setText("Fan Diameter")
        dialog.data_type_combo.setCurrentIndex(dialog.data_type_combo.findData("number"))
        dialog.apply_button.click()
        app.processEvents()

        assert dialog.result() == QDialog.Accepted
        assert panel._selected_identity == ("schema_row", "fan_diameter")
        assert panel.inventory_table.model().row_for_identity(panel._selected_identity) is not None
        assert panel.detail_state_label.text().startswith("Fan Diameter")
        assert panel.save_button.isEnabled()
        assert panel._state.draft_changed
        raw_index = panel._state.draft_row_identities.index(panel._selected_identity)
        assert panel.draft_table.model().cell_value(raw_index, 2) == "fan_diameter"
        assert dialog.intent_combo.isHidden()
    finally:
        dialog.deleteLater()
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_unified_add_menu_routes_existing_modes_and_cancel_does_not_mutate(
    tmp_path,
    monkeypatch,
):
    app = _app()
    panel = DataDefinitionPanel(controller=_controller(tmp_path))
    before = panel._state.draft_rows
    opened: list[tuple[str | None, bool]] = []

    class _CancelledDialog:
        def __init__(
            self,
            _on_apply,
            *,
            standalone_mapping_attribute=False,
            initial_intent=None,
            parent=None,
        ) -> None:
            del parent
            opened.append((initial_intent, standalone_mapping_attribute))

        def exec(self) -> int:
            return QDialog.Rejected

    monkeypatch.setattr(
        data_definition_panel_module,
        "DataDefinitionAddDialog",
        _CancelledDialog,
    )
    try:
        panel.add_manual_action.trigger()
        panel.add_mapping_predict_action.trigger()
        panel.add_mapping_attribute_action.trigger()
        app.processEvents()
        assert opened == [
            ("manual_predict", False),
            ("mapping_predict", False),
            (None, True),
        ]
        assert panel._state.draft_rows == before
        assert not panel._state.draft_changed
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_unified_add_menu_drives_valid_manual_submit_and_mapping_attribute_cancel(
    tmp_path,
):
    app = _app()
    panel = DataDefinitionPanel(controller=_controller(tmp_path))
    panel.show()
    app.processEvents()

    def submit_manual() -> None:
        dialog = app.activeModalWidget()
        assert isinstance(dialog, DataDefinitionAddDialog)
        assert dialog.intent_combo.currentData() == "manual_predict"
        assert dialog.intent_combo.isHidden()
        dialog.label_input.setText("Menu Fan Diameter")
        dialog.key_input.setText("menu_fan_diameter")
        dialog.apply_button.click()

    QTimer.singleShot(0, submit_manual)
    panel.add_manual_action.trigger()
    app.processEvents()
    app.processEvents()
    app.processEvents()
    QTest.qWait(5)

    assert panel._selected_identity == ("schema_row", "menu_fan_diameter")
    assert panel._state.draft_changed
    focused = panel.window().focusWidget()
    assert focused is panel.inventory_table, (
        type(focused).__name__ if focused is not None else "none",
        focused.accessibleName() if focused is not None else "",
    )

    panel._reset_draft()
    app.processEvents()
    before = panel._state.draft_rows

    def cancel_attribute() -> None:
        dialog = app.activeModalWidget()
        assert isinstance(dialog, DataDefinitionAddDialog)
        assert dialog.windowTitle() == "Add Mapping Attribute"
        dialog.reject()

    QTimer.singleShot(0, cancel_attribute)
    panel.add_mapping_attribute_action.trigger()
    app.processEvents()
    app.processEvents()
    app.processEvents()
    QTest.qWait(5)

    assert panel._state.draft_rows == before
    assert not panel._state.draft_changed
    focused = panel.window().focusWidget()
    assert focused is panel.add_definition_button, (
        type(focused).__name__ if focused is not None else "none",
        focused.accessibleName() if focused is not None else "",
    )
    panel.close()


def test_standalone_mapping_dialog_projects_hidden_requirement(tmp_path):
    app = _app()
    panel = DataDefinitionPanel(controller=_controller(tmp_path))
    dialog = DataDefinitionAddDialog(
        panel._apply_add_intent,
        standalone_mapping_attribute=True,
        parent=panel,
    )
    try:
        dialog.label_input.setText("Cond Inner Area")
        dialog.key_input.setText("cond_inner_area")
        dialog.mapping_combo.setCurrentIndex(
            dialog.mapping_combo.findData("cond_specs_lookup")
        )
        dialog.attribute_input.setText("Cond Inner Area")
        dialog.apply_button.click()
        app.processEvents()

        assert dialog.result() == QDialog.Accepted
        identity = ("schema_row", "cond_inner_area")
        index = panel._state.draft_row_identities.index(identity)
        values = {cell.field_name: cell.value for cell in panel._state.draft_rows[index]}
        assert values["visible"] == "false"
        assert values["model_input_enabled"] == "false"
        assert any(row[0] == "cond_inner_area" for row in panel._state.mapping_requirement_rows)
    finally:
        dialog.deleteLater()
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_edit_dialog_prefills_and_applies_one_atomic_metadata_edit(tmp_path):
    app = _app()
    panel = DataDefinitionPanel(controller=_controller(tmp_path))
    identity = ("schema_row", "idu")
    panel._selected_identity = identity
    panel._apply_inventory()
    values = panel._selected_values()
    assert values is not None
    dialog = DataDefinitionEditDialog(identity, values, panel._apply_edit_intent, panel)
    try:
        assert dialog.label_input.text() == "실내기"
        dialog.label_input.setText("Indoor Unit")
        dialog.notes_input.setText("Controlled edit")
        apply_button = next(
            item for item in dialog.findChildren(type(panel.save_button))
            if item.accessibleName() == "Apply Edit Definition to Draft"
        )
        apply_button.click()
        app.processEvents()

        assert dialog.result() == QDialog.Accepted
        index = panel._state.draft_row_identities.index(identity)
        changed = {
            cell.field_name: cell.value
            for cell in panel._state.draft_rows[index]
            if cell.changed
        }
        assert changed == {"label": "Indoor Unit", "notes": "Controlled edit"}
        assert panel._selected_identity == identity
        assert panel.save_button.isEnabled()
    finally:
        dialog.deleteLater()
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_edit_dialog_projects_role_aware_complete_shape_options(tmp_path):
    app = _app()
    panel = DataDefinitionPanel(controller=_controller(tmp_path))
    identity = ("schema_row", "id_volume")
    panel._selected_identity = identity
    panel._apply_inventory()
    values = panel._selected_values()
    assert values is not None
    dialog = DataDefinitionEditDialog(identity, values, panel._apply_edit_intent, panel)
    try:
        assert dialog.value_source_combo.count() == 1
        assert dialog.value_source_combo.currentData() == "mapping_lookup"
        assert dialog.value_source_combo.findData("manual") == -1
        assert dialog.editor_combo.count() == 1
        assert dialog.editor_combo.currentData() == "readonly"
        assert set(
            dialog.data_type_combo.itemData(index)
            for index in range(dialog.data_type_combo.count())
        ) == {"number", "string"}
        assert dialog.readonly_checkbox.isChecked()
        assert not dialog.readonly_checkbox.isEnabled()
        assert dialog.one_hot_input.isEnabled() is False
    finally:
        dialog.reject()
        dialog.deleteLater()
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_invalid_controlled_edit_keeps_selection_and_draft_unchanged(tmp_path):
    app = _app()
    panel = DataDefinitionPanel(controller=_controller(tmp_path))
    identity = ("schema_row", "id_volume")
    panel._selected_identity = identity
    panel._apply_inventory()
    before_rows = panel._state.draft_rows
    before_changes = panel._state.draft_change_rows
    try:
        accepted, message = panel._apply_edit_intent(
            EditDefinitionIntent(identity, (("value_source", "manual"),))
        )
        app.processEvents()

        assert not accepted
        assert "requires mapping lookup" in message
        assert panel._selected_identity == identity
        assert panel._state.draft_rows == before_rows
        assert panel._state.draft_change_rows == before_changes
        assert not panel._state.draft_changed
        assert "role_value_source_unsupported" in {
            row[0] for row in panel._state.command_issue_rows
        }
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_controller_reset_removes_controlled_add_and_edit_results(tmp_path):
    controller = _controller(tmp_path)
    initial = controller.refresh()
    added = controller.add_definition(
        AddDefinitionIntent("manual_predict", "Fan Diameter", "fan_diameter", "number")
    )
    edited = controller.edit_definition(
        EditDefinitionIntent(("schema_row", "idu"), (("label", "Indoor Unit"),))
    )

    reset = controller.reset_draft()

    assert added.draft_changed and edited.draft_changed
    assert reset.draft_row_identities == initial.draft_row_identities
    assert ("schema_row", "fan_diameter") not in reset.draft_row_identities
    idu_index = reset.draft_row_identities.index(("schema_row", "idu"))
    assert next(
        cell.value for cell in reset.draft_rows[idu_index] if cell.field_name == "label"
    ) == "실내기"
    assert not reset.draft_changed


def _controller(tmp_path) -> DataDefinitionController:
    schema_path = tmp_path / "schema.csv"
    shutil.copyfile(DEFAULT_SCHEMA_PATH, schema_path)
    return DataDefinitionController(DataDefinitionService(schema_path=schema_path))
