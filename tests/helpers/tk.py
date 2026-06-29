"""Small Tkinter test-isolation helpers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import tkinter as tk


def make_hidden_root() -> tk.Tk:
    """Create a withdrawn Tk root for tests."""
    root = tk.Tk()
    root.withdraw()
    return root


def drain_tk_events(widget: tk.Misc, *, cycles: int = 1) -> None:
    """Drain geometry/idletask work without entering the full Tk event loop."""
    for _ in range(max(1, cycles)):
        widget.update_idletasks()


def cancel_pending_after_callbacks(widget: tk.Misc) -> None:
    """Cancel pending Tk ``after`` callbacks without deleting Python commands."""
    try:
        callback_ids = widget.tk.call("after", "info")
    except tk.TclError:
        return
    if isinstance(callback_ids, str):
        callback_ids = (callback_ids,) if callback_ids else ()
    for callback_id in tuple(callback_ids):
        try:
            widget.tk.call("after", "cancel", callback_id)
        except tk.TclError:
            pass


def destroy_tk_root(root: tk.Misc) -> None:
    """Cancel pending callbacks, drain idletasks, and destroy a Tk test root."""
    cancel_pending_after_callbacks(root)
    try:
        drain_tk_events(root)
    except tk.TclError:
        pass
    try:
        root.destroy()
    except tk.TclError:
        pass


@contextmanager
def hidden_tk_root() -> Iterator[tk.Tk]:
    """Yield a withdrawn Tk root with test-only teardown cleanup."""
    root = make_hidden_root()
    try:
        yield root
    finally:
        destroy_tk_root(root)
