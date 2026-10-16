"""Opt-in drag targets within the dialog shell's existing outer padding."""
from tkinter import ttk

from apps.calculator.ui.layout_constants import BATCH_DIALOG_RESIZE_EDGE_SIZE


class DialogResizeEdges:
    def __init__(self, window):
        self.window = window
        self.origin = None
        self.edges = {}
        size = BATCH_DIALOG_RESIZE_EDGE_SIZE
        for name, cursor, axes, placement in (
            ("bottom", "sb_v_double_arrow", (False, True),
             dict(relx=0, rely=1, relwidth=1, height=size, anchor="sw")),
            ("right", "sb_h_double_arrow", (True, False),
             dict(relx=1, rely=0, relheight=1, width=size, anchor="ne")),
            ("corner", "bottom_right_corner", (True, True),
             dict(relx=1, rely=1, width=size, height=size, anchor="se")),
        ):
            edge = ttk.Frame(window, name=f"resize_{name}", cursor=cursor)
            edge.place(**placement)
            edge.bind("<Button-1>", lambda event, axes=axes: self.begin(event, axes))
            edge.bind("<B1-Motion>", self.drag)
            edge.bind("<ButtonRelease-1>", self.end)
            self.edges[name] = edge

    def begin(self, event, axes):
        allowed = self.window.resizable()
        axes = tuple(requested and enabled for requested, enabled in zip(axes, allowed))
        self.last_size = (self.window.winfo_width(), self.window.winfo_height())
        self.origin = (event.x_root, event.y_root, *self.last_size, axes)

    def drag(self, event):
        if self.origin is None:
            return
        x, y, width, height, (horizontal, vertical) = self.origin
        min_width, min_height = self.window.minsize()
        size = (max(min_width, width + event.x_root - x) if horizontal else width,
                max(min_height, height + event.y_root - y) if vertical else height)
        if size != self.last_size:
            # Omit position: retain the window manager's current monitor/origin.
            self.window.geometry(f"{size[0]}x{size[1]}")
            self.last_size = size

    def end(self, _event):
        self.origin = None
