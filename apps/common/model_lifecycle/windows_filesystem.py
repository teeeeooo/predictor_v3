"""Windows path-based primitives for the shared lifecycle filesystem owner."""

from __future__ import annotations

import os
import stat
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from .durability_errors import PostRenameDurabilityError
from .errors import LifecycleFilesystemError

if TYPE_CHECKING:
    from .filesystem import LifecycleFilesystem


class WindowsFilesystemPrimitives:
    """Avoid unsupported directory descriptors while retaining identity checks."""

    def __init__(self, filesystem: LifecycleFilesystem) -> None:
        self._filesystem = filesystem

    def create_child_directory(self, parent: Path, path: Path) -> None:
        parent_entry = self._filesystem.require_directory(parent)
        path.mkdir()
        self._filesystem._require_unchanged_directory(parent, parent_entry)

    @contextmanager
    def open_exclusive_descriptor(self, path: Path, flags: int):
        parent_entry = self._filesystem.require_directory(path.parent)
        descriptor = os.open(path, flags, 0o600)
        try:
            self._filesystem._require_opened_regular(path, descriptor)
            self._filesystem._require_unchanged_directory(
                path.parent,
                parent_entry,
            )
            yield descriptor
        finally:
            os.close(descriptor)

    def publish_directory(
        self,
        staging: Path,
        final: Path,
        stage_entry: os.stat_result,
        after_replace,
    ) -> None:  # noqa: ANN001
        source_parent = self._filesystem.require_directory(staging.parent)
        target_parent = self._filesystem.require_directory(final.parent)
        self._filesystem._require_unchanged_directory(staging, stage_entry)
        _move_path(staging, final, replace_existing=False)
        try:
            self._filesystem._require_unchanged_directory(final, stage_entry)
            self._filesystem._require_unchanged_directory(
                staging.parent,
                source_parent,
            )
            self._filesystem._require_unchanged_directory(
                final.parent,
                target_parent,
            )
            if after_replace is not None:
                after_replace()
        except Exception as exc:
            raise PostRenameDurabilityError(
                "Candidate rename completed but durability failed"
            ) from exc

    def replace_file(
        self,
        temporary: Path,
        destination: Path,
        after_replace,
    ) -> None:  # noqa: ANN001
        parent_entry = self._filesystem.require_directory(temporary.parent)
        temporary_entry = self._filesystem.require_regular_file(temporary)
        _move_path(temporary, destination, replace_existing=True)
        try:
            self._filesystem._require_unchanged_regular(
                destination,
                temporary_entry,
            )
            self._filesystem._require_unchanged_directory(
                destination.parent,
                parent_entry,
            )
            if after_replace is not None:
                after_replace()
        except Exception as exc:
            raise PostRenameDurabilityError(
                "Active rename completed but durability failed"
            ) from exc

    def publish_file_exclusive(
        self,
        temporary: Path,
        destination: Path,
        temporary_entry: os.stat_result,
        after_publish,
    ) -> None:  # noqa: ANN001
        parent_entry = self._filesystem.require_directory(temporary.parent)
        _move_path(temporary, destination, replace_existing=False)
        published = destination.lstat()
        if (
            self._filesystem._is_link_like(published)
            or not stat.S_ISREG(published.st_mode)
            or (temporary_entry.st_dev, temporary_entry.st_ino)
            != (published.st_dev, published.st_ino)
        ):
            raise LifecycleFilesystemError(
                "exclusive lifecycle publication identity mismatch"
            )
        try:
            self._filesystem._require_unchanged_directory(
                temporary.parent,
                parent_entry,
            )
            if after_publish is not None:
                after_publish()
        except Exception as exc:
            raise PostRenameDurabilityError(
                "file publication committed but durability failed"
            ) from exc

    def rollback_directory(self, final: Path, staging: Path) -> None:
        final_entry = self._filesystem.require_directory(final)
        source_parent = self._filesystem.require_directory(final.parent)
        target_parent = self._filesystem.require_directory(staging.parent)
        _move_path(final, staging, replace_existing=False)
        self._filesystem._require_unchanged_directory(staging, final_entry)
        self._filesystem._require_unchanged_directory(
            final.parent,
            source_parent,
        )
        self._filesystem._require_unchanged_directory(
            staging.parent,
            target_parent,
        )

    def remove_file(self, path: Path, *, missing_ok: bool) -> None:
        try:
            current = path.lstat()
        except FileNotFoundError:
            if missing_ok:
                return
            raise
        if (
            self._filesystem._is_link_like(current)
            or not stat.S_ISREG(current.st_mode)
        ):
            raise LifecycleFilesystemError(
                f"lifecycle artifact is not an owned regular file: {path.name}"
            )
        self._filesystem._require_resolved_owner(path.resolve(strict=True))
        parent_entry = self._filesystem.require_directory(path.parent)
        os.unlink(path)
        self._filesystem._require_unchanged_directory(path.parent, parent_entry)


def _move_path(source: Path, destination: Path, *, replace_existing: bool) -> None:
    """Use write-through Windows rename; retain stdlib calls for host simulation."""
    if os.name != "nt":
        if not replace_existing and destination.exists():
            raise FileExistsError(f"lifecycle destination exists: {destination.name}")
        operation = os.replace if replace_existing else os.rename
        operation(source, destination)
        return
    import ctypes

    move_file = ctypes.WinDLL("kernel32", use_last_error=True).MoveFileExW
    move_file.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
    move_file.restype = ctypes.c_int
    flags = 0x8 | (0x1 if replace_existing else 0)  # WRITE_THROUGH | REPLACE
    if not move_file(str(source), str(destination), flags):
        raise ctypes.WinError(ctypes.get_last_error())
