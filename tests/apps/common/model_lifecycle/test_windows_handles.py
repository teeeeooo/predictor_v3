"""Native Windows handle compatibility regressions."""

from __future__ import annotations

import ctypes
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps.common.model_lifecycle import deployment_export_windows
from apps.common.model_lifecycle import windows_filesystem
from apps.common.model_lifecycle import windows_handles

_GENERIC_READ = 0x80000000
_GENERIC_WRITE = 0x40000000
_INVALID_HANDLE = ctypes.c_void_p(-1).value


class _Function:
    argtypes = None
    restype = None

    def __init__(self, callback):  # noqa: ANN001
        self._callback = callback

    def __call__(self, *args):  # noqa: ANN002, ANN202
        return self._callback(*args)


class _Kernel32:
    def __init__(self) -> None:
        self.handle = 321
        self.create_result = self.handle
        self.last_error = 0
        self.create_calls: list[tuple] = []
        self.closed: list[int] = []
        self.CreateFileW = _Function(self._create_file)
        self.CloseHandle = _Function(self._close_handle)

    def _create_file(self, *args):  # noqa: ANN002, ANN202
        self.create_calls.append(args)
        return self.create_result

    def _close_handle(self, handle: int) -> int:
        self.closed.append(handle)
        return 1


@pytest.fixture
def native_handle_semantics(monkeypatch):
    fake_os = SimpleNamespace(
        name="nt",
        O_RDONLY=0,
        O_WRONLY=1,
        O_RDWR=2,
        O_APPEND=0x0008,
        O_CREAT=0x0100,
        O_EXCL=0x0400,
        O_NOINHERIT=0x0080,
        O_TEXT=0x4000,
        O_BINARY=0x8000,
    )
    kernel = _Kernel32()
    crt_calls: list[tuple[int, int]] = []
    fake_msvcrt = SimpleNamespace(
        open_osfhandle=lambda handle, flags: crt_calls.append((handle, flags)) or 41
    )

    monkeypatch.setattr(windows_handles, "os", fake_os)
    monkeypatch.setattr(
        windows_handles.ctypes,
        "WinDLL",
        lambda *_args, **_kwargs: kernel,
        raising=False,
    )
    monkeypatch.setattr(
        windows_handles.ctypes,
        "get_last_error",
        lambda: kernel.last_error,
        raising=False,
    )
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)
    return SimpleNamespace(
        os=fake_os,
        kernel=kernel,
        crt_calls=crt_calls,
        msvcrt=fake_msvcrt,
    )


def test_lifecycle_and_deployment_export_share_native_handle_owner():
    assert windows_filesystem._open_file_descriptor is windows_handles.open_file_descriptor
    assert deployment_export_windows.open_file_descriptor is windows_handles.open_file_descriptor


@pytest.mark.parametrize(
    ("flags", "expected_access", "expected_crt_mode"),
    [
        (0, _GENERIC_READ, 0),
        (1, _GENERIC_WRITE, 1),
        (2, _GENERIC_READ | _GENERIC_WRITE, 2),
    ],
)
def test_windows_access_modes_do_not_require_os_accmode(
    native_handle_semantics,
    flags,
    expected_access,
    expected_crt_mode,
):
    semantics = native_handle_semantics

    descriptor = windows_handles.open_file_descriptor(Path("artifact.bin"), flags, 0o600)

    assert not hasattr(semantics.os, "O_ACCMODE")
    assert descriptor == 41
    call = semantics.kernel.create_calls[-1]
    assert call[1] == expected_access
    assert call[2] == 0x1 | 0x2
    assert call[4] == 3
    assert call[5] & 0x00200000
    assert semantics.crt_calls == [(semantics.kernel.handle, expected_crt_mode)]
    assert semantics.kernel.closed == []


@pytest.mark.parametrize(
    ("flags", "expected_disposition"),
    [
        (1 | 0x0100, 4),
        (1 | 0x0100 | 0x0400, 1),
    ],
)
def test_windows_create_disposition_is_preserved(
    native_handle_semantics, flags, expected_disposition
):
    semantics = native_handle_semantics

    windows_handles.open_file_descriptor(Path("artifact.bin"), flags, 0o600)

    assert semantics.kernel.create_calls[-1][4] == expected_disposition


def test_windows_exclusive_create_collision_remains_no_clobber(
    native_handle_semantics,
):
    semantics = native_handle_semantics
    semantics.kernel.create_result = _INVALID_HANDLE
    semantics.kernel.last_error = 183
    flags = semantics.os.O_WRONLY | semantics.os.O_CREAT | semantics.os.O_EXCL

    with pytest.raises(FileExistsError):
        windows_handles.open_file_descriptor(Path("artifact.bin"), flags, 0o600)

    assert semantics.crt_calls == []
    assert semantics.kernel.closed == []


def test_crt_conversion_failure_closes_owned_native_handle(
    native_handle_semantics,
):
    semantics = native_handle_semantics
    flags = (
        semantics.os.O_WRONLY
        | semantics.os.O_CREAT
        | semantics.os.O_EXCL
        | semantics.os.O_APPEND
        | semantics.os.O_BINARY
        | semantics.os.O_NOINHERIT
    )
    conversion_calls: list[tuple[int, int]] = []

    def fail_conversion(handle: int, crt_flags: int) -> int:
        conversion_calls.append((handle, crt_flags))
        raise RuntimeError("crt conversion failed")

    semantics.msvcrt.open_osfhandle = fail_conversion

    with pytest.raises(RuntimeError, match="crt conversion failed"):
        windows_handles.open_file_descriptor(Path("artifact.bin"), flags, 0o600)

    expected_crt = (
        semantics.os.O_WRONLY
        | semantics.os.O_APPEND
        | semantics.os.O_BINARY
        | semantics.os.O_NOINHERIT
    )
    assert semantics.kernel.create_calls[-1][4] == 1
    assert conversion_calls == [(semantics.kernel.handle, expected_crt)]
    assert semantics.crt_calls == []
    assert semantics.kernel.closed == [semantics.kernel.handle]
