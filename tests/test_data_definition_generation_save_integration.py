"""Phase 4B Data Definition application persistence integration tests."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.app import PROJECT_ROOT, create_shell, default_generation_root
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from core.data_definition.contract import bootstrap_manifest
from apps.train.state.training_run_state import TrainingRequest
from core.data_definition.draft import replace_draft_row
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH


def _service(tmp_path):  # noqa: ANN001
    repository = DataDefinitionGenerationRepository(tmp_path / "definition-store")
    repository.publish(bootstrap_manifest())
    return DataDefinitionService(generation_repository=repository), repository


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_production_create_shell_bootstraps_and_publishes_generation_save(tmp_path):
    _app()
    legacy_schema_before = DEFAULT_SCHEMA_PATH.read_bytes()
    root = tmp_path / "production-definition-store"

    shell = create_shell(generation_root=root)
    repository = DataDefinitionGenerationRepository(root)
    initial_generation = repository.active_generation_id()
    initial_registry = shell.train_controller.registry_snapshot()
    assert initial_registry.generation_id == initial_generation
    assert shell.predict_workspace.generation_id == initial_generation
    shell.data_definition_controller.refresh()
    changed = shell.data_definition_controller.edit_cell(
        ("schema_row", "cooling_capa"),
        "label",
        "Production generation presentation",
    )
    saved = shell.data_definition_controller.save_schema()

    assert initial_generation.startswith("bootstrap-")
    assert changed.draft_changed
    assert saved.status == "saved"
    assert repository.active_generation_id() != initial_generation
    assert shell.train_controller.registry_snapshot() == initial_registry
    assert shell.predict_workspace.generation_id == initial_generation
    captured = []

    class CaptureExecution:
        def start(self, request, callbacks=None):  # noqa: ANN001
            captured.append(request)

        def cancel(self):
            return True

    data = tmp_path / "process-a.csv"
    data.write_text("sentinel\n", encoding="utf-8")
    shell.train_controller._execution = CaptureExecution()
    shell.train_controller.start(TrainingRequest("process-a", str(data)))
    assert captured[0].generation_id == initial_generation
    assert captured[0].registry_fingerprint == initial_registry.registry_fingerprint
    assert repository.read_active().projections.predict[0].label == (
        "Production generation presentation"
    )
    assert DEFAULT_SCHEMA_PATH.read_bytes() == legacy_schema_before
    restarted_shell = create_shell(generation_root=root)
    assert restarted_shell.train_controller.registry_snapshot().generation_id == repository.active_generation_id()
    assert restarted_shell.predict_workspace.generation_id == repository.active_generation_id()
    assert repository.read_active().projections.predict[0].label == (
        "Production generation presentation"
    )
    restarted_shell.close()
    shell.close()


def test_application_persistence_depends_on_repository_port_not_filesystem_adapter():
    sources = (
        Path("apps/train/services/data_definition_persistence_service.py"),
        Path("apps/train/services/data_definition_service.py"),
    )
    for source in sources:
        text = source.read_text(encoding="utf-8")
        assert "DataDefinitionGenerationRepositoryPort" in text
        assert "apps.train.adapters.data_definition_generation_repository" not in text


def test_train_app_and_generation_adapter_import_without_posix_fcntl_dependency():
    script = """
import builtins
original_import = builtins.__import__
def guarded_import(name, *args, **kwargs):
    if name == 'fcntl':
        raise ModuleNotFoundError('fcntl blocked for Windows import simulation')
    return original_import(name, *args, **kwargs)
