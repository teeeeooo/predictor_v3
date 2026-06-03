"""Calculator UI design tokens.

Pure Python token registry derived from
``docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md``. Token *names* are the
contract; the values bound here are the conservative palette that
captures hex / size / spacing values already used inline across
``ui/calc_window.py`` and ``ui/calculators_2point.py``.

This module is intentionally framework-agnostic:

- No PyQt5 import. Importing this module on a system without PyQt5
  must succeed.
- Helper functions return plain strings / numbers / tuples — never
  ``QColor`` / ``QFont``. Call sites convert as needed.
- This is a foundation only. Inline hex sweep across the whole UI is
  deliberately *not* part of this slice (see report 108).
"""

from __future__ import annotations

import re
from typing import Mapping

__all__ = [
    "COLOR_TOKENS",
    "FONT_TOKENS",
    "SPACING_TOKENS",
    "color",
    "spacing",
    "font_token",
]


# Hex color values captured from current inline usage. Values are
# preserved as-is; this slice does not redesign the palette.
COLOR_TOKENS: Mapping[str, str] = {
    "color.bg.app": "#F6F7F9",
    "color.bg.card": "#FFFFFF",
    "color.bg.header": "#F5F5F5",
    "color.bg.cell.readonly": "#EEF1F4",
    "color.bg.cell.invalid": "#FDEDEC",
    "color.text.primary": "#102A43",
    "color.text.secondary": "#526071",
    "color.text.disabled": "#8A94A3",
    "color.accent": "#2F6F9F",
    "color.success": "#2E7D32",
    "color.warning": "#B26A00",
    "color.danger": "#E74C3C",
    "color.border": "#DCE1E7",
}


# Font tokens carry ``(family, size_pt, weight)``. ``family=None`` means
# "use the application default family". ``weight`` follows the Qt
# convention (``"normal"`` / ``"bold"``). Call sites decide how to bind
# these into ``QFont``.
FONT_TOKENS: Mapping[str, tuple] = {
    "font.window_title": (None, 16, "bold"),
    "font.card_title": (None, 14, "bold"),
    "font.section_label": (None, 12, "bold"),
    "font.body": (None, 11, "normal"),
    "font.table.header": (None, 11, "bold"),
    "font.table.cell": (None, 11, "normal"),
    "font.caption": (None, 10, "normal"),
}


# Spacing tokens are pixel integers. Values capture current layout
# margins / padding already used by the calculator UI.
SPACING_TOKENS: Mapping[str, int] = {
    "space.outer": 15,
    "space.card": 12,
    "space.section": 8,
    "space.row": 6,
    "space.button": 8,
    "space.cell": 6,
}


_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def color(name: str) -> str:
    """Return the hex string for a registered color token."""
    try:
        return COLOR_TOKENS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown color token: {name!r}") from exc


def spacing(name: str) -> int:
    """Return the pixel value for a registered spacing token."""
    try:
        return SPACING_TOKENS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown spacing token: {name!r}") from exc


def font_token(name: str) -> tuple:
    """Return ``(family, size_pt, weight)`` for a registered font token."""
    try:
        return FONT_TOKENS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown font token: {name!r}") from exc
