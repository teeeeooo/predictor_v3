"""Windows-semantics tests for Deployment Export publication."""

from __future__ import annotations

import ctypes
import os
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps.common.model_lifecycle import deployment_export_publication as publication
from apps.common.model_lifecycle import deployment_export_windows as windows
from tests.apps.common.model_lifecycle.conftest import publish_candidate


def _active_export_source(repository, registry_snapshot):  # noqa: ANN001
    candidate = publish_candidate(repository, registry_snapshot, "candidate-export")
    active = repository.replace_active(
        candidate.manifest.candidate_id,
        activated_at="2026-08-06T00:00:00+00:00",
        source="test",
        expected_revision=0,
    )
    return active, candidate


@pytest.fixture
def windows_export_semantics(monkeypatch):
    opened: dict[int, int] = {}
    synced_flags: list[int] = []
    real_open = os.open
    real_close = os.close
    real_fsync = os.fsync

    class PublicationOS:
        name = os.name
        O_RDONLY = os.O_RDONLY

        def __getattr__(self, name):  # noqa: ANN001, ANN202
            return getattr(os, name)

        @staticmethod
        def open(path, flags, *args, **kwargs):  # noqa: ANN001, ANN202
            raise AssertionError(f"Windows export opened a directory: {path}")

        @staticmethod
        def fsync(_descriptor):
            raise AssertionError("Windows export used POSIX directory fsync")

    class WindowsOS:
        name = os.name
        O_RDWR = os.O_RDWR
        O_BINARY = getattr(os, "O_BINARY", 0)
        path = os.path

        def __getattr__(self, name):  # noqa: ANN001, ANN202
            return getattr(os, name)

        @staticmethod
        def fstat(descriptor):
            return os.fstat(descriptor)

        @staticmethod
        def fsync(descriptor):
            flags = opened[descriptor]
            if flags & os.O_ACCMODE == os.O_RDONLY:
                raise OSError(9, "Bad file descriptor")
            synced_flags.append(flags)
            real_fsync(descriptor)

        @staticmethod
        def close(descriptor):
            opened.pop(descriptor, None)
            real_close(descriptor)

        @staticmethod
        def rename(source, target):
            os.rename(source, target)

    def open_descriptor(path, flags, mode):  # noqa: ANN001, ANN202
        if Path(path).is_dir():
            raise AssertionError("Windows export opened a directory descriptor")
        descriptor = real_open(path, flags, mode)
        opened[descriptor] = flags
        return descriptor

    monkeypatch.setattr(publication, "_platform_name", lambda: "nt")
    monkeypatch.setattr(publication, "os", PublicationOS())
    monkeypatch.setattr(windows, "os", WindowsOS())
    monkeypatch.setattr(windows, "open_file_descriptor", open_descriptor)
    return SimpleNamespace(opened=opened, synced_flags=synced_flags)


@pytest.fixture
def substitution_guard(monkeypatch):
    guarded: dict[Path, int] = {}
    blocked: list[Path] = []

    @contextmanager
    def fake_hold(path):  # noqa: ANN001, ANN202
        absolute = Path(os.path.abspath(path))
        guarded[absolute] = guarded.get(absolute, 0) + 1
        try:
            yield
        finally:
            if guarded[absolute] == 1:
                del guarded[absolute]
            else:
                guarded[absolute] -= 1

    def attack(path: Path, preserved: Path, external: Path) -> None:
        absolute = Path(os.path.abspath(path))
        if absolute in guarded:
            blocked.append(absolute)
            return
        path.rename(preserved)
        path.symlink_to(external, target_is_directory=True)

    monkeypatch.setattr(windows, "hold_directory", fake_hold)
    return attack, blocked


def test_windows_export_uses_writable_file_sync_and_no_directory_sync(
    repository,
    registry_snapshot,
    tmp_path,
    windows_export_semantics,
):
    active, candidate = _active_export_source(repository, registry_snapshot)
    parent = tmp_path / "exports"
    parent.mkdir()
    export_id = "predictor-v3-candidate-export-r1"
    target = parent / export_id

    publication.publish_deployment_export(
        parent,
        target,
        export_id,
        active=active,
        candidate=candidate,
    )

    assert target.is_dir()
    assert sorted(path.name for path in target.iterdir()) == [
        "checksums.sha256",
        "export_summary.json",
        "manifest.json",
        "model.pkl",
    ]
    assert windows_export_semantics.opened == {}
    assert len(windows_export_semantics.synced_flags) == 4
    assert all(
        flags & os.O_ACCMODE != os.O_RDONLY
        for flags in windows_export_semantics.synced_flags
    )


