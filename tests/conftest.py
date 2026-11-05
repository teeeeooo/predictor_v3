"""Shared pytest fixtures with no import-time UI application side effects."""

from __future__ import annotations

import os

import pytest

# This module pumps real window drawing. On macOS, Tk's update() can then spin
# forever if an earlier Tk root in the same process was destroyed. It therefore
# runs first, and no test module may create a Tk root at import time.
_FIRST_TK_MODULE = ("apps", "calculator", "combinations", "test_ui.py")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Give the combination UI module the process's first Tk interpreter."""
    items.sort(key=lambda item: item.path.parts[-4:] != _FIRST_TK_MODULE)


@pytest.fixture(scope="session")
def qprocess_app():
    """Keep one strong QApplication identity across Core and Widget tests."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
    app.processEvents()
