"""Contain in-place bootstrap recovery inside one validated generation directory."""

from __future__ import annotations

import ctypes
import os
import stat
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Callable, Mapping
from uuid import uuid4

MutationHook = Callable[[], None]


def reconstruct_matching_residue(
    root: Path,
    generations: Path,
    final: Path,
    expected_files: Mapping[str, bytes],
    *,
    before_mutation: MutationHook | None = None,
) -> None:
    """Fill a proven matching residue without following substituted paths."""
    if _platform_name() == "nt":
        _recover_windows(root, generations, final, expected_files, before_mutation)
        return
    _recover_posix(root, final, expected_files, before_mutation)


def _recover_posix(
    root: Path,
    final: Path,
    expected: Mapping[str, bytes],
    hook: MutationHook | None,
) -> None:
    with _open_owned_directory(root, final) as final_fd:
        projection_fd = _open_projection_fd(final_fd, create=False)
        try:
            _validate_fd_residue(final_fd, projection_fd, expected)
            if hook is not None:
                hook()
            if projection_fd is None:
                os.mkdir("projections", dir_fd=final_fd)
                projection_fd = _open_projection_fd(final_fd, create=False)
            _validate_fd_residue(final_fd, projection_fd, expected)
            _write_missing_fd_files(final_fd, projection_fd, expected)
            _publish_bundle_fd(final_fd, expected["bundle.json"])
        finally:
            if projection_fd is not None:
                os.close(projection_fd)


def _recover_windows(
    root: Path,
    generations: Path,
    final: Path,
    expected: Mapping[str, bytes],
    hook: MutationHook | None,
) -> None:
    paths = (root, generations, final)
    entries = tuple(_require_owned_directory(root, path) for path in paths)
    with ExitStack() as stack:
        for path in paths:
            stack.enter_context(_hold_windows_directory(path))
        for path, entry in zip(paths, entries, strict=True):
            _require_same_directory(root, path, entry)
        projection = final / "projections"
        projection_entry = None
        if projection.exists():
            projection_entry = _require_owned_directory(root, projection)
            stack.enter_context(_hold_windows_directory(projection))
            _require_same_directory(root, projection, projection_entry)
        _validate_path_residue(final, expected)
        if hook is not None:
            hook()
        if not projection.exists():
            projection.mkdir()
            projection_entry = _require_owned_directory(root, projection)
            stack.enter_context(_hold_windows_directory(projection))
        elif projection_entry is None:
            projection_entry = _require_owned_directory(root, projection)
            stack.enter_context(_hold_windows_directory(projection))
        _require_same_directory(root, projection, projection_entry)
        _validate_path_residue(final, expected)
        _write_missing_path_files(final, expected)
        _publish_bundle_path(final, expected["bundle.json"])


@contextmanager
def _open_owned_directory(root: Path, path: Path):
    entry = _require_owned_directory(root, path)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        current = os.fstat(descriptor)
        if not stat.S_ISDIR(current.st_mode) or not os.path.samestat(entry, current):
            raise ValueError("recoverable generation directory changed during validation")
        yield descriptor
    finally:
        os.close(descriptor)


def _open_projection_fd(final_fd: int, *, create: bool) -> int | None:
    if create:
        os.mkdir("projections", dir_fd=final_fd)
    try:
        entry = os.stat("projections", dir_fd=final_fd, follow_symlinks=False)
    except FileNotFoundError:
        return None
    if _is_link_like(entry) or not stat.S_ISDIR(entry.st_mode):
        raise ValueError("recoverable generation residue contains a link or non-directory")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open("projections", flags, dir_fd=final_fd)
    opened = os.fstat(descriptor)
    if not stat.S_ISDIR(opened.st_mode) or not os.path.samestat(entry, opened):
        os.close(descriptor)
        raise ValueError("recoverable generation directory changed during validation")
    return descriptor


def _validate_fd_residue(
    final_fd: int,
    projection_fd: int | None,
    expected: Mapping[str, bytes],
) -> None:
    root_entries = set(os.listdir(final_fd))
    if "bundle.json" in root_entries:
        raise ValueError("existing immutable generation is incomplete or corrupt")
    if root_entries - {"manifest.json", "projections"}:
        raise ValueError("recoverable generation residue has unknown files")
    _validate_existing_fd_file(final_fd, "manifest.json", expected["manifest.json"])
    projection_names = {item.split("/", 1)[1] for item in expected if item.startswith("projections/")}
    if projection_fd is None:
        if "projections" in root_entries:
            raise ValueError("recoverable generation residue contains a link or non-directory")
        return
    entries = set(os.listdir(projection_fd))
    if entries - projection_names:
        raise ValueError("recoverable generation residue has unknown files")
    for name in entries:
        _validate_existing_fd_file(projection_fd, name, expected[f"projections/{name}"])


