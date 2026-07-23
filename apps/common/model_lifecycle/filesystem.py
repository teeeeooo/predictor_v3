"""Symlink-safe filesystem primitives for the model lifecycle workspace."""

from __future__ import annotations

import json
import os
import stat
from contextlib import contextmanager
from pathlib import Path

from .errors import LifecycleFilesystemError


class LifecycleFilesystem:
    """Validate lifecycle ownership with lstat, resolved containment, and fstat."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(os.path.abspath(root))
        self._resolved_root = self.root.resolve(strict=False)

    def ensure_directory(self, path: Path) -> None:
        self._require_lexical_owner(path, allow_root=True)
        if path == self.root:
            path.mkdir(parents=True, exist_ok=True)
        else:
            self.ensure_directory(path.parent)
            try:
                path.mkdir()
            except FileExistsError:
                pass
        self.require_directory(path)

    def create_child_directory(self, parent: Path, name: str) -> Path:
        self.ensure_directory(parent)
        with self._directory_fd(parent) as parent_fd:
            os.mkdir(name, dir_fd=parent_fd)
        path = parent / name
        self.require_directory(path)
        return path

    def require_directory(self, path: Path) -> os.stat_result:
        self._require_lexical_owner(path, allow_root=True)
        entry = path.lstat()
        if stat.S_ISLNK(entry.st_mode) or not stat.S_ISDIR(entry.st_mode):
            raise LifecycleFilesystemError(
                f"lifecycle directory is not an owned regular directory: {path.name}"
            )
        resolved = path.resolve(strict=True)
        self._require_resolved_owner(resolved, allow_root=True)
        with self._directory_fd(path) as descriptor:
            opened = os.fstat(descriptor)
        if (entry.st_dev, entry.st_ino) != (opened.st_dev, opened.st_ino):
            raise LifecycleFilesystemError("lifecycle directory changed during validation")
        return entry

    def require_regular_file(self, path: Path) -> os.stat_result:
        self._require_lexical_owner(path)
        entry = path.lstat()
        if stat.S_ISLNK(entry.st_mode) or not stat.S_ISREG(entry.st_mode):
            raise LifecycleFilesystemError(
                f"lifecycle artifact is not an owned regular file: {path.name}"
            )
        self._require_resolved_owner(path.resolve(strict=True))
        with self.open_regular(path):
            pass
        return entry

    @contextmanager
    def open_regular(self, path: Path):
        self._require_lexical_owner(path)
        entry = path.lstat()
        if stat.S_ISLNK(entry.st_mode) or not stat.S_ISREG(entry.st_mode):
            raise LifecycleFilesystemError(
                f"lifecycle artifact is not an owned regular file: {path.name}"
            )
        self._require_resolved_owner(path.resolve(strict=True))
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode):
                raise LifecycleFilesystemError(
                    f"lifecycle artifact is not a regular file: {path.name}"
                )
            if (entry.st_dev, entry.st_ino) != (opened.st_dev, opened.st_ino):
                raise LifecycleFilesystemError(
                    "lifecycle artifact changed during validation"
                )
            yield os.fdopen(descriptor, "rb", closefd=False)
        finally:
            os.close(descriptor)

    def read_json(self, path: Path) -> dict[str, object]:
        self.require_regular_file(path)
        with self.open_regular(path) as source:
            return json.loads(source.read().decode("utf-8"))

    def write_json_exclusive(self, path: Path, payload: object) -> None:
        encoded = (
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8")
        with self.open_exclusive(path) as target:
            target.write(encoded)

    @contextmanager
    def open_exclusive(self, path: Path):
        self._require_lexical_owner(path)
        self.require_directory(path.parent)
        with self._directory_fd(path.parent) as parent_fd:
            flags = (
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | getattr(os, "O_NOFOLLOW", 0)
            )
            descriptor = os.open(path.name, flags, 0o600, dir_fd=parent_fd)
            try:
                with os.fdopen(descriptor, "wb", closefd=False) as target:
                    yield target
                    target.flush()
                    os.fsync(descriptor)
            finally:
                os.close(descriptor)

    def entry_exists(self, path: Path) -> bool:
        self._require_lexical_owner(path, allow_root=True)
        try:
            path.lstat()
        except FileNotFoundError:
            return False
        return True

    def is_owned_directory(self, path: Path) -> bool:
        try:
            self.require_directory(path)
        except (FileNotFoundError, LifecycleFilesystemError):
            return False
        return True

    def publish_directory(self, staging: Path, final: Path) -> None:
        stage_entry = self.require_directory(staging)
        self.fsync_tree(staging)
        self.require_directory(staging.parent)
        self.require_directory(final.parent)
        if self.entry_exists(final):
            raise LifecycleFilesystemError(
                f"final Candidate path already exists: {final.name}"
            )
        with self._directory_fd(staging.parent) as source_fd, (
            self._directory_fd(final.parent)
        ) as target_fd:
            current = os.stat(staging.name, dir_fd=source_fd, follow_symlinks=False)
            if (
                not stat.S_ISDIR(current.st_mode)
                or (stage_entry.st_dev, stage_entry.st_ino)
                != (current.st_dev, current.st_ino)
            ):
                raise LifecycleFilesystemError(
                    "Candidate staging changed before atomic publication"
                )
            os.replace(
                staging.name,
                final.name,
                src_dir_fd=source_fd,
                dst_dir_fd=target_fd,
            )
            os.fsync(target_fd)

    def replace_file(self, temporary: Path, destination: Path) -> None:
        self.require_regular_file(temporary)
        self.require_directory(temporary.parent)
        if self.entry_exists(destination):
            self.require_regular_file(destination)
        with self._directory_fd(temporary.parent) as parent_fd:
            os.replace(
                temporary.name,
                destination.name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
            )
            os.fsync(parent_fd)

    def fsync_tree(self, path: Path) -> None:
        self.require_directory(path)
        for item in sorted(path.rglob("*")):
            if item.is_symlink():
                raise LifecycleFilesystemError(
                    f"symlink is not allowed in Candidate staging: {item.name}"
                )
            if item.is_file():
                self.require_regular_file(item)
                with self.open_regular(item) as source:
                    os.fsync(source.fileno())
            elif item.is_dir():
                self.require_directory(item)
            else:
                raise LifecycleFilesystemError(
                    f"unsupported Candidate filesystem object: {item.name}"
                )
        with self._directory_fd(path) as descriptor:
            os.fsync(descriptor)

    @contextmanager
    def _directory_fd(self, path: Path):
        self._require_lexical_owner(path, allow_root=True)
        entry = path.lstat()
        if stat.S_ISLNK(entry.st_mode) or not stat.S_ISDIR(entry.st_mode):
            raise LifecycleFilesystemError(
                f"lifecycle directory is not an owned regular directory: {path.name}"
            )
        self._require_resolved_owner(path.resolve(strict=True), allow_root=True)
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISDIR(opened.st_mode):
                raise LifecycleFilesystemError(
                    f"lifecycle path is not a directory: {path.name}"
                )
            if (entry.st_dev, entry.st_ino) != (opened.st_dev, opened.st_ino):
                raise LifecycleFilesystemError(
                    "lifecycle directory changed during validation"
                )
            yield descriptor
        finally:
            os.close(descriptor)

    def _require_lexical_owner(self, path: Path, *, allow_root: bool = False) -> None:
        absolute = Path(os.path.abspath(path))
        try:
            relative = absolute.relative_to(self.root)
        except ValueError as exc:
            raise LifecycleFilesystemError(
                "lifecycle path is outside the workspace root"
            ) from exc
        if not allow_root and not relative.parts:
            raise LifecycleFilesystemError("artifact path cannot be the workspace root")

    def _require_resolved_owner(
        self, resolved: Path, *, allow_root: bool = False
    ) -> None:
        try:
            relative = resolved.relative_to(self._resolved_root)
        except ValueError as exc:
            raise LifecycleFilesystemError(
                "resolved lifecycle path escapes the workspace root"
            ) from exc
        if not allow_root and not relative.parts:
            raise LifecycleFilesystemError("resolved artifact cannot be workspace root")
