"""Compatibility exports for row-per-case batch table surfaces.

New table interaction behavior is owned by :mod:`ui_tk.table`.
This module remains so existing batch imports do not need to know the new
subpackage boundary yet.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from ui_tk.batch.models import BatchColumnRole
from ui_tk.table.interaction_core import (
    CellAddress as GridAddress,
    ClipboardMatrix,
    SelectionBounds,
    editable_clear_targets as _editable_clear_targets,
    editable_paste_targets as _editable_paste_targets,
    positions_in_bounds,
    resolve_adjacent_position,
    resolve_next_position,
    selection_bounds,
)
from ui_tk.table.roles import CellRole
from ui_tk.table.surface import TkTableSurface as BatchTableSurface


def batch_roles_to_cell_roles(roles: Sequence[BatchColumnRole]) -> tuple[CellRole, ...]:
    return tuple(
        CellRole.EDITABLE if role is BatchColumnRole.INPUT else CellRole.RESULT
        for role in roles
    )


def editable_paste_targets(
    matrix: ClipboardMatrix,
    bounds: SelectionBounds,
    column_roles: Sequence[BatchColumnRole],
) -> dict[GridAddress, str]:
    return _editable_paste_targets(
        matrix,
        bounds,
        batch_roles_to_cell_roles(column_roles),
    )


def editable_clear_targets(
    positions: Iterable[GridAddress],
    column_roles: Sequence[BatchColumnRole],
) -> dict[GridAddress, str]:
    return _editable_clear_targets(
        positions,
        batch_roles_to_cell_roles(column_roles),
    )


__all__ = [
    "BatchTableSurface",
    "ClipboardMatrix",
    "GridAddress",
    "SelectionBounds",
    "batch_roles_to_cell_roles",
    "editable_clear_targets",
    "editable_paste_targets",
    "positions_in_bounds",
    "resolve_adjacent_position",
    "resolve_next_position",
    "selection_bounds",
]
