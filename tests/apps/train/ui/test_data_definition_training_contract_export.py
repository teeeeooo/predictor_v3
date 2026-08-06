"""Offscreen UI coverage for saved-generation Training Contract exports."""

from __future__ import annotations

import csv
import os

from PySide6.QtWidgets import QApplication

from apps.common.runtime_generation.repository import DataDefinitionGenerationRepository
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.ui.data_definition_panel import DataDefinitionPanel
import apps.train.ui.data_definition.training_contract_export as export_ui
from core.data_definition import RenameDefinitionIntent
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _panel(tmp_path):  # noqa: ANN001, ANN202
    repository = DataDefinitionGenerationRepository(tmp_path / "definition-store")
    repository.publish(bootstrap_manifest())
    snapshot = repository.read_active()
    controller = DataDefinitionController(
        DataDefinitionService(generation_repository=repository)
    )
    controller.bind_runtime_generation(snapshot)
    panel = DataDefinitionPanel(controller=controller)
    return panel, controller, snapshot


def test_header_export_action_writes_saved_generation_and_reports_completion(
    tmp_path, monkeypatch
):
    app = _app()
    panel, _controller, snapshot = _panel(tmp_path)
    destination = tmp_path / "headers.csv"
    messages = []
    warnings = []
    monkeypatch.setattr(
        export_ui.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(destination), export_ui.CSV_FILTER),
    )
    monkeypatch.setattr(
        export_ui.QMessageBox, "information",
        lambda _parent, title, message: messages.append((title, message)),
    )
    monkeypatch.setattr(
        export_ui.QMessageBox, "warning",
        lambda _parent, title, message: warnings.append((title, message)),
    )

    try:
        panel.task_header.export_training_headers_action.trigger()
        app.processEvents()
        with destination.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.reader(stream))
        assert rows == [list(model_registry_snapshot(snapshot.manifest).training_headers)]
        assert not warnings
        assert messages[-1][0] == "Training Contract Export"
        assert snapshot.manifest.generation.generation_id in messages[-1][1]
        assert "saved Train generation" in (
            panel.task_header.export_training_headers_action.toolTip()
        )
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_dirty_draft_export_warns_that_saved_generation_excludes_draft(
    tmp_path, monkeypatch
):
    app = _app()
    panel, controller, snapshot = _panel(tmp_path)
    destination = tmp_path / "reference.csv"
    messages = []
    monkeypatch.setattr(
        export_ui.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(destination), export_ui.CSV_FILTER),
    )
    monkeypatch.setattr(
        export_ui.QMessageBox, "information",
        lambda _parent, title, message: messages.append((title, message)),
    )
    monkeypatch.setattr(export_ui.QMessageBox, "warning", lambda *_args: None)
    try:
        state = controller.rename_definition(RenameDefinitionIntent(
            ("schema_row", "cooling_capa"),
            ml_name="Cooling Capacity Draft",
        ))
        panel._apply_state(state)
        panel.task_header.export_definition_reference_action.trigger()
        app.processEvents()

        saved_notice = next(
            message for title, message in messages
            if title == "Saved Training Contract"
        )
        assert snapshot.manifest.generation.generation_id in saved_notice
        assert "Unsaved Data Definition draft changes are excluded" in saved_notice
        assert destination.is_file()
        assert controller.training_contract_export_context().draft_dirty
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()
