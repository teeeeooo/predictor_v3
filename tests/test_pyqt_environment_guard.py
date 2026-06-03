import pytest

from tests.helpers import pyqt_env
from tests.helpers.pyqt_env import PyQtEnvironment


def env(system, version, available=True, pyqt="5.15.11", qt="5.15.14"):
    return PyQtEnvironment(
        system=system,
        python_version=version,
        pyqt_available=available,
        pyqt_version=pyqt if available else None,
        qt_version=qt if available else None,
    )


def test_macos_python314_with_pyqt_is_known_bad():
    assert pyqt_env.is_macos_python314_pyqt5_known_bad(
        env("Darwin", (3, 14, 4))
    )


def test_macos_python312_is_not_known_bad():
    assert not pyqt_env.is_macos_python314_pyqt5_known_bad(
        env("Darwin", (3, 12, 8))
    )


def test_windows_python314_is_not_known_bad():
    assert not pyqt_env.is_macos_python314_pyqt5_known_bad(
        env("Windows", (3, 14, 4))
    )


def test_linux_python314_is_not_known_bad():
    assert not pyqt_env.is_macos_python314_pyqt5_known_bad(
        env("Linux", (3, 14, 4))
    )


def test_python315_is_not_known_bad_until_verified():
    assert not pyqt_env.is_macos_python314_pyqt5_known_bad(
        env("Darwin", (3, 15, 0))
    )


def test_pyqt_unavailable_is_not_known_bad():
    assert not pyqt_env.is_macos_python314_pyqt5_known_bad(
        env("Darwin", (3, 14, 4), available=False)
    )


def test_current_environment_handles_pyqt_import_failure(monkeypatch):
    monkeypatch.setattr(pyqt_env.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(pyqt_env, "_current_python_version", lambda: (3, 14, 4))
    monkeypatch.setattr(pyqt_env, "_load_pyqt_versions", lambda: (False, None, None))

    current = pyqt_env.current_pyqt_environment()

    assert current.pyqt_available is False
    assert not pyqt_env.is_macos_python314_pyqt5_known_bad(current)
    assert "PyQt5 unavailable" in pyqt_env.describe_pyqt_environment(current)


def test_describe_pyqt_environment_includes_versions():
    description = pyqt_env.describe_pyqt_environment(
        env("Darwin", (3, 14, 4), pyqt="5.15.11", qt="5.15.14")
    )

    assert "Darwin" in description
    assert "Python 3.14.4" in description
    assert "PyQt5 5.15.11" in description
    assert "Qt 5.15.14" in description


def test_skip_helper_raises_module_level_skip_on_known_bad(monkeypatch):
    monkeypatch.setattr(
        pyqt_env,
        "current_pyqt_environment",
        lambda: env("Darwin", (3, 14, 4)),
    )

    with pytest.raises(pytest.skip.Exception) as exc_info:
        pyqt_env.skip_if_macos_python314_pyqt5_known_bad()

    assert "known-bad PyQt widget test environment" in str(exc_info.value)


def test_skip_helper_does_not_skip_supported_host(monkeypatch):
    monkeypatch.setattr(
        pyqt_env,
        "current_pyqt_environment",
        lambda: env("Windows", (3, 14, 4)),
    )

    pyqt_env.skip_if_macos_python314_pyqt5_known_bad()


def test_skip_mark_includes_known_bad_reason(monkeypatch):
    monkeypatch.setattr(
        pyqt_env,
        "current_pyqt_environment",
        lambda: env("Darwin", (3, 14, 4)),
    )

    mark = pyqt_env.macos_python314_pyqt5_known_bad_skip_mark()

    assert mark.name == "skipif"
    assert mark.args == (True,)
    assert "known-bad PyQt widget test environment" in mark.kwargs["reason"]
