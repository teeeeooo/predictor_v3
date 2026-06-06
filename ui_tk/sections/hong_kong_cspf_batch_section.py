"""Hong Kong CSPF row-per-case batch section."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
import tkinter as tk
from tkinter import ttk

from ui_tk.auto_calc import DebouncedAutoCalc
from ui_tk.batch_case_table import BatchCaseTable
from ui_tk.batch_controller import BatchCalculationController
from ui_tk.layout_constants import ISO_SECTION_BLOCK_GAP, ISO_SECTION_PADX
from ui_tk.sections.hong_kong_cspf_batch_spec import (
    HONG_KONG_CSPF_BATCH_SPEC,
    HongKongCspfBatchHandler,
)
from ui_tk.window_geometry import parent_centered_content_geometry


_BATCH_DIALOG_MIN_SIZE = (920, 320)


class HongKongCspfBatchSection:
    """Auto-calculated batch surface for Hong Kong CSPF cases."""

    result_panel = None

    def __init__(
        self,
        parent: tk.Widget,
        region_label: str,
        *,
        initial_snapshot: object | None = None,
    ) -> None:
        self._frame = ttk.LabelFrame(parent, text=f"CSPF Batch ({region_label})")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(0, weight=1)
        self.status_var = tk.StringVar(master=self._frame, value="")
        self.table = BatchCaseTable(self._frame, HONG_KONG_CSPF_BATCH_SPEC)
        self.table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 6),
        )
        self.controller = BatchCalculationController(
            self.table,
            HongKongCspfBatchHandler(region_label),
        )
        self._auto_calc = DebouncedAutoCalc(
            self._frame,
            self._recalculate_now,
            delay_ms=150,
        )
        self.table.set_values_changed_callback(self._auto_calc.schedule)
        if initial_snapshot is not None:
            self.table.restore_snapshot(initial_snapshot)
        action_row = ttk.Frame(self._frame)
        action_row.grid(
            row=1,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        ttk.Button(action_row, text="Add Row", command=self.table.add_row).pack(side=tk.LEFT)
        ttk.Button(action_row, text="Remove Row", command=self.table.remove_last_row).pack(
            side=tk.LEFT,
            padx=(6, 0),
        )
        ttk.Label(action_row, textvariable=self.status_var).pack(side=tk.LEFT, padx=(12, 0))
        self._auto_calc.flush_now()

    def pack(self, **kwargs: object) -> None:
        self._frame.pack(**kwargs)

    def dispose(self) -> None:
        self._auto_calc.dispose()

    def _recalculate_now(self) -> None:
        summary = self.controller.recalculate()
        self.status_var.set(
            f"{summary.valid_rows} valid / {summary.blank_rows} blank"
            + (f" / {summary.error_rows} invalid" if summary.error_rows else "")
        )


class HongKongCspfBatchDialog:
    """Toplevel owner for the Hong Kong CSPF batch surface."""

    def __init__(
        self,
        parent: tk.Widget,
        region_label: str,
        *,
        initial_snapshot: object | None = None,
        on_close: Callable[[list[dict[str, str]]], None] | None = None,
    ) -> None:
        self._on_close = on_close
        self.window = tk.Toplevel(parent)
        self.window.withdraw()
        self.window.title(f"CSPF Batch ({region_label})")
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.section = HongKongCspfBatchSection(
            self.window,
            region_label,
            initial_snapshot=initial_snapshot,
        )
        self.section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._apply_initial_geometry(parent)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.deiconify()
        self.window.lift()

    def _apply_initial_geometry(self, parent: tk.Widget) -> None:
        parent_toplevel = parent.winfo_toplevel()
        parent_toplevel.update_idletasks()
        self.window.update_idletasks()
        self.window.minsize(*_BATCH_DIALOG_MIN_SIZE)
        geometry = parent_centered_content_geometry(
            parent_toplevel.geometry(),
            (self.window.winfo_reqwidth(), self.window.winfo_reqheight()),
            self.window.winfo_screenwidth(),
            self.window.winfo_screenheight(),
            _BATCH_DIALOG_MIN_SIZE,
        )
        self.window.geometry(geometry)

    def close(self) -> None:
        snapshot = self.snapshot()
        self.section.dispose()
        if self.window.winfo_exists():
            self.window.destroy()
        if self._on_close is not None:
            self._on_close(snapshot)

    def snapshot(self) -> list[dict[str, str]]:
        raw_snapshot: Any = self.section.table.snapshot()
        if not isinstance(raw_snapshot, list):
            return []
        return [dict(row) for row in raw_snapshot if isinstance(row, dict)]

    def focus(self) -> None:
        if self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
