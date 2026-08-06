"""Phase 4B immutable generation publication and recovery tests."""

import hashlib
import json
import multiprocessing
import sys
import threading
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps.common.runtime_generation import repository as repository_module
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


def _publish_process(root, candidate, barrier, results) -> None:  # noqa: ANN001
    repository = DataDefinitionGenerationRepository(root)
    barrier.wait()
    try:
        repository.publish(candidate)
    except ValueError as exc:
        results.put((candidate.generation.generation_id, str(exc)))
    else:
        results.put((candidate.generation.generation_id, "published"))


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


def test_runtime_unavailable_derived_operand_is_blocked_before_staging(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "store")
    initial = bootstrap_manifest()
    repository.publish(initial)
    source = next(item for item in initial.features if item.ml_name == "Cooling Capa")
    invalid = replace(
        initial,
        generation=replace(
            initial.generation,
            generation_id="generation-runtime-shape-invalid",
            parent_generation_id=initial.generation.generation_id,
        ),
        features=tuple(
            replace(item, ml_name="Calculated Later", value_source="formula")
            if item.identity == source.identity else item
            for item in initial.features
        ),
    )

    with pytest.raises(ValueError, match="derived_operand_runtime_unavailable"):
        repository.publish(invalid)

    assert repository.active_generation_id() == initial.generation.generation_id
    assert repository.read_active().manifest == initial
    assert {item.name for item in repository.generations_path.iterdir()} == {
        initial.generation.generation_id
    }
    assert not list(repository.generations_path.glob(".staging-*"))
    assert not list(repository.root.glob(".active-generation-*.tmp"))


def test_duplicate_predict_display_order_is_blocked_before_publication(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "store")
    initial = bootstrap_manifest()
    repository.publish(initial)
    invalid = replace(
        initial,
        generation=replace(
            initial.generation,
            generation_id="generation-duplicate-display-order",
            parent_generation_id=initial.generation.generation_id,
        ),
        features=(
            initial.features[0],
            replace(
                initial.features[1],
                display_order=initial.features[0].display_order,
            ),
            *initial.features[2:],
        ),
    )

    with pytest.raises(ValueError, match="predict_display_order_duplicate"):
        repository.publish(invalid)

    assert repository.active_generation_id() == initial.generation.generation_id
    assert not (
        repository.generations_path / "generation-duplicate-display-order"
    ).exists()


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


def test_cross_process_writers_are_serialized_across_parent_check_and_replace(tmp_path):
    root = tmp_path / "store"
    repository = DataDefinitionGenerationRepository(root)
    initial = bootstrap_manifest()
    repository.publish(initial)
    candidates = (
        _candidate(initial, "generation-process-a", label="Process A"),
        _candidate(initial, "generation-process-b", label="Process B"),
    )
    context = multiprocessing.get_context("spawn")
    barrier = context.Barrier(2)
    results = context.Queue()
    processes = [
        context.Process(
            target=_publish_process,
            args=(str(root), candidate, barrier, results),
        )
        for candidate in candidates
    ]

    for process in processes:
        process.start()
    outcomes = [results.get(timeout=20) for _process in processes]
    for process in processes:
        process.join(timeout=20)

    assert not any(process.is_alive() for process in processes)
    assert all(process.exitcode == 0 for process in processes)
    assert len([result for _generation, result in outcomes if result == "published"]) == 1
    assert len([
        result for _generation, result in outcomes if "stale generation parent" in result
    ]) == 1
    assert repository.active_generation_id() in {
        "generation-process-a",
        "generation-process-b",
    }


def test_lock_acquisition_failure_preserves_active_generation(tmp_path, monkeypatch):
    repository = DataDefinitionGenerationRepository(tmp_path / "store")
    initial = bootstrap_manifest()
    repository.publish(initial)

    def fail_lock(_descriptor: int) -> None:
        raise OSError("injected lock acquisition failure")

    monkeypatch.setattr(repository_module, "_lock_descriptor", fail_lock)
    with pytest.raises(OSError, match="lock acquisition"):
        repository.publish(_candidate(initial, "generation-lock-failed"))

    assert repository.read_active().manifest == initial
    assert not (repository.generations_path / "generation-lock-failed").exists()
    assert not list(repository.generations_path.glob(".staging-*"))
    assert not list(repository.root.glob(".active-generation-*.tmp"))


def test_windows_lock_backend_supports_publication_stale_rejection_and_rollback(
    tmp_path,
    monkeypatch,
):
    calls: list[int] = []
    synced_paths: list[Path] = []
    open_files: dict[int, tuple[Path, str]] = {}
    real_path_open = Path.open
    real_fsync = repository_module.os.fsync

    class TrackedBinaryFile:
        def __init__(self, handle, path: Path, mode: str) -> None:  # noqa: ANN001
            self._handle = handle
            self._descriptor = handle.fileno()
            open_files[self._descriptor] = (path, mode)

        def __enter__(self):  # noqa: ANN204
            return self

        def __exit__(self, *args) -> None:  # noqa: ANN002
            try:
                self._handle.close()
            finally:
                open_files.pop(self._descriptor, None)

        def __getattr__(self, name: str):  # noqa: ANN204
            return getattr(self._handle, name)

    def tracked_path_open(
        path: Path,
        mode: str = "r",
        *args,
        **kwargs,
    ):  # noqa: ANN002, ANN003, ANN202
        handle = real_path_open(path, mode, *args, **kwargs)
        if "b" not in mode:
            return handle
        return TrackedBinaryFile(handle, path, mode)

    def windows_restricted_fsync(descriptor: int) -> None:
        tracked = open_files.get(descriptor)
        if tracked is not None:
            path, mode = tracked
            if "+" not in mode and not any(flag in mode for flag in "wax"):
                raise OSError(9, "Bad file descriptor")
            synced_paths.append(path)
        real_fsync(descriptor)

    fake_msvcrt = SimpleNamespace(
        LK_LOCK=1,
        LK_UNLCK=2,
        locking=lambda _descriptor, operation, _count: calls.append(operation),
    )
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)
    monkeypatch.setattr(repository_module, "_platform_name", lambda: "nt")
    monkeypatch.setattr(Path, "open", tracked_path_open)
    monkeypatch.setattr(repository_module.os, "fsync", windows_restricted_fsync)
    repository = DataDefinitionGenerationRepository(tmp_path / "windows-store")
    initial = bootstrap_manifest()

    repository.publish(initial)
    first = _candidate(initial, "generation-windows-first", label="Windows")
    repository.publish(first)
    with pytest.raises(ValueError, match="stale generation parent"):
        repository.publish(_candidate(initial, "generation-windows-stale"))
    restored = repository.rollback(initial.generation.generation_id)

    assert restored.manifest == initial
    assert repository.read_active().manifest == initial
    assert calls.count(fake_msvcrt.LK_LOCK) == calls.count(fake_msvcrt.LK_UNLCK)
    assert calls.count(fake_msvcrt.LK_LOCK) >= 4
    assert any(
        any(part.startswith(".staging-") for part in path.parts)
        for path in synced_paths
    )
    assert any(path.name.startswith(".active-generation-") for path in synced_paths)
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
