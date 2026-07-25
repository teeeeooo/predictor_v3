"""Legacy migration and startup resolver tests."""

from pathlib import Path
import hashlib
import json

import joblib
import pytest

from apps.common.model_lifecycle import (
    ActiveModelResolver,
    LegacyModelMigrationService,
    ModelLifecycleRepository,
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


@pytest.mark.parametrize(
    "corruption",
    ("hash-mismatch", "manifest-json", "deserialize", "missing-result"),
)
def test_existing_corrupt_legacy_candidate_fails_closed_and_is_idempotent(
    tmp_path, registry_snapshot, corruption
):
    legacy = tmp_path / "model.pkl"
    joblib.dump(artifact_for(registry_snapshot), legacy)
    original = legacy.read_bytes()
    root = tmp_path / "lifecycle"
    importing = ModelLifecycleRepository(
        root,
        failure_hook=lambda stage: (
            (_ for _ in ()).throw(OSError("activation interrupted"))
            if stage == "before_active_replace"
            else None
        ),
    )
    first = LegacyModelMigrationService(
        importing, lambda: registry_snapshot
    ).migrate_if_needed(legacy)
    assert first.status == "bootstrap"
    candidate_path = root / "candidates" / first.candidate_id

    if corruption == "hash-mismatch":
        (candidate_path / "model.pkl").write_bytes(b"changed")
    elif corruption == "manifest-json":
        (candidate_path / "manifest.json").write_text("{invalid", encoding="utf-8")
    elif corruption == "deserialize":
        broken = b"not-a-joblib-model"
        (candidate_path / "model.pkl").write_bytes(broken)
        manifest_path = candidate_path / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["model_sha256"] = hashlib.sha256(broken).hexdigest()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    else:
        (candidate_path / "result.json").unlink()

    repository = ModelLifecycleRepository(root)
    service = LegacyModelMigrationService(repository, lambda: registry_snapshot)
    results = (
        service.migrate_if_needed(legacy),
        service.migrate_if_needed(legacy),
    )

    assert {item.status for item in results} == {"retraining-required"}
    assert {item.reason_code for item in results} == {"legacy_candidate_corrupt"}
    assert legacy.read_bytes() == original
    assert repository.read_active(optional=True) is None
    assert len(tuple((root / "candidates").iterdir())) == 1
    assert not (root / "active_model.json").exists()


def test_legacy_migration_does_not_hide_registry_provider_programmer_error(
    repository, registry_snapshot, tmp_path
):
    legacy = tmp_path / "model.pkl"
    joblib.dump(artifact_for(registry_snapshot), legacy)
    service = LegacyModelMigrationService(
        repository,
        lambda: (_ for _ in ()).throw(RuntimeError("provider defect")),
    )

    with pytest.raises(RuntimeError, match="provider defect"):
        service.migrate_if_needed(legacy)

    assert legacy.is_file()
    assert repository.read_active(optional=True) is None


def test_new_resolver_observes_active_change_but_loaded_service_keeps_path(
    repository, registry_snapshot
):
    first = publish_candidate(repository, registry_snapshot, "candidate-a")
    second = publish_candidate(repository, registry_snapshot, "candidate-b")
    repository.replace_active(
        "candidate-a",
        activated_at="2026-01-01T00:00:00+00:00",
        source="test",
        expected_revision=0,
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


def test_resolver_controls_missing_active_candidate(repository):
    repository.replace_active(
        "missing-candidate",
        activated_at="2026-01-01T00:00:00+00:00",
        source="test",
        expected_revision=0,
    )

    resolution = ActiveModelResolver(repository).resolve()

    assert resolution.status == "invalid-active"
    assert "Candidate does not exist" in resolution.message


@pytest.mark.parametrize(
    "programmer_error",
    (
        AssertionError("resolver invariant defect"),
        TypeError("resolver contract defect"),
    ),
)
def test_resolver_does_not_hide_unexpected_programmer_error(
    repository, monkeypatch, programmer_error
):
    def fail_read_active(*, optional):  # noqa: ARG001
        raise programmer_error

    monkeypatch.setattr(repository, "read_active", fail_read_active)

    with pytest.raises(type(programmer_error), match=str(programmer_error)):
        ActiveModelResolver(repository).resolve()
