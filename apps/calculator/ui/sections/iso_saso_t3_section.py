"""SASO T3 calculation section for Tkinter."""

from __future__ import annotations

from collections.abc import Callable

import tkinter as tk
from tkinter import ttk

from apps.calculator.application.saso_t3 import SasoT3UseCase
from apps.calculator.application.saso_t3.usecase import (
    OPTIONAL_TRACE_LABEL,
    REQUIRED_TRACE_LABEL,
)
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table.visual_policy import SemanticTone
from apps.calculator.ui.layout_constants import (
    BATCH_INPUT_BUTTON_TEXT,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from apps.calculator.ui.sections.detail_visibility import DetailPanelVisibility
from apps.calculator.ui.sections.iso_saso_t3_result_table import IsoSasoT3ResultTable
from apps.calculator.ui.result_actions import add_result_actions
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.batch_dialogs.profiles.saso_t3 import SasoT3BatchDialog

_POINTS: tuple[tuple[str, str, str], ...] = (
    ("46_full", "full_46", "46 Full"),
    ("35_full", "full_35", "35 Full"),
    ("35_half", "half_35", "35 Half"),
    ("35_min", "min_35", "35 Min"),
)

class IsoSasoT3Section:
    """SASO T3 input, optional 35 Min toggle, and scenario comparison."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_trace_visibility_changed: Callable[[], None] | None = None,
    ) -> None:
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self._trace_results: dict[str, list[dict]] = {}
        self._detail_summaries: dict[str, tuple[tuple[str, str], ...]] = {}
        self._detail_statuses: dict[str, str] = {}
        self._trace_status: str | None = "상세 데이터 없음"
        self._usecase = SasoT3UseCase()
        self._batch_handle: BatchDialogHandle[
            list[dict[str, str]], SasoT3BatchDialog
        ] = BatchDialogHandle()
        self._frame = ttk.LabelFrame(parent, text="SASO T3 입력")
        self._frame.columnconfigure(0, weight=1)

        ttk.Label(self._frame, text="시험 입력").grid(
            row=0, column=0, sticky="w", padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 4),
        )
        self.input_table = MetricInputTable(
            self._frame,
            columns=tuple((column_key, label) for _, column_key, label in _POINTS),
            rows=(("capacity", "능력 [W]"), ("power", "전력 [W]")),
            editable_cells={
                ("capacity", "full_46"): "full_46_capacity",
                ("power", "full_46"): "full_46_power",
                ("capacity", "full_35"): "full_35_capacity",
                ("power", "full_35"): "full_35_power",
                ("capacity", "half_35"): "half_35_capacity",
                ("power", "half_35"): "half_35_power",
                ("capacity", "min_35"): "min_35_capacity",
                ("power", "min_35"): "min_35_power",
            },
            visual_style="shared",
        )
        self.input_table.grid(
            row=1, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, 6),
        )

        self.optional_min_enabled = tk.BooleanVar(master=self._frame, value=True)
        self.optional_min_toggle = ttk.Checkbutton(
            self._frame,
            text="",
            variable=self.optional_min_enabled,
            command=self._on_optional_min_toggled,
        )

        self.result_table = IsoSasoT3ResultTable(self._frame)
        self.result_table.show_placeholder(
            (REQUIRED_TRACE_LABEL, OPTIONAL_TRACE_LABEL), status="입력 대기"
        )
        self.result_panel = self.result_table
        self.result_table.grid(
            row=3, column=0, sticky="w", padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.action_row = ttk.Frame(self._frame)
        self.action_row.grid(
            row=4,
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
        self.batch_button.surface_role = "saso_t3_batch_open"
        self.batch_button.pack(side=tk.LEFT)
        self.detail_toggle = ttk.Button(
            self.action_row,
            text="상세 보기 ↓",
            command=self._toggle_detail,
        )
        self.detail_toggle.surface_role = "saso_t3_detail_toggle"
        self.detail_toggle.pack(side=tk.LEFT, padx=(6, 0))
        self.result_actions = add_result_actions(
            self.action_row,
            parent=self._frame,
            result_owner=self.result_table,
            csv_filename="saso_t3_result.csv",
            surface_prefix="saso_t3_result",
        )
        self.copy_button = self.result_actions.copy_button
        self.export_button = self.result_actions.export_button
        self.detail_panel = BinDetailPanel(
            self._frame,
            source_labels=(REQUIRED_TRACE_LABEL, OPTIONAL_TRACE_LABEL),
            default_source=OPTIONAL_TRACE_LABEL,
            csv_filename="saso_t3_bin_detail.csv",
        )
        self._detail_visibility = DetailPanelVisibility(
            panel=self.detail_panel,
            button=self.detail_toggle,
            grid_options={
                "row": 5,
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
        self.trace_profile_combo = self.detail_panel.source_combo

        self.input_controller = TkTableController(self.input_table)
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.input_table.set_values_changed_callback(self._auto_calc.schedule)
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._sync_optional_min_state()
        self._auto_calc.flush_now()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def cancel_pending(self) -> None:
        self._auto_calc.cancel()

    def recalculate_now(self) -> None:
        result = self._usecase.calculate(self.input_table.get_text_values())
        self.input_table.clear_invalid_fields()
        if result.invalid_fields:
            self.input_table.set_invalid_fields(result.invalid_fields)
        if result.detail_status is not None:
            self._clear_trace(result.detail_status)
        else:
            self._trace_results = {
                label: list(rows) for label, rows in (result.detail_sources or {}).items()
            }
            self._detail_summaries = dict(result.detail_summaries or {})
            self._detail_statuses = dict(result.detail_statuses or {})
            self._trace_status = None
            self._update_detail_panel()
        if result.rows:
            self.result_table.set_rows(
                result.rows,
                status=result.status_text,
                invalid_row_labels=(
                    frozenset({OPTIONAL_TRACE_LABEL})
                    if result.status == "partial"
                    else frozenset()
                ),
            )
        else:
            self.result_table.set_status(
                result.status_text,
                tone=(
                    SemanticTone.PENDING
                    if result.status == "empty"
                    else SemanticTone.INVALID
                ),
            )

    def _on_optional_min_toggled(self) -> None:
        self._sync_optional_min_state()
        self._sync_optional_trace_state()
        self._auto_calc.schedule()

    def _sync_optional_min_state(self) -> None:
        for field_key in ("min_35_capacity", "min_35_power"):
            self.input_table.editable_entries[field_key].configure(state=tk.NORMAL)

    def _sync_optional_trace_state(self) -> None:
        self.optional_min_enabled.set(True)
        self._sync_optional_min_state()

    def _open_batch_dialog(self) -> None:
        self._batch_handle.open_or_focus(
            lambda: SasoT3BatchDialog(
                self._frame.winfo_toplevel(),
                initial_snapshot=self._batch_handle.snapshot,
                on_close=self._clear_batch_dialog,
            )
        )

    def _clear_batch_dialog(self, snapshot: list[dict[str, str]] | None = None) -> None:
        self._batch_handle.clear(snapshot)

    @property
    def _batch_dialog(self) -> SasoT3BatchDialog | None:
        return self._batch_handle.dialog

    @_batch_dialog.setter
    def _batch_dialog(self, dialog: SasoT3BatchDialog | None) -> None:
        self._batch_handle.dialog = dialog

    @property
    def _batch_snapshot(self) -> list[dict[str, str]] | None:
        return self._batch_handle.snapshot

    @_batch_snapshot.setter
    def _batch_snapshot(self, snapshot: list[dict[str, str]] | None) -> None:
        self._batch_handle.snapshot = snapshot

    def _toggle_detail(self) -> None:
        self._detail_visibility.toggle()

    def _update_detail_panel(self) -> None:
        if self._trace_status is not None:
            self.detail_panel.set_status(self._trace_status)
            return
        sources = {}
        for label in (OPTIONAL_TRACE_LABEL, REQUIRED_TRACE_LABEL):
            if label in self._trace_results:
                sources[label] = BinDetailSource(
                    rows=tuple(self._trace_results[label]),
                    summary=self._detail_summaries.get(label, ()),
                )
            elif label in self._detail_statuses:
                sources[label] = BinDetailSource(status=self._detail_statuses[label])
        self.detail_panel.set_sources(
            sources,
            source_order=(OPTIONAL_TRACE_LABEL, REQUIRED_TRACE_LABEL),
            panel_status="상세 데이터 없음",
        )

    def _clear_trace(self, status: str) -> None:
        self._trace_results = {}
        self._detail_summaries = {}
        self._detail_statuses = {}
        self._trace_status = status
        self._update_detail_panel()

    def _copy_result_table(self) -> bool:
        return self.result_table.copy_table()

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
            self._batch_handle.dispose()
