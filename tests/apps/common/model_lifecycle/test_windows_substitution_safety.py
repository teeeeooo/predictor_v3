"""Adversarial Windows root-substitution safety regressions."""

from __future__ import annotations

import ctypes
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps.common.model_lifecycle import filesystem as filesystem_module
from apps.common.model_lifecycle.filesystem import LifecycleFilesystem
from apps.common.model_lifecycle.locking import lifecycle_lock
from apps.common.model_lifecycle import windows_filesystem as windows_module


@pytest.fixture
def simulated_windows(monkeypatch):
    fake_msvcrt = SimpleNamespace(
        LK_LOCK=1,
        LK_NBLCK=2,
        LK_UNLCK=3,
        locking=lambda *_args: None,
    )
    monkeypatch.setattr(filesystem_module, "_platform_name", lambda: "nt")
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)


@pytest.fixture
def substitution_attack(monkeypatch):
    guarded: dict[Path, int] = {}
    blocked: list[Path] = []

    @contextmanager
    def fake_directory_guard(path: Path):
        absolute = Path(os.path.abspath(path))
        guarded[absolute] = guarded.get(absolute, 0) + 1
        try:
            yield
        finally:
            remaining = guarded[absolute] - 1
            if remaining:
                guarded[absolute] = remaining
            else:
                del guarded[absolute]

    monkeypatch.setattr(
        windows_module,
        "_open_directory_guard",
        fake_directory_guard,
    )

    def inject(root: Path, preserved: Path, external: Path) -> None:
        absolute = Path(os.path.abspath(root))
        if absolute in guarded:
            blocked.append(absolute)
            return
        root.rename(preserved)
        root.symlink_to(external, target_is_directory=True)

    return inject, blocked


def _tree_state(root: Path) -> dict[str, bytes | None]:
    return {
        str(path.relative_to(root)): path.read_bytes() if path.is_file() else None
        for path in sorted(root.rglob("*"))
    }


def test_windows_lock_and_exclusive_creation_block_root_substitution(
    tmp_path,
    monkeypatch,
    simulated_windows,
    substitution_attack,
):
    inject, blocked = substitution_attack
    root = tmp_path / "lifecycle"
    external = tmp_path / "external"
    preserved = tmp_path / "preserved"
    external.mkdir()
    filesystem = LifecycleFilesystem(root)
    filesystem.ensure_directory(root)
    before = _tree_state(external)
    real_open = windows_module._open_file_descriptor

    def attacked_open(path, flags, mode):  # noqa: ANN001, ANN202
        inject(root, preserved, external)
        return real_open(path, flags, mode)

    monkeypatch.setattr(windows_module, "_open_file_descriptor", attacked_open)

    with lifecycle_lock(root / ".lifecycle-write.lock", filesystem=filesystem):
        pass
    with filesystem.open_exclusive(root / "permit.json") as target:
        target.write(b"safe\n")

    assert len(blocked) == 2
    assert _tree_state(external) == before
    assert not (external / ".lifecycle-write.lock").exists()
    assert not (external / "permit.json").exists()


@pytest.mark.parametrize("publication_name", ["candidate", "run-evidence"])
def test_windows_directory_publication_blocks_parent_substitution(
    tmp_path,
    monkeypatch,
    simulated_windows,
    substitution_attack,
    publication_name,
):
    inject, blocked = substitution_attack
    root = tmp_path / "lifecycle"
    external = tmp_path / "external"
    external.mkdir()
    filesystem = LifecycleFilesystem(root)
    filesystem.ensure_directory(root)
    staging_parent = filesystem.create_child_directory(root, ".staging")
    staging = filesystem.create_child_directory(
        staging_parent,
        f".{publication_name}.tmp",
    )
    (staging / "payload.json").write_text("{}\n", encoding="utf-8")
    final_parent = filesystem.create_child_directory(
        root,
        f"{publication_name}-finals",
    )
    preserved = root / f".{publication_name}-finals-preserved"
    final = final_parent / publication_name
    before = _tree_state(external)
    real_move = windows_module._move_path

    def attacked_move(source, destination, *, replace_existing):  # noqa: ANN001, ANN202
        inject(final_parent, preserved, external)
        return real_move(source, destination, replace_existing=replace_existing)

    monkeypatch.setattr(windows_module, "_move_path", attacked_move)

    filesystem.publish_directory(staging, final)

    assert blocked == [final_parent]
    assert _tree_state(external) == before
    assert (final / "payload.json").read_text(encoding="utf-8") == "{}\n"