def _validate_existing_fd_file(directory_fd: int, name: str, expected: bytes) -> None:
    try:
        entry = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if _is_link_like(entry) or not stat.S_ISREG(entry.st_mode):
        raise ValueError("recoverable generation residue contains a link or non-file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(name, flags, dir_fd=directory_fd)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or not os.path.samestat(entry, opened):
            raise ValueError("recoverable generation artifact changed during validation")
        with os.fdopen(descriptor, "rb", closefd=False) as source:
            actual = source.read()
    finally:
        os.close(descriptor)
    if actual != expected:
        raise ValueError(f"recoverable generation residue conflicts with bootstrap: {name}")


def _write_missing_fd_files(
    final_fd: int,
    projection_fd: int,
    expected: Mapping[str, bytes],
) -> None:
    for identity, payload in expected.items():
        if identity == "bundle.json":
            continue
        directory_fd, name = (
            (projection_fd, identity.split("/", 1)[1])
            if identity.startswith("projections/")
            else (final_fd, identity)
        )
        try:
            _write_exclusive_fd(directory_fd, name, payload)
        except FileExistsError:
            _validate_existing_fd_file(directory_fd, name, payload)
    os.fsync(projection_fd)


def _write_exclusive_fd(directory_fd: int, name: str, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(name, flags, 0o600, dir_fd=directory_fd)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as target:
            target.write(payload)
            target.flush()
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _publish_bundle_fd(final_fd: int, payload: bytes) -> None:
    temporary = f".bundle-{uuid4().hex}.tmp"
    _write_exclusive_fd(final_fd, temporary, payload)
    try:
        os.link(
            temporary,
            "bundle.json",
            src_dir_fd=final_fd,
            dst_dir_fd=final_fd,
            follow_symlinks=False,
        )
        os.fsync(final_fd)
    finally:
        try:
            os.unlink(temporary, dir_fd=final_fd)
        except FileNotFoundError:
            pass


def _validate_path_residue(final: Path, expected: Mapping[str, bytes]) -> None:
    root_entries = {item.name for item in final.iterdir()}
    if "bundle.json" in root_entries:
        raise ValueError("existing immutable generation is incomplete or corrupt")
    if root_entries - {"manifest.json", "projections"}:
        raise ValueError("recoverable generation residue has unknown files")
    _validate_existing_path_file(final / "manifest.json", expected["manifest.json"])
    projection = final / "projections"
    if not projection.exists():
        return
    _require_owned_directory(final, projection)
    allowed = {item.split("/", 1)[1] for item in expected if item.startswith("projections/")}
    entries = {item.name for item in projection.iterdir()}
    if entries - allowed:
        raise ValueError("recoverable generation residue has unknown files")
    for name in entries:
        _validate_existing_path_file(projection / name, expected[f"projections/{name}"])


def _validate_existing_path_file(path: Path, expected: bytes) -> None:
    try:
        entry = path.lstat()
    except FileNotFoundError:
        return
    if _is_link_like(entry) or not stat.S_ISREG(entry.st_mode):
        raise ValueError("recoverable generation residue contains a link or non-file")
    if path.read_bytes() != expected:
        raise ValueError(f"recoverable generation residue conflicts with bootstrap: {path.name}")


def _write_missing_path_files(final: Path, expected: Mapping[str, bytes]) -> None:
    for identity, payload in expected.items():
        if identity == "bundle.json":
            continue
        destination = final / identity
        if destination.exists():
            _validate_existing_path_file(destination, payload)
            continue
        try:
            with destination.open("xb") as target:
                target.write(payload)
                target.flush()
                os.fsync(target.fileno())
        except FileExistsError:
            _validate_existing_path_file(destination, payload)


def _publish_bundle_path(final: Path, payload: bytes) -> None:
    bundle = final / "bundle.json"
    temporary = final / f".bundle-{uuid4().hex}.tmp"
    try:
        with temporary.open("xb") as target:
            target.write(payload)
            target.flush()
            os.fsync(target.fileno())
        if bundle.exists():
            raise ValueError("existing immutable generation is incomplete or corrupt")
        os.rename(temporary, bundle)
    finally:
        temporary.unlink(missing_ok=True)


def _require_owned_directory(root: Path, path: Path) -> os.stat_result:
    try:
        entry = path.lstat()
    except FileNotFoundError as exc:
        raise ValueError("recoverable generation path is missing") from exc
    if _is_link_like(entry) or not stat.S_ISDIR(entry.st_mode):
        raise ValueError("recoverable generation path is not an owned regular directory")
    resolved_root = root.resolve(strict=True)
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("recoverable generation path escapes repository ownership") from exc
    return entry


def _require_same_directory(root: Path, path: Path, expected: os.stat_result) -> None:
    current = _require_owned_directory(root, path)
    if not os.path.samestat(expected, current):
        raise ValueError("recoverable generation directory changed during validation")


def _is_link_like(entry: os.stat_result) -> bool:
    attributes = getattr(entry, "st_file_attributes", 0)
    return stat.S_ISLNK(entry.st_mode) or bool(attributes & _windows_reparse_attribute())


def _windows_reparse_attribute() -> int:
    return getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


@contextmanager
def _hold_windows_directory(path: Path):
    """Pin a Windows directory by denying delete sharing during recovery mutation."""
    if os.name != "nt":
        yield
        return
    create_file = ctypes.WinDLL("kernel32", use_last_error=True).CreateFileW
    create_file.argtypes = (
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
    )
    create_file.restype = ctypes.c_void_p
    handle = create_file(
        str(path),
        0x80,
        0x1 | 0x2,
        None,
        3,
        0x02000000 | 0x00200000,
        None,
    )
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        yield
    finally:
        close_handle = ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle
        close_handle.argtypes = (ctypes.c_void_p,)
        close_handle.restype = ctypes.c_int
        if not close_handle(handle):
            raise ctypes.WinError(ctypes.get_last_error())


def _platform_name() -> str:
    return os.name
