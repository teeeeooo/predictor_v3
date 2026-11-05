"""Persistent error log for the windowed Calculator build.

A ``--noconsole`` build has no stderr, so an unhandled exception would vanish
without a trace. Exceptions raised in Tk callbacks never reach
``sys.excepthook``: Tk reports them through ``report_callback_exception``, so
both hooks are needed to cover callbacks and startup failures.
"""

from __future__ import annotations

from collections.abc import Mapping
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
import tkinter as tk

_MAX_BYTES = 1_000_000
_BACKUP_COUNT = 3


def default_log_path(
    *,
    platform_name: str | None = None,
    environment: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> Path:
    resolved_platform = platform_name or os.name
    resolved_environment = environment if environment is not None else os.environ
    resolved_home = home or Path.home()
    if resolved_platform == "nt":
        fallback = resolved_home / "AppData" / "Local"
        base = Path(resolved_environment.get("LOCALAPPDATA", fallback))
    else:
        fallback = resolved_home / ".local" / "state"
        base = Path(resolved_environment.get("XDG_STATE_HOME", fallback))
    return base / "predictor_v3" / "calculator" / "crash_log.txt"


def install_error_log(log_path: Path | None = None) -> Path | None:
    """Record unhandled exceptions to a file, keeping the existing reporting.

    Returns the log path, or ``None`` when its folder cannot be created. A
    logging failure never stops the application.
    """
    path = log_path if log_path is not None else default_log_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None

    handler = RotatingFileHandler(
        path,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
        delay=True,
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger = logging.Logger("predictor_v3.calculator.errors", logging.ERROR)
    logger.addHandler(handler)

    def record(message: str, exc_info) -> None:
        logger.error(message, exc_info=exc_info)
        # Release the file between errors so it can be opened or rotated
        # while another running instance also holds this log.
        try:
            handler.close()
        except OSError:
            pass

    previous_report = tk.Tk.report_callback_exception
    previous_excepthook = sys.excepthook

    def report_callback_exception(self, exc, value, traceback) -> None:
        record("Tk callback exception", (exc, value, traceback))
        previous_report(self, exc, value, traceback)

    def excepthook(exc, value, traceback) -> None:
        record("Unhandled exception", (exc, value, traceback))
        previous_excepthook(exc, value, traceback)

    tk.Tk.report_callback_exception = report_callback_exception
    sys.excepthook = excepthook
    return path