def test_windows_active_rollback_and_removal_block_parent_substitution(
    tmp_path,
    monkeypatch,
    simulated_windows,
    substitution_attack,
):
    inject, blocked = substitution_attack
    root = tmp_path / "lifecycle"
    external = tmp_path / "external"
    preserved = tmp_path / "preserved"
    external.mkdir()
    filesystem = LifecycleFilesystem(root)
    filesystem.ensure_directory(root)
    temporary = root / ".active.tmp"
    active = root / "active.json"
    temporary.write_text("new\n", encoding="utf-8")
    active.write_text("old\n", encoding="utf-8")
    (external / temporary.name).write_text("outside-new\n", encoding="utf-8")
    (external / active.name).write_text("outside-old\n", encoding="utf-8")
    final = filesystem.create_child_directory(root, "candidate-final")
    (external / final.name).mkdir()
    removable = root / "recovery-marker.json"
    removable.write_text("inside\n", encoding="utf-8")
    (external / removable.name).write_text("outside\n", encoding="utf-8")
    before = _tree_state(external)
    real_move = windows_module._move_path
    real_unlink = windows_module.os.unlink

    def attacked_move(source, destination, *, replace_existing):  # noqa: ANN001, ANN202
        inject(root, preserved, external)
        return real_move(source, destination, replace_existing=replace_existing)

    def attacked_unlink(path, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        inject(root, preserved, external)
        return real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(windows_module, "_move_path", attacked_move)
    monkeypatch.setattr(windows_module.os, "unlink", attacked_unlink)

    filesystem.replace_file(temporary, active)
    filesystem.rollback_directory(final, root / ".candidate-rollback")
    filesystem.remove_file(removable)

    assert len(blocked) == 3
    assert _tree_state(external) == before
    assert active.read_text(encoding="utf-8") == "new\n"
    assert (root / ".candidate-rollback").is_dir()
    assert not removable.exists()


def test_native_windows_guards_deny_delete_sharing_and_reparse_following(
    monkeypatch,
):
    calls: list[tuple[object, ...]] = []

    class NativeCall:
        argtypes = None
        restype = None

        def __init__(self, name: str, result: int):
            self.name = name
            self.result = result

        def __call__(self, *args):  # noqa: ANN002, ANN202
            calls.append((self.name, *args))
            return self.result

    kernel32 = SimpleNamespace(
        CreateFileW=NativeCall("create", 101),
        CloseHandle=NativeCall("close", 1),
    )
    fake_msvcrt = SimpleNamespace(open_osfhandle=lambda handle, flags: 202)
    monkeypatch.setattr(windows_module.os, "name", "nt")
    monkeypatch.setattr(
        ctypes,
        "WinDLL",
        lambda *_args, **_kwargs: kernel32,
        raising=False,
    )
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)

    with windows_module._open_directory_guard(Path("lifecycle")):
        pass
    descriptor = windows_module._open_file_descriptor(
        Path("permit.json"),
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600,
    )

    directory_open, directory_close, file_open = calls
    assert descriptor == 202
    assert directory_open[3] == 0x1 | 0x2
    assert directory_open[6] == 0x02000000 | 0x00200000
    assert directory_close == ("close", 101)
    assert file_open[3] == 0x1 | 0x2
    assert file_open[5] == 1
    assert file_open[6] == 0x80 | 0x00200000
