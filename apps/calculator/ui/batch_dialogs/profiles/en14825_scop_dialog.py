"""Shell adapter and dialog wrapper for the EN14825 SCOP batch profile."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk

from apps.calculator.ui.batch_dialogs.profiles.en14825_scop import (
    En14825ScopBatchSection,
)
from apps.calculator.ui.batch_dialogs.shell import BatchDialogShell
from apps.calculator.ui.en14825.scop_batch_session import En14825ScopBatchSnapshot

__all__ = ["En14825ScopBatchDialog"]


class En14825ScopBatchAdapter:
    """Composition adapter for the generic batch dialog shell."""

    def __init__(self, initial_snapshot: En14825ScopBatchSnapshot | None = None) -> None:
        self.initial_snapshot = initial_snapshot
        self.section: En14825ScopBatchSection | None = None
        self.last_snapshot = initial_snapshot

    @property
    def title(self) -> str:
        return "EN14825 SCOP Batch"

    @property
    def min_size(self) -> tuple[int, int]:
        return (1100, 410)

    def build_content(self, parent: tk.Widget) -> tk.Widget:
        self.section = En14825ScopBatchSection(
            parent,
            initial_snapshot=self.initial_snapshot,
        )
        return self.section._frame

    def dispose(self) -> None:
        if self.section is not None:
            self.section.dispose()

    def snapshot(self) -> list[dict[str, str]]:
        if self.section is None:
            return []
        self.last_snapshot = self.section.snapshot()
        return [dict(case) for case in self.last_snapshot.cases]


class En14825ScopBatchDialog:
    """Toplevel owner for the SCOP batch profile."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: En14825ScopBatchSnapshot | None = None,
        on_close: Callable[[En14825ScopBatchSnapshot], None] | None = None,
    ) -> None:
        self.adapter = En14825ScopBatchAdapter(initial_snapshot)

        def handle_close(_cases: list[dict[str, str]]) -> None:
            if on_close is not None and self.adapter.last_snapshot is not None:
                on_close(self.adapter.last_snapshot)

        self._shell = BatchDialogShell(parent, self.adapter, on_close=handle_close)
        self.section = self.adapter.section
        self.window = self._shell.window

    def close(self) -> None:
        self._shell.close()

    def snapshot(self) -> En14825ScopBatchSnapshot:
        if self.section is None:
            raise RuntimeError("SCOP batch dialog content is not available")
        return self.section.snapshot()

    def focus(self) -> None:
        self._shell.focus()
