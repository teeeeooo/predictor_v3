"""Window geometry helpers for the Tkinter calculator shell.

These functions are separated from the app shell so the shell stays
thin and the geometry policy lives in a dedicated module.
"""

from __future__ import annotations

import re
import tkinter as tk
from typing import Protocol

from ui_tk.layout_constants import (
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


_GEOMETRY_RE = re.compile(r"^(?P<width>\d+)x(?P<height>\d+)(?P<x>[+-]\d+)(?P<y>[+-]\d+)$")


def parse_window_geometry(geometry: str) -> tuple[int, int, int, int]:
    match = _GEOMETRY_RE.match(geometry)
    if match is None:
        raise ValueError(f"Unsupported window geometry: {geometry!r}")
    return (
        int(match.group("width")),
        int(match.group("height")),
        int(match.group("x")),
        int(match.group("y")),
    )


def format_window_geometry(width: int, height: int, x: int, y: int) -> str:
    return f"{width}x{height}{x:+d}{y:+d}"


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
    margin_y = int(screen_height * APP_WINDOW_SCREEN_MARGIN_Y_RATIO)
    max_width = min(screen_width - margin_x, int(screen_width * APP_WINDOW_MAX_WIDTH_RATIO))
    max_height = min(screen_height - margin_y, int(screen_height * APP_WINDOW_MAX_HEIGHT_RATIO))
    return (
        min(requested_width, max_width),
        min(requested_height, max_height),
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
    root.minsize(
        min(APP_WINDOW_FALLBACK_MIN_WIDTH, init_w),
        min(APP_WINDOW_FALLBACK_MIN_HEIGHT, init_h),
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
    margin_y = int(screen_height * APP_WINDOW_SCREEN_MARGIN_Y_RATIO)
    max_height = min(screen_height - margin_y, int(screen_height * APP_WINDOW_MAX_HEIGHT_RATIO))
    new_h = min(h + delta, max_height)
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
    width, height, x, y = parse_window_geometry(geometry)
    margin_y = int(screen_height * APP_WINDOW_SCREEN_MARGIN_Y_RATIO)
    visible_bottom = screen_height - margin_y
    if height >= visible_bottom:
        new_y = 0
    else:
        new_y = min(max(0, y), visible_bottom - height)
    return format_window_geometry(width, height, x, new_y)


def clamp_window_to_visible_bounds(root: tk.Tk) -> None:
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
    margin_y = int(screen_height * APP_WINDOW_SCREEN_MARGIN_Y_RATIO)
    max_height = min(screen_height - margin_y, int(screen_height * APP_WINDOW_MAX_HEIGHT_RATIO))
    new_h = min(h + delta, max_height)
    if new_h > h:
        root.geometry(format_window_geometry(w, new_h, x, y))
        root.update_idletasks()
