"""Dialog/access lifecycle for Appendix M batch calculation."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.ahri_m.batch_sections import (
    AhriMBatchSnapshot,
    AhriMHspfBatchSection,
    AhriMSeerBatchSection,
)
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.batch_dialogs.shell import BatchDialogShell
from apps.calculator.ui.layout_constants import (
    BATCH_DIALOG_SAFETY_MIN_SIZE,
    BATCH_INPUT_BUTTON_TEXT,
)


class _BatchProfileAdapter:
    def __init__(self, metric: str, initial_snapshot: AhriMBatchSnapshot | None = None) -> None:
        self.metric = metric
        self.initial_snapshot = initial_snapshot
        self.section: AhriMSeerBatchSection | AhriMHspfBatchSection | None = None
        self.last_snapshot = initial_snapshot or AhriMBatchSnapshot({}, ())

    @property
    def title(self) -> str:
        return f"AHRI 210/240 M {self.metric} Batch"

    @property
    def min_size(self) -> tuple[int, int]:
        return BATCH_DIALOG_SAFETY_MIN_SIZE
    def build_content(self, parent: tk.Widget) -> tk.Widget:
        section_type = AhriMSeerBatchSection if self.metric == "SEER" else AhriMHspfBatchSection
        self.section = section_type(parent, initial_snapshot=self.initial_snapshot)
        return self.section._frame

    def dispose(self) -> None:
        if self.section is not None:
            self.section.dispose()

    def snapshot(self) -> list[dict[str, str]]:
        if self.section is None:
            return []
        self.last_snapshot = self.section.snapshot()
        return [dict(case) for case in self.last_snapshot.cases]


class AhriMBatchDialog:
    def __init__(self, parent: tk.Widget, *, metric: str, initial_snapshot: AhriMBatchSnapshot | None = None, on_close: Callable[[AhriMBatchSnapshot], None] | None = None) -> None:
        self.adapter = _BatchProfileAdapter(metric, initial_snapshot)
        def handle_close(_cases: list[dict[str, str]]) -> None:
            if on_close is not None:
                on_close(self.adapter.last_snapshot)
        self._shell = BatchDialogShell(parent, self.adapter, on_close=handle_close)
        self.section = self.adapter.section
        self.window = self._shell.window

    def close(self) -> None:
        self._shell.close()

    def focus(self) -> None:
        self._shell.focus()
class AhriMBatchAccess:
    def __init__(self, parent: tk.Widget, *, metric: str, shell_parent: tk.Widget | None = None) -> None:
        self.metric = metric
        self._shell_parent = shell_parent or parent
        self._handle: BatchDialogHandle[AhriMBatchSnapshot, AhriMBatchDialog] = BatchDialogHandle()
        self.button = ttk.Button(parent, text=BATCH_INPUT_BUTTON_TEXT, command=self.open)
        self.button.pack(side=tk.LEFT)

    def open(self) -> None:
        self._handle.open_or_focus(
            lambda: AhriMBatchDialog(
                self._shell_parent.winfo_toplevel(),
                metric=self.metric,
                initial_snapshot=self._handle.snapshot,
                on_close=self._handle.clear,
            )
        )

    def dispose(self) -> None:
        self._handle.dispose()

    @property
    def dialog(self) -> AhriMBatchDialog | None:
        return self._handle.dialog