@pytest.mark.parametrize("failure_stage", ["before-publication", "after-publication"])
def test_windows_export_failure_cleans_only_new_stage_or_final(
    repository,
    registry_snapshot,
    tmp_path,
    monkeypatch,
    windows_export_semantics,
    failure_stage,
):
    active, candidate = _active_export_source(repository, registry_snapshot)
    parent = tmp_path / "exports"
    parent.mkdir()
    existing = parent / "existing-export"
    existing.mkdir()
    (existing / "preserved.txt").write_text("preserved", encoding="utf-8")
    export_id = "predictor-v3-candidate-export-r1"
    target = parent / export_id

    if failure_stage == "before-publication":
        monkeypatch.setattr(
            publication,
            "_verify_export",
            lambda *_args: (_ for _ in ()).throw(OSError("verify failed")),
        )
    else:
        calls = {"parent": 0}
        original = publication._fsync_directory

        def fail_after_publish(path):  # noqa: ANN001, ANN202
            if path == parent:
                calls["parent"] += 1
                if calls["parent"] == 1:
                    raise OSError("post-publication durability failed")
            return original(path)

        monkeypatch.setattr(publication, "_fsync_directory", fail_after_publish)

    with pytest.raises(OSError):
        publication.publish_deployment_export(
            parent,
            target,
            export_id,
            active=active,
            candidate=candidate,
        )

    assert not target.exists()
    assert not tuple(parent.glob(".*.staging"))
    assert (existing / "preserved.txt").read_text(encoding="utf-8") == "preserved"


def test_windows_export_parent_substitution_cannot_mutate_external_directory(
    repository,
    registry_snapshot,
    tmp_path,
    monkeypatch,
    windows_export_semantics,
    substitution_guard,
):
    active, candidate = _active_export_source(repository, registry_snapshot)
    parent = tmp_path / "exports"
    parent.mkdir()
    external = tmp_path / "external"
    external.mkdir()
    (external / "sentinel.txt").write_text("unchanged", encoding="utf-8")
    preserved = tmp_path / "preserved-exports"
    attack, blocked = substitution_guard

    real_rename = windows.rename_directory_no_replace

    def attacked_rename(source, target):  # noqa: ANN001, ANN202
        attack(parent, preserved, external)
        real_rename(source, target)

    monkeypatch.setattr(windows, "rename_directory_no_replace", attacked_rename)
    export_id = "predictor-v3-candidate-export-r1"
    target = parent / export_id

    publication.publish_deployment_export(
        parent,
        target,
        export_id,
        active=active,
        candidate=candidate,
    )

    assert blocked == [parent]
    assert (external / "sentinel.txt").read_text(encoding="utf-8") == "unchanged"
    assert [path.name for path in external.iterdir()] == ["sentinel.txt"]
    assert target.is_dir()


def test_windows_export_stage_substitution_cannot_write_external_artifacts(
    repository,
    registry_snapshot,
    tmp_path,
    monkeypatch,
    windows_export_semantics,
    substitution_guard,
):
    active, candidate = _active_export_source(repository, registry_snapshot)
    parent = tmp_path / "exports"
    parent.mkdir()
    external = tmp_path / "external"
    external.mkdir()
    (external / "sentinel.txt").write_text("unchanged", encoding="utf-8")
    preserved = tmp_path / "preserved-stage"
    attack, blocked = substitution_guard
    real_copy = publication.shutil.copyfile

    def attacked_copy(source, target):  # noqa: ANN001, ANN202
        attack(Path(target).parent, preserved, external)
        return real_copy(source, target)

    monkeypatch.setattr(publication.shutil, "copyfile", attacked_copy)
    export_id = "predictor-v3-candidate-export-r1"
    target = parent / export_id

    publication.publish_deployment_export(
        parent,
        target,
        export_id,
        active=active,
        candidate=candidate,
    )

    assert len(blocked) == 1
    assert blocked[0].name.endswith(".staging")
    assert [path.name for path in external.iterdir()] == ["sentinel.txt"]
    assert target.is_dir()


def test_native_windows_export_move_is_write_through_and_no_replace(monkeypatch):
    calls: list[tuple[str, str, int]] = []

    class MoveFile:
        argtypes = None
        restype = None

        def __call__(self, source: str, target: str, flags: int) -> int:
            calls.append((source, target, flags))
            return 1

    move_file = MoveFile()
    monkeypatch.setattr(windows, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(
        ctypes,
        "WinDLL",
        lambda *_args, **_kwargs: SimpleNamespace(MoveFileExW=move_file),
        raising=False,
    )

    windows.rename_directory_no_replace("stage", "final")

    assert calls == [("stage", "final", 0x8)]
