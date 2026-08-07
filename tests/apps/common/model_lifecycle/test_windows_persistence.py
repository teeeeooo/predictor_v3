"""Windows filesystem-semantics regressions for shared lifecycle persistence."""

from __future__ import annotations

import os
import sys
import ctypes
from types import SimpleNamespace

import pytest

from apps.common.model_lifecycle import (
    LifecycleRecoveryRequiredError,
    ModelLifecycleRepository,
)
from apps.common.model_lifecycle import filesystem as filesystem_module
from apps.common.model_lifecycle.filesystem import LifecycleFilesystem
from apps.common.model_lifecycle.locking import lifecycle_lock
from apps.common.model_lifecycle import windows_filesystem as windows_module

from .conftest import publish_candidate


def _access_mode(flags: int) -> int:
    return flags & (os.O_WRONLY | os.O_RDWR)


@pytest.fixture
def windows_filesystem_semantics(monkeypatch):
    """Reject POSIX-only calls instead of letting the macOS host accept them."""
    open_descriptors: dict[int, tuple[object, int]] = {}
    lock_calls: list[int] = []
    real_open = os.open
    real_close = os.close
    real_fsync = os.fsync

    def guarded_open(path, flags, mode=0o777, *, dir_fd=None):  # noqa: ANN001, ANN202
        if dir_fd is not None:
            raise AssertionError("Windows simulation forbids open(dir_fd=...)")
        if os.path.isdir(path):
            raise AssertionError("Windows simulation forbids opening directories")
        descriptor = real_open(path, flags, mode)
        open_descriptors[descriptor] = (path, flags)
        return descriptor

    def guarded_close(descriptor: int) -> None:
        open_descriptors.pop(descriptor, None)
        real_close(descriptor)

    def guarded_fsync(descriptor: int) -> None:
        opened = open_descriptors.get(descriptor)
        if opened is not None:
            path, flags = opened
            if _access_mode(flags) == os.O_RDONLY:
                raise OSError(9, "Bad file descriptor")
            if os.path.isdir(path):
                raise AssertionError("Windows simulation forbids directory fsync")
        real_fsync(descriptor)

    def reject_dir_fd(function):  # noqa: ANN001, ANN202
        def guarded(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            for name in ("dir_fd", "src_dir_fd", "dst_dir_fd"):
                if kwargs.get(name) is not None:
                    raise AssertionError(
                        f"Windows simulation forbids {name} in {function.__name__}"
                    )
            return function(*args, **kwargs)

        return guarded

    fake_msvcrt = SimpleNamespace(
        LK_LOCK=1,
        LK_NBLCK=2,
        LK_UNLCK=3,
        locking=lambda _descriptor, operation, _count: lock_calls.append(operation),
    )
    monkeypatch.setattr(filesystem_module, "_platform_name", lambda: "nt")
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)
    monkeypatch.setattr(os, "open", guarded_open)
    monkeypatch.setattr(os, "close", guarded_close)
    monkeypatch.setattr(os, "fsync", guarded_fsync)
    for name in ("link", "mkdir", "rename", "replace", "stat", "unlink"):
        monkeypatch.setattr(os, name, reject_dir_fd(getattr(os, name)))
    return fake_msvcrt, lock_calls


def test_windows_candidate_and_run_evidence_publication_use_compatible_primitives(
    tmp_path,
    registry_snapshot,
    windows_filesystem_semantics,
):
    fake_msvcrt, lock_calls = windows_filesystem_semantics
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")

    candidate = publish_candidate(repository, registry_snapshot, "candidate-windows")
    staging = repository.create_staging("run-windows")
    (staging / "training_result.json").write_text("{}\n", encoding="utf-8")
    evidence = repository.preserve_run_evidence(staging, "run-windows")

    assert repository.read_candidate("candidate-windows") == candidate
    assert (evidence / "training_result.json").read_text(encoding="utf-8") == "{}\n"
    assert lock_calls.count(fake_msvcrt.LK_LOCK) == lock_calls.count(
        fake_msvcrt.LK_UNLCK
    )
    assert lock_calls.count(fake_msvcrt.LK_LOCK) >= 2


