"""Persistent error log behavior for the windowed Calculator build."""

from __future__ import annotations

from pathlib import Path
import sys
import tkinter as tk

import pytest

from apps.calculator.ui import calculator_app, error_log
from apps.calculator.ui.error_log import default_log_path, install_error_log
from tests.helpers.tk import destroy_tk_root, make_hidden_root


@pytest.fixture(autouse=True)
def restore_process_hooks(monkeypatch):
    monkeypatch.setattr(
        tk.Tk,
        "report_callback_exception",
        tk.Tk.report_callback_exception,
    )
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)


def _raise_and_report(message: str) -> None:
    try:
        raise RuntimeError(message)
    except RuntimeError:
        sys.excepthook(*sys.exc_info())


def test_default_log_path_uses_local_app_data_on_windows() -> None:
    assert default_log_path(
        platform_name="nt",
        environment={"LOCALAPPDATA": "local-app-data"},
        home=Path("home"),
    ) == Path("local-app-data") / "predictor_v3" / "calculator" / "crash_log.txt"
    assert default_log_path(
        platform_name="nt",
        environment={},
        home=Path("home"),
    ) == (
        Path("home")
        / "AppData"
        / "Local"
        / "predictor_v3"
        / "calculator"
        / "crash_log.txt"
    )


def test_default_log_path_uses_state_home_elsewhere() -> None:
    assert default_log_path(
        platform_name="posix",
        environment={},
        home=Path("home"),
    ) == (
        Path("home")
        / ".local"
        / "state"
        / "predictor_v3"
        / "calculator"
        / "crash_log.txt"
    )


def test_tk_callback_exception_is_recorded_without_console(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    log_path = tmp_path / "logs" / "crash_log.txt"
    assert install_error_log(log_path) == log_path
    try:
        root = make_hidden_root()
    except tk.TclError as exc:
        pytest.skip(f"Tk not available: {exc}")

    def fail() -> None:
        raise ValueError("Unsupported window geometry")

    monkeypatch.setattr(sys, "stdout", None)
    monkeypatch.setattr(sys, "stderr", None)
    try:
        tk.Button(root, command=fail).invoke()
        dialog = tk.Toplevel(root)
        dialog.withdraw()
        tk.Button(dialog, command=fail).invoke()
    finally:
        destroy_tk_root(root)

    text = log_path.read_text(encoding="utf-8")
    assert text.count("Tk callback exception") == 2
    assert text.count("Traceback (most recent call last)") == 2
    assert "ValueError: Unsupported window geometry" in text


def test_unhandled_exception_is_recorded_and_forwarded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    forwarded: list[type[BaseException]] = []
    monkeypatch.setattr(sys, "excepthook", lambda exc, *_rest: forwarded.append(exc))
    log_path = tmp_path / "crash_log.txt"
    install_error_log(log_path)

    _raise_and_report("계산기 시작 실패")

    assert forwarded == [RuntimeError]
    assert "RuntimeError: 계산기 시작 실패" in log_path.read_text(encoding="utf-8")


def test_log_folder_failure_leaves_hooks_untouched(tmp_path: Path) -> None:
    blocker = tmp_path / "blocker"
    blocker.write_text("", encoding="utf-8")
    report = tk.Tk.report_callback_exception
    excepthook = sys.excepthook

    assert install_error_log(blocker / "logs" / "crash_log.txt") is None

    assert tk.Tk.report_callback_exception is report
    assert sys.excepthook is excepthook


def test_log_write_failure_still_forwards_the_exception(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    forwarded: list[type[BaseException]] = []
    monkeypatch.setattr(sys, "excepthook", lambda exc, *_rest: forwarded.append(exc))
    unwritable = tmp_path / "crash_log.txt"
    unwritable.mkdir()
    install_error_log(unwritable)

    _raise_and_report("log target is a folder")

    assert forwarded == [RuntimeError]


def test_log_rotates_and_keeps_writing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(error_log, "_MAX_BYTES", 200)
    monkeypatch.setattr(sys, "excepthook", lambda *_args: None)
    log_path = tmp_path / "crash_log.txt"
    install_error_log(log_path)

    for index in range(3):
        _raise_and_report(f"error {index}")

    assert (tmp_path / "crash_log.txt.1").exists()
    assert "error 2" in log_path.read_text(encoding="utf-8")


def test_main_installs_error_log_before_building_the_app(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    class FakeApp:
        def __init__(self) -> None:
            calls.append("build")

        def run(self) -> None:
            calls.append("run")

    monkeypatch.setattr(
        calculator_app,
        "install_error_log",
        lambda: calls.append("log"),
    )
    monkeypatch.setattr(calculator_app, "CalculatorTkApp", FakeApp)

    calculator_app.main()

    assert calls == ["log", "build", "run"]
