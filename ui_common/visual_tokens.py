"""Project-wide semantic visual token foundation.

This module contains toolkit-neutral visual role values for later PyQt and
Tkinter adapters. It imports neither PyQt nor Tkinter, returns only plain
Python values, and does not migrate any existing UI in this slice.
Application and adapter adoption are intentionally deferred follow-up work.
"""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "visual_color",
    "visual_spacing",
    "visual_radius",
    "visual_font",
    "visual_roles",
]


_COLORS: Mapping[str, str] = {
    "surface.default": "#F7F7F6",
    "surface.panel": "#FFFFFF",
    "text.default": "#181818",
    "text.muted": "#626262",
    "border.default": "#D6D6D3",
    "border.focus": "#343434",
    "table.header": "#EDEDEB",
    "table.input": "#FFFFFF",
    "table.fixed": "#F1F2F2",
    "table.calculated": "#EEF2F4",
    "table.invalid": "#FDEDEC",
    "table.warning": "#FFF4DC",
    "table.selected": "#E5EDF2",
    "table.focus": "#343434",
    "result.good": "#2E7D32",
    "result.warning": "#B26A00",
    "result.error": "#C0392B",
}

_SPACING: Mapping[str, int] = {
    "space.xs": 4,
    "space.sm": 8,
    "space.md": 16,
    "space.lg": 24,
}

_RADII: Mapping[str, int] = {
    "radius.cell": 4,
    "radius.panel": 8,
    "radius.pill": 999,
}

_FONTS: Mapping[str, Mapping[str, object]] = {
    "font.body": {
        "family": None,
        "size": 11,
        "weight": "normal",
        "role": "body",
    },
    "font.label": {
        "family": None,
        "size": 11,
        "weight": "medium",
        "role": "label",
    },
    "font.mono_label": {
        "family": "monospace",
        "size": 10,
        "weight": "normal",
        "role": "mono_label",
    },
}

_ROLE_REGISTRIES: Mapping[str, Mapping[str, object]] = {
    "color": _COLORS,
    "spacing": _SPACING,
    "radius": _RADII,
    "font": _FONTS,
}


def visual_color(role: str) -> str:
    """Return the toolkit-neutral color string registered for *role*."""
    try:
        return _COLORS[role]
    except KeyError as exc:
        raise KeyError(f"Unknown visual color role: {role!r}") from exc


def visual_spacing(role: str) -> int:
    """Return the spacing value in pixels registered for *role*."""
    try:
        return _SPACING[role]
    except KeyError as exc:
        raise KeyError(f"Unknown visual spacing role: {role!r}") from exc


def visual_radius(role: str) -> int:
    """Return the geometry radius value in pixels registered for *role*."""
    try:
        return _RADII[role]
    except KeyError as exc:
        raise KeyError(f"Unknown visual radius role: {role!r}") from exc


def visual_font(role: str) -> dict[str, object]:
    """Return a plain toolkit-neutral font descriptor registered for *role*."""
    try:
        return dict(_FONTS[role])
    except KeyError as exc:
        raise KeyError(f"Unknown visual font role: {role!r}") from exc


def visual_roles(kind: str) -> tuple[str, ...]:
    """Return semantic role names for ``color``, ``spacing``, ``radius`` or ``font``."""
    try:
        registry = _ROLE_REGISTRIES[kind]
    except KeyError as exc:
        raise KeyError(f"Unknown visual token kind: {kind!r}") from exc
    return tuple(registry)
