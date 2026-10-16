"""One real Tk Entry per drawn table; drafts stay in the existing table model."""
import tkinter as tk

class CanvasCellEditor:
    def __init__(self, view):
        self.view = view
        self.controller = None
        self.position = None
        self._syncing = False
        self.variable = tk.StringVar(view.frame)
        self.entry = tk.Entry(view.frame, textvariable=self.variable,
            relief=tk.FLAT, borderwidth=0, highlightthickness=0, takefocus=False,
            justify=tk.CENTER, font=view.policy.body_font)
        self.entry.surface_role = "editable_entry"
        self._trace = self.variable.trace_add("write", self._changed)

    def editable(self, position):
        table = self.controller.table
        return (position is not None and 0 <= position[0] < table.row_count()
                and 0 <= position[1] < table.column_count()
                and self.controller._is_editable(position))

    def focus_widget(self, position):
        self.view.reveal(position)
        if not self.editable(position):
            self.hide()
            return self.view.frame
        self.position = position
        self.refresh()
        return self.entry

    def refresh(self):
        if self.controller is None or self.position is None:
            return
        if not self.editable(self.position):
            self.hide()
            return
        value = self.controller.table.text_at_position(self.position)
        if self.variable.get() != value:
            self._syncing = True
            try:
                self.variable.set(value)
            finally:
                self._syncing = False
        x1, y1, x2, y2 = self.view.cell_bbox(self.position)
        policy = self.view.policy
        self.entry.configure(background=self.view.cell_background(self.position))
        self.entry.place(x=x1+policy.cell_padx, y=y1+policy.cell_pady,
                         width=max(1, x2-x1-2*policy.cell_padx-policy.divider_width),
                         height=max(1, y2-y1-2*policy.cell_pady-policy.divider_width))

    def selection_changed(self, active):
        if self.position is not None:
            if active != self.position:
                if self.editable(active):
                    self.position = active
                else:
                    self.hide()
            self.refresh()

    def hide(self):
        if self.entry.focus_get() is self.entry:
            self.view.frame.focus_set()
        self.entry.place_forget()
        self.position = None

    def _changed(self, *_args):
        if not self._syncing and self.controller and self.editable(self.position):
            self.controller.table.set_positions_batch({self.position: self.variable.get()})

    def dispose(self):
        self.variable.trace_remove("write", self._trace)
        self.controller = None
