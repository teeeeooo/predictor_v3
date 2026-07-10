"""Window geometry helpers for the Tkinter calculator shell.

These functions are separated from the app shell so the shell stays
thin and the geometry policy lives in a dedicated module.
"""

from __future__ import annotations

import re
import tkinter as tk
from typing import Protocol

from apps.calculator.ui.layout_constants import (
    APP_WINDOW_FALLBACK_MIN_HEIGHT,
    APP_WINDOW_FALLBACK_MIN_WIDTH,
    APP_WINDOW_MAX_HEIGHT_RATIO,
    APP_WINDOW_MAX_WIDTH_RATIO,
    APP_WINDOW_MIN_VISIBLE_HEIGHT,
    APP_WINDOW_MIN_VISIBLE_WIDTH,
    APP_WINDOW_SCREEN_MARGIN_X_RATIO,
    APP_WINDOW_SCREEN_MARGIN_Y_RATIO,
)


class SupportsVerticalOverflowDelta(Protocol):
    """Protocol for objects that expose vertical_overflow_delta."""
    def vertical_overflow_delta(self) -> int: ...


_GEOMETRY_RE = re.compile(
    r"^(?P<width>\d+)x(?P<height>\d+)(?P<x>(?:[+-]|--)\d+)(?P<y>(?:[+-]|--)\d+)$"
)


def parse_window_geometry(geometry: str) -> tuple[int, int, int, int]:
    match = _GEOMETRY_RE.match(geometry)
    if match is None:
        raise ValueError(f"Unsupported window geometry: {geometry!r}")
    return (
        int(match.group("width")),
        int(match.group("height")),
        _parse_geometry_coordinate(match.group("x")),
        _parse_geometry_coordinate(match.group("y")),
    )


def format_window_geometry(width: int, height: int, x: int, y: int) -> str:
    return f"{width}x{height}{x:+d}{y:+d}"


def _parse_geometry_coordinate(value: str) -> int:
    if value.startswith("--"):
        return -int(value[2:])
    return int(value)


def _screen_margin_y(screen_height: int) -> int:
    return int(screen_height * APP_WINDOW_SCREEN_MARGIN_Y_RATIO)


def _max_auto_fit_height(screen_height: int) -> int:
    return min(
        screen_height - _screen_margin_y(screen_height),
        int(screen_height * APP_WINDOW_MAX_HEIGHT_RATIO),
    )


def _visible_bottom_y(screen_height: int) -> int:
    return screen_height - _screen_margin_y(screen_height)


def capped_window_size(
    requested_width: int,
    requested_height: int,
    screen_width: int,
    screen_height: int,
    preferred_content_size: tuple[int, int] | None = None,
) -> tuple[int, int]:
    if preferred_content_size is not None:
        requested_width = max(requested_width, preferred_content_size[0])
        requested_height = max(requested_height, preferred_content_size[1])
    margin_x = int(screen_width * APP_WINDOW_SCREEN_MARGIN_X_RATIO)
    max_width = min(screen_width - margin_x, int(screen_width * APP_WINDOW_MAX_WIDTH_RATIO))
    max_height = _max_auto_fit_height(screen_height)
    return (
        max(
            APP_WINDOW_MIN_VISIBLE_WIDTH,
            min(requested_width, max_width),
        ),
        max(
            APP_WINDOW_MIN_VISIBLE_HEIGHT,
            min(requested_height, max_height),
        ),
    )


