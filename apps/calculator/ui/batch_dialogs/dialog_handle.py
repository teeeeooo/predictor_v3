"""Small state handle for calculator batch dialog lifecycle."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import Generic, Protocol, TypeVar

SnapshotT = TypeVar("SnapshotT")
DialogT = TypeVar("DialogT", bound="BatchDialogProtocol")


class BatchDialogProtocol(Protocol):
    window: tk.Misc

    def focus(self) -> None:
        ...

    def close(self) -> None:
        ...


class BatchDialogHandle(Generic[SnapshotT, DialogT]):
    """Own a single batch dialog reference and its latest close snapshot."""

    def __init__(
        self,
        *,
        snapshot: SnapshotT | None = None,
        should_store_snapshot: Callable[[SnapshotT | None], bool] | None = None,
    ) -> None:
        self.dialog: DialogT | None = None
        self.snapshot: SnapshotT | None = snapshot
        self._should_store_snapshot = should_store_snapshot or (
            lambda value: value is not None
        )

    def open_or_focus(self, factory: Callable[[], DialogT]) -> DialogT:
        if self._dialog_is_live():
            assert self.dialog is not None
            self.dialog.focus()
            return self.dialog
        self.dialog = None
        self.dialog = factory()
        return self.dialog

    def clear(self, snapshot: SnapshotT | None = None) -> None:
        if self._should_store_snapshot(snapshot):
            self.snapshot = snapshot
        self.dialog = None

    def dispose(self) -> None:
        dialog = self.dialog
        if dialog is not None:
            try:
                dialog.close()
            finally:
                self.dialog = None

    def _dialog_is_live(self) -> bool:
        dialog = self.dialog
        if dialog is None:
            return False
        try:
            return bool(dialog.window.winfo_exists())
        except tk.TclError:
            return False
