"""Shell adapter and dialog wrapper for the AHRI HSPF2 batch profile."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk

from apps.calculator.ui.ahri.hspf2_batch_session import AhriHspf2BatchSnapshot
from apps.calculator.ui.batch_dialogs.profiles.ahri_hspf2 import AhriHspf2BatchSection
from apps.calculator.ui.batch_dialogs.shell import BatchDialogShell


class AhriHspf2BatchAdapter:
    def __init__(self, initial_snapshot: AhriHspf2BatchSnapshot | None = None) -> None:
        self.initial_snapshot = initial_snapshot
        self.section: AhriHspf2BatchSection | None = None
        self.last_snapshot = initial_snapshot

    @property
    def title(self) -> str:
        return "AHRI 210/240 HSPF2 Batch"

    @property
    def min_size(self) -> tuple[int, int]:
        return (1180, 420)

    def build_content(self, parent: tk.Widget) -> tk.Widget:
        self.section = AhriHspf2BatchSection(parent, initial_snapshot=self.initial_snapshot)
        return self.section._frame

    def dispose(self) -> None:
        if self.section is not None:
            self.section.dispose()

    def snapshot(self) -> list[dict[str, str]]:
        if self.section is None:
            return []
        self.last_snapshot = self.section.snapshot()
        return [dict(case) for case in self.last_snapshot.cases]


class AhriHspf2BatchDialog:
    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: AhriHspf2BatchSnapshot | None = None,
        on_close: Callable[[AhriHspf2BatchSnapshot], None] | None = None,
    ) -> None:
        self.adapter = AhriHspf2BatchAdapter(initial_snapshot)

        def handle_close(_cases: list[dict[str, str]]) -> None:
            if on_close is not None and self.adapter.last_snapshot is not None:
                on_close(self.adapter.last_snapshot)

        self._shell = BatchDialogShell(parent, self.adapter, on_close=handle_close)
        self.section = self.adapter.section
        self.window = self._shell.window

    def close(self) -> None:
        self._shell.close()

    def snapshot(self) -> AhriHspf2BatchSnapshot:
        if self.section is None:
            raise RuntimeError("HSPF2 batch dialog content is not available")
        return self.section.snapshot()

    def focus(self) -> None:
        self._shell.focus()