def centered_geometry(
    width: int, height: int, screen_width: int, screen_height: int
) -> str:
    width = max(APP_WINDOW_MIN_VISIBLE_WIDTH, width)
    height = max(APP_WINDOW_MIN_VISIBLE_HEIGHT, height)
    x = max(APP_WINDOW_MIN_VISIBLE_WIDTH - 1, (screen_width - width) // 2)
    y = max(APP_WINDOW_MIN_VISIBLE_HEIGHT - 1, (screen_height - height) // 2)
    return f"{width}x{height}+{x}+{y}"


def initial_window_geometry(
    requested_width: int,
    requested_height: int,
    screen_width: int,
    screen_height: int,
    preferred_content_size: tuple[int, int] | None = None,
) -> str:
    width, height = capped_window_size(
        requested_width,
        requested_height,
        screen_width,
        screen_height,
        preferred_content_size,
    )
    return centered_geometry(width, height, screen_width, screen_height)


def parent_centered_content_geometry(
    parent_geometry: str,
    requested_content_size: tuple[int, int],
    screen_width: int,
    screen_height: int,
    min_size: tuple[int, int] = (1, 1),
) -> str:
    """Center a dialog on its parent without moving it to monitor one.

    Tk exposes the primary screen dimensions but not a portable per-monitor
    work area. Clamp an axis only when the parent intersects that primary
    area. A parent wholly outside it is already on another monitor, so its
    centered coordinate must be preserved.
    """
    parent_width, parent_height, parent_x, parent_y = parse_window_geometry(parent_geometry)
    requested_width = max(requested_content_size[0], min_size[0])
    requested_height = max(requested_content_size[1], min_size[1])
    width, height = capped_window_size(
        requested_width,
        requested_height,
        screen_width,
        screen_height,
    )
    x = parent_x + (parent_width - width) // 2
    y = parent_y + (parent_height - height) // 2
    x = _clamp_axis_when_parent_intersects_primary(
        coordinate=x,
        extent=width,
        screen_extent=screen_width,
        parent_coordinate=parent_x,
        parent_extent=parent_width,
    )
    y = _clamp_axis_when_parent_intersects_primary(
        coordinate=y,
        extent=height,
        screen_extent=screen_height,
        parent_coordinate=parent_y,
        parent_extent=parent_height,
    )
    return format_window_geometry(width, height, x, y)


def _clamp_axis_when_parent_intersects_primary(
    *,
    coordinate: int,
    extent: int,
    screen_extent: int,
    parent_coordinate: int,
    parent_extent: int,
) -> int:
    parent_end = parent_coordinate + parent_extent
    parent_intersects_primary = parent_coordinate < screen_extent and parent_end > 0
    if not parent_intersects_primary:
        return coordinate
    return min(max(0, coordinate), max(0, screen_extent - extent))


def resolve_min_window_size(screen_width: int, screen_height: int) -> tuple[int, int]:
    return (
        min(APP_WINDOW_FALLBACK_MIN_WIDTH, screen_width),
        min(APP_WINDOW_FALLBACK_MIN_HEIGHT, screen_height),
    )


def center_window(
    root: tk.Tk, preferred_content_size: tuple[int, int] | None = None
) -> None:
    root.update_idletasks()
    width = max(root.winfo_reqwidth(), root.winfo_width())
    height = max(root.winfo_reqheight(), root.winfo_height())
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    geom = initial_window_geometry(
        width, height, screen_width, screen_height, preferred_content_size
    )
    root.geometry(geom)
    # Ensure minsize does not force the initial window larger than the
    # computed geometry on platforms that enforce minsize on display.
    init_w, init_h, _x, _y = parse_window_geometry(geom)
    min_height = min(APP_WINDOW_FALLBACK_MIN_HEIGHT, init_h)
    if preferred_content_size is not None:
        min_height = min(min_height, preferred_content_size[1])
    root.minsize(
        min(APP_WINDOW_FALLBACK_MIN_WIDTH, init_w),
        min_height,
    )


def apply_overflow_correction(root: tk.Tk, tab: SupportsVerticalOverflowDelta) -> None:
    """One-shot init-only correction: if the tab has vertical overflow and screen
    cap allows, grow the window by the measured delta so the scrollbar
    can be hidden without cutting content.  This is called once during
    CalculatorTkApp construction; it must not be bound to resize events.
    """
    root.update_idletasks()
    delta = tab.vertical_overflow_delta()
    if delta <= 0:
        return
    geom = root.geometry()
    w, h, x, y = parse_window_geometry(geom)
    screen_height = root.winfo_screenheight()
    new_h = min(h + delta, _max_auto_fit_height(screen_height))
    if new_h > h:
        root.geometry(format_window_geometry(w, new_h, x, y))
        root.update_idletasks()


def _geometry_size(geometry: str) -> tuple[int, int]:
    w, h, _x, _y = parse_window_geometry(geometry)
    return (w, h)


def clamp_geometry_to_visible_bounds(
    geometry: str, screen_width: int, screen_height: int
) -> str:
    width, height, x, y = parse_window_geometry(geometry)
    max_x = max(0, screen_width - width)
    max_y = max(0, screen_height - height)
    return format_window_geometry(width, height, min(max(0, x), max_x), min(max(0, y), max_y))


def clamp_geometry_vertically_to_visible_bounds(
    geometry: str, screen_height: int
) -> str:
    """Clamp y only for profile/detail fit; preserve x for multi-monitor use."""
    width, height, x, y = parse_window_geometry(geometry)
    margin_y = _screen_margin_y(screen_height)
    visible_bottom = _visible_bottom_y(screen_height)
    large_height_threshold = int(screen_height * 0.75)
    if height >= visible_bottom:
        new_y = 0
    elif height >= large_height_threshold:
        new_y = min(margin_y, visible_bottom - height)
    else:
        new_y = min(max(0, y), visible_bottom - height)
    return format_window_geometry(width, height, x, new_y)


def clamp_window_to_visible_bounds(root: tk.Tk) -> None:
    """Initial-launch full visible clamp; may adjust x and y."""
    geom = clamp_geometry_to_visible_bounds(
        root.geometry(),
        root.winfo_screenwidth(),
        root.winfo_screenheight(),
    )
    if root.geometry() != geom:
        root.geometry(geom)
        root.update_idletasks()


def clamp_window_vertically_to_visible_bounds(root: tk.Tk) -> None:
    geom = clamp_geometry_vertically_to_visible_bounds(
        root.geometry(),
        root.winfo_screenheight(),
    )
    if root.geometry() != geom:
        root.geometry(geom)
        root.update_idletasks()


def preferred_content_fit_geometry(
    current_geometry: str,
    preferred_content_size: tuple[int, int],
    screen_width: int,
    screen_height: int,
) -> str:
    _current_w, _current_h, x, y = parse_window_geometry(current_geometry)
    width, height = capped_window_size(
        preferred_content_size[0],
        preferred_content_size[1],
        screen_width,
        screen_height,
    )
    return format_window_geometry(width, height, x, y)


def fit_window_to_preferred_content(
    root: tk.Tk, preferred_content_size: tuple[int, int]
) -> None:
    """One-shot exact content fit for explicit profile/content switches.

    This is intentionally event-driven by callers, not bound to
    ``<Configure>``. It reuses the initial geometry screen-cap policy
    and lets the current profile's preferred size grow or shrink the window.
    """
    root.update_idletasks()
    geom = preferred_content_fit_geometry(
        root.geometry(),
        preferred_content_size,
        root.winfo_screenwidth(),
        root.winfo_screenheight(),
    )
    if root.geometry() != geom:
        root.geometry(geom)
        root.update_idletasks()


def grow_window_by_vertical_delta(root: tk.Tk, delta: int) -> None:
    """Grow window height by a measured overflow delta once, capped to screen."""
    if delta <= 0:
        return
    root.update_idletasks()
    geom = root.geometry()
    w, h, x, y = parse_window_geometry(geom)
    screen_height = root.winfo_screenheight()
    new_h = min(h + delta, _max_auto_fit_height(screen_height))
    if new_h > h:
        root.geometry(format_window_geometry(w, new_h, x, y))
        root.update_idletasks()
