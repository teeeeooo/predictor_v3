"""Candidate publication integrity and immutability tests."""

from dataclasses import replace

import joblib
import pytest

from apps.common.model_lifecycle import (
    LifecycleDurabilityError,
    LifecycleRecoveryRequiredError,
    ModelLifecycleRepository,
)

from .conftest import artifact_for, publish_candidate


def test_publication_is_atomic_and_does_not_change_active(repository, registry_snapshot):
    candidate = publish_candidate(repository, registry_snapshot, "candidate-a")

    assert candidate.model_path.is_file()
    assert repository.read_active(optional=True) is None
    assert [item.manifest.candidate_id for item in repository.list_candidates()] == [
        "candidate-a"
    ]


def test_incomplete_staging_is_not_listed(repository, registry_snapshot):
    repository.create_staging("candidate-incomplete")

    assert repository.list_candidates() == ()


def test_hash_mismatch_and_invalid_model_are_blocked(repository, registry_snapshot):
    candidate = publish_candidate(repository, registry_snapshot, "candidate-a")
    candidate.model_path.write_bytes(b"changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        repository.read_candidate("candidate-a")

    staging = repository.create_staging("candidate-b")
    (staging / "model.pkl").write_bytes(b"not-joblib")
    manifest = replace(
        candidate.manifest,
        candidate_id="candidate-b",
        run_id="run-b",
        model_sha256=__import__("hashlib").sha256(b"not-joblib").hexdigest(),
    )
    with pytest.raises(Exception):
        repository.publish(staging, manifest, replace(
            candidate.result, candidate_id="candidate-b", run_id="run-b"
        ))


def test_same_identity_is_idempotent_only_for_same_content(repository, registry_snapshot):
    first = publish_candidate(repository, registry_snapshot, "candidate-a")
    staging = repository.create_staging("candidate-a")
    joblib.dump(artifact_for(registry_snapshot), staging / "model.pkl")

    with pytest.raises(FileExistsError, match="identity conflict"):
        repository.publish(
            staging,
            replace(first.manifest, created_at="different"),
            first.result,
        )
    assert repository.read_candidate("candidate-a").manifest == first.manifest


def test_candidate_directory_cannot_be_republished_with_conflicting_content(
    repository, registry_snapshot
):
    first = publish_candidate(repository, registry_snapshot, "candidate-a")
    artifact = artifact_for(registry_snapshot)
    artifact["extra"] = "different"
    staging = repository.create_staging("candidate-a")
    joblib.dump(artifact, staging / "model.pkl")
    changed = replace(
        first.manifest,
        model_sha256=__import__("hashlib").sha256(
            (staging / "model.pkl").read_bytes()
        ).hexdigest(),
    )
    with pytest.raises(FileExistsError):
        repository.publish(staging, changed, first.result)


def test_default_workspace_path_is_not_repository_identity(tmp_path):
    from apps.common.model_lifecycle.paths import default_model_lifecycle_root

    path = default_model_lifecycle_root(
        platform_name="posix", environment={"XDG_STATE_HOME": str(tmp_path)}
    )
    assert path.relative_to(tmp_path).as_posix() == (
        "predictor_v3/model_lifecycle/workspaces/default"
    )
    with pytest.raises(ValueError, match="only the default workspace"):
        default_model_lifecycle_root(workspace_id="another")


def test_candidate_failure_before_final_rename_is_not_visible(
    tmp_path, registry_snapshot
):
    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle",
        failure_hook=lambda stage: (
            (_ for _ in ()).throw(OSError("before rename"))
            if stage == "before_candidate_replace" else None
        ),
    )
    with pytest.raises(OSError, match="before rename"):
        publish_candidate(repository, registry_snapshot, "candidate-a")

    assert repository.list_candidates() == ()
    assert not (repository.candidates_path / "candidate-a").exists()
    assert not list(repository.root.glob(".candidate-recovery-*"))


def test_candidate_post_rename_durability_failure_rolls_back_visibility(
    tmp_path, registry_snapshot
):
    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle",
        failure_hook=lambda stage: (
            (_ for _ in ()).throw(OSError("candidate fsync"))
            if stage == "after_candidate_replace" else None
        ),
    )
    with pytest.raises(LifecycleDurabilityError, match="rolled back"):
        publish_candidate(repository, registry_snapshot, "candidate-a")

    assert repository.list_candidates() == ()
    assert not (repository.candidates_path / "candidate-a").exists()
    assert len(list(repository.staging_path.iterdir())) == 1
    assert not list(repository.root.glob(".candidate-recovery-*"))


def test_candidate_failed_rollback_is_hidden_and_requires_recovery(
    tmp_path, registry_snapshot
):
    enabled = {"value": True}

    def fail(stage):  # noqa: ANN001
        if enabled["value"] and stage in {
            "after_candidate_replace",
            "before_candidate_rollback",
        }:
            raise OSError(stage)

    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle", failure_hook=fail
    )
    with pytest.raises(LifecycleRecoveryRequiredError):
        publish_candidate(repository, registry_snapshot, "candidate-a")

    assert (repository.candidates_path / "candidate-a").is_dir()
    assert repository.list_candidates() == ()
    with pytest.raises(LifecycleRecoveryRequiredError):
        repository.read_candidate("candidate-a")
    assert list(repository.root.glob(".candidate-recovery-candidate-a.json"))
    enabled["value"] = False

    repository.recover_candidate_publication("candidate-a")

    assert repository.list_candidates() == ()
    assert not (repository.candidates_path / "candidate-a").exists()
    assert len(list(repository.staging_path.iterdir())) == 1
    assert not list(repository.root.glob(".candidate-recovery-*"))
