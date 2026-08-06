"""Symlink-safe filesystem primitives for the model lifecycle workspace."""

from __future__ import annotations

import json
import os
import stat
from contextlib import contextmanager, nullcontext
from pathlib import Path

from .errors import LifecycleFilesystemError
from .durability_errors import PostRenameDurabilityError
from .windows_filesystem import WindowsFilesystemPrimitives


class LifecycleFilesystem:
    """Validate lifecycle ownership with lstat, resolved containment, and fstat."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(os.path.abspath(root))
        self._resolved_root = self.root.resolve(strict=False)
        self.platform_name = _platform_name()
        self._windows = (
            WindowsFilesystemPrimitives(self)
            if self.platform_name == "nt" else None
        )

    def ensure_directory(self, path: Path) -> None:
        self._require_lexical_owner(path, allow_root=True)
        if path == self.root:
            path.mkdir(parents=True, exist_ok=True)
        else:
            self.ensure_directory(path.parent)
            try:
                if self._windows is not None:
                    self._windows.create_child_directory(path.parent, path)
                else:
                    path.mkdir()
            except FileExistsError:
                pass
        self.require_directory(path)

    def create_child_directory(self, parent: Path, name: str) -> Path:
        self.ensure_directory(parent)
        path = parent / name
        if self._windows is not None:
            self._windows.create_child_directory(parent, path)
        else:
            with self._directory_fd(parent) as parent_fd:
                os.mkdir(name, dir_fd=parent_fd)
        self.require_directory(path)
        return path

    def require_directory(self, path: Path) -> os.stat_result:
        self._require_lexical_owner(path, allow_root=True)
        entry = path.lstat()
        if self._is_link_like(entry) or not stat.S_ISDIR(entry.st_mode):
            raise LifecycleFilesystemError(
                f"lifecycle directory is not an owned regular directory: {path.name}"
            )
        resolved = path.resolve(strict=True)
        self._require_resolved_owner(resolved, allow_root=True)
        if self._windows is not None:
            self._require_unchanged_directory(path, entry)
            return entry
        with self._directory_fd(path) as descriptor:
            opened = os.fstat(descriptor)
        if (entry.st_dev, entry.st_ino) != (opened.st_dev, opened.st_ino):
            raise LifecycleFilesystemError("lifecycle directory changed during validation")
        return entry

    def require_regular_file(self, path: Path) -> os.stat_result:
        self._require_lexical_owner(path)
        entry = path.lstat()
        if self._is_link_like(entry) or not stat.S_ISREG(entry.st_mode):
            raise LifecycleFilesystemError(
                f"lifecycle artifact is not an owned regular file: {path.name}"
            )
        self._require_resolved_owner(path.resolve(strict=True))
        with self.open_regular(path):
            pass
        return entry

    @contextmanager
    def open_regular(self, path: Path, *, writable: bool = False):
        guard = (
            self._windows.guard_directories(path.parent)
            if self._windows is not None else nullcontext()
        )
        with guard:
            self._require_lexical_owner(path)
            entry = path.lstat()
            if self._is_link_like(entry) or not stat.S_ISREG(entry.st_mode):
                raise LifecycleFilesystemError(
                    f"lifecycle artifact is not an owned regular file: {path.name}"
                )
            self._require_resolved_owner(path.resolve(strict=True))
            flags = (os.O_RDWR if writable else os.O_RDONLY)
            flags |= getattr(os, "O_NOFOLLOW", 0)
            flags |= getattr(os, "O_BINARY", 0)
            descriptor = (
                self._windows.open_file_descriptor(path, flags)
                if self._windows is not None else os.open(path, flags)
            )
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
                mode = "r+b" if writable else "rb"
                with os.fdopen(descriptor, mode, closefd=False) as source:
                    yield source
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
        with self._exclusive_descriptor(path) as descriptor:
            with os.fdopen(descriptor, "wb", closefd=False) as target:
                yield target
                target.flush()
                os.fsync(descriptor)

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

    def publish_directory(
        self,
        staging: Path,
        final: Path,
        *,
        after_replace=None,  # noqa: ANN001
    ) -> None:
        stage_entry = self.require_directory(staging)
        self.fsync_tree(staging)
        self.require_directory(staging.parent)
        self.require_directory(final.parent)
        if self.entry_exists(final):
            raise LifecycleFilesystemError(
                f"final Candidate path already exists: {final.name}"
            )
        if self._windows is not None:
            self._windows.publish_directory(
                staging,
                final,
                stage_entry,
                after_replace,
            )
            return
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
            try:
                if after_replace is not None:
                    after_replace()
                os.fsync(target_fd)
            except Exception as exc:
                raise PostRenameDurabilityError(
                    "Candidate rename completed but directory durability failed"
                ) from exc

    def replace_file(
        self,
        temporary: Path,
        destination: Path,
        *,
        after_replace=None,  # noqa: ANN001
    ) -> None:
        self.require_regular_file(temporary)
        self.require_directory(temporary.parent)
        if self.entry_exists(destination):
            self.require_regular_file(destination)
        if self._windows is not None:
            self._windows.replace_file(
                temporary,
                destination,
                after_replace,
            )
            return
        with self._directory_fd(temporary.parent) as parent_fd:
            os.replace(
                temporary.name,
                destination.name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
            )
            try:
                if after_replace is not None:
                    after_replace()
                os.fsync(parent_fd)
            except Exception as exc:
                raise PostRenameDurabilityError(
                    "Active rename completed but directory durability failed"
                ) from exc

    def publish_file_exclusive(
        self,
        temporary: Path,
        destination: Path,
        *,
        after_publish=None,  # noqa: ANN001
    ) -> None:
        """Atomically link one durable file into an absent final name."""
        temporary_entry = self.require_regular_file(temporary)
        if temporary.parent != destination.parent:
            raise LifecycleFilesystemError(
                "exclusive file publication requires one directory"
            )
        self.require_directory(temporary.parent)
        if self._windows is not None:
            self._windows.publish_file_exclusive(
                temporary,
                destination,
                temporary_entry,
                after_publish,
            )
            return
        with self._directory_fd(temporary.parent) as parent_fd:
            current = os.stat(
                temporary.name,
                dir_fd=parent_fd,
                follow_symlinks=False,
            )
            if (
                not stat.S_ISREG(current.st_mode)
                or (temporary_entry.st_dev, temporary_entry.st_ino)
                != (current.st_dev, current.st_ino)
            ):
                raise LifecycleFilesystemError(
                    "temporary lifecycle file changed before publication"
                )
            os.link(
                temporary.name,
                destination.name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
                follow_symlinks=False,
            )
            published = os.stat(
                destination.name,
                dir_fd=parent_fd,
                follow_symlinks=False,
            )
            if (
                not stat.S_ISREG(published.st_mode)
                or (current.st_dev, current.st_ino)
                != (published.st_dev, published.st_ino)
            ):
                raise LifecycleFilesystemError(
                    "exclusive lifecycle publication identity mismatch"
                )
            try:
                os.fsync(parent_fd)
                if after_publish is not None:
                    after_publish()
            except Exception as exc:
                raise PostRenameDurabilityError(
                    "file publication committed but directory durability failed"
                ) from exc

    def rollback_directory(self, final: Path, staging: Path) -> None:
        self.require_directory(final)
        self.require_directory(final.parent)
        self.require_directory(staging.parent)
        if self.entry_exists(staging):
            raise LifecycleFilesystemError(
                f"Candidate rollback staging already exists: {staging.name}"
            )
        if self._windows is not None:
            self._windows.rollback_directory(final, staging)
            return
        with self._directory_fd(final.parent) as source_fd, (
            self._directory_fd(staging.parent)
        ) as target_fd:
            os.replace(
                final.name,
                staging.name,
                src_dir_fd=source_fd,
                dst_dir_fd=target_fd,
            )
            os.fsync(source_fd)
            if target_fd != source_fd:
                os.fsync(target_fd)

    def remove_file(self, path: Path, *, missing_ok: bool = False) -> None:
        self._require_lexical_owner(path)
        self.require_directory(path.parent)
        if self._windows is not None:
            self._windows.remove_file(path, missing_ok=missing_ok)
            return
        with self._directory_fd(path.parent) as parent_fd:
            try:
                current = os.stat(
                    path.name, dir_fd=parent_fd, follow_symlinks=False
                )
            except FileNotFoundError:
                if missing_ok:
                    return
                raise
            if stat.S_ISLNK(current.st_mode) or not stat.S_ISREG(current.st_mode):
                raise LifecycleFilesystemError(
                    f"lifecycle artifact is not an owned regular file: {path.name}"
                )
            os.unlink(path.name, dir_fd=parent_fd)
            os.fsync(parent_fd)

    def copy_regular_exclusive(self, source: Path, destination: Path) -> None:
        with self.open_regular(source) as source_file, (
            self.open_exclusive(destination)
        ) as target:
            while chunk := source_file.read(1024 * 1024):
                target.write(chunk)

    @contextmanager
    def open_windows_lock_descriptor(self, path: Path, flags: int):
        if self._windows is None:
            raise LifecycleFilesystemError("Windows lock descriptor requested on POSIX")
        with self._windows.open_lock_descriptor(path, flags) as descriptor:
            yield descriptor

    def fsync_tree(self, path: Path) -> None:
        self.require_directory(path)
        for item in sorted(path.rglob("*")):
            if item.is_symlink():
                raise LifecycleFilesystemError(
                    f"symlink is not allowed in Candidate staging: {item.name}"
                )
            if item.is_file():
                self.require_regular_file(item)
                with self.open_regular(
                    item,
                    writable=self.platform_name == "nt",
                ) as source:
                    os.fsync(source.fileno())
            elif item.is_dir():
                self.require_directory(item)
            else:
                raise LifecycleFilesystemError(
                    f"unsupported Candidate filesystem object: {item.name}"
                )
        if self.platform_name != "nt":
            with self._directory_fd(path) as descriptor:
                os.fsync(descriptor)

    @contextmanager
    def _exclusive_descriptor(self, path: Path):
        flags = (
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_BINARY", 0)
        )
        if self._windows is not None:
            with self._windows.open_exclusive_descriptor(
                path,
                flags,
            ) as descriptor:
                yield descriptor
            return
        with self._directory_fd(path.parent) as parent_fd:
            descriptor = os.open(path.name, flags, 0o600, dir_fd=parent_fd)
            try:
                self._require_opened_regular(path, descriptor)
                yield descriptor
            finally:
                os.close(descriptor)

    def _require_opened_regular(self, path: Path, descriptor: int) -> None:
        opened = os.fstat(descriptor)
        current = path.lstat()
        if (
            self._is_link_like(current)
            or not stat.S_ISREG(current.st_mode)
            or (current.st_dev, current.st_ino)
            != (opened.st_dev, opened.st_ino)
        ):
            raise LifecycleFilesystemError(
                "exclusive lifecycle artifact changed during creation"
            )
        self._require_resolved_owner(path.resolve(strict=True))

    def _require_unchanged_directory(
        self,
        path: Path,
        expected: os.stat_result,
    ) -> None:
        current = path.lstat()
        if (
            self._is_link_like(current)
            or not stat.S_ISDIR(current.st_mode)
            or (current.st_dev, current.st_ino)
            != (expected.st_dev, expected.st_ino)
        ):
            raise LifecycleFilesystemError(
                "lifecycle directory changed during validation"
            )
        self._require_resolved_owner(
            path.resolve(strict=True),
            allow_root=path == self.root,
        )

    def _require_unchanged_regular(
        self,
        path: Path,
        expected: os.stat_result,
    ) -> None:
        current = path.lstat()
        if (
            self._is_link_like(current)
            or not stat.S_ISREG(current.st_mode)
            or (current.st_dev, current.st_ino)
            != (expected.st_dev, expected.st_ino)
        ):
            raise LifecycleFilesystemError(
                "lifecycle artifact changed during validation"
            )
        self._require_resolved_owner(path.resolve(strict=True))

    @staticmethod
    def _is_link_like(entry: os.stat_result) -> bool:
        reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        attributes = getattr(entry, "st_file_attributes", 0)
        return stat.S_ISLNK(entry.st_mode) or bool(reparse and attributes & reparse)

    @contextmanager
    def _directory_fd(self, path: Path):
        if self.platform_name == "nt":
            raise LifecycleFilesystemError(
                "Windows lifecycle persistence does not use directory descriptors"
            )
        self._require_lexical_owner(path, allow_root=True)
        entry = path.lstat()
        if self._is_link_like(entry) or not stat.S_ISDIR(entry.st_mode):
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

    @contextmanager
    def trusted_directory(self, path: Path):
        """Yield a descriptor whose identity was checked with lstat/open/fstat."""
        with self._directory_fd(path) as descriptor:
            yield descriptor

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


def _platform_name() -> str:
    return os.name
