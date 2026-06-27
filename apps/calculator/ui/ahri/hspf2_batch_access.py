"""Thin parent access and lifecycle owner for the HSPF2 batch dialog."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.ahri.hspf2_batch_session import AhriHspf2BatchSnapshot
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.batch_dialogs.profiles.ahri_hspf2_dialog import (
    AhriHspf2BatchDialog,
)
from apps.calculator.ui.layout_constants import ISO_SECTION_BLOCK_GAP, ISO_SECTION_PADX


class AhriHspf2BatchAccess:
    """Keep batch dialog state out of the already-large main section."""

    def __init__(self, parent: tk.Widget, *, row: int) -> None:
        self._parent = parent
        self._handle: BatchDialogHandle[
            AhriHspf2BatchSnapshot, AhriHspf2BatchDialog
        ] = BatchDialogHandle()
        self.button = ttk.Button(parent, text="HSPF2 Batch", command=self.open)
        self.button.grid(
            row=row,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )

    def open(self) -> None:
        self._handle.open_or_focus(
            lambda: AhriHspf2BatchDialog(
                self._parent.winfo_toplevel(),
                initial_snapshot=self._handle.snapshot,
                on_close=self._clear,
            )
        )

    def _clear(self, snapshot: AhriHspf2BatchSnapshot) -> None:
        self._handle.clear(snapshot)

    def dispose(self) -> None:
        self._handle.dispose()

    @property
    def dialog(self) -> AhriHspf2BatchDialog | None:
        return self._handle.dialog

    @dialog.setter
    def dialog(self, dialog: AhriHspf2BatchDialog | None) -> None:
        self._handle.dialog = dialog

    @property
    def snapshot(self) -> AhriHspf2BatchSnapshot | None:
        return self._handle.snapshot

    @snapshot.setter
    def snapshot(self, snapshot: AhriHspf2BatchSnapshot | None) -> None:
        self._handle.snapshot = snapshot
