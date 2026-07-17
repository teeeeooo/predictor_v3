"""Phase 4B immutable generation publication and recovery tests."""

import hashlib
import json
import threading
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


def test_stale_candidate_cannot_replace_first_published_generation(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "store")
    initial = bootstrap_manifest()
    repository.publish(initial)
    first = _candidate(initial, "generation-first", label="First writer")
    stale = _candidate(initial, "generation-stale", label="Stale writer")

    repository.publish(first)
    with pytest.raises(ValueError, match="stale generation parent"):
        repository.publish(stale)

    assert repository.read_active().manifest == first
    assert not (repository.generations_path / "generation-stale").exists()
    assert not list(repository.generations_path.glob(".staging-*"))
    assert not list(repository.root.glob(".active-generation-*.tmp"))


def test_concurrent_stale_writers_are_serialized_across_parent_check_and_replace(tmp_path):
    root = tmp_path / "store"
    repository = DataDefinitionGenerationRepository(root)
    initial = bootstrap_manifest()
    repository.publish(initial)
    candidates = (
        _candidate(initial, "generation-a", label="Writer A"),
        _candidate(initial, "generation-b", label="Writer B"),
    )
    barrier = threading.Barrier(2)
    outcomes: list[tuple[str, str]] = []

    def publish(candidate) -> None:  # noqa: ANN001
        contender = DataDefinitionGenerationRepository(root)
        barrier.wait()
        try:
            contender.publish(candidate)
        except ValueError as exc:
            outcomes.append((candidate.generation.generation_id, str(exc)))
        else:
            outcomes.append((candidate.generation.generation_id, "published"))

    threads = [threading.Thread(target=publish, args=(item,)) for item in candidates]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert not any(thread.is_alive() for thread in threads)
    assert len([result for _generation, result in outcomes if result == "published"]) == 1
    stale_results = [
        result
        for _generation, result in outcomes
        if "stale generation parent" in result
    ]
    assert len(stale_results) == 1
    assert repository.active_generation_id() in {"generation-a", "generation-b"}
    assert not list(repository.generations_path.glob(".staging-*"))
    assert not list(repository.root.glob(".active-generation-*.tmp"))


def test_bundle_read_rejects_projection_from_a_different_generation(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "store")
    manifest = bootstrap_manifest()
    repository.publish(manifest)
    generation_path = repository.generations_path / manifest.generation.generation_id
    projection_path = generation_path / "projections" / "one_hot.json"
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    projection["generation_id"] = "different-generation"
    projection_path.write_text(
        json.dumps(projection, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    bundle_path = generation_path / "bundle.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle["files"]["projections/one_hot.json"] = hashlib.sha256(
        projection_path.read_bytes()
    ).hexdigest()
    bundle_path.write_text(
        json.dumps(bundle, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="generated projection does not match manifest"):
        repository.read_generation(manifest.generation.generation_id)
