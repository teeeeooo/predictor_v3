"""Compatibility wrapper for the common Tk table controller."""

from __future__ import annotations

from apps.calculator.ui.table.controller import TkTableController


class BatchTableController(TkTableController):
    """Deprecated batch-specific name for the common table controller."""