def test_windows_candidate_failure_remains_hidden_until_recovery(
    tmp_path,
    registry_snapshot,
    windows_filesystem_semantics,
):
    failures = {"after_candidate_replace", "before_candidate_rollback"}
    enabled = {"value": True}

    def fail(stage: str) -> None:
        if enabled["value"] and stage in failures:
            raise OSError(stage)

    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle",
        failure_hook=fail,
    )

    with pytest.raises(LifecycleRecoveryRequiredError):
        publish_candidate(repository, registry_snapshot, "candidate-windows")

    assert repository.list_candidates() == ()
    marker = repository.root / ".candidate-recovery-candidate-windows.json"
    assert marker.is_file()
    enabled["value"] = False
    repository.recover_candidate_publication("candidate-windows")
    assert repository.list_candidates() == ()
    assert not marker.exists()


def test_windows_active_failure_restores_previous_revision_through_recovery(
    tmp_path,
    registry_snapshot,
    windows_filesystem_semantics,
):
    enabled = {"value": False}

    def fail(stage: str) -> None:
        if enabled["value"] and stage in {
            "after_active_replace",
            "before_active_rollback",
        }:
            raise OSError(stage)

    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle",
        failure_hook=fail,
    )
    for candidate_id in ("candidate-a", "candidate-b"):
        publish_candidate(repository, registry_snapshot, candidate_id)
    first = repository.replace_active(
        "candidate-a",
        activated_at="2026-08-06T00:00:00+00:00",
        source="test",
        expected_revision=0,
    )
    enabled["value"] = True

    with pytest.raises(LifecycleRecoveryRequiredError):
        repository.replace_active(
            "candidate-b",
            activated_at="2026-08-06T00:01:00+00:00",
            source="test",
            expected_revision=1,
        )

    enabled["value"] = False
    recovered = repository.recover_active_reference()
    assert recovered == first
    assert repository.read_active() == first


def test_windows_exclusive_safety_artifact_is_durable_and_no_clobber(
    tmp_path,
    windows_filesystem_semantics,
):
    filesystem = LifecycleFilesystem(tmp_path / "lifecycle")
    filesystem.ensure_directory(filesystem.root)
    temporary = filesystem.root / ".permit.tmp"
    final = filesystem.root / "permit.json"
    with filesystem.open_exclusive(temporary) as target:
        target.write(b'{"permit": true}\n')

    filesystem.publish_file_exclusive(temporary, final)

    assert final.read_bytes() == b'{"permit": true}\n'
    replacement = filesystem.root / ".permit-replacement.tmp"
    with filesystem.open_exclusive(replacement) as target:
        target.write(b'{"permit": false}\n')
    with pytest.raises(FileExistsError):
        filesystem.publish_file_exclusive(replacement, final)
    assert final.read_bytes() == b'{"permit": true}\n'


def test_windows_lock_rejects_replaced_workspace_root_without_external_write(
    tmp_path,
    windows_filesystem_semantics,
):
    root = tmp_path / "lifecycle"
    filesystem = LifecycleFilesystem(root)
    filesystem.ensure_directory(root)
    preserved = tmp_path / "preserved"
    external = tmp_path / "external"
    external.mkdir()
    root.rename(preserved)
    root.symlink_to(external, target_is_directory=True)

    with pytest.raises(ValueError, match="owned regular directory"):
        with lifecycle_lock(root / ".lifecycle-write.lock", filesystem=filesystem):
            pass

    assert not (external / ".lifecycle-write.lock").exists()


def test_native_windows_move_requests_write_through_and_bounded_replacement(
    monkeypatch,
):
    calls: list[tuple[str, str, int]] = []

    class MoveFile:
        argtypes = None
        restype = None

        def __call__(self, source: str, destination: str, flags: int) -> int:
            calls.append((source, destination, flags))
            return 1

    move_file = MoveFile()
    kernel32 = SimpleNamespace(MoveFileExW=move_file)
    monkeypatch.setattr(windows_module.os, "name", "nt")
    monkeypatch.setattr(
        ctypes,
        "WinDLL",
        lambda *_args, **_kwargs: kernel32,
        raising=False,
    )

    windows_module._move_path(
        "candidate-stage", "candidate-final", replace_existing=False
    )
    windows_module._move_path(
        "active-temp", "active.json", replace_existing=True
    )

    assert calls == [
        ("candidate-stage", "candidate-final", 0x8),
        ("active-temp", "active.json", 0x9),
    ]
