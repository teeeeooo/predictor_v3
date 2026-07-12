"""Scrollable frame helper with auto-hide scrollbar.

This widget owns a Canvas, a vertical Scrollbar, and a content Frame.
The scrollbar is shown only when content exceeds the canvas viewport.
Mousewheel handling is included.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.theme import APP_SURFACE


def mousewheel_units(event) -> int:
    if getattr(event, "num", None) == 4:
        return -1
    if getattr(event, "num", None) == 5:
        return 1
    delta = getattr(event, "delta", 0)
    if delta > 0:
        return -1
    if delta < 0:
        return 1
    return 0


class ScrollableFrame(tk.Frame):
    """A frame with a scrollable content area and auto-hide scrollbar."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, background=APP_SURFACE)

        self._canvas = tk.Canvas(
            self,
            background=APP_SURFACE,
            highlightthickness=0,
            borderwidth=0,
        )
        self._scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self._canvas.yview
        )
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrollbar_visible = False
        self._update_scrollbar_visibility()

        self._content = ttk.Frame(self._canvas)
        self._content_window = self._canvas.create_window(
            (0, 0), window=self._content, anchor="nw"
        )
        self._content.bind("<Configure>", self._on_content_configured)
        self._canvas.bind("<Configure>", self._on_canvas_configured)
        self.bind("<Configure>", self._sync_content_width)
        self._mousewheel_toplevel = self.winfo_toplevel()
        self._mousewheel_bindings = (
            (
                "<MouseWheel>",
                self._mousewheel_toplevel.bind(
                    "<MouseWheel>", self._on_mousewheel, add="+"
                ),
            ),
            (
                "<Button-4>",
                self._mousewheel_toplevel.bind(
                    "<Button-4>", self._on_mousewheel, add="+"
                ),
            ),
            (
                "<Button-5>",
                self._mousewheel_toplevel.bind(
                    "<Button-5>", self._on_mousewheel, add="+"
                ),
            ),
        )
        self.bind("<Destroy>", self._unbind_mousewheel, add="+")

    @property
    def content(self) -> ttk.Frame:
        return self._content

    @property
    def canvas(self) -> tk.Canvas:
        return self._canvas

    @property
    def scrollbar(self) -> ttk.Scrollbar:
        return self._scrollbar

    @property
    def scrollbar_visible(self) -> bool:
        return self._scrollbar_visible

    def vertical_overflow_delta(self) -> int:
        """Return measured vertical overflow in pixels, or 0 if none."""
        bbox = self._canvas.bbox("all")
        if bbox is None:
            return 0
        content_height = bbox[3] - bbox[1]
        canvas_height = self._canvas.winfo_height()
        return max(0, content_height - canvas_height)

    def reset_scroll_position(self) -> None:
        """Move the viewport back to the top of the content."""
        self._canvas.yview_moveto(0)

    def _update_scrollbar_visibility(self, _event=None) -> None:
        """Show scrollbar only when content exceeds canvas viewport."""
        bbox = self._canvas.bbox("all")
        if bbox is None:
            content_height = 0
        else:
            content_height = bbox[3] - bbox[1]
        canvas_height = self._canvas.winfo_height()
        needed = content_height > canvas_height
        if needed and not self._scrollbar_visible:
            self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self._scrollbar_visible = True
        elif not needed and self._scrollbar_visible:
            self._scrollbar.pack_forget()
            self._scrollbar_visible = False

    def _on_content_configured(self, _event=None) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._update_scrollbar_visibility()

    def _on_canvas_configured(self, event) -> None:
        self._canvas.itemconfigure(self._content_window, width=event.width)

    def _sync_content_width(self, _event=None) -> None:
        width = self._canvas.winfo_width()
        if _event is not None and getattr(_event, "width", 0) > width:
            width = _event.width - self._scrollbar.winfo_reqwidth()
        width = max(1, width)
        # The canvas window controls the rendered viewport width. Do not also set
        # the embedded frame's requested width: a wide hidden sibling tab would
        # then overwrite the intrinsic content measurement used to fit the active
        # Calculator tab.
        self._canvas.itemconfigure(self._content_window, width=width)

    def _unbind_mousewheel(self, _event=None) -> None:
        if _event is not None and getattr(_event, "widget", None) is not self:
            return
        for sequence, funcid in self._mousewheel_bindings:
            self._mousewheel_toplevel.unbind(sequence, funcid)
        self._mousewheel_bindings = ()

    def _contains_widget(self, widget) -> bool:
        while widget is not None:
            if widget is self:
                return True
            widget = getattr(widget, "master", None)
        return False

    def _on_mousewheel(self, event) -> str:
        if not self._contains_widget(getattr(event, "widget", None)):
            return ""
        if self.vertical_overflow_delta() <= 0:
            return "break"
        units = mousewheel_units(event)
        if units:
            self._canvas.yview_scroll(units, "units")
        return "break"
