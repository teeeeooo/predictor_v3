"""Content-hugging shell helpers for Tkinter windows.

This module owns the first Tkinter shell/form slice for measuring visible
content targets and applying one coalesced geometry mutation. Event-loop
scheduling stays in ``ui_tk.window_refit``; primitive geometry policy stays in
``ui_tk.window_geometry``.
"""

from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk

from ui_tk.window_geometry import (
    clamp_geometry_vertically_to_visible_bounds,
    preferred_content_fit_geometry,
)


@dataclass(frozen=True)
class ContentFitResult:
    """Result of one content-hugging fit attempt."""

    target_geometry: str
    applied: bool


def visible_content_fit_geometry(
    *,
    current_geometry: str,
    preferred_content_size: tuple[int, int],
    screen_width: int,
    screen_height: int,
    vertical_overflow_delta: int = 0,
) -> str:
    """Return one geometry string for the current visible content.

    The target height includes a positive overflow delta before the geometry is
    applied, so callers do not need a separate grow-then-clamp mutation. X is
    preserved by the primitive geometry helper to avoid moving windows between
    monitors during profile/detail refits; Y is clamped into visible bounds.
    """

    preferred_width, preferred_height = preferred_content_size
    target_preferred = (
        preferred_width,
        preferred_height + max(0, vertical_overflow_delta),
    )
    geometry = preferred_content_fit_geometry(
        current_geometry,
        target_preferred,
        screen_width,
        screen_height,
    )
    return clamp_geometry_vertically_to_visible_bounds(geometry, screen_height)


class TkContentHuggingShell:
    """Apply content-hugging geometry for a Tk toplevel."""

    def __init__(self, root: tk.Tk | tk.Toplevel) -> None:
        self._root = root

    def fit_visible_content(
        self,
        preferred_content_size: tuple[int, int],
        *,
        vertical_overflow_delta: int = 0,
    ) -> ContentFitResult:
        """Fit the toplevel to visible content with at most one geometry call."""

        root = self._root
        root.update_idletasks()
        target_geometry = visible_content_fit_geometry(
            current_geometry=root.geometry(),
            preferred_content_size=preferred_content_size,
            screen_width=root.winfo_screenwidth(),
            screen_height=root.winfo_screenheight(),
            vertical_overflow_delta=vertical_overflow_delta,
        )
        if root.geometry() == target_geometry:
            return ContentFitResult(target_geometry=target_geometry, applied=False)

        root.geometry(target_geometry)
        root.update_idletasks()
        return ContentFitResult(target_geometry=target_geometry, applied=True)
