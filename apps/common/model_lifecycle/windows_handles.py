"""Native Windows handles used to bind lifecycle mutation paths."""

from __future__ import annotations

import ctypes
import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def hold_directory(path: Path):
    """Deny delete sharing so a validated directory cannot be substituted."""
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
        0x80,  # FILE_READ_ATTRIBUTES
        0x1 | 0x2,  # FILE_SHARE_READ | FILE_SHARE_WRITE; deliberately no DELETE
        None,
        3,  # OPEN_EXISTING
        0x02000000 | 0x00200000,  # BACKUP_SEMANTICS | OPEN_REPARSE_POINT
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


def open_file_descriptor(path: Path, flags: int, mode: int) -> int:
    """Open one Windows file without following a substituted reparse point."""
    if os.name != "nt":
        return os.open(path, flags, mode)
    import msvcrt

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
    access_mode = flags & (os.O_WRONLY | os.O_RDWR)
    access = 0
    if access_mode in {os.O_RDONLY, os.O_RDWR}:
        access |= 0x80000000  # GENERIC_READ
    if access_mode in {os.O_WRONLY, os.O_RDWR}:
        access |= 0x40000000  # GENERIC_WRITE
    if flags & os.O_CREAT:
        disposition = 1 if flags & os.O_EXCL else 4  # CREATE_NEW | OPEN_ALWAYS
    else:
        disposition = 3  # OPEN_EXISTING
    handle = create_file(
        str(path),
        access,
        0x1 | 0x2,  # deny delete sharing for the opened artifact too
        None,
        disposition,
        0x80 | 0x00200000,  # FILE_ATTRIBUTE_NORMAL | OPEN_REPARSE_POINT
        None,
    )
    if handle == ctypes.c_void_p(-1).value:
        error = ctypes.get_last_error()
        if disposition == 1 and error in {80, 183}:
            raise FileExistsError(error, "lifecycle artifact already exists", path)
        raise ctypes.WinError(error)
    try:
        crt_flags = access_mode | (flags & (
            getattr(os, "O_APPEND", 0)
            | getattr(os, "O_BINARY", 0)
            | getattr(os, "O_TEXT", 0)
            | getattr(os, "O_NOINHERIT", 0)
        ))
        return msvcrt.open_osfhandle(handle, crt_flags)
    except Exception:
        ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle(handle)
        raise
