"""Legacy migration and startup resolver tests."""

from pathlib import Path

import joblib

from apps.common.model_lifecycle import (
    ActiveModelResolver,
    LegacyModelMigrationService,
)
from apps.predict.services.prediction_service import PredictionService

from .conftest import artifact_for, publish_candidate


def test_compatible_legacy_is_preserved_imported_and_activated_once(
    repository, registry_snapshot, tmp_path
):
    legacy = tmp_path / "model.pkl"
    joblib.dump(artifact_for(registry_snapshot), legacy)
    original = legacy.read_bytes()
    service = LegacyModelMigrationService(repository, lambda: registry_snapshot)

    first = service.migrate_if_needed(legacy)
    second = service.migrate_if_needed(legacy)

    assert first.status == "active"
    assert second.status == "not-needed"
    assert legacy.read_bytes() == original
    assert len(repository.list_candidates()) == 1
    assert len(repository.read_active().history) == 1


def test_insufficient_legacy_metadata_imports_without_auto_active(
    repository, registry_snapshot, tmp_path
):
    legacy = tmp_path / "model.pkl"
    artifact = artifact_for(registry_snapshot)
    artifact["training_contract"].pop("generation_id")
    joblib.dump(artifact, legacy)
    original_hash = __import__("hashlib").sha256(legacy.read_bytes()).hexdigest()

    result = LegacyModelMigrationService(
        repository, lambda: registry_snapshot
    ).migrate_if_needed(legacy)

    assert result.status == "retraining-required"
    assert repository.read_active(optional=True) is None
    candidate = repository.list_candidates()[0]
    assert candidate.manifest.original_model_sha256 == original_hash
    assert not candidate.manifest.promotion_eligible
    assert legacy.is_file()


def test_invalid_legacy_fails_to_bootstrap_without_damage(
    repository, registry_snapshot, tmp_path
):
    legacy = tmp_path / "model.pkl"
    legacy.write_bytes(b"invalid")

    result = LegacyModelMigrationService(
        repository, lambda: registry_snapshot
    ).migrate_if_needed(legacy)

    assert result.status == "bootstrap"
    assert legacy.read_bytes() == b"invalid"
    assert repository.read_active(optional=True) is None


def test_new_resolver_observes_active_change_but_loaded_service_keeps_path(
    repository, registry_snapshot
):
    first = publish_candidate(repository, registry_snapshot, "candidate-a")
    second = publish_candidate(repository, registry_snapshot, "candidate-b")
    repository.replace_active(
        "candidate-a", activated_at="2026-01-01T00:00:00+00:00", source="test"
    )
    service = PredictionService(
        model_file=str(first.model_path),
        runtime_snapshot=None,
    )
    repository.replace_active(
        "candidate-b", activated_at="2026-01-02T00:00:00+00:00",
        source="test", expected_revision=1,
    )

    resolution = ActiveModelResolver(repository).resolve()

    assert resolution.model_path == str(second.model_path)
    assert Path(service._model_file) == first.model_path
