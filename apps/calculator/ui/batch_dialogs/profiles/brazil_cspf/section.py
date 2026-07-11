"""Brazil CSPF Tk batch section."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch.controller import BatchMatrixCalculationController
from apps.calculator.ui.batch.matrix_table import BatchMatrixTable
from apps.calculator.ui.batch_dialogs.profiles.brazil_cspf.row_adapter import (
    BrazilCspfBatchHandler,
)
from apps.calculator.ui.batch_dialogs.profiles.brazil_cspf.schema import (
    BRAZIL_CSPF_MATRIX_SPEC,
)
from apps.calculator.ui.layout_constants import (
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table_csv_export import export_table_to_csv
from .presentation import brazil_batch_cell_background


class BrazilCspfBatchSection:
    """Two-row matrix batch surface for Brazil CSPF compliance cases."""

    result_panel = None

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: object | None = None,
    ) -> None:
        self._frame = ttk.LabelFrame(parent, text="Brazil CSPF Compliance Batch")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(0, weight=1)
        self.status_var = tk.StringVar(master=self._frame, value="")
        self.table = BatchMatrixTable(self._frame, BRAZIL_CSPF_MATRIX_SPEC)
        self.table.default_cell_background = lambda position: (
            brazil_batch_cell_background(self.table, position)
        )
        self.table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 6),
        )
        self.table.interaction_controller = TkTableController(self.table)
        self.controller = BatchMatrixCalculationController(
            self.table,
            BrazilCspfBatchHandler(),
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
        ttk.Button(action_row, text="Add Case", command=self.table.add_case).pack(
            side=tk.LEFT
        )
        ttk.Button(
            action_row,
            text="Remove Case",
            command=self.table.remove_case,
        ).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(action_row, text="Copy All", command=self.table.copy_all).pack(
            side=tk.LEFT, padx=(6, 0)
        )
        ttk.Button(
            action_row,
            text="Export CSV",
            command=self._export_csv,
        ).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Label(action_row, textvariable=self.status_var).pack(
            side=tk.LEFT, padx=(12, 0)
        )
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

    def _export_csv(self) -> None:
        headers, rows = self.table.table_export_data()
        export_table_to_csv(self._frame, "brazil_cspf_batch.csv", headers, rows)


__all__ = ["BrazilCspfBatchSection"]
