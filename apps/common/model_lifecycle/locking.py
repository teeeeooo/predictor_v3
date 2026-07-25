"""Small cross-platform filesystem lock for lifecycle state transitions."""

from __future__ import annotations

import os
import stat
import sys
from contextlib import contextmanager
from pathlib import Path

from .errors import LifecycleFilesystemError
from .filesystem import LifecycleFilesystem


@contextmanager
def lifecycle_lock(path: Path, *, filesystem: LifecycleFilesystem):
    absolute_root = filesystem.root
    absolute_path = Path(os.path.abspath(path))
    try:
        relative = absolute_path.relative_to(absolute_root)
    except ValueError as exc:
        raise LifecycleFilesystemError("lifecycle lock escapes workspace root") from exc
    if len(relative.parts) != 1:
        raise LifecycleFilesystemError("lifecycle lock must be workspace-owned")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    if os.name == "nt":
        descriptor = _open_windows_lock(absolute_path, flags)
        root_descriptor = None
    else:
        root_context = filesystem.trusted_directory(absolute_root)
        root_descriptor = root_context.__enter__()
        try:
            descriptor = os.open(relative.name, flags, 0o600, dir_fd=root_descriptor)
        except BaseException:
            root_context.__exit__(*sys.exc_info())
            raise
    locked = False
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise LifecycleFilesystemError("lifecycle lock is not a regular file")
        current = (
            absolute_path.lstat()
            if root_descriptor is None
            else os.stat(relative.name, dir_fd=root_descriptor, follow_symlinks=False)
        )
        if (
            stat.S_ISLNK(current.st_mode)
            or not stat.S_ISREG(current.st_mode)
            or (current.st_dev, current.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise LifecycleFilesystemError("lifecycle lock changed during validation")
        if opened.st_size == 0:
            os.write(descriptor, b"\0")
            os.fsync(descriptor)
        os.lseek(descriptor, 0, os.SEEK_SET)
        _lock(descriptor)
        locked = True
        yield
    finally:
        if locked:
            os.lseek(descriptor, 0, os.SEEK_SET)
            _unlock(descriptor)
        os.close(descriptor)
        if root_descriptor is not None:
            root_context.__exit__(None, None, None)


def _open_windows_lock(path: Path, flags: int) -> int:
    """Retain the existing Windows lock path while validating its object type."""
    try:
        entry = path.lstat()
    except FileNotFoundError:
        entry = None
    if entry is not None and (
        stat.S_ISLNK(entry.st_mode) or not stat.S_ISREG(entry.st_mode)
    ):
        raise LifecycleFilesystemError("lifecycle lock is not a regular file")
    return os.open(path, flags, 0o600)


def _lock(descriptor: int) -> None:
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(descriptor, msvcrt.LK_LOCK, 1)
    else:
        import fcntl

        fcntl.flock(descriptor, fcntl.LOCK_EX)


def _unlock(descriptor: int) -> None:
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(descriptor, fcntl.LOCK_UN)
