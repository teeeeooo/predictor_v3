"""Brazil batch semantic cell-background policy."""

from __future__ import annotations

from apps.calculator.ui.batch.matrix_models import MatrixCellKind
from apps.calculator.ui.layout_constants import (
    TABLE_ERROR_BG,
    TABLE_EDITABLE_BG,
    TABLE_PASS_BG,
    TABLE_STATIC_BG,
)

from .schema import FINAL, RULE_1, RULE_2

_JUDGEMENT_KEYS = frozenset((RULE_1, RULE_2, FINAL))


def brazil_batch_cell_background(table, position: tuple[int, int]) -> str:
    cell = table.spec.resolve_cell(position)
    if cell.kind is not MatrixCellKind.RESULT or cell.result_key is None:
        return TABLE_EDITABLE_BG if cell.editable else TABLE_STATIC_BG
    value = table.text_at_position(position)
    if cell.result_key in _JUDGEMENT_KEYS:
        if value == "OK":
            return TABLE_PASS_BG
        if value == "NG":
            return TABLE_ERROR_BG
        return TABLE_STATIC_BG
    return TABLE_PASS_BG if value else TABLE_STATIC_BG


__all__ = ["brazil_batch_cell_background"]
