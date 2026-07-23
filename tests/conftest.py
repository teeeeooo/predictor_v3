"""Shared pytest fixtures with no import-time UI application side effects."""

from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def qprocess_app():
    """Keep one strong QApplication identity across Core and Widget tests."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
    app.processEvents()
