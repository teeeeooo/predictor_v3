"""Tests for the shared calculator table cell-background policy."""

from apps.calculator.ui.layout_constants import (
    TABLE_EDITABLE_BG,
    TABLE_INVALID_BG,
    TABLE_STATIC_BG,
)
from apps.calculator.ui.table.cell_background import cell_background


def test_cell_background_uses_editable_and_static_tokens() -> None:
    assert cell_background(editable=True) == TABLE_EDITABLE_BG
    assert cell_background(editable=False) == TABLE_STATIC_BG


def test_invalid_state_overrides_editability() -> None:
    assert cell_background(editable=True, invalid=True) == TABLE_INVALID_BG
    assert cell_background(editable=False, invalid=True) == TABLE_INVALID_BG
