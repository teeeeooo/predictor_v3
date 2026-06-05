"""Toolkit-neutral-ish cell role semantics for Tk table adapters."""

from __future__ import annotations

from enum import Enum


class CellRole(str, Enum):
    EDITABLE = "editable"
    RESULT = "result"
    READONLY = "readonly"
    HEADER = "header"
    ROW_HEADER = "row_header"
    DISABLED = "disabled"


def is_mutable(role: CellRole) -> bool:
    return role is CellRole.EDITABLE


def is_selectable(role: CellRole) -> bool:
    return role in {CellRole.EDITABLE, CellRole.RESULT, CellRole.READONLY}


def is_copyable(role: CellRole) -> bool:
    return is_selectable(role)
