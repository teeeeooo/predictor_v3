"""Adversarial filesystem ownership tests for immutable Candidates."""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import replace

import joblib
import pytest

from apps.common.model_lifecycle import ModelLifecycleRepository

from .conftest import artifact_for, publish_candidate


def _publication_input(repository, snapshot, candidate_id):  # noqa: ANN001
    template = repository.read_candidate("candidate-active")
    staging = repository.create_staging(candidate_id)
    model = staging / "model.pkl"
    joblib.dump(artifact_for(snapshot), model)
    manifest = replace(
        template.manifest,
        candidate_id=candidate_id,
        run_id=f"run-{candidate_id}",
        model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
    )
    result = replace(
        template.result,
        candidate_id=candidate_id,
        run_id=f"run-{candidate_id}",
    )
    return staging, manifest, result


def _active_repository(tmp_path, snapshot, *, failure_hook=None):  # noqa: ANN001
    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle", failure_hook=failure_hook
    )
    publish_candidate(repository, snapshot, "candidate-active")
    repository.replace_active(
        "candidate-active",
        activated_at="2026-07-23T00:00:00+00:00",
        source="test",
        expected_revision=0,
    )
    return repository


def _assert_active_preserved(repository) -> None:  # noqa: ANN001
    active = repository.read_active()
    assert (active.candidate_id, active.revision) == ("candidate-active", 1)


def test_staging_directory_symlink_swap_cannot_write_external(
    tmp_path, registry_snapshot
):
    repository = _active_repository(tmp_path, registry_snapshot)
    staging, manifest, result = _publication_input(
        repository, registry_snapshot, "candidate-new"
    )
    external = tmp_path / "external"
    external.mkdir()
    external_model = external / "model.pkl"
    external_model.write_bytes((staging / "model.pkl").read_bytes())
    before = external_model.read_bytes()
    repository.discard_staging(staging)
    staging.symlink_to(external, target_is_directory=True)

    with pytest.raises(ValueError, match="owned regular directory"):
        repository.publish(staging, manifest, result)

    assert external_model.read_bytes() == before
    assert set(path.name for path in external.iterdir()) == {"model.pkl"}
    _assert_active_preserved(repository)


def test_final_candidate_symlink_is_rejected_without_external_mutation(
    tmp_path, registry_snapshot
):
    repository = _active_repository(tmp_path, registry_snapshot)
    staging, manifest, result = _publication_input(
        repository, registry_snapshot, "candidate-new"
    )
    external = tmp_path / "external-final"
    external.mkdir()
    sentinel = external / "sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")
    (repository.candidates_path / "candidate-new").symlink_to(
        external, target_is_directory=True
    )

    with pytest.raises(ValueError, match="corrupt"):
        repository.publish(staging, manifest, result)

    assert sentinel.read_text(encoding="utf-8") == "preserve"
    assert repository.list_candidates()[0].manifest.candidate_id == "candidate-active"
    _assert_active_preserved(repository)


def test_model_symlink_is_rejected_without_touching_target(
    tmp_path, registry_snapshot
):
    repository = _active_repository(tmp_path, registry_snapshot)
    staging, manifest, result = _publication_input(
        repository, registry_snapshot, "candidate-new"
    )
    external_model = tmp_path / "external-model.pkl"
    shutil.copy2(staging / "model.pkl", external_model)
    (staging / "model.pkl").unlink()
    (staging / "model.pkl").symlink_to(external_model)
    before = external_model.read_bytes()

    with pytest.raises(ValueError, match="owned regular file"):
        repository.publish(staging, manifest, result)

    assert external_model.read_bytes() == before
    _assert_active_preserved(repository)


def test_staged_model_copy_never_follows_external_symlink(
    tmp_path, registry_snapshot
):
    repository = _active_repository(tmp_path, registry_snapshot)
    staging = repository.create_staging("candidate-new")
    external = tmp_path / "external-copy-target.pkl"
    external.write_bytes(b"preserve")
    (staging / "model.pkl").symlink_to(external)
    source = tmp_path / "legacy-source.pkl"
    joblib.dump(artifact_for(registry_snapshot), source)

    with pytest.raises(FileExistsError):
        repository.copy_model_to_staging(staging, source)

    assert external.read_bytes() == b"preserve"
    _assert_active_preserved(repository)


@pytest.mark.parametrize("artifact_name", ("model.pkl", "manifest.json", "result.json"))
def test_published_candidate_file_symlink_is_never_read_as_candidate(
    tmp_path, registry_snapshot, artifact_name
):
    repository = _active_repository(tmp_path, registry_snapshot)
    candidate = publish_candidate(repository, registry_snapshot, "candidate-new")
    external = tmp_path / f"external-{artifact_name}"
    shutil.copy2(candidate.path / artifact_name, external)
    (candidate.path / artifact_name).unlink()
    (candidate.path / artifact_name).symlink_to(external)
    before = external.read_bytes()

    with pytest.raises(ValueError, match="corrupt"):
        repository.read_candidate("candidate-new")
    with pytest.raises(ValueError, match="corrupt"):
        repository.list_candidates()

    assert external.read_bytes() == before
    _assert_active_preserved(repository)


def test_metadata_symlink_swap_before_publication_is_rejected(
    tmp_path, registry_snapshot
):
    swapped = {"stage": None}
    external = tmp_path / "external-metadata.json"
    external.write_text("preserve", encoding="utf-8")

    def swap_manifest(stage):  # noqa: ANN001
        if stage == "before_candidate_replace" and swapped["stage"] is not None:
            manifest_path = swapped["stage"] / "manifest.json"
            manifest_path.unlink()
            manifest_path.symlink_to(external)

    repository = _active_repository(
        tmp_path, registry_snapshot, failure_hook=swap_manifest
    )
    staging, manifest, result = _publication_input(
        repository, registry_snapshot, "candidate-new"
    )
    swapped["stage"] = staging

    with pytest.raises(ValueError, match="symlink"):
        repository.publish(staging, manifest, result)

    assert external.read_text(encoding="utf-8") == "preserve"
    assert not (repository.candidates_path / "candidate-new").exists()
    _assert_active_preserved(repository)


def test_prefix_similar_external_staging_is_not_owned(
    tmp_path, registry_snapshot
):
    repository = _active_repository(tmp_path, registry_snapshot)
    template = repository.read_candidate("candidate-active")
    external_stage = tmp_path / "lifecycle-evil" / ".staging" / "candidate-new"
    external_stage.mkdir(parents=True)
    shutil.copy2(template.model_path, external_stage / "model.pkl")
    sentinel = external_stage / "sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")

    with pytest.raises(ValueError, match="belong"):
        repository.publish(
            external_stage,
            replace(
                template.manifest,
                candidate_id="candidate-new",
                run_id="run-candidate-new",
            ),
            replace(
                template.result,
                candidate_id="candidate-new",
                run_id="run-candidate-new",
            ),
        )

    assert sentinel.read_text(encoding="utf-8") == "preserve"
    _assert_active_preserved(repository)
