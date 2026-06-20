"""Tkinter viewport helper for batch table surfaces."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.scrollable_frame import mousewheel_units


class BatchTableViewport(ttk.Frame):
    """Canvas-backed vertical containment for a batch table grid."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        content_name: str,
        content_background: str,
    ) -> None:
        super().__init__(master, name="batch_table_viewport")
        self.surface_role = "batch_table_viewport"
        self.layout_policy = "vertical_scroll_containment"
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
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrollbar_visible = False
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
        )
        self.bind("<Destroy>", self._unbind_mousewheel, add="+")

    @property
    def scrollbar_visible(self) -> bool:
        return self._scrollbar_visible

    def sync(self, max_visible_height: int) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        content_height = self.content.winfo_reqheight()
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
        needed = content_height > viewport_height
        if needed and not self._scrollbar_visible:
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self._scrollbar_visible = True
        elif not needed and self._scrollbar_visible:
            self.scrollbar.pack_forget()
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
