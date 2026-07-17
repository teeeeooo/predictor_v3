"""Phase 4B Data Definition application persistence integration tests."""

import os

from PySide6.QtWidgets import QApplication

from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.app import create_shell
from apps.train.services.data_definition_service import DataDefinitionService
from core.data_definition.contract import bootstrap_manifest
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
    assert repository.read_active().projections.predict[0].label == (
        "Production generation presentation"
    )
    assert DEFAULT_SCHEMA_PATH.read_bytes() == legacy_schema_before
    shell.close()


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
    assert "ml_compatibility_projection_write_required" in {
        item.code for item in result.issues
    }
    assert repository.active_generation_id() == initial_generation
    assert changed.is_changed


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


def test_legacy_schema_writer_remains_default_compatibility_path(tmp_path):
    schema = tmp_path / "schema.csv"
    service = DataDefinitionService(schema_path=schema)
    assert service.schema_path == schema
