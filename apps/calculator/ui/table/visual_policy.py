"""Shared Tk presentation policy for Calculator table families."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from apps.calculator.ui.layout_constants import (
    RESULT_VALUE_BG,
    TABLE_ACTIVE_BG,
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
    TABLE_EDITABLE_BG,
    TABLE_ERROR_BG,
    TABLE_FOCUS_BORDER,
    TABLE_GRID_COLOR,
    TABLE_HEADER_BG,
    TABLE_HEADER_FG,
    TABLE_HEADER_FONT,
    TABLE_HEADER_PADY,
    TABLE_INVALID_BG,
    TABLE_PASS_BG,
    TABLE_SELECTED_BG,
    TABLE_STATIC_FG,
)


class AlignmentRole(str, Enum):
    IDENTITY_TEXT = "identity_text"
    DESCRIPTIVE_TEXT = "descriptive_text"
    NUMERIC_INPUT = "numeric_input"
    NUMERIC_RESULT = "numeric_result"
    DENSE_NUMERIC_RESULT = "dense_numeric_result"
    STATUS_TEXT = "status_text"
    HEADER_IDENTITY = "header_identity"
    HEADER_VALUE = "header_value"


class SemanticTone(str, Enum):
    DEFAULT = "default"
    CALCULATED = "calculated"
    PASS = "pass"
    FAIL = "fail"
    INVALID = "invalid"
    WARNING = "warning"
    PENDING = "pending"


@dataclass(frozen=True)
class TkTableVisualPolicy:
    """Concrete binding of approved table roles to existing Calculator tokens."""

    divider_color: str = TABLE_GRID_COLOR
    divider_width: int = 1
    outer_border_width: int = 0
    focus_border_color: str = TABLE_FOCUS_BORDER
    header_background: str = TABLE_HEADER_BG
    header_foreground: str = TABLE_HEADER_FG
    header_font: tuple = TABLE_HEADER_FONT
    body_font: tuple = TABLE_BODY_FONT
    cell_padx: int = TABLE_CELL_PADX
    cell_pady: int = TABLE_CELL_PADY
    header_pady: int = TABLE_HEADER_PADY

    def anchor(self, role: AlignmentRole) -> str:
        if role in {
            AlignmentRole.IDENTITY_TEXT,
            AlignmentRole.DESCRIPTIVE_TEXT,
            AlignmentRole.STATUS_TEXT,
            AlignmentRole.HEADER_IDENTITY,
        }:
            return "w"
        if role is AlignmentRole.DENSE_NUMERIC_RESULT:
            return "e"
        return "center"

    def background(self, tone: SemanticTone, *, editable: bool = False) -> str:
        if tone in {SemanticTone.CALCULATED, SemanticTone.PASS}:
            return TABLE_PASS_BG
        if tone in {SemanticTone.FAIL, SemanticTone.INVALID}:
            return TABLE_ERROR_BG if tone is SemanticTone.FAIL else TABLE_INVALID_BG
        if editable:
            return TABLE_EDITABLE_BG
        return RESULT_VALUE_BG

    def foreground(self, *, muted: bool = False) -> str:
        return TABLE_STATIC_FG if muted else TABLE_HEADER_FG

    @staticmethod
    def overlay_background(name: str) -> str:
        if name == "active" or name == "focus":
            return TABLE_ACTIVE_BG
        if name == "selected":
            return TABLE_SELECTED_BG
        raise ValueError(f"unknown table interaction overlay: {name!r}")


DEFAULT_TABLE_VISUAL_POLICY = TkTableVisualPolicy()
