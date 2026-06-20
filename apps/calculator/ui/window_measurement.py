"""Visible content measurement adapters for Tkinter window shells.

This module owns toolkit-specific measurement policy. Window shell fitting
stays in ``apps.calculator.ui.window_shell``; event-loop scheduling stays in
``apps.calculator.ui.window_refit``; primitive geometry calculations stay in
``apps.calculator.ui.window_geometry``.
"""

from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass, field
from typing import Any, Callable, ContextManager, Mapping

from apps.calculator.ui.layout_constants import APP_WINDOW_CONTENT_SAFETY_MARGIN_RATIO


SuppressMeasurement = Callable[[], ContextManager[object]]


@dataclass(frozen=True)
class NestedNotebookMeasurement:
    """Measured size data for one nested notebook."""

    max_tab_width: int = 0
    max_tab_height: int = 0
    widest_tab_width: int = 0
    current_tab_width: int = 0
    current_tab_height: int = 0
    notebook_height: int = 0
    notebook_width: int = 0


@dataclass(frozen=True)
class VisibleContentSnapshot:
    """One settled measurement snapshot for content-hugging fit."""

    preferred_size: tuple[int, int]
    vertical_overflow_delta: int = 0
    include_overflow_in_fit: bool = False
    diagnostics: Mapping[str, int] = field(default_factory=dict)


class TkVisibleContentMeasurement:
    """Measure visible Tk content for a content-hugging window shell."""

    def __init__(
        self,
        *,
        content: Any,
        scrollbar: Any,
        overflow_source: Any,
        nested_notebook: Any | None = None,
        nested_notebook_active: Callable[[], bool] | None = None,
        suppress_measurement: SuppressMeasurement | None = None,
        horizontal_margin_ratio: float = APP_WINDOW_CONTENT_SAFETY_MARGIN_RATIO,
        vertical_margin_cap: int = 18,
    ) -> None:
        self._content = content
        self._scrollbar = scrollbar
        self._overflow_source = overflow_source
        self._nested_notebook = nested_notebook
        self._nested_notebook_active = nested_notebook_active or (lambda: True)
        self._suppress_measurement = suppress_measurement or nullcontext
        self._horizontal_margin_ratio = horizontal_margin_ratio
        self._vertical_margin_cap = vertical_margin_cap
        self._chrome_height_estimate: int | None = None
        self._chrome_width_estimate: int | None = None

    def preferred_size(self) -> tuple[int, int]:
        """Return preferred size for the current visible content state."""

        return self.snapshot().preferred_size

    def vertical_overflow_delta(self) -> int:
        """Return positive vertical overflow from the scroll container."""

        return self.snapshot().vertical_overflow_delta

    def snapshot(self) -> VisibleContentSnapshot:
        """Return preferred size and overflow from one measurement turn."""

        self._content.update_idletasks()
        nested = self._measure_nested_notebook()

        content_width = self._content.winfo_reqwidth()
        content_height = self._content.winfo_reqheight()

        if nested.notebook_width > 0 and self._chrome_width_estimate is not None:
            # Replace the notebook's full width contribution with chrome + current tab.
            # This works even when notebook_width is sticky at a previous max tab
            # because we use a one-time chrome estimate (tab border/padding) rather
            # than max_tab_width.
            content_width = (
                content_width
                - nested.notebook_width
                + self._chrome_width_estimate
                + nested.current_tab_width
            )
        elif nested.max_tab_width > 0:
            content_width = max(content_width, nested.max_tab_width)

        if nested.notebook_height > 0 and self._chrome_height_estimate is not None:
            # Replace the notebook's full height contribution with chrome + current tab.
            # This works even when notebook_height is sticky at a previous max tab
            # because we use a one-time chrome estimate (tab bar height) rather
            # than max_tab_height.
            content_height = (
                content_height
                - nested.notebook_height
                + self._chrome_height_estimate
                + nested.current_tab_height
            )

        margin = self._horizontal_margin_ratio
        vertical_margin = min(int(content_height * margin), self._vertical_margin_cap)
        preferred_size = (
            int(content_width * (1 + margin)) + self._scrollbar.winfo_reqwidth(),
            content_height + vertical_margin,
        )
        overflow_delta = self._overflow_source.vertical_overflow_delta()
        diagnostics = {
            "content_reqwidth": self._content.winfo_reqwidth(),
            "content_reqheight": self._content.winfo_reqheight(),
            "nested_max_tab_width": nested.max_tab_width,
            "nested_max_tab_height": nested.max_tab_height,
            "nested_widest_tab_width": nested.widest_tab_width,
            "nested_current_tab_width": nested.current_tab_width,
            "nested_current_tab_height": nested.current_tab_height,
            "nested_notebook_height": nested.notebook_height,
            "nested_notebook_width": nested.notebook_width,
            "chrome_height_estimate": self._chrome_height_estimate or 0,
            "chrome_width_estimate": self._chrome_width_estimate or 0,
            "vertical_overflow_delta": overflow_delta,
        }
        return VisibleContentSnapshot(
            preferred_size=preferred_size,
            vertical_overflow_delta=overflow_delta,
            include_overflow_in_fit=False,
            diagnostics=diagnostics,
        )

    def _measure_nested_notebook(self) -> NestedNotebookMeasurement:
        notebook = self._nested_notebook
        if notebook is None or not self._nested_notebook_active():
            return NestedNotebookMeasurement()

        tabs = tuple(notebook.tabs())
        if not tabs:
            return NestedNotebookMeasurement()

        current_tab = notebook.select() or tabs[0]
        current_widget = notebook.nametowidget(current_tab)
        current_tab_width = current_widget.winfo_reqwidth()
        current_tab_height = current_widget.winfo_reqheight()
        tab_widths = tuple(
            notebook.nametowidget(tab_id).winfo_reqwidth() for tab_id in tabs
        )
        tab_heights = tuple(
            notebook.nametowidget(tab_id).winfo_reqheight() for tab_id in tabs
        )
        widest_tab_width = max((current_tab_width, *tab_widths), default=current_tab_width)
        tallest_tab_height = max(
            (current_tab_height, *tab_heights), default=current_tab_height
        )
        notebook_height = notebook.winfo_reqheight()
        notebook_width = notebook.winfo_reqwidth()

        # Tk notebook requested height can already be sticky at a taller hidden
        # tab. Subtract the tallest known tab so sibling height is not cached as
        # tab-bar chrome for a shorter current tab.
        if self._chrome_height_estimate is None:
            self._chrome_height_estimate = max(0, notebook_height - tallest_tab_height)

        # Estimate tab border/padding chrome width once. Tk notebook requested
        # width can already be sticky at a hidden wide tab, so subtract the
        # widest known tab instead of the current visible tab.
        if self._chrome_width_estimate is None:
            self._chrome_width_estimate = max(0, notebook_width - widest_tab_width)

        return NestedNotebookMeasurement(
            max_tab_width=current_tab_width,
            max_tab_height=tallest_tab_height,
            widest_tab_width=widest_tab_width,
            current_tab_width=current_tab_width,
            current_tab_height=current_tab_height,
            notebook_height=notebook_height,
            notebook_width=notebook_width,
        )
