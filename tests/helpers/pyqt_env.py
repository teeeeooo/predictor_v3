"""PyQt test environment guards.

These helpers avoid creating QApplication, QTableView, clipboard, or any
other widget. They only inspect platform, Python, and PyQt/Qt versions.
"""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class PyQtEnvironment:
    system: str
    python_version: tuple[int, int, int]
    pyqt_available: bool
    pyqt_version: str | None = None
    qt_version: str | None = None


def _current_python_version() -> tuple[int, int, int]:
    info = sys.version_info
    return (info.major, info.minor, info.micro)


def _load_pyqt_versions() -> tuple[bool, str | None, str | None]:
    try:
        import PyQt5.QtCore as QtCore
    except Exception:
        return False, None, None
    return True, QtCore.PYQT_VERSION_STR, QtCore.QT_VERSION_STR


def current_pyqt_environment() -> PyQtEnvironment:
    available, pyqt_version, qt_version = _load_pyqt_versions()
    return PyQtEnvironment(
        system=platform.system(),
        python_version=_current_python_version(),
        pyqt_available=available,
        pyqt_version=pyqt_version,
        qt_version=qt_version,
    )


def is_macos_python314_pyqt5_known_bad(
    env: PyQtEnvironment | None = None,
) -> bool:
    env = env or current_pyqt_environment()
    return (
        env.system == "Darwin"
        and env.python_version[:2] == (3, 14)
        and env.pyqt_available
    )


def describe_pyqt_environment(env: PyQtEnvironment | None = None) -> str:
    env = env or current_pyqt_environment()
    py = ".".join(str(part) for part in env.python_version)
    if env.pyqt_available:
        pyqt = env.pyqt_version or "unknown"
        qt = env.qt_version or "unknown"
        return f"{env.system} Python {py} PyQt5 {pyqt} Qt {qt}"
    return f"{env.system} Python {py} PyQt5 unavailable"


def macos_python314_pyqt5_known_bad_skip_mark():
    env = current_pyqt_environment()
    return pytest.mark.skipif(
        is_macos_python314_pyqt5_known_bad(env),
        reason=(
            "known-bad PyQt widget test environment: "
            f"{describe_pyqt_environment(env)} can native-abort during "
            "pytest QTableView subclass construction"
        ),
    )


def skip_if_macos_python314_pyqt5_known_bad() -> None:
    env = current_pyqt_environment()
    if is_macos_python314_pyqt5_known_bad(env):
        pytest.skip(
            "known-bad PyQt widget test environment: "
            f"{describe_pyqt_environment(env)} can native-abort during "
            "pytest QTableView subclass construction",
            allow_module_level=True,
        )
