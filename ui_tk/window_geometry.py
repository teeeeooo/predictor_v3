"""Window geometry helpers for the Tkinter calculator shell.

These functions are separated from the app shell so the shell stays
thin and the geometry policy lives in a dedicated module.
"""

from __future__ import annotations

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
    if preferred_content_size is not None:
        requested_width = max(requested_width, preferred_content_size[0])
        requested_height = max(requested_height, preferred_content_size[1])
    margin_x = int(screen_width * APP_WINDOW_SCREEN_MARGIN_X_RATIO)
    margin_y = int(screen_height * APP_WINDOW_SCREEN_MARGIN_Y_RATIO)
    max_width = min(screen_width - margin_x, int(screen_width * APP_WINDOW_MAX_WIDTH_RATIO))
    max_height = min(screen_height - margin_y, int(screen_height * APP_WINDOW_MAX_HEIGHT_RATIO))
    width = min(requested_width, max_width)
    height = min(requested_height, max_height)
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
    size_part = geom.split("+")[0]
    init_w, init_h = (int(v) for v in size_part.split("x"))
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
    size_part = geom.split("+")[0]
    pos_part = "+".join(geom.split("+")[1:])
    w, h = (int(v) for v in size_part.split("x"))
    screen_height = root.winfo_screenheight()
    margin_y = int(screen_height * APP_WINDOW_SCREEN_MARGIN_Y_RATIO)
    max_height = min(screen_height - margin_y, int(screen_height * APP_WINDOW_MAX_HEIGHT_RATIO))
    new_h = min(h + delta, max_height)
    if new_h > h:
        root.geometry(f"{w}x{new_h}+{pos_part}")
        root.update_idletasks()
