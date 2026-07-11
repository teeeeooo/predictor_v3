"""KOREA KS C 9306 HSPF single-calculation section."""

from __future__ import annotations

from collections.abc import Callable

import tkinter as tk
from tkinter import ttk

from apps.calculator.application.korea import KoreaHspfUseCase
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.batch_dialogs.profiles.korea_hspf import KoreaHspfBatchDialog
from apps.calculator.ui.layout_constants import (
    BATCH_INPUT_BUTTON_TEXT,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.result_models import ResultSummary, result_status
from apps.calculator.ui.result_panel import ResultPanel
from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from apps.calculator.ui.sections.bin_detail_schema import HEATING_HSPF_BIN_DETAIL_SCHEMA
from apps.calculator.ui.sections.detail_visibility import DetailPanelVisibility
from apps.calculator.ui.sections.korea_midpoint_guide_table import (
    KoreaMidpointGuideTable,
)
from apps.calculator.ui.table.controller import TkTableController


class KoreaHspfSection:
    """KOREA HSPF table input with separated midpoint guide display."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_trace_visibility_changed: Callable[[], None] | None = None,
    ) -> None:
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self._trace_rows: list[dict] = []
        self._detail_summary: tuple[tuple[str, str], ...] = ()
        self._trace_status: str | None = "상세 데이터 없음"
        self._usecase = KoreaHspfUseCase()
        self._batch_handle: BatchDialogHandle[
            list[dict[str, str]], KoreaHspfBatchDialog
        ] = BatchDialogHandle()
        self._frame = ttk.LabelFrame(parent, text="KS C 9306 HSPF 입력")
        self._frame.columnconfigure(0, weight=1)

        self.rated_table = MetricInputTable(
            self._frame,
            columns=(("capacity", "능력 [W]"),),
            rows=(("rated", "정격 냉방능력"),),
            editable_cells={("rated", "capacity"): "rated_cooling_capacity"},
            visual_style="shared",
        )
        self.rated_table.grid(
            row=0,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 6),
        )
        ttk.Label(self._frame, text="시험 입력").grid(
            row=1, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, 4)
        )
        self.input_table = MetricInputTable(
            self._frame,
            columns=(
                ("full", "7 Full"),
                ("half", "7 Half"),
                ("min", "7 Min"),
                ("defrost", "2 Defrost"),
                ("max", "-7 Max"),
            ),
            rows=(("capacity", "능력 [W]"), ("power", "전력 [W]")),
            editable_cells={
                ("capacity", "full"): "full_capacity",
                ("power", "full"): "full_power",
                ("capacity", "half"): "half_capacity",
                ("power", "half"): "half_power",
                ("capacity", "min"): "min_capacity",
                ("power", "min"): "min_power",
                ("capacity", "defrost"): "defrost_capacity",
                ("power", "defrost"): "defrost_power",
                ("capacity", "max"): "max_capacity",
                ("power", "max"): "max_power",
            },
            visual_style="shared",
        )
        self.input_table.grid(
            row=2,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self._guide = KoreaMidpointGuideTable(self._frame)
        self.guide_table = self._guide.table
        self._guide.grid(
            row=3,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.result_panel = ResultPanel(self._frame, title="HSPF 결과")
        self.result_panel.grid(
            row=4,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.action_row = ttk.Frame(self._frame)
        self.action_row.grid(
            row=5,
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
        self.batch_button.surface_role = "korea_hspf_batch_open"
        self.batch_button.pack(side=tk.LEFT)
        self.detail_toggle = ttk.Button(
            self.action_row,
            text="상세 보기 ↓",
            command=self._toggle_detail,
        )
        self.detail_toggle.surface_role = "korea_hspf_detail_toggle"
        self.detail_toggle.pack(side=tk.LEFT, padx=(6, 0))
        self.detail_panel = BinDetailPanel(
            self._frame,
            source_labels=("KOREA HSPF",),
            default_source="KOREA HSPF",
            csv_filename="korea_hspf_bin_detail.csv",
            show_source_selector=False,
            schema=HEATING_HSPF_BIN_DETAIL_SCHEMA,
        )
        self._detail_visibility = DetailPanelVisibility(
            panel=self.detail_panel,
            button=self.detail_toggle,
            grid_options={
                "row": 6,
                "column": 0,
                "sticky": "ew",
                "padx": 0,
                "pady": (0, ISO_SECTION_BLOCK_GAP),
            },
            before_show=self._update_detail_panel,
            on_change=lambda: self._on_detail_visibility_changed()
            if self._on_detail_visibility_changed is not None
            else None,
        )
        self.trace_table = self.detail_panel.table
        self.rated_controller = TkTableController(self.rated_table)
        self.input_controller = TkTableController(self.input_table)
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.rated_table.set_values_changed_callback(self._auto_calc.schedule)
        self.input_table.set_values_changed_callback(self._auto_calc.schedule)
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._auto_calc.flush_now()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    @property
    def _batch_dialog(self) -> KoreaHspfBatchDialog | None:
        return self._batch_handle.dialog

    @_batch_dialog.setter
    def _batch_dialog(self, dialog: KoreaHspfBatchDialog | None) -> None:
        self._batch_handle.dialog = dialog

    @property
    def _batch_snapshot(self) -> list[dict[str, str]] | None:
        return self._batch_handle.snapshot

    @_batch_snapshot.setter
    def _batch_snapshot(self, snapshot: list[dict[str, str]] | None) -> None:
        self._batch_handle.snapshot = snapshot

    def _open_batch_dialog(self) -> None:
        self._batch_handle.open_or_focus(
            lambda: KoreaHspfBatchDialog(
                self._frame.winfo_toplevel(),
                initial_snapshot=self._batch_handle.snapshot,
                on_close=self._clear_batch_dialog,
            )
        )

    def _clear_batch_dialog(self, snapshot: list[dict[str, str]] | None = None) -> None:
        self._batch_handle.clear(snapshot)

    def recalculate_now(self) -> None:
        raw_values = {
            **self.input_table.get_text_values(),
            **self.rated_table.get_text_values(),
        }
        result = self._usecase.calculate(raw_values)
        self.input_table.clear_invalid_fields()
        self.rated_table.clear_invalid_fields()
        if result.invalid_fields:
            input_invalid = {
                key: value
                for key, value in result.invalid_fields.items()
                if key != "rated_cooling_capacity"
            }
            if input_invalid:
                self.input_table.set_invalid_fields(input_invalid)
            if "rated_cooling_capacity" in result.invalid_fields:
                self.rated_table.set_invalid_fields(
                    {
                        "rated_cooling_capacity": result.invalid_fields[
                            "rated_cooling_capacity"
                        ]
                    }
                )
        self._guide.set_values(result.guide_fields)
        if result.guide_status and not result.guide_fields:
            self._guide.set_status(result.guide_status)
        if not result.is_ok:
            self._clear_trace(result.detail_status or result.status_text)
            self.result_panel.set_summaries(
                (result_status(result.summary_title, result.status_text),)
            )
            return
        self._trace_rows = list(result.detail_rows)
        self._detail_summary = result.detail_summary
        self._trace_status = None
        self._update_detail_panel()
        self.result_panel.set_summaries(
            (
                ResultSummary(
                    title=result.summary_title,
                    fields=result.summary_fields,
                    status=result.status_text,
                ),
            )
        )

    def _toggle_detail(self) -> None:
        self._detail_visibility.toggle()

    def _update_detail_panel(self) -> None:
        if self._trace_status is not None:
            self.detail_panel.set_status(self._trace_status)
            return
        self.detail_panel.set_sources(
            {
                "KOREA HSPF": BinDetailSource(
                    rows=tuple(self._trace_rows),
                    summary=self._detail_summary,
                )
            },
            source_order=("KOREA HSPF",),
            panel_status="상세 데이터 없음",
        )

    def _clear_trace(self, status: str) -> None:
        self._trace_rows = []
        self._detail_summary = ()
        self._trace_status = status
        self._update_detail_panel()

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
            self._batch_handle.dispose()
