"""Slice 2C Data Mapping validation, dirty, Save, and Reload workflow tests."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_mapping_service import DataMappingService, RuntimeMappingCatalogProvider
from apps.train.ui.data_mapping_panel import DataMappingPanel
from core.data_definition.model import MappingRequirement
from core.mapping.editor_persistence import MappingEditorSaveResult

RUNTIME_FIXTURE = Path("tests/fixtures/mapping/mapping_runtime_equivalent.json")


class RequirementProvider:
    def load_mapping_requirements(self):
        return (
            MappingRequirement(
                column_key="cond_inner_area",
                ml_name="Cond_Inner_Area",
                mapping_entity="odu_cond_specs",
                mapping_attribute="Cond Inner Area",
                trigger_column="odu",
                data_type="number",
                required=False,
            ),
        )


class FailingReloadProvider(RuntimeMappingCatalogProvider):
    def __init__(self, mapping_file: str) -> None:
        super().__init__(mapping_file)
        self.loads = 0
        self.fail = False

    def load_draft(self):
        self.loads += 1
        if self.fail:
            raise OSError("reload unavailable")
        return super().load_draft()


def _copy_mapping(tmp_path: Path) -> Path:
    destination = tmp_path / "runtime_mapping.json"
    shutil.copy2(RUNTIME_FIXTURE, destination)
    return destination


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def _cleanup_widgets():
    yield
    app = QApplication.instance()
    if app is not None:
        for widget in QApplication.topLevelWidgets():
            widget.close()
            widget.deleteLater()
        app.processEvents()


def test_dirty_is_actual_baseline_diff_for_edit_back_add_delete_and_undo(tmp_path):
    service = DataMappingService(RuntimeMappingCatalogProvider(str(_copy_mapping(tmp_path))))
    baseline = service.load_snapshot()
    original = baseline.draft.group("idu").rows[0].value_for("Size")

    assert service.edit_cell("idu", 0, "Size", "changed").dirty
    assert not service.edit_cell("idu", 0, "Size", original).dirty

    initial_rows = len(service.current_snapshot().draft.group("idu").rows)
    assert service.add_row("idu").dirty
    assert not service.delete_row("idu", initial_rows).dirty

    service.edit_cell("idu", 0, "Size", "changed-again")
    snapshot, result = service.undo()
    assert result.applied == 1
    assert not snapshot.dirty


def test_save_success_sets_baseline_and_failure_preserves_it(tmp_path, monkeypatch):
    mapping_file = _copy_mapping(tmp_path)
    service = DataMappingService(RuntimeMappingCatalogProvider(str(mapping_file)))
    original = service.load_snapshot().draft.group("idu").rows[0].value_for("Size")
    service.edit_cell("idu", 0, "Size", "saved-value")

    result, saved = service.save_mapping()
    assert result.success
    assert result.path == mapping_file
    assert result.backup_path is not None and result.backup_path.is_file()
    assert not saved.dirty

    service.edit_cell("idu", 0, "Size", "failed-value")
    monkeypatch.setattr(
        "apps.train.services.data_mapping_service.save_mapping_editor_draft",
        lambda draft, path: MappingEditorSaveResult(False, Path(path), message="disk denied"),
    )
    failed, snapshot = service.save_mapping()
    assert not failed.success
    assert snapshot.dirty
    assert service.edit_cell("idu", 0, "Size", "saved-value").dirty is False
    assert json.loads(mapping_file.read_text(encoding="utf-8"))["idu"]["MOT1"]["Size"] == "saved-value"
    assert original != "saved-value"


def test_reload_success_replaces_baseline_and_failure_preserves_draft_and_baseline(tmp_path):
    mapping_file = _copy_mapping(tmp_path)
    provider = FailingReloadProvider(str(mapping_file))
    controller = DataMappingController(DataMappingService(provider))
    controller.refresh("idu")
    controller.edit_cell("idu", 0, "Size", "draft-value")

    provider.fail = True
    failed = controller.reload("idu")
    assert failed.dirty
    assert failed.values[0].values[2] == "draft-value"
    assert failed.validation_rows[-1].code == "reload_failed"
    assert failed.issue_targets[-1] is None

    provider.fail = False
    reloaded = controller.reload("idu")
    assert not reloaded.dirty
    assert reloaded.values[0].values[2] != "draft-value"
    assert reloaded.message == "Reloaded from source."
    assert provider.loads == 3


def test_validation_issue_uses_structured_target_and_panel_focuses_exact_cell(tmp_path):
    _app()
    controller = DataMappingController(
        DataMappingService(RuntimeMappingCatalogProvider(str(_copy_mapping(tmp_path))))
    )
    invalid = controller.edit_cell("idu", 1, "ID Volume", "not-a-number")
    issue_index = next(
        index for index, issue in enumerate(invalid.validation_rows) if issue.code == "invalid_number"
    )
    target = invalid.issue_targets[issue_index]
    assert target is not None
    assert (target.group_key, target.row_index, target.column_index) == ("idu", 1, 1)
    assert (1, 1) in invalid.invalid_cells

    panel = DataMappingPanel(controller=controller)
    panel.show()
    panel._apply_state(invalid)
    issue_cell = panel.validation_table.model().index(issue_index, 0)
    panel.validation_table.clicked.emit(issue_cell)
    QApplication.processEvents()

    assert panel._selected_group_key == "idu"
    assert panel.row_table.currentIndex() == panel.row_table.model().index(1, 1)
    assert panel.row_table.hasFocus()
    assert panel.row_table.model().data(
        panel.row_table.model().index(1, 1), Qt.BackgroundRole
    ) is not None

    resolved = controller.edit_cell("idu", 1, "ID Volume", "60")
    assert not any(issue.code == "invalid_number" for issue in resolved.validation_rows)


def test_source_operation_issue_does_not_move_primary_selection(tmp_path):
    _app()
    mapping_file = _copy_mapping(tmp_path)
    provider = FailingReloadProvider(str(mapping_file))
    controller = DataMappingController(DataMappingService(provider))
    panel = DataMappingPanel(controller=controller)
    panel._select_row(2)
    before = panel.row_table.currentIndex()

    provider.fail = True
    state = controller.reload("idu")
    panel._apply_state(state)
    issue_row = len(state.validation_rows) - 1
    panel.validation_table.clicked.emit(panel.validation_table.model().index(issue_row, 0))

    assert state.issue_targets[issue_row] is None
    assert panel.row_table.currentIndex().row() == before.row()


def test_export_menu_separates_review_snapshot_and_exchange_package(tmp_path):
    _app()
    controller = DataMappingController(
        DataMappingService(RuntimeMappingCatalogProvider(str(_copy_mapping(tmp_path))))
    )
    panel = DataMappingPanel(controller=controller)
    export_button = panel.toolbar.buttons["export_csv_v2"]
    actions = panel.toolbar._export_menu_actions

    assert export_button.text() == "Export"
    assert actions["exchange"].text() == "Mapping Exchange Package…"
    assert actions["review"].text() == "Review Snapshot…"
    assert actions["exchange"].isEnabled()
    assert actions["review"].isEnabled()

    invalid = controller.edit_cell("idu", 0, "ID Volume", "not-a-number")
    panel._apply_state(invalid)

    assert not actions["exchange"].isEnabled()
    assert actions["review"].isEnabled()


def test_refresh_preserves_baseline_undo_and_selection_without_provider_reload(tmp_path):
    _app()
    mapping_file = _copy_mapping(tmp_path)
    provider = FailingReloadProvider(str(mapping_file))
    service = DataMappingService(provider)
    controller = DataMappingController(service)
    panel = DataMappingPanel(controller=controller)
    panel._select_row(3)
    controller.edit_cell("idu", 3, "Size", "temporary")
    loads = provider.loads

    panel.refresh()
    assert provider.loads == loads
    assert panel.row_table.currentIndex().row() == 3
    assert panel._dirty
    undone = controller.undo("idu")
    assert not undone.dirty


def test_save_reload_round_trip_preserves_dynamic_pfc_and_hidden_payload(tmp_path):
    mapping_file = _copy_mapping(tmp_path)
    raw = json.loads(mapping_file.read_text(encoding="utf-8"))
    raw["idu"]["MOT1"]["Internal Calibration"] = {"synthetic": True}
    mapping_file.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_file)),
        mapping_requirement_provider=RequirementProvider(),
    )
    service.load_snapshot()
    service.edit_cell("idu", 0, "Size", "round-trip")
    service.edit_cell("odu_cond_specs", 0, "Cond Inner Area", "12.5")
    service.edit_cell("odu_cond_specs", 4, "Cond Area", "46.5")

    result, saved = service.save_mapping()
    assert result.success and not saved.dirty
    reloaded = service.reload_snapshot()
    assert not reloaded.dirty
    assert reloaded.draft.group("idu").rows[0].value_for("Size") == "round-trip"
    cond = reloaded.draft.group("odu_cond_specs")
    assert cond.rows[0].value_for("Cond Inner Area") == 12.5
    assert cond.rows[4].value_for("Pi") == ""
    persisted = json.loads(mapping_file.read_text(encoding="utf-8"))
    assert persisted["idu"]["MOT1"]["Internal Calibration"] == {"synthetic": True}
