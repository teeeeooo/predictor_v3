"""Small undo binding for form-style Tk entries."""

from __future__ import annotations

import tkinter as tk


def attach_form_entry_undo(entry: tk.Widget, variable: tk.StringVar) -> None:
    """Bind Ctrl/Cmd-Z to restore the previous textvariable value.

    Tk and ttk Entry widgets do not expose a native ``undo`` option. This helper
    covers simple form entries without replacing the table controller undo stack.
    """

    state = {
        "last": variable.get(),
        "stack": [],
        "restoring": False,
    }

    def on_write(*_args) -> None:
        current = variable.get()
        if state["restoring"]:
            state["last"] = current
            return
        if current == state["last"]:
            return
        state["stack"].append(state["last"])
        state["last"] = current

    def undo(_event=None) -> str:
        stack = state["stack"]
        if not stack:
            return "break"
        previous = stack.pop()
        state["restoring"] = True
        try:
            variable.set(previous)
        finally:
            state["restoring"] = False
        state["last"] = previous
        try:
            entry.icursor(tk.END)
        except tk.TclError:
            pass
        return "break"

    trace_id = variable.trace_add("write", on_write)
    entry.bind("<Control-z>", undo)
    entry.bind("<Command-z>", undo)
    entry.bind("<Control-Z>", undo)
    entry.bind("<Command-Z>", undo)
    entry._form_entry_undo_state = state
    entry._form_entry_undo_trace_id = trace_id
    entry._form_entry_undo = undo
