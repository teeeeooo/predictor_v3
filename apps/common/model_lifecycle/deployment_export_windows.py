"""Windows durability and path-binding primitives for deployment export."""

from __future__ import annotations

import ctypes
import os
import stat
from contextlib import ExitStack, contextmanager
from pathlib import Path

from .windows_handles import hold_directory, open_file_descriptor


@contextmanager
def hold_export_parent(parent: Path):
    """Pin the canonical filesystem path to one export destination parent."""
    expected = {
        component: _require_regular_directory(component)
        for component in _directory_chain(parent)
    }
    with ExitStack() as stack:
        for component in expected:
            stack.enter_context(hold_directory(component))
        for component, identity in expected.items():
            if _require_regular_directory(component) != identity:
                raise OSError("Export destination changed during validation")
        yield


def fsync_regular_file(path: Path) -> None:
    flags = os.O_RDWR | getattr(os, "O_BINARY", 0)
    descriptor = open_file_descriptor(path, flags, 0o600)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise OSError(f"Export artifact is not a regular file: {path.name}")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def rename_directory_no_replace(source: Path, target: Path) -> None:
    """Publish one directory without replacement and with write-through."""
    if os.name != "nt":
        os.rename(source, target)
        return
    move_file = ctypes.WinDLL("kernel32", use_last_error=True).MoveFileExW
    move_file.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
    move_file.restype = ctypes.c_int
    if move_file(str(source), str(target), 0x8):  # MOVEFILE_WRITE_THROUGH
        return
    error = ctypes.get_last_error()
    if error in {80, 183}:
        raise FileExistsError(error, "immutable export already exists", target)
    raise ctypes.WinError(error)


def directory_identity(path: Path) -> tuple[int, int]:
    return _require_regular_directory(path)


def require_directory_identity(
    path: Path,
    expected: tuple[int, int],
) -> None:
    if _require_regular_directory(path) != expected:
        raise OSError("Published export directory identity changed")


def _directory_chain(path: Path) -> tuple[Path, ...]:
    absolute = Path(os.path.abspath(path))
    chain = [absolute]
    while chain[-1].parent != chain[-1]:
        chain.append(chain[-1].parent)
    chain.reverse()
    return tuple(chain)


def _require_regular_directory(path: Path) -> tuple[int, int]:
    entry = path.lstat()
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    attributes = getattr(entry, "st_file_attributes", 0)
    if (
        stat.S_ISLNK(entry.st_mode)
        or not stat.S_ISDIR(entry.st_mode)
        or bool(reparse and attributes & reparse)
    ):
        raise OSError(f"Export destination is not a regular directory: {path}")
    return entry.st_dev, entry.st_ino
