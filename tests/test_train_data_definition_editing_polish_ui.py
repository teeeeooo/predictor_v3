"""Slice 3E keyboard, focus, accessibility, and compact-layout guards."""

from __future__ import annotations

import os
import shutil

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableView,
)

from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.controllers.data_definition_interaction import (
    project_data_definition_interaction,
)
from apps.train.controllers.data_definition_presentation import (
    project_data_definition_inventory,
)
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.data_definition_add_dialog import DataDefinitionAddDialog
from apps.train.ui.data_definition_edit_dialog import DataDefinitionEditDialog
from apps.train.ui.data_definition_panel import DataDefinitionPanel
from core.data_definition import AddDefinitionIntent, EditDefinitionIntent
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _controller(tmp_path) -> DataDefinitionController:  # noqa: ANN001
    schema_path = tmp_path / "schema.csv"
    shutil.copyfile(DEFAULT_SCHEMA_PATH, schema_path)
    return DataDefinitionController(DataDefinitionService(schema_path=schema_path))


class _CountingController(DataDefinitionController):
    def __init__(self, service: DataDefinitionService) -> None:
        super().__init__(service)
        self.save_calls = 0

    def save_schema(self):  # noqa: ANN201
        self.save_calls += 1
        return super().save_schema()


def _counting_controller(tmp_path):  # noqa: ANN001, ANN201
    schema_path = tmp_path / "schema.csv"
    shutil.copyfile(DEFAULT_SCHEMA_PATH, schema_path)
    return _CountingController(DataDefinitionService(schema_path=schema_path))


def test_qt_free_action_copy_distinguishes_clean_dirty_blocked_and_retry(tmp_path):
    controller = _controller(tmp_path)
    clean = controller.refresh()
    clean_inventory = project_data_definition_inventory(clean)
    clean_actions = project_data_definition_interaction(clean, clean_inventory)
    assert not clean_actions.save.enabled
    assert clean_actions.save.reason == "No unsaved schema changes."

    dirty = controller.edit_definition(
        EditDefinitionIntent(("schema_row", "idu"), (("label", "Indoor Unit"),))
    )
    dirty_actions = project_data_definition_interaction(
        dirty,
        project_data_definition_inventory(dirty, selected_identity=("schema_row", "idu")),
    )
    assert dirty_actions.save.enabled
    assert dirty_actions.save.reason == "Save schema changes."

    blocked = controller.edit_definition(EditDefinitionIntent(
        ("schema_row", "cooling_capa"),
        (("ml_name", "Cooling Capacity Renamed"),),
    ))
    blocked_actions = project_data_definition_interaction(
        blocked,
        project_data_definition_inventory(
            blocked,
            selected_identity=("schema_row", "cooling_capa"),
        ),
    )
    assert not blocked_actions.save.enabled
    assert "compatibility blockers" in blocked_actions.save.reason
    assert blocked_actions.review_blockers.enabled


def test_keyboard_search_selection_no_match_and_deterministic_recovery(tmp_path):
    app = _app()
    panel = DataDefinitionPanel(controller=_controller(tmp_path))
    panel.resize(1100, 760)
    panel.show()
    app.processEvents()
    panel._behavior.focus_search()
    QTest.keyClicks(panel.search_input, "volume")
    QTest.keyClick(panel.search_input, Qt.Key_Return)
    app.processEvents()

    assert panel.inventory_table.hasFocus()
    first = panel._selected_identity
    QTest.keyClick(panel.inventory_table, Qt.Key_Down)
    app.processEvents()
    assert panel._selected_identity != first
    preferred = panel._selected_identity
    assert preferred is not None
    assert panel.inventory_table.model().row_for_identity(preferred) is not None

    panel.search_input.setText("definitely-no-match")
    app.processEvents()
    assert panel._selected_identity is None
    assert not panel.inventory_table.currentIndex().isValid()
    assert not panel.details_action.isEnabled()

    panel.search_input.setFocus()
    QTest.keyClick(panel.search_input, Qt.Key_Escape)
    app.processEvents()
    assert panel.search_input.text() == ""
    assert panel._selected_identity == preferred
    assert panel.search_input.hasFocus()
    panel.close()


def test_dialog_invalid_focus_correction_apply_and_escape_cancel(tmp_path):
    app = _app()
    panel = DataDefinitionPanel(controller=_controller(tmp_path))
    panel.show()
    app.processEvents()
    before_rows = panel._state.draft_rows

    cancelled = DataDefinitionAddDialog(panel._apply_add_intent, parent=panel)
    cancelled.show()
    app.processEvents()
    QTest.keyClicks(cancelled.label_input, "Cancelled Definition")
    QTest.keyClick(cancelled, Qt.Key_Escape)
    app.processEvents()
    assert cancelled.result() == QDialog.Rejected
    assert panel._state.draft_rows == before_rows

    dialog = DataDefinitionAddDialog(panel._apply_add_intent, parent=panel)
    dialog.show()
    app.processEvents()
    dialog.label_input.setText("Keyboard Definition")
    dialog.key_input.setText("cooling_capa")
    QTest.mouseClick(dialog.apply_button, Qt.LeftButton)
    app.processEvents()
    assert dialog.isVisible()
    assert dialog.error_label.hasFocus()
    assert dialog.error_label.accessibleDescription() == dialog.error_label.text()

    dialog.key_input.setText("keyboard_definition")
    QTest.mouseClick(dialog.apply_button, Qt.LeftButton)
    app.processEvents()
    assert dialog.result() == QDialog.Accepted
    assert panel._selected_identity[1].startswith("ufm_feature_")
    assert panel._selected_values()["column_key"] == "keyboard_definition"
    assert panel.inventory_table.model().row_for_identity(panel._selected_identity) is not None
    panel.close()


