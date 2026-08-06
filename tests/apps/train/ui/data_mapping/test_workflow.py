"""Slice 2C Data Mapping validation, dirty, Save, and Reload workflow tests."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QMessageBox

from apps.train.adapters.mapping import parse_legacy_mapping_csv
from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_mapping_service import DataMappingService, RuntimeMappingCatalogProvider
from apps.train.ui.data_mapping.import_preview_dialog import DataMappingImportPreviewDialog
from apps.train.ui.data_mapping.issue_navigation import focus_cell_target
from apps.train.ui.data_mapping_panel import DataMappingPanel
from core.data_definition.model import MappingRequirement
from core.mapping.editor_commands import duplicate_draft_row, set_draft_cell
from core.mapping.editor_persistence import MappingEditorSaveResult
from core.mapping.editor_projection import (
    apply_mapping_requirements_to_editor_draft,
    project_runtime_mapping_to_editor_draft,
)

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


class MutableRequirementProvider:
    def __init__(self, requirements=()):  # noqa: ANN001
        self.requirements = tuple(requirements)

    def load_mapping_requirements(self):  # noqa: ANN201
        return self.requirements


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


def test_duplicate_occurrence_coverage_and_issue_navigation_focus_same_exact_cell():
    _app()
    requirement = MappingRequirement(
        column_key="fan_diameter",
        ml_name="",
        mapping_entity="idu",
        mapping_attribute="Fan Diameter",
        trigger_column="idu",
        data_type="number",
        required=False,
    )
    draft = apply_mapping_requirements_to_editor_draft(
        project_runtime_mapping_to_editor_draft(
            {
                "idu": {"IDU-A": {"ID Volume": 1.25, "Fan Diameter": 2.5}},
                "ref_type": {"R32": {}},
                "exp_type": {"EEV": {}},
            }
        ),
        (requirement,),
    )
    draft = duplicate_draft_row(draft, "idu", 0)
    draft = set_draft_cell(draft, "idu", 1, "Fan Diameter", "bad")

    class DuplicateProvider:
        source_label = "synthetic duplicate mapping rows"

        def load_draft(self):  # noqa: ANN201
            return draft

    class DuplicateRequirementProvider:
        def load_mapping_requirements(self):  # noqa: ANN201
            return (requirement,)

    controller = DataMappingController(
        DataMappingService(DuplicateProvider(), DuplicateRequirementProvider())
    )
    panel = DataMappingPanel(controller=controller)
    panel.show()
    state = panel._current_state
    coverage = next(
        item for item in state.coverage_items if item.definition_column_key == "fan_diameter"
    )
    fan_column = state.value_headers.index("Fan Diameter")

    assert (coverage.ready_rows, coverage.invalid_rows) == (1, 1)
    assert coverage.first_unresolved.row_occurrence == 1
    panel.coverage_panel.go_button.click()
    QApplication.processEvents()
    assert panel.row_table.currentIndex() == panel.row_table.model().index(1, fan_column)

    invalid_issue = next(
        index
        for index, issue in enumerate(state.validation_rows)
        if issue.code == "invalid_number"
    )
    issue_cell = panel.validation_table.model().index(invalid_issue, 0)
    panel.validation_table.clicked.emit(issue_cell)
    QApplication.processEvents()
    assert panel.row_table.currentIndex() == panel.row_table.model().index(1, fan_column)

    stale_target = coverage.first_unresolved
    after_delete = controller.delete_row("idu", 0)
    panel._apply_state(after_delete)
    assert not focus_cell_target(stale_target, after_delete, panel.row_table)
    assert panel.row_table.currentIndex().row() != 1


def test_shared_requirement_contract_drives_one_offscreen_column_and_coverage(tmp_path):
    _app()
    requirements = (
        MappingRequirement(
            column_key="fan_attribute_b",
            ml_name="",
            mapping_entity="idu",
            mapping_attribute="Fan Attribute",
            trigger_column="idu",
            data_type="number",
            required=False,
        ),
        MappingRequirement(
            column_key="fan_attribute_a",
            ml_name="",
            mapping_entity="idu",
            mapping_attribute="Fan Attribute",
            trigger_column="idu",
            data_type="number",
            required=True,
        ),
    )
    requirement_provider = MutableRequirementProvider(requirements)
    controller = DataMappingController(
        DataMappingService(
            RuntimeMappingCatalogProvider(str(_copy_mapping(tmp_path))),
            requirement_provider,
        )
    )
    panel = DataMappingPanel(controller=controller)
    panel.show()
    state = panel._current_state
    fan_column = state.value_headers.index("Fan Attribute")
    coverage = next(
        item for item in state.coverage_items if item.mapping_attribute == "Fan Attribute"
    )

    assert state.value_headers.count("Fan Attribute") == 1
    assert panel.coverage_panel.selector.count() == 1
    assert coverage.required
    assert coverage.source_definition_column_keys == (
        "fan_attribute_a",
        "fan_attribute_b",
    )
    assert not next(
        action.enabled for action in state.actions if action.key == "save_mapping_json"
    )

    model = panel.row_table.model()
    for row_index in range(model.rowCount()):
        assert model.setData(model.index(row_index, fan_column), "2.5", Qt.EditRole)
        QApplication.processEvents()
        model = panel.row_table.model()
    ready = panel._current_state
    assert next(
        item for item in ready.coverage_items if item.mapping_attribute == "Fan Attribute"
    ).status == "ready"
    assert next(
        action.enabled for action in ready.actions if action.key == "save_mapping_json"
    )


def test_untouched_projection_blank_is_not_saved_by_offscreen_unrelated_edit(tmp_path):
    _app()
    mapping_file = _copy_mapping(tmp_path)
    requirement_provider = MutableRequirementProvider(
        (
            MappingRequirement(
                column_key="fan_attribute",
                ml_name="",
                mapping_entity="idu",
                mapping_attribute="Fan Attribute",
                trigger_column="idu",
                data_type="number",
                required=False,
            ),
        )
    )
    service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_file)),
        requirement_provider,
    )
    controller = DataMappingController(service)
    panel = DataMappingPanel(controller=controller)
    panel.show()

    assert "Fan Attribute" in panel._current_state.value_headers
    assert not service.current_snapshot().draft.group("idu").rows[0].has_concrete_value_for(
        "Fan Attribute"
    )

    requirement_provider.requirements = ()
    panel._apply_state(controller.refresh("idu"))
    assert "Fan Attribute" not in panel._current_state.value_headers
    size_column = panel._current_state.value_headers.index("Size")
    model = panel.row_table.model()
    assert model.setData(model.index(0, size_column), "offscreen-edit", Qt.EditRole)
    QApplication.processEvents()
    panel._save()
    QApplication.processEvents()

    payload = json.loads(mapping_file.read_text(encoding="utf-8"))
    first_key = next(iter(payload["idu"]))
    assert payload["idu"][first_key]["Size"] == "offscreen-edit"
    assert "Fan Attribute" not in payload["idu"][first_key]


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


def test_import_bundle_action_is_separate_from_review_export_and_clipboard_surface(tmp_path):
    _app()
    service = DataMappingService(RuntimeMappingCatalogProvider(str(_copy_mapping(tmp_path))))
    controller = DataMappingController(service)
    panel = DataMappingPanel(controller=controller)

    import_button = panel.toolbar.buttons["import_mapping_bundle"]

    assert import_button.text() == "Import"
    assert import_button.isEnabled()
    assert panel.toolbar.buttons["export_csv_v2"].text() == "Export"
    assert panel.row_table is not import_button


def test_import_preview_dialog_shows_summary_and_draft_only_apply(tmp_path):
    _app()
    service = DataMappingService(RuntimeMappingCatalogProvider(str(_copy_mapping(tmp_path))))
    controller = DataMappingController(service)
    bundle = tmp_path / "renamed-external-tool.csv"
    result, _snapshot = service.export_exchange(bundle)
    assert result.success

    preview = controller.preview_exchange_import(bundle)
    dialog = DataMappingImportPreviewDialog(preview)
    dialog.show()
    QApplication.processEvents()

    assert dialog.windowTitle() == "Import Mapping Bundle Preview"
    assert dialog.apply_button.isEnabled()
    assert dialog.cancel_button.isEnabled()
    labels = {label.accessibleName() for label in dialog.findChildren(QLabel)}
    assert "Mapping Bundle format version" in labels
    assert "Mapping Bundle change summary" in labels
    assert "Mapping Bundle save destination notice" in labels
    assert dialog.accessibleName() == "Mapping Bundle Import Preview"
    dialog.reject()


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



def test_missing_mapping_panel_exposes_legacy_bootstrap_separately_from_bundle_import(tmp_path):
    _app()
    mapping_file = tmp_path / "mapping.json"
    service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_file)),
        legacy_bootstrap_parser=parse_legacy_mapping_csv,
    )
    panel = DataMappingPanel(controller=DataMappingController(service))
    QApplication.processEvents()

    assert panel._buttons["bootstrap_legacy_csv"].text() == "Legacy Bootstrap"
    assert panel._buttons["bootstrap_legacy_csv"].isEnabled()
    assert not panel._buttons["import_mapping_bundle"].isEnabled()
    assert "legacy-wide CSV" in panel._buttons["bootstrap_legacy_csv"].toolTip()
    assert not mapping_file.exists()


def test_legacy_bootstrap_file_picker_cancel_preserves_missing_state(tmp_path, monkeypatch):
    _app()
    mapping_file = tmp_path / "mapping.json"
    service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_file)),
        legacy_bootstrap_parser=parse_legacy_mapping_csv,
    )
    controller = DataMappingController(service)
    panel = DataMappingPanel(controller=controller)
    calls = []
    monkeypatch.setattr(
        "apps.train.ui.data_mapping_panel.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: ("", ""),
    )
    monkeypatch.setattr(
        controller,
        "preview_legacy_bootstrap",
        lambda source: calls.append(source),
    )

    panel._bootstrap_legacy_mapping()

    assert calls == []
    assert service.current_snapshot() is None
    assert not mapping_file.exists()
    assert panel.status_label.text() == "Mapping resource not found."


def test_legacy_bootstrap_replacement_cancel_preserves_unsaved_draft(tmp_path, monkeypatch):
    _app()
    mapping_file = tmp_path / "mapping.json"
    shutil.copy2(RUNTIME_FIXTURE, mapping_file)
    service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_file)),
        legacy_bootstrap_parser=parse_legacy_mapping_csv,
    )
    controller = DataMappingController(service)
    panel = DataMappingPanel(controller=controller)
    controller.edit_cell("idu", 0, "ID Volume", "123.5")
    mapping_file.unlink()
    panel.refresh()
    before = service.current_snapshot()
    monkeypatch.setattr(
        "apps.train.ui.data_mapping_panel.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: (
            str(Path("tests/fixtures/mapping/mapping_tables_legacy_wide.csv")),
            "Legacy Mapping CSV (*.csv)",
        ),
    )
    monkeypatch.setattr(
        "apps.train.ui.data_mapping_panel.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.No,
    )

    panel._bootstrap_legacy_mapping()

    after = service.current_snapshot()
    assert after.draft == before.draft
    assert after.dirty
    assert after.draft.group("idu").rows[0].value_for("ID Volume") == 123.5
    assert not mapping_file.exists()
