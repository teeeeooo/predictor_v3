"""Brazil CSPF batch dialog composition and lifecycle adapter."""

from __future__ import annotations

from collections.abc import Callable

import tkinter as tk

from apps.calculator.ui.batch_dialogs.profiles.brazil_cspf.section import (
    BrazilCspfBatchSection,
)
from apps.calculator.ui.batch_dialogs.shell import BatchDialogShell
from apps.calculator.ui.layout_constants import BATCH_DIALOG_SAFETY_MIN_SIZE


class BrazilCspfBatchAdapter:
    """Composition adapter implementing the common batch dialog protocol."""

    def __init__(self, initial_snapshot: object | None = None) -> None:
        self.initial_snapshot = initial_snapshot
        self.section: BrazilCspfBatchSection | None = None

    @property
    def title(self) -> str:
        return "Brazil CSPF Compliance Batch"

    @property
    def min_size(self) -> tuple[int, int]:
        return BATCH_DIALOG_SAFETY_MIN_SIZE

    def build_content(self, parent: tk.Widget) -> tk.Widget:
        self.section = BrazilCspfBatchSection(
            parent,
            initial_snapshot=self.initial_snapshot,
        )
        return self.section._frame

    def dispose(self) -> None:
        if self.section is not None:
            self.section.dispose()

    def snapshot(self) -> list[dict[str, str]]:
        if self.section is not None:
            raw_snapshot = self.section.table.snapshot()
            if isinstance(raw_snapshot, (tuple, list)):
                return [dict(row) for row in raw_snapshot if isinstance(row, dict)]
        return []


class BrazilCspfBatchDialog:
    """Toplevel wrapper using the shared hidden-first batch shell."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: object | None = None,
        on_close: Callable[[list[dict[str, str]]], None] | None = None,
    ) -> None:
        self.adapter = BrazilCspfBatchAdapter(initial_snapshot=initial_snapshot)
        self._shell = BatchDialogShell(parent, self.adapter, on_close=on_close)
        self.section = self.adapter.section
        self.window = self._shell.window

    def close(self) -> None:
        self._shell.close()

    def snapshot(self) -> list[dict[str, str]]:
        return self._shell.snapshot()

    def focus(self) -> None:
        self._shell.focus()


__all__ = ["BrazilCspfBatchAdapter", "BrazilCspfBatchDialog"]
