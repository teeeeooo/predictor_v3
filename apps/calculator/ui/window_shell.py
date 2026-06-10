"""Content-hugging shell helpers for Tkinter windows.

This module owns the first Tkinter shell/form slice for measuring visible
content targets and applying one coalesced geometry mutation. Event-loop
scheduling stays in ``apps.calculator.ui.window_refit``; primitive geometry policy stays in
``apps.calculator.ui.window_geometry``.
"""

from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from typing import Callable, Protocol

from apps.calculator.ui.window_geometry import (
    clamp_geometry_vertically_to_visible_bounds,
    parse_window_geometry,
    preferred_content_fit_geometry,
)


@dataclass(frozen=True)
class ContentFitResult:
    """Result of one content-hugging fit attempt."""

    target_geometry: str
    applied: bool


class VisibleContentSnapshotLike(Protocol):
    preferred_size: tuple[int, int]
    vertical_overflow_delta: int
    include_overflow_in_fit: bool


PreferredSizeProvider = Callable[[], tuple[int, int]]
OverflowProvider = Callable[[], int]
SnapshotProvider = Callable[[], VisibleContentSnapshotLike]
AfterFitHook = Callable[[ContentFitResult], None]


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


class TkContentHuggingForm:
    """Reusable content-hugging binding for one Tk screen/dialog surface."""

    def __init__(
        self,
        shell: "TkContentHuggingShell",
        *,
        snapshot_provider: SnapshotProvider | None = None,
        preferred_size_provider: PreferredSizeProvider,
        overflow_provider: OverflowProvider | None = None,
        after_fit: AfterFitHook | None = None,
    ) -> None:
        self._shell = shell
        self._snapshot_provider = snapshot_provider
        self._preferred_size_provider = preferred_size_provider
        self._overflow_provider = overflow_provider
        self._after_fit = after_fit

    def fit(self) -> ContentFitResult:
        """Measure visible content through providers and fit the shell."""

        if self._snapshot_provider is not None:
            snapshot = self._snapshot_provider()
            result = self._shell.fit_visible_content(
                snapshot.preferred_size,
                vertical_overflow_delta=(
                    snapshot.vertical_overflow_delta
                    if snapshot.include_overflow_in_fit
                    else 0
                ),
            )
            if self._after_fit is not None:
                self._after_fit(result)
            return result

        result = self._shell.fit_visible_content(
            self._preferred_size_provider(),
            vertical_overflow_delta=(
                self._overflow_provider() if self._overflow_provider is not None else 0
            ),
        )
        if self._after_fit is not None:
            self._after_fit(result)
        return result


class TkContentHuggingShell:
    """Content-hugging shell/form template for a Tk toplevel."""

    def __init__(self, root: tk.Tk | tk.Toplevel) -> None:
        self._root = root

    def register_content(
        self,
        *,
        content: tk.Widget | None = None,
        snapshot_provider: SnapshotProvider | None = None,
        preferred_size_provider: PreferredSizeProvider | None = None,
        overflow_provider: OverflowProvider | None = None,
        after_fit: AfterFitHook | None = None,
    ) -> TkContentHuggingForm:
        """Register a reusable content surface with measurement providers.

        ``preferred_size_provider`` is preferred for nested/profile surfaces
        whose visible-height policy differs from raw widget requested size.
        Plain screens/dialogs may pass ``content`` and use the default widget
        requested-size measurement.
        """

        if snapshot_provider is None and preferred_size_provider is None:
            if content is None:
                raise ValueError(
                    "content, snapshot_provider, or preferred_size_provider is required"
                )

            def preferred_size_provider() -> tuple[int, int]:
                content.update_idletasks()
                return (content.winfo_reqwidth(), content.winfo_reqheight())
        elif snapshot_provider is not None and preferred_size_provider is None:
            preferred_size_provider = lambda: snapshot_provider().preferred_size

        return TkContentHuggingForm(
            self,
            snapshot_provider=snapshot_provider,
            preferred_size_provider=preferred_size_provider,
            overflow_provider=overflow_provider,
            after_fit=after_fit,
        )

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
