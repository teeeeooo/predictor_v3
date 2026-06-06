"""Tkinter viewport helper for batch table surfaces."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


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

    def _on_content_configured(self, _event: tk.Event | None = None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._sync_scrollbar_visibility()

    def _on_canvas_configured(self, event: tk.Event | None = None) -> None:
        if event is not None:
            self.canvas.itemconfigure(self._content_window, width=event.width)
        self._sync_scrollbar_visibility()

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
