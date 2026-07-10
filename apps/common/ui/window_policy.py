"""Shared PySide window placement policy for desktop app shells."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QCursor, QGuiApplication
from PySide6.QtWidgets import QWidget


MAX_INITIAL_WIDTH_RATIO = 0.86
MAX_INITIAL_HEIGHT_RATIO = 0.82
DEFAULT_MINIMUM_SIZE = (720, 480)


@dataclass(frozen=True)
class WindowRect:
    """Integer window rectangle inside one available monitor work area."""

    x: int
    y: int
    width: int
    height: int


def initial_window_rect(
    preferred_size: tuple[int, int],
    available_rect: tuple[int, int, int, int],
    *,
    minimum_size: tuple[int, int] = DEFAULT_MINIMUM_SIZE,
    max_width_ratio: float = MAX_INITIAL_WIDTH_RATIO,
    max_height_ratio: float = MAX_INITIAL_HEIGHT_RATIO,
) -> WindowRect:
    """Return a centered, monitor-local initial rectangle."""

    left, top, available_width, available_height = available_rect
    if available_width < 1 or available_height < 1:
        raise ValueError("available monitor size must be positive")
    if not 0 < max_width_ratio <= 1 or not 0 < max_height_ratio <= 1:
        raise ValueError("window cap ratios must be in (0, 1]")

    max_width = max(1, int(available_width * max_width_ratio))
    max_height = max(1, int(available_height * max_height_ratio))
    min_width = min(max(1, minimum_size[0]), max_width)
    min_height = min(max(1, minimum_size[1]), max_height)
    width = min(max(preferred_size[0], min_width), max_width)
    height = min(max(preferred_size[1], min_height), max_height)
    return WindowRect(
        x=left + (available_width - width) // 2,
        y=top + (available_height - height) // 2,
        width=width,
        height=height,
    )


def apply_initial_window_layout(
    window: QWidget,
    preferred_size: tuple[int, int],
    *,
    minimum_size: tuple[int, int] = DEFAULT_MINIMUM_SIZE,
) -> WindowRect:
    """Apply the policy using the monitor under the pointer when possible."""

    screen = (
        QGuiApplication.screenAt(QCursor.pos())
        or window.screen()
        or QGuiApplication.primaryScreen()
    )
    if screen is None:
        window.resize(*preferred_size)
        return WindowRect(0, 0, *preferred_size)

    available = screen.availableGeometry()
    target = initial_window_rect(
        preferred_size,
        (available.x(), available.y(), available.width(), available.height()),
        minimum_size=minimum_size,
    )
    window.setMinimumSize(
        min(minimum_size[0], target.width),
        min(minimum_size[1], target.height),
    )
    window.resize(target.width, target.height)
    window.move(target.x, target.y)
    return target


__all__ = ["WindowRect", "apply_initial_window_layout", "initial_window_rect"]