builtins.__import__ = guarded_import
import apps.train.adapters.data_definition_generation_repository
import apps.train.app
"""
    subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def test_default_generation_root_is_per_user_runtime_state(tmp_path):
    windows_root = default_generation_root(
        platform_name="nt",
        environment={"LOCALAPPDATA": str(tmp_path / "LocalAppData")},
        home=tmp_path / "home",
    )
    posix_root = default_generation_root(
        platform_name="posix",
        environment={"XDG_STATE_HOME": str(tmp_path / "state")},
        home=tmp_path / "home",
    )

    assert windows_root == tmp_path / "LocalAppData" / "predictor_v3" / "data_definition"
    assert posix_root == tmp_path / "state" / "predictor_v3" / "data_definition"
    assert PROJECT_ROOT not in windows_root.parents
    assert PROJECT_ROOT not in posix_root.parents


def test_legacy_source_config_generation_store_is_git_ignored():
    result = subprocess.run(
        [
            "git",
            "check-ignore",
            "config/data_definition/generation_store/active_generation.json",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_persistence_owner_selection_is_explicit(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "store")
    repository.publish(bootstrap_manifest())

    with pytest.raises(ValueError, match="exactly one persistence owner"):
        DataDefinitionService()
    with pytest.raises(ValueError, match="exactly one persistence owner"):
        DataDefinitionService(
            schema_path=tmp_path / "schema.csv",
            generation_repository=repository,
        )
    with pytest.raises(ValueError, match="explicit service"):
        DataDefinitionController()


def test_canonical_save_publishes_predict_presentation_change_as_complete_generation(tmp_path):
    service, repository = _service(tmp_path)
    draft = service.load_draft()
    identity = next(row.identity for row in draft.rows if row.column_key == "cooling_capa")
    changed = replace_draft_row(draft, identity, label="Cooling capacity presentation")
    plan = service.preview_save_plan(changed)
    assert "candidate_feature_projection_mismatch" in {
        item.code for item in plan.blocked_reasons
    }
    result = service.save_schema_draft(changed)
    assert result.status == "written"
    assert repository.active_generation_id().startswith("generation-")
    active = repository.read_active()
    assert active.manifest.generation.parent_generation_id.startswith("bootstrap-")
    assert active.projections.predict[0].label == "Cooling capacity presentation"
    assert active.projections.ml[0].label == "Cooling capacity presentation"
    assert not service.load_draft().is_changed
    assert service.load_report().parity_issues == ()


def test_protected_ml_name_change_remains_blocked_without_consumer_migration(tmp_path):
    service, repository = _service(tmp_path)
    initial_generation = repository.active_generation_id()
    draft = service.load_draft()
    identity = next(row.identity for row in draft.rows if row.column_key == "cooling_capa")
    changed = replace_draft_row(draft, identity, ml_name="Cooling Capacity Renamed")
    result = service.save_schema_draft(changed)
    assert result.status == "blocked"
    assert "restricted_field_edit_not_allowed" in {
        item.code for item in result.issues
    }
    assert repository.active_generation_id() == initial_generation
    assert changed.is_changed


def test_stale_application_save_preserves_first_generation_and_stale_draft(tmp_path):
    first_service, repository = _service(tmp_path)
    stale_service = DataDefinitionService(generation_repository=repository)
    first_draft = first_service.load_draft()
    stale_draft = stale_service.load_draft()
    identity = next(
        row.identity for row in first_draft.rows if row.column_key == "cooling_capa"
    )
    first_changed = replace_draft_row(first_draft, identity, label="First save")
    stale_changed = replace_draft_row(stale_draft, identity, label="Stale save")

    first_result = first_service.save_schema_draft(first_changed)
    stale_result = stale_service.save_schema_draft(stale_changed)

    assert first_result.status == "written"
    assert stale_result.status == "error"
    assert "stale generation parent" in stale_result.message
    assert repository.read_active().projections.predict[0].label == "First save"
    assert stale_changed.is_changed


def test_rejected_generation_save_preserves_draft_and_does_not_touch_external_owners(tmp_path):
    service, repository = _service(tmp_path)
    mapping_path = tmp_path / "mapping.json"
    model_path = tmp_path / "model.pkl"
    mapping_path.write_text("mapping-owner", encoding="utf-8")
    model_path.write_bytes(b"model-owner")
    draft = service.load_draft()
    identity = next(row.identity for row in draft.rows if row.column_key == "cooling_capa")
    changed = replace_draft_row(draft, identity, ml_name="Unsafe")
    result = service.save_schema_draft(changed)
    assert result.status == "blocked"
    assert changed.is_changed
    assert mapping_path.read_text(encoding="utf-8") == "mapping-owner"
    assert model_path.read_bytes() == b"model-owner"
    assert repository.read_active().manifest == bootstrap_manifest()


def test_explicit_service_without_repository_uses_legacy_compatibility_path(tmp_path):
    schema = tmp_path / "schema.csv"
    service = DataDefinitionService(schema_path=schema)
    assert service.schema_path == schema
