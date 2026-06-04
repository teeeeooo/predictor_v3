"""Hong Kong CSPF row-per-case batch section."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from ui_tk.batch_case_table import BatchCaseTable
from ui_tk.batch_controller import BatchCalculationController
from ui_tk.layout_constants import ISO_SECTION_BLOCK_GAP, ISO_SECTION_PADX
from ui_tk.sections.hong_kong_cspf_batch_spec import (
    HONG_KONG_CSPF_BATCH_SPEC,
    HongKongCspfBatchHandler,
)


class HongKongCspfBatchSection:
    """Explicit-run batch surface for Hong Kong CSPF cases."""

    result_panel = None

    def __init__(self, parent: tk.Widget, region_label: str) -> None:
        self._frame = ttk.LabelFrame(parent, text=f"CSPF Batch ({region_label})")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(0, weight=1)
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
        action_row = ttk.Frame(self._frame)
        action_row.grid(
            row=1,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        ttk.Button(action_row, text="Run Batch", command=self.controller.run_batch).pack(
            side=tk.LEFT
        )
        ttk.Button(action_row, text="Clear Results", command=self.controller.clear_results).pack(
            side=tk.LEFT,
            padx=(6, 0),
        )
        ttk.Button(action_row, text="Add Row", command=self.table.add_row).pack(
            side=tk.LEFT,
            padx=(6, 0),
        )
        ttk.Button(action_row, text="Remove Row", command=self.table.remove_last_row).pack(
            side=tk.LEFT,
            padx=(6, 0),
        )

    def pack(self, **kwargs: object) -> None:
        self._frame.pack(**kwargs)


class HongKongCspfBatchDialog:
    """Toplevel owner for the Hong Kong CSPF batch surface."""

    def __init__(
        self,
        parent: tk.Widget,
        region_label: str,
        *,
        on_close: Callable[[], None] | None = None,
    ) -> None:
        self._on_close = on_close
        self.window = tk.Toplevel(parent)
        self.window.title(f"CSPF Batch ({region_label})")
        self.window.geometry("1120x360")
        self.window.minsize(920, 300)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.section = HongKongCspfBatchSection(self.window, region_label)
        self.section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def close(self) -> None:
        if self.window.winfo_exists():
            self.window.destroy()
        if self._on_close is not None:
            self._on_close()

    def focus(self) -> None:
        if self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
