"""Offscreen group-centered One-hot authoring UI tests."""

import os

from PySide6.QtWidgets import QApplication, QAbstractItemView

from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.data_definition.one_hot.intent_dialogs import (
    OneHotCategoryIntentDialog,
    OneHotGroupIntentDialog,
)
from apps.train.ui.data_definition.one_hot.manager_dialog import OneHotManagerDialog
from apps.train.ui.data_definition_panel import DataDefinitionPanel
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.one_hot.model import VocabularyCategory, VocabularySnapshot


def _app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _controller(tmp_path, snapshots=()):
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    repository.publish(bootstrap_manifest())
    return DataDefinitionController(DataDefinitionService(
        generation_repository=repository,
        vocabulary_snapshots=snapshots,
    ))


def test_feature_manager_exposes_group_centered_one_hot_entry(tmp_path):
    _app()
    panel = DataDefinitionPanel(controller=_controller(tmp_path))
    try:
        assert panel.task_header.manage_one_hot_action.text() == "One-hot Group / Category"
        assert "group-centered" in panel.task_header.manage_one_hot_action.toolTip()
    finally:
        panel.close()


def test_manager_shows_existing_groups_categories_order_owner_and_drift(tmp_path):
    _app()
    controller = _controller(tmp_path)
    controller.refresh()
    dialog = OneHotManagerDialog(controller, lambda _state: None)
    try:
        assert dialog.group_choice.count() == 2
        assert dialog.table.rowCount() == 3
        assert [dialog.table.item(row, 1).text() for row in range(3)] == [
            "R410A", "R32", "R290"
        ]
        assert "Data Mapping owns" in dialog.group_details.text()
        assert "Category order changes only this group block" in dialog.group_details.text()
        assert dialog.table.editTriggers() == QAbstractItemView.NoEditTriggers
        assert any(button.text() == "Change source" for button in dialog.group_buttons)
        assert any(button.text() == "Move Up" for button in dialog.category_buttons)
    finally:
        dialog.close()


def test_external_mode_is_disabled_without_provider_and_mapping_value_is_read_only(tmp_path):
    _app()
    mapping = VocabularySnapshot(
        "mapping_backed", "ref_type", (VocabularyCategory("mapping:r32", "R32"),)
    )
    controller = _controller(tmp_path, (mapping,))
    controller.refresh()
    projection = controller.one_hot_authoring_projection()
    group_dialog = OneHotGroupIntentDialog(projection)
    category_dialog = OneHotCategoryIntentDialog(
        projection.groups[0], projection.vocabulary_snapshots
    )
    try:
        external_index = group_dialog.mode.findData("external")
        assert not group_dialog.mode.model().item(external_index).isEnabled()
        assert projection.external_disabled_reason
        assert not category_dialog.source_choice.isEditable()
        assert not category_dialog.source.isVisible()
        assert category_dialog.source_choice.itemText(0) == "R32"
    finally:
        group_dialog.close()
        category_dialog.close()
