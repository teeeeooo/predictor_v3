"""Visible content measurement adapters for Tkinter window shells.

This module owns toolkit-specific measurement policy. Window shell fitting
stays in ``ui_tk.window_shell``; event-loop scheduling stays in
``ui_tk.window_refit``; primitive geometry calculations stay in
``ui_tk.window_geometry``.
"""

from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass
from typing import Any, Callable, ContextManager

from ui_tk.layout_constants import APP_WINDOW_CONTENT_SAFETY_MARGIN_RATIO


SuppressMeasurement = Callable[[], ContextManager[object]]


@dataclass(frozen=True)
class NestedNotebookMeasurement:
    """Measured size data for one nested notebook."""

    max_tab_width: int = 0
    max_tab_height: int = 0
    current_tab_height: int = 0
    notebook_height: int = 0


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

    def preferred_size(self) -> tuple[int, int]:
        """Return preferred size for the current visible content state."""

        self._content.update_idletasks()
        nested = self._measure_nested_notebook()

        content_width = max(self._content.winfo_reqwidth(), nested.max_tab_width)
        content_height = self._content.winfo_reqheight()

        if nested.notebook_height > 0:
            notebook_chrome_height = max(0, nested.notebook_height - nested.max_tab_height)
            content_height = (
                content_height
                - nested.notebook_height
                + notebook_chrome_height
                + nested.current_tab_height
            )

        margin = self._horizontal_margin_ratio
        vertical_margin = min(int(content_height * margin), self._vertical_margin_cap)
        return (
            int(content_width * (1 + margin)) + self._scrollbar.winfo_reqwidth(),
            content_height + vertical_margin,
        )

    def vertical_overflow_delta(self) -> int:
        """Return positive vertical overflow from the scroll container."""

        return self._overflow_source.vertical_overflow_delta()

    def _measure_nested_notebook(self) -> NestedNotebookMeasurement:
        notebook = self._nested_notebook
        if notebook is None or not self._nested_notebook_active():
            return NestedNotebookMeasurement()

        tabs = tuple(notebook.tabs())
        if not tabs:
            return NestedNotebookMeasurement()

        original_tab = notebook.select()
        current_tab = original_tab or tabs[0]
        max_tab_width = 0
        max_tab_height = 0
        current_tab_height = 0

        with self._suppress_measurement():
            for tab_id in tabs:
                notebook.select(tab_id)
                notebook.update_idletasks()
                widget = notebook.nametowidget(tab_id)
                width = widget.winfo_reqwidth()
                height = widget.winfo_reqheight()
                max_tab_width = max(max_tab_width, width)
                max_tab_height = max(max_tab_height, height)
                if tab_id == current_tab:
                    current_tab_height = height
            notebook.select(current_tab)
            notebook.update_idletasks()

        if current_tab_height <= 0:
            current_widget = notebook.nametowidget(current_tab)
            current_tab_height = current_widget.winfo_reqheight()

        return NestedNotebookMeasurement(
            max_tab_width=max_tab_width,
            max_tab_height=max_tab_height,
            current_tab_height=current_tab_height,
            notebook_height=notebook.winfo_reqheight(),
        )