def test_edit_dialog_rejection_keeps_values_then_applies_and_keeps_selection(tmp_path):
    app = _app()
    panel = DataDefinitionPanel(controller=_controller(tmp_path))
    panel.show()
    identity = ("schema_row", "id_volume")
    panel._selected_identity = identity
    panel._apply_inventory()
    values = panel._selected_values()
    assert values is not None
    dialog = DataDefinitionEditDialog(identity, values, panel._apply_edit_intent, panel)
    dialog.show()
    app.processEvents()
    assert dialog.label_input.hasFocus()

    dialog.label_input.setText("Indoor Volume")
    dialog.attribute_input.clear()
    QTest.mouseClick(dialog.apply_button, Qt.LeftButton)
    app.processEvents()
    assert dialog.isVisible()
    assert dialog.error_label.hasFocus()
    assert dialog.label_input.text() == "Indoor Volume"
    assert dialog.attribute_input.text() == ""

    dialog.attribute_input.setText("ID Volume")
    QTest.mouseClick(dialog.apply_button, Qt.LeftButton)
    app.processEvents()
    assert dialog.result() == QDialog.Accepted
    assert panel._selected_identity == identity
    row = panel.inventory_table.model().row_for_identity(identity)
    assert row is not None
    assert panel.inventory_table.model().cell_value(row, 0) == "Indoor Volume"
    panel.close()


def test_standard_save_shortcut_writes_only_when_enabled_and_restores_focus(tmp_path):
    app = _app()
    controller = _counting_controller(tmp_path)
    panel = DataDefinitionPanel(controller=controller)
    panel.show()
    app.processEvents()

    panel.inventory_table.setFocus()
    QTest.keySequence(panel.inventory_table, QKeySequence(QKeySequence.StandardKey.Save))
    app.processEvents()
    assert controller.save_calls == 0

    accepted, _message = panel._apply_add_intent(AddDefinitionIntent(
        "mapping_attribute",
        "Keyboard Mapping Attribute",
        "keyboard_mapping_attribute",
        "number",
        mapping_entity="idu",
        mapping_attribute="Keyboard Mapping Attribute",
        trigger_column="idu",
    ))
    assert accepted and panel.save_button.isEnabled()
    QTest.keySequence(panel.inventory_table, QKeySequence(QKeySequence.StandardKey.Save))
    app.processEvents()
    assert controller.save_calls == 1
    assert not panel._state.draft_changed
    assert panel._selected_identity == ("schema_row", "keyboard_mapping_attribute")
    assert panel.inventory_table.hasFocus()

    panel._apply_edit_intent(EditDefinitionIntent(
        ("schema_row", "cooling_capa"),
        (("ml_name", "Cooling Capacity Renamed"),),
    ))
    assert not panel.save_button.isEnabled()
    QTest.keySequence(panel.inventory_table, QKeySequence(QKeySequence.StandardKey.Save))
    app.processEvents()
    assert controller.save_calls == 1
    panel.review_blockers_button.click()
    app.processEvents()
    assert panel.impact_view.save_label.hasFocus()
    panel.reset_action.trigger()
    app.processEvents()
    assert not panel._state.draft_changed
    assert panel._selected_identity == ("schema_row", "cooling_capa")
    assert panel.inventory_table.hasFocus()
    panel.close()


def test_accessible_names_label_relations_and_compact_actions_remain_visible(tmp_path):
    app = _app()
    panel = DataDefinitionPanel(controller=_controller(tmp_path))
    panel.resize(900, 640)
    panel.show()
    app.processEvents()
    assert (panel.width(), panel.height()) == (900, 640)
    assert panel.inventory_table.horizontalScrollBar().maximum() == 0

    interactive_types = (QPushButton, QComboBox, QLineEdit, QTableView)
    interactive = [
        widget
        for widget_type in interactive_types
        for widget in panel.findChildren(widget_type)
        if widget.isVisible()
    ]
    assert interactive
    assert all(widget.accessibleName().strip() for widget in interactive)
    action_names = [
        button.accessibleName()
        for button in panel.findChildren(QPushButton)
        if button.isVisible()
    ]
    assert len(action_names) == len(set(action_names))
    for button in (
        panel.add_definition_button,
        panel.edit_button,
        panel.save_button,
    ):
        assert button.isVisible()
        assert panel.rect().intersects(button.geometry())
        assert button.geometry().width() > 0 and button.geometry().height() > 0
        assert [action.text() for action in panel.task_header.add_menu.actions()] == [
            "Manual Predict input",
            "Mapping-backed Predict input",
            "Data Mapping attribute",
            "Predict-only Feature",
            "ML-only Feature",
            "Helper / Hidden Feature",
        ]
    assert not panel.status_label.wordWrap()

    add_dialog = DataDefinitionAddDialog(panel._apply_add_intent, parent=panel)
    for field in (
        add_dialog.label_input,
        add_dialog.key_input,
        add_dialog.data_type_combo,
        add_dialog.required_checkbox,
        add_dialog.notes_input,
    ):
        label = add_dialog.form.labelForField(field)
        assert isinstance(label, QLabel)
        assert label.buddy() is field

    identity = ("schema_row", "idu")
    panel._selected_identity = identity
    panel._apply_inventory()
    values = panel._selected_values()
    assert values is not None
    edit_dialog = DataDefinitionEditDialog(identity, values, panel._apply_edit_intent, panel)
    edit_dialog.resize(560, 440)
    edit_dialog.show()
    app.processEvents()
    assert edit_dialog.apply_button.isVisible()
    assert edit_dialog.rect().intersects(edit_dialog.apply_button.geometry())
    assert edit_dialog.apply_button.geometry().height() > 0
    edit_dialog.close()
    add_dialog.close()
    panel.close()
