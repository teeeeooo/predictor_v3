"""Small cross-platform filesystem lock for lifecycle state transitions."""

from __future__ import annotations

import os
import stat
from contextlib import contextmanager
from pathlib import Path

from .errors import LifecycleFilesystemError


@contextmanager
def lifecycle_lock(path: Path, *, root: Path):
    absolute_root = Path(os.path.abspath(root))
    absolute_path = Path(os.path.abspath(path))
    try:
        relative = absolute_path.relative_to(absolute_root)
    except ValueError as exc:
        raise LifecycleFilesystemError("lifecycle lock escapes workspace root") from exc
    if len(relative.parts) != 1:
        raise LifecycleFilesystemError("lifecycle lock must be workspace-owned")
    try:
        entry = absolute_path.lstat()
    except FileNotFoundError:
        entry = None
    if entry is not None and (
        stat.S_ISLNK(entry.st_mode) or not stat.S_ISREG(entry.st_mode)
    ):
        raise LifecycleFilesystemError("lifecycle lock is not a regular file")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(absolute_path, flags, 0o600)
    locked = False
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise LifecycleFilesystemError("lifecycle lock is not a regular file")
        current = absolute_path.lstat()
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
