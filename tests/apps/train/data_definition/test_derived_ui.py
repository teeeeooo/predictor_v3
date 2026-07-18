"""Offscreen restricted Derived authoring UI tests."""

import os

from PySide6.QtWidgets import QApplication, QDialog

from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.data_definition.derived_dialogs import DerivedDefinitionDialog
from apps.train.ui.data_definition.derived_actions import project_derived_operand_options
from apps.train.ui.data_definition_panel import DataDefinitionPanel
from core.data_definition import AddDerivedIntent
from core.data_definition.contract import bootstrap_manifest


def _app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _panel(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    repository.publish(bootstrap_manifest())
    return DataDefinitionPanel(controller=DataDefinitionController(
        DataDefinitionService(generation_repository=repository)
    ))


def test_derived_menu_selection_and_manual_move_policy(tmp_path):
    app = _app()
    panel = _panel(tmp_path)
    derived = next(
        identity for identity in panel._state.draft_row_identities
        if identity[0] == "derived_policy"
    )
    row = panel.inventory_table.model().row_for_identity(derived)
    panel.inventory_table.selectRow(row)
    app.processEvents()
    try:
        assert panel.task_header.add_derived_action.text() == "Derived Feature"
        assert panel.edit_button.isEnabled()
        assert panel.rename_action.text() == "Rename Derived"
        assert not panel.move_predict_up_action.isEnabled()
        assert not panel.move_ml_down_action.isEnabled()
        assert panel._selected_values()["operation"] == "safe_ratio"
        assert panel._selected_values()["zero_denominator_policy"] == "constant"
    finally:
        panel.close()


def test_add_dialog_collects_only_canonical_candidates_and_defaults_inactive(tmp_path):
    app = _app()
    panel = _panel(tmp_path)
    captured = []
    dialog = DerivedDefinitionDialog(
        lambda intent: (captured.append(intent) is None, ""),
        project_derived_operand_options(panel._state),
        parent=panel,
    )
    try:
        dialog.ml_name.setText("Dialog_ratio")
        dialog.numerator.setCurrentIndex(1)
        dialog.denominator.setCurrentIndex(2)
        dialog.zero_value.clear()
        dialog._accept_intent()
        app.processEvents()
        assert dialog.result() == QDialog.Accepted
        assert len(captured) == 1 and isinstance(captured[0], AddDerivedIntent)
        assert captured[0].zero_denominator_policy == "constant"
        assert captured[0].zero_value == ""
        assert not captured[0].active
        assert captured[0].numerator_identity.startswith("ufm_")
    finally:
        dialog.close()
        panel.close()
