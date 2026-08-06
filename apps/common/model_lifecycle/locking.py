"""Small cross-platform filesystem lock for lifecycle state transitions."""

from __future__ import annotations

import os
import stat
import sys
from errno import EACCES, EAGAIN, EDEADLK
from contextlib import contextmanager
from pathlib import Path

from .errors import LifecycleFilesystemError
from .filesystem import LifecycleFilesystem


@contextmanager
def lifecycle_lock(path: Path, *, filesystem: LifecycleFilesystem):
    with _lifecycle_lock(path, filesystem=filesystem, blocking=True) as acquired:
        if not acquired:
            raise LifecycleFilesystemError("blocking lifecycle lock was unavailable")
        yield


@contextmanager
def try_lifecycle_lock(path: Path, *, filesystem: LifecycleFilesystem):
    """Yield whether one process-lifetime lock could be acquired immediately."""
    with _lifecycle_lock(path, filesystem=filesystem, blocking=False) as acquired:
        yield acquired


@contextmanager
def _lifecycle_lock(
    path: Path,
    *,
    filesystem: LifecycleFilesystem,
    blocking: bool,
):
    absolute_root = filesystem.root
    absolute_path = Path(os.path.abspath(path))
    try:
        relative = absolute_path.relative_to(absolute_root)
    except ValueError as exc:
        raise LifecycleFilesystemError("lifecycle lock escapes workspace root") from exc
    if len(relative.parts) != 1:
        raise LifecycleFilesystemError("lifecycle lock must be workspace-owned")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    platform_name = filesystem.platform_name
    if platform_name == "nt":
        lock_context = filesystem.open_windows_lock_descriptor(
            absolute_path,
            flags,
        )
        descriptor = lock_context.__enter__()
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
        try:
            _lock(descriptor, blocking=blocking, platform_name=platform_name)
        except OSError as exc:
            if blocking or exc.errno not in {EACCES, EAGAIN, EDEADLK}:
                raise
            yield False
        else:
            locked = True
            yield True
    finally:
        if locked:
            os.lseek(descriptor, 0, os.SEEK_SET)
            _unlock(descriptor, platform_name=platform_name)
        if root_descriptor is None:
            lock_context.__exit__(None, None, None)
        else:
            os.close(descriptor)
            root_context.__exit__(None, None, None)


def _lock(descriptor: int, *, blocking: bool, platform_name: str) -> None:
    if platform_name == "nt":
        import msvcrt

        mode = msvcrt.LK_LOCK if blocking else msvcrt.LK_NBLCK
        msvcrt.locking(descriptor, mode, 1)
    else:
        import fcntl

        flags = fcntl.LOCK_EX
        if not blocking:
            flags |= fcntl.LOCK_NB
        fcntl.flock(descriptor, flags)


def _unlock(descriptor: int, *, platform_name: str) -> None:
    if platform_name == "nt":
        import msvcrt

        msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(descriptor, fcntl.LOCK_UN)
