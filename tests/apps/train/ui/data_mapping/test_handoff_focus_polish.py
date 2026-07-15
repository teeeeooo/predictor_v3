"""Slice 3E keyboard/focus guards for saved Mapping Requirement handoff."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from apps.train.application.data_mapping import DataMappingNavigationRequest
from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_mapping_service import (
    DataDefinitionMappingRequirementProvider,
    DataMappingService,
    RuntimeMappingCatalogProvider,
)
from apps.train.ui.data_mapping_panel import DataMappingPanel
from core.data_definition import MappingRequirement
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH

RUNTIME_FIXTURE = Path("tests/fixtures/mapping/mapping_runtime_equivalent.json")


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _mapping_path(tmp_path) -> Path:  # noqa: ANN001
    path = tmp_path / "mapping.json"
    shutil.copyfile(RUNTIME_FIXTURE, path)
    return path


def test_ready_handoff_focuses_coverage_context_without_arbitrary_cell(tmp_path):
    app = _app()
    controller = DataMappingController(DataMappingService(
        RuntimeMappingCatalogProvider(str(_mapping_path(tmp_path))),
        DataDefinitionMappingRequirementProvider(DEFAULT_SCHEMA_PATH),
    ))
    panel = DataMappingPanel(controller=controller)
    panel.show()
    app.processEvents()
    panel.row_table.setCurrentIndex(panel.row_table.model().index(3, 1))

    result = panel.open_requirement(DataMappingNavigationRequest(
        definition_identity=("schema_row", "id_volume"),
        definition_column_key="id_volume",
        definition_label="Indoor Volume",
        mapping_entity="idu",
        mapping_attribute="ID Volume",
        resolved_group_key="idu",
        required=False,
        data_type="number",
    ))
    app.processEvents()

    assert result.status == "coverage_ready"
    assert panel._current_state.selected_group_key == "idu"
    assert panel.coverage_panel.selector.currentData() == "id_volume"
    assert panel.coverage_panel.selector.hasFocus()
    assert not panel.row_table.currentIndex().isValid()
    assert not panel.coverage_panel.go_button.isEnabled()
    assert "Coverage ready" in panel.coverage_panel.summary.text()
    panel.close()


class _RequirementProvider:
    def load_mapping_requirements(self):  # noqa: ANN201
        return (
            MappingRequirement(
                column_key="keyboard_attribute",
                ml_name="",
                mapping_entity="idu",
                mapping_attribute="Keyboard Attribute",
                trigger_column="idu",
                data_type="number",
                required=True,
            ),
        )


def test_incomplete_handoff_and_keyboard_go_focus_exact_unresolved_cell(tmp_path):
    app = _app()
    controller = DataMappingController(DataMappingService(
        RuntimeMappingCatalogProvider(str(_mapping_path(tmp_path))),
        _RequirementProvider(),
    ))
    panel = DataMappingPanel(controller=controller)
    panel.show()
    app.processEvents()
    request = DataMappingNavigationRequest(
        definition_identity=("schema_row", "keyboard_attribute"),
        definition_column_key="keyboard_attribute",
        definition_label="Keyboard Attribute",
        mapping_entity="idu",
        mapping_attribute="Keyboard Attribute",
        resolved_group_key="idu",
        required=True,
        data_type="number",
    )

    result = panel.open_requirement(request)
    app.processEvents()
    column = panel._current_state.value_headers.index("Keyboard Attribute")
    assert result.status == "opened_unresolved"
    assert panel.row_table.currentIndex() == panel.row_table.model().index(0, column)
    assert panel.row_table.hasFocus()

    assert panel.row_table.model().setData(
        panel.row_table.model().index(0, column),
        "2.5",
        Qt.EditRole,
    )
    QTest.qWait(20)
    app.processEvents()
    panel.coverage_panel.go_button.setFocus()
    QTest.keyClick(panel.coverage_panel.go_button, Qt.Key_Space)
    app.processEvents()
    assert panel.row_table.currentIndex() == panel.row_table.model().index(1, column)
    assert panel.row_table.hasFocus()

    before = panel.row_table.currentIndex()
    dirty_before = panel._current_state.dirty
    stale = panel.open_requirement(DataMappingNavigationRequest(
        definition_identity=("schema_row", "stale_attribute"),
        definition_column_key="stale_attribute",
        definition_label="Stale Attribute",
        mapping_entity="idu",
        mapping_attribute="Stale Attribute",
        resolved_group_key="idu",
        required=False,
        data_type="number",
    ))
    app.processEvents()
    assert stale.status == "requirement_not_saved"
    assert panel._current_state.dirty == dirty_before
    assert (
        panel.row_table.currentIndex().row(),
        panel.row_table.currentIndex().column(),
    ) == (before.row(), before.column())
    assert panel.coverage_panel.selector.hasFocus()
    panel.close()
