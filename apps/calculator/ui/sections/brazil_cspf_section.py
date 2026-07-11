"""Brazil CSPF single calculation section for Tkinter."""

from __future__ import annotations

from collections.abc import Callable

import tkinter as tk
from tkinter import ttk

from apps.calculator.application.brazil_cspf import BrazilCspfUseCase
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.batch_dialogs.profiles.brazil_cspf import BrazilCspfBatchDialog
from apps.calculator.ui.layout_constants import (
    BATCH_INPUT_BUTTON_TEXT,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from apps.calculator.ui.sections.detail_visibility import DetailPanelVisibility
from apps.calculator.ui.sections.brazil_cspf_result_table import BrazilCspfResultTable
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table_csv_export import export_table_to_csv


class BrazilCspfSection:
    """Brazil 3-point input with automatic compliance comparison."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_trace_visibility_changed: Callable[[], None] | None = None,
    ) -> None:
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self._detail_sources: dict[str, tuple[dict[str, object], ...]] = {}
        self._detail_summaries: dict[str, tuple[tuple[str, str], ...]] = {}
        self._detail_status: str | None = "입력 대기"
        self._usecase = BrazilCspfUseCase()
        self._batch_handle: BatchDialogHandle[
            list[dict[str, str]], BrazilCspfBatchDialog
        ] = BatchDialogHandle()
        self._frame = ttk.LabelFrame(parent, text="Brazil CSPF 입력")
        self._frame.columnconfigure(0, weight=1)
        ttk.Label(self._frame, text="시험 입력").grid(
            row=0,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 4),
        )
        self.input_table = MetricInputTable(
            self._frame,
            columns=(
                ("full", "35 Full"),
                ("half", "35 Half"),
                ("half_29", "29 Half"),
            ),
            rows=(("capacity", "능력 [W]"), ("power", "전력 [W]")),
            editable_cells={
                ("capacity", "full"): "full_capacity",
                ("power", "full"): "full_power",
                ("capacity", "half"): "half_capacity",
                ("power", "half"): "half_power",
                ("capacity", "half_29"): "half_29_capacity",
                ("power", "half_29"): "half_29_power",
            },
        )
        self.input_table.grid(
            row=1,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.result_table = BrazilCspfResultTable(self._frame)
        self.result_panel = self.result_table
        self.result_table.grid(
            row=2,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.action_row = ttk.Frame(self._frame)
        self.action_row.grid(
            row=3,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.batch_button = ttk.Button(
            self.action_row,
            text=BATCH_INPUT_BUTTON_TEXT,
            command=self._open_batch_dialog,
        )
        self.batch_button.surface_role = "brazil_cspf_batch_open"
        self.batch_button.pack(side=tk.LEFT)
        self.detail_toggle = ttk.Button(
            self.action_row,
            text="상세 보기 ↓",
            command=self._toggle_detail,
        )
        self.detail_toggle.surface_role = "brazil_cspf_detail_toggle"
        self.detail_toggle.pack(side=tk.LEFT, padx=(6, 0))
        self.export_button = ttk.Button(
            self.action_row,
            text="Export CSV",
            command=self._export_csv,
        )
        self.export_button.surface_role = "brazil_cspf_export"
        self.export_button.pack(side=tk.LEFT, padx=(6, 0))

        self.detail_panel = BinDetailPanel(
            self._frame,
            source_labels=("3-point", "2-point"),
            default_source="3-point",
            csv_filename="brazil_cspf_bin_detail.csv",
        )
        self._detail_visibility = DetailPanelVisibility(
            panel=self.detail_panel,
            button=self.detail_toggle,
            grid_options={
                "row": 4,
                "column": 0,
                "sticky": "ew",
                "padx": 0,
                "pady": (0, ISO_SECTION_BLOCK_GAP),
            },
            before_show=self._update_detail_panel,
            on_change=self._on_detail_visibility_changed,
        )

        self.input_controller = TkTableController(self.input_table)
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.input_table.set_values_changed_callback(self._auto_calc.schedule)
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._auto_calc.flush_now()

    def pack(self, **kwargs: object) -> None:
        self._frame.pack(**kwargs)

    def cancel_pending(self) -> None:
        self._auto_calc.cancel()

    def recalculate_now(self) -> None:
        result = self._usecase.calculate(self.input_table.get_text_values())
        if not result.is_ok:
            self._clear_detail(result.detail_status or result.status_text)
            self.result_table.set_status(result.status_text)
            return
        self._detail_sources = dict(result.detail_sources or {})
        self._detail_summaries = dict(result.detail_summaries or {})
        self._detail_status = result.detail_status
        self._update_detail_panel()
        self.result_table.set_result(
            result.rows,
            result.rules,
            final_status=result.final_status or "NG",
            status=result.status_text,
        )

    def _open_batch_dialog(self) -> None:
        self._batch_handle.open_or_focus(
            lambda: BrazilCspfBatchDialog(
                self._frame.winfo_toplevel(),
                initial_snapshot=self._batch_handle.snapshot,
                on_close=self._clear_batch_dialog,
            )
        )

    def _clear_batch_dialog(self, snapshot: list[dict[str, str]] | None = None) -> None:
        self._batch_handle.clear(snapshot)

    def _export_csv(self) -> None:
        headers, rows = self.result_table.table_export_data()
        export_table_to_csv(self._frame, "brazil_cspf_result.csv", headers, rows)

    def _toggle_detail(self) -> None:
        self._detail_visibility.toggle()

    def _update_detail_panel(self) -> None:
        if self._detail_status is not None:
            self.detail_panel.set_status(self._detail_status)
            return
        sources = {
            label: BinDetailSource(
                rows=tuple(rows),
                summary=self._detail_summaries.get(label, ()),
            )
            for label, rows in self._detail_sources.items()
        }
        self.detail_panel.set_sources(
            sources,
            source_order=("3-point", "2-point"),
            panel_status="상세 데이터 없음",
        )

    def _clear_detail(self, status: str) -> None:
        self._detail_sources = {}
        self._detail_summaries = {}
        self._detail_status = status
        self._update_detail_panel()

    @property
    def _batch_dialog(self) -> BrazilCspfBatchDialog | None:
        return self._batch_handle.dialog

    @_batch_dialog.setter
    def _batch_dialog(self, dialog: BrazilCspfBatchDialog | None) -> None:
        self._batch_handle.dialog = dialog

    @property
    def _batch_snapshot(self) -> list[dict[str, str]] | None:
        return self._batch_handle.snapshot

    @_batch_snapshot.setter
    def _batch_snapshot(self, snapshot: list[dict[str, str]] | None) -> None:
        self._batch_handle.snapshot = snapshot

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
            self._batch_handle.dispose()
