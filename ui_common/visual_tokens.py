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
    "surface.default": "#F4F7F8",
    "surface.panel": "#FFFFFF",
    "surface.header": "#EAF0F2",
    "text.default": "#162A31",
    "text.muted": "#60737B",
    "text.disabled": "#93A1A6",
    "text.on_accent": "#FFFFFF",
    "border.default": "#CBD5DF",
    "border.focus": "#14B8A6",
    "accent.primary": "#0F766E",
    "action.primary": "#0F766E",
    "action.hover": "#0B625C",
    "action.pressed": "#084F4A",
    "table.header": "#E8F0F2",
    "table.input": "#FFFFFF",
    "table.fixed": "#EEF2F4",
    "table.calculated": "#EAF3F5",
    "table.result": "#E8F5EF",
    "table.invalid": "#FDEAEA",
    "table.warning": "#FFF4D8",
    "table.selected": "#D9EEEC",
    "table.active": "#BDE0DC",
    "table.focus": "#0F766E",
    "result.good": "#177A52",
    "result.warning": "#A96D12",
    "result.error": "#B94343",
    "status.neutral": "#52666E",
    "status.ready": "#177A52",
    "status.missing": "#A96D12",
    "status.running": "#2563A6",
}

_SPACING: Mapping[str, int] = {
    "space.xs": 4,
    "space.sm": 8,
    "space.md": 16,
    "space.lg": 24,
    "space.outer": 15,
    "space.panel": 12,
    "space.row": 6,
    "space.cell": 6,
}

_RADII: Mapping[str, int] = {
    "radius.cell": 4,
    "radius.panel": 8,
    "radius.pill": 999,
}

_FONTS: Mapping[str, Mapping[str, object]] = {
    "font.body": {
        "family": None,
        "size": 10,
        "weight": "normal",
        "role": "body",
    },
    "font.label": {
        "family": None,
        "size": 10,
        "weight": "medium",
        "role": "label",
    },
    "font.window_title": {
        "family": None,
        "size": 18,
        "weight": "bold",
        "role": "window_title",
    },
    "font.panel_title": {
        "family": None,
        "size": 13,
        "weight": "bold",
        "role": "panel_title",
    },
    "font.table.header": {
        "family": None,
        "size": 10,
        "weight": "bold",
        "role": "table_header",
    },
    "font.table.cell": {
        "family": None,
        "size": 10,
        "weight": "normal",
        "role": "table_cell",
    },
    "font.caption": {
        "family": None,
        "size": 10,
        "weight": "normal",
        "role": "caption",
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
