"""KOREA KS C 9306 CSPF single-calculation section."""

from __future__ import annotations

from collections.abc import Callable

import tkinter as tk
from tkinter import ttk

from apps.calculator.application.korea import KoreaCspfUseCase
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.batch_dialogs.profiles.korea_cspf import KoreaCspfBatchDialog
from apps.calculator.ui.layout_constants import (
    BATCH_INPUT_BUTTON_TEXT,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.result_models import ResultSummary, result_status
from apps.calculator.ui.result_panel import ResultPanel
from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from apps.calculator.ui.sections.detail_visibility import DetailPanelVisibility
from apps.calculator.ui.table.controller import TkTableController


_GUIDE_ROWS = (
    ("current_tc", "현재 tc"),
    ("recommended_tc", "권장 tc"),
    ("recommended_mid_capacity", "권장 Mid capacity"),
)
_GUIDE_ADDRESSES = tuple((row_key, "value") for row_key, _label in _GUIDE_ROWS)


class KoreaCspfSection:
    """KOREA CSPF table input with separated midpoint guide display."""

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
        self._usecase = KoreaCspfUseCase()
        self._batch_handle: BatchDialogHandle[
            list[dict[str, str]], KoreaCspfBatchDialog
        ] = BatchDialogHandle()
        self._frame = ttk.LabelFrame(parent, text="KS C 9306 CSPF 입력")
        self._frame.columnconfigure(0, weight=1)

        self.rated_table = MetricInputTable(
            self._frame,
            columns=(("capacity", "능력 [W]"),),
            rows=(("rated", "정격 표기치"),),
            editable_cells={("rated", "capacity"): "declared_capacity"},
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
                ("full", "35 Full"),
                ("half", "35 Half"),
                ("min", "29 Min"),
            ),
            rows=(("capacity", "능력 [W]"), ("power", "전력 [W]")),
            editable_cells={
                ("capacity", "full"): "full_capacity",
                ("power", "full"): "full_power",
                ("capacity", "half"): "half_capacity",
                ("power", "half"): "half_power",
                ("capacity", "min"): "min_capacity",
                ("power", "min"): "min_power",
            },
        )
        self.input_table.grid(
            row=2,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.guide_table = MetricInputTable(
            self._frame,
            columns=(("value", "값"),),
            rows=_GUIDE_ROWS,
            editable_cells={address: address[0] for address in _GUIDE_ADDRESSES},
            row_header_chars=20,
            data_column_chars=14,
        )
        self.guide_table.set_readonly_addresses(_GUIDE_ADDRESSES)
        self.guide_table.grid(
            row=3,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.result_panel = ResultPanel(self._frame, title="CSPF 결과")
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
        self.batch_button.surface_role = "korea_cspf_batch_open"
        self.batch_button.pack(side=tk.LEFT)
        self.detail_toggle = ttk.Button(
            self.action_row,
            text="상세 보기 ↓",
            command=self._toggle_detail,
        )
        self.detail_toggle.surface_role = "korea_cspf_detail_toggle"
        self.detail_toggle.pack(side=tk.LEFT, padx=(6, 0))
        self.detail_panel = BinDetailPanel(
            self._frame,
            source_labels=("KOREA CSPF",),
            default_source="KOREA CSPF",
            csv_filename="korea_cspf_bin_detail.csv",
            show_source_selector=False,
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
        self.guide_controller = TkTableController(self.guide_table)
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.rated_table.set_values_changed_callback(self._auto_calc.schedule)
        self.input_table.set_values_changed_callback(self._auto_calc.schedule)
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._auto_calc.flush_now()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    @property
    def _batch_dialog(self) -> KoreaCspfBatchDialog | None:
        return self._batch_handle.dialog

    @_batch_dialog.setter
    def _batch_dialog(self, dialog: KoreaCspfBatchDialog | None) -> None:
        self._batch_handle.dialog = dialog

    @property
    def _batch_snapshot(self) -> list[dict[str, str]] | None:
        return self._batch_handle.snapshot

    @_batch_snapshot.setter
    def _batch_snapshot(self, snapshot: list[dict[str, str]] | None) -> None:
        self._batch_handle.snapshot = snapshot

    def _open_batch_dialog(self) -> None:
        self._batch_handle.open_or_focus(
            lambda: KoreaCspfBatchDialog(
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
                if key != "declared_capacity"
            }
            if input_invalid:
                self.input_table.set_invalid_fields(input_invalid)
            if "declared_capacity" in result.invalid_fields:
                self.rated_table.set_invalid_fields(
                    {"declared_capacity": result.invalid_fields["declared_capacity"]}
                )
        self._set_guide_values(result.guide_fields)
        if result.guide_status and not result.guide_fields:
            self._set_guide_status(result.guide_status)
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

    def _set_guide_values(self, fields: tuple[tuple[str, str], ...]) -> None:
        values = {key: value for key, value in fields}
        self.guide_table.set_values_batch(
            {row_key: values.get(row_key, "-") for row_key, _label in _GUIDE_ROWS}
        )
        self.guide_table.set_readonly_addresses(
            _GUIDE_ADDRESSES,
            display_values={(row_key, "value"): values.get(row_key, "-") for row_key, _label in _GUIDE_ROWS},
        )

    def _set_guide_status(self, status: str) -> None:
        self.guide_table.set_values_batch(
            {
                "current_tc": status,
                "recommended_tc": "-",
                "recommended_mid_capacity": "-",
            }
        )
        self.guide_table.set_readonly_addresses(
            _GUIDE_ADDRESSES,
            display_values={
                ("current_tc", "value"): status,
                ("recommended_tc", "value"): "-",
                ("recommended_mid_capacity", "value"): "-",
            },
        )

    def _toggle_detail(self) -> None:
        self._detail_visibility.toggle()

    def _update_detail_panel(self) -> None:
        if self._trace_status is not None:
            self.detail_panel.set_status(self._trace_status)
            return
        self.detail_panel.set_sources(
            {
                "KOREA CSPF": BinDetailSource(
                    rows=tuple(self._trace_rows),
                    summary=self._detail_summary,
                )
            },
            source_order=("KOREA CSPF",),
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
