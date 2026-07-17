"""Phase 4B immutable generation publication and recovery tests."""

from dataclasses import replace

import pytest

from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from core.data_definition.contract import bootstrap_manifest


def _candidate(manifest, generation_id: str, *, label: str | None = None):  # noqa: ANN001
    features = manifest.features
    if label is not None:
        features = (replace(features[0], label=label), *features[1:])
    return replace(
        manifest,
        generation=replace(
            manifest.generation,
            generation_id=generation_id,
            parent_generation_id=manifest.generation.generation_id,
            source="data_definition_save",
        ),
        features=features,
    )


def test_publish_exposes_only_one_complete_generation_and_preserves_history(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "store")
    initial = bootstrap_manifest()
    first = repository.publish(initial)
    second_manifest = _candidate(initial, "generation-2", label="Changed presentation")
    second = repository.publish(second_manifest)
    assert first.previous_generation_id == ""
    assert second.previous_generation_id == initial.generation.generation_id
    assert repository.active_generation_id() == "generation-2"
    assert repository.read_active().manifest == second_manifest
    assert repository.read_generation(initial.generation.generation_id).manifest == initial
    assert not list(repository.generations_path.glob(".staging-*"))


def test_invalid_candidate_does_not_create_files_or_change_active_pointer(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "store")
    initial = bootstrap_manifest()
    repository.publish(initial)
    invalid = replace(initial, ordering=replace(initial.ordering, ml=initial.ordering.ml[:-1]))
    with pytest.raises(ValueError, match="ml_order_incomplete"):
        repository.publish(invalid)
    assert repository.active_generation_id() == initial.generation.generation_id
    assert {item.name for item in repository.generations_path.iterdir()} == {
        initial.generation.generation_id
    }


@pytest.mark.parametrize("failure_stage", ["after_staging", "before_pointer_replace"])
def test_publication_failure_preserves_previous_active_generation(tmp_path, failure_stage):
    root = tmp_path / "store"
    initial_repository = DataDefinitionGenerationRepository(root)
    initial = bootstrap_manifest()
    initial_repository.publish(initial)

    def fail(stage: str) -> None:
        if stage == failure_stage:
            raise OSError(f"injected {stage} failure")

    failing = DataDefinitionGenerationRepository(root, failure_hook=fail)
    candidate = _candidate(initial, "generation-failed", label="Candidate")
    with pytest.raises(OSError, match="injected"):
        failing.publish(candidate)
    assert initial_repository.active_generation_id() == initial.generation.generation_id
    assert initial_repository.read_active().manifest == initial
    assert not list(initial_repository.generations_path.glob(".staging-*"))


def test_rollback_repoints_only_after_complete_bundle_validation(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "store")
    initial = bootstrap_manifest()
    repository.publish(initial)
    repository.publish(_candidate(initial, "generation-2", label="Changed"))
    restored = repository.rollback(initial.generation.generation_id)
    assert restored.manifest == initial
    assert repository.active_generation_id() == initial.generation.generation_id


def test_published_generation_is_immutable(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "store")
    initial = bootstrap_manifest()
    repository.publish(initial)
    conflicting = _candidate(initial, initial.generation.generation_id, label="Conflict")
    with pytest.raises(FileExistsError, match="immutable generation"):
        repository.publish(conflicting)
    assert repository.read_active().manifest == initial
