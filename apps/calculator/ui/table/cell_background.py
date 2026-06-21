"""Shared calculator table cell-background presentation policy."""

from __future__ import annotations

from apps.calculator.ui.layout_constants import (
    TABLE_EDITABLE_BG,
    TABLE_INVALID_BG,
    TABLE_STATIC_BG,
)

__all__ = ["cell_background"]


def cell_background(*, editable: bool, invalid: bool = False) -> str:
    """Return the semantic background token for a calculator table cell."""
    if invalid:
        return TABLE_INVALID_BG
    if editable:
        return TABLE_EDITABLE_BG
    return TABLE_STATIC_BG
