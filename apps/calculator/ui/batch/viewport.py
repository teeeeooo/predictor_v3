"""Tkinter viewport helper for batch table surfaces."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.scrollable_frame import mousewheel_units


class BatchTableViewport(ttk.Frame):
    """Canvas-backed two-axis containment for a batch table grid."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        content_name: str,
        content_background: str,
    ) -> None:
        super().__init__(master, name="batch_table_viewport")
        self.surface_role = "batch_table_viewport"
        self.layout_policy = "table_local_two_axis_scroll_containment"
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(
            self,
            name="batch_table_viewport_canvas",
            highlightthickness=0,
            borderwidth=0,
        )
        self.scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
        )
        self.horizontal_scrollbar = ttk.Scrollbar(
            self,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview,
        )
        self.canvas.configure(
            yscrollcommand=self.scrollbar.set,
            xscrollcommand=self.horizontal_scrollbar.set,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        # Keep the horizontal affordance stable. Dynamically adding/removing it
        # from a canvas <Configure> callback makes Tk recalculate the viewport,
        # which can oscillate forever when a batch dialog is reopened with a
        # different row count on macOS.
        self.horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        self._scrollbar_visible = False
        self._horizontal_scrollbar_visible = True
        self.content = tk.Frame(
            self.canvas,
            name=content_name,
            background=content_background,
            borderwidth=1,
            relief=tk.SOLID,
        )
        self._content_window = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw",
        )
        self.content.bind("<Configure>", self._on_content_configured)
        self.canvas.bind("<Configure>", self._on_canvas_configured)
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
            (
                "<Shift-MouseWheel>",
                self._mousewheel_toplevel.bind(
                    "<Shift-MouseWheel>", self._on_shift_mousewheel, add="+"
                ),
            ),
            (
                "<Shift-Button-4>",
                self._mousewheel_toplevel.bind(
                    "<Shift-Button-4>", self._on_shift_mousewheel, add="+"
                ),
            ),
            (
                "<Shift-Button-5>",
                self._mousewheel_toplevel.bind(
                    "<Shift-Button-5>", self._on_shift_mousewheel, add="+"
                ),
            ),
        )
        self.bind("<Destroy>", self._unbind_mousewheel, add="+")

    @property
    def scrollbar_visible(self) -> bool:
        return self._scrollbar_visible

    @property
    def horizontal_scrollbar_visible(self) -> bool:
        return self._horizontal_scrollbar_visible

    def preferred_content_size(self) -> tuple[int, int]:
        """Return the table surface's natural size before viewport allocation."""
        self.content.update_idletasks()
        return (self.content.winfo_reqwidth(), self.content.winfo_reqheight())

    def sync(self, max_visible_height: int) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        content_width, content_height = self.preferred_content_size()
        if content_width > 1:
            self.canvas.configure(width=content_width)
        if content_height > 1:
            self.canvas.configure(height=min(content_height, max_visible_height))
        self._sync_scrollbar_visibility()

    def scroll_to_bottom(self) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1.0)
        self._sync_scrollbar_visibility()

    def vertical_overflow_delta(self) -> int:
        bbox = self.canvas.bbox("all")
        if bbox is None:
            return 0
        content_height = bbox[3] - bbox[1]
        viewport_height = self.canvas.winfo_height()
        return max(0, content_height - viewport_height)

    def horizontal_overflow_delta(self) -> int:
        bbox = self.canvas.bbox("all")
        if bbox is None:
            return 0
        content_width = bbox[2] - bbox[0]
        viewport_width = self.canvas.winfo_width()
        return max(0, content_width - viewport_width)

    def _on_content_configured(self, _event: tk.Event | None = None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._sync_content_width(self.canvas.winfo_width())
        self._sync_scrollbar_visibility()

    def _on_canvas_configured(self, event: tk.Event | None = None) -> None:
        if event is not None:
            self._sync_content_width(event.width)
        self._sync_scrollbar_visibility()

    def _sync_content_width(self, viewport_width: int) -> None:
        content_width = max(viewport_width, self.content.winfo_reqwidth())
        self.canvas.itemconfigure(self._content_window, width=content_width)

    def _sync_scrollbar_visibility(self) -> None:
        bbox = self.canvas.bbox("all")
        content_height = 0 if bbox is None else bbox[3] - bbox[1]
        viewport_height = self.canvas.winfo_height()
        vertical_needed = content_height > viewport_height
        if vertical_needed and not self._scrollbar_visible:
            self.scrollbar.grid(row=0, column=1, sticky="ns")
            self._scrollbar_visible = True
        elif not vertical_needed and self._scrollbar_visible:
            self.scrollbar.grid_remove()
            self._scrollbar_visible = False

    def _unbind_mousewheel(self, _event: tk.Event | None = None) -> None:
        if _event is not None and getattr(_event, "widget", None) is not self:
            return
        for sequence, funcid in self._mousewheel_bindings:
            self._mousewheel_toplevel.unbind(sequence, funcid)
        self._mousewheel_bindings = ()

    def _contains_widget(self, widget: tk.Misc | None) -> bool:
        while widget is not None:
            if widget is self:
                return True
            widget = getattr(widget, "master", None)
        return False

    def _on_mousewheel(self, event: tk.Event) -> str:
        if not self._contains_widget(getattr(event, "widget", None)):
            return ""
        if self.vertical_overflow_delta() <= 0:
            return "break"
        units = mousewheel_units(event)
        if units:
            self.canvas.yview_scroll(units, "units")
        return "break"

    def _on_shift_mousewheel(self, event: tk.Event) -> str:
        if not self._contains_widget(getattr(event, "widget", None)):
            return ""
        if self.horizontal_overflow_delta() <= 0:
            return "break"
        units = mousewheel_units(event)
        if units:
            self.canvas.xview_scroll(units, "units")
        return "break"
