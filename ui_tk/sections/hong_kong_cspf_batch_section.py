"""Hong Kong CSPF row-per-case batch section."""

from __future__ import annotations

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
        self.table = BatchCaseTable(self._frame, HONG_KONG_CSPF_BATCH_SPEC)
        self.table.grid(
            row=0,
            column=0,
            sticky="ew",
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

    def pack(self, **kwargs: object) -> None:
        self._frame.pack(**kwargs)
