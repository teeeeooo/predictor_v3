"""AHRI 210/240 SEER2 main calculation section for Tkinter."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.ahri import (
    AHRI_SEER2_POINT_ORDER,
    AHRI_SEER2_TEMPERATURES_C,
    AhriSeer2Adapter,
    AhriSeer2InputError,
)
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch_dialogs.profiles.ahri_seer2 import (
    AhriSeer2BatchDialog,
    AhriSeer2BatchSnapshot,
)
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.layout_constants import (
    CONTROL_EQUIPMENT_TYPE_SELECTOR_WIDTH_CHARS,
    CONTROL_LABEL_GAP,
    CONTROL_ROW_PADY,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
    METRIC_TABLE_DESCRIPTIVE_ROW_HEADER_CHARS,
    METRIC_TABLE_POINT_DATA_COLUMN_CHARS,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.result_models import ResultSummary
from apps.calculator.ui.result_panel import ResultPanel
from apps.calculator.ui.sections.ahri_seer2_detail import format_seer2_bin_details
from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from apps.calculator.ui.sections.bin_detail_schema import AHRI_SEER2_BIN_DETAIL_SCHEMA
from apps.calculator.ui.table.controller import TkTableController


class AhriSeer2Section:
    """Type option, five-point matrix, and compact SEER2 result surface."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        adapter: AhriSeer2Adapter | None = None,
        on_trace_visibility_changed: Callable[[], None] | None = None,
    ) -> None:
        self.adapter = adapter or AhriSeer2Adapter()
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self._detail_visible = False
        self._detail_status = "입력 대기"
        self._batch_handle: BatchDialogHandle[
            AhriSeer2BatchSnapshot, AhriSeer2BatchDialog
        ] = BatchDialogHandle()
        self._frame = ttk.LabelFrame(parent, text="SEER2")
        self._frame.columnconfigure(0, weight=1)

        option_frame = ttk.LabelFrame(self._frame, text="Options")
        option_frame.grid(
            row=0,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, ISO_SECTION_BLOCK_GAP),
        )
        ttk.Label(option_frame, text="Type").pack(
            side=tk.LEFT,
            padx=(CONTROL_ROW_PADY, CONTROL_LABEL_GAP),
            pady=CONTROL_ROW_PADY,
        )
        self.type_var = tk.StringVar(value="HP")
        self.type_selector = ttk.Combobox(
            option_frame,
            textvariable=self.type_var,
            values=("HP", "AC"),
            state="readonly",
            width=CONTROL_EQUIPMENT_TYPE_SELECTOR_WIDTH_CHARS,
        )
        self.type_selector.pack(
            side=tk.LEFT,
            padx=(0, CONTROL_ROW_PADY),
            pady=CONTROL_ROW_PADY,
        )

        editable_cells = {
            (row, point): f"{row}_{point}"
            for point in AHRI_SEER2_POINT_ORDER
            for row in ("capacity", "power")
        }
        self.input_table = MetricInputTable(
            self._frame,
            columns=tuple((point, point) for point in AHRI_SEER2_POINT_ORDER),
            rows=(
                ("condition_temp", "Condition / Temp"),
                ("capacity", "Capacity [Btu/h]"),
                ("power", "Power [W]"),
                ("eer2", "EER2"),
            ),
            editable_cells=editable_cells,
            row_header_chars=METRIC_TABLE_DESCRIPTIVE_ROW_HEADER_CHARS,
            data_column_chars=METRIC_TABLE_POINT_DATA_COLUMN_CHARS,
            layout_policy="content_hug",
            values_changed_callback=self.schedule_recalculate,
        )
        self.input_table.grid(
            row=1,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.input_controller = TkTableController(self.input_table)
        for point in AHRI_SEER2_POINT_ORDER:
            self._set_static_cell(
                ("condition_temp", point),
                f"Cooling / {AHRI_SEER2_TEMPERATURES_C[point]:.1f} °C",
            )
            self._set_static_cell(("eer2", point), "")

        self.result_panel = ResultPanel(self._frame, title="AHRI 210/240 SEER2 결과")
        self.result_panel.grid(
            row=2,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )

        self.batch_button = ttk.Button(
            self._frame,
            text="SEER2 Batch",
            command=self._open_batch_dialog,
        )
        self.batch_button.grid(
            row=3,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )

        detail_action_row = ttk.Frame(self._frame)
        detail_action_row.grid(
            row=4,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.detail_toggle = ttk.Button(
            detail_action_row,
            text="상세 보기 ↓",
            command=self._toggle_detail,
        )
        self.detail_toggle.surface_role = "ahri_seer2_detail_toggle"
        self.detail_toggle.pack(side=tk.LEFT)
        self.detail_panel = BinDetailPanel(
            self._frame,
            source_labels=("SEER2",),
            default_source="SEER2",
            csv_filename="ahri_seer2_bin_detail.csv",
            show_source_selector=False,
            schema=AHRI_SEER2_BIN_DETAIL_SCHEMA,
        )

        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.input_table.set_values_changed_callback(self._on_input_changed)
        self.type_var.trace_add("write", lambda *_args: self._on_input_changed())
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self.recalculate_now()

    def pack(self, **kwargs: object) -> None:
        self._frame.pack(**kwargs)

    def schedule_recalculate(self) -> None:
        self._auto_calc.schedule()

    def _on_input_changed(self) -> None:
        self._clear_detail("입력 대기")
        self.schedule_recalculate()

    @property
    def _batch_dialog(self) -> AhriSeer2BatchDialog | None:
        return self._batch_handle.dialog

    @_batch_dialog.setter
    def _batch_dialog(self, dialog: AhriSeer2BatchDialog | None) -> None:
        self._batch_handle.dialog = dialog

    @property
    def _batch_snapshot(self) -> AhriSeer2BatchSnapshot | None:
        return self._batch_handle.snapshot

    @_batch_snapshot.setter
    def _batch_snapshot(self, snapshot: AhriSeer2BatchSnapshot | None) -> None:
        self._batch_handle.snapshot = snapshot

    def _open_batch_dialog(self) -> None:
        self._batch_handle.open_or_focus(
            lambda: AhriSeer2BatchDialog(
                self._frame.winfo_toplevel(),
                initial_snapshot=self._batch_handle.snapshot,
                on_close=self._clear_batch_dialog,
            )
        )

    def _clear_batch_dialog(
        self,
        snapshot: AhriSeer2BatchSnapshot | None = None,
    ) -> None:
        self._batch_handle.clear(snapshot)

    def recalculate_now(self) -> None:
        try:
            summary = self.adapter.calculate(
                self.input_table.get_text_values(),
                system_type=self.type_var.get(),
            )
        except AhriSeer2InputError as exc:
            self.input_table.set_invalid_fields(exc.field_errors)
            self._clear_results("입력 오류: 숫자 입력을 확인하세요.")
            return
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            self._clear_results("계산 오류")
            return

        self.input_table.clear_invalid_fields()
        if summary is None:
            self._clear_results("입력 대기")
            return
        for point, eer2 in summary.eer2_by_point.items():
            self._set_static_cell(("eer2", point), f"{eer2:.2f}")
        self.result_panel.set_summaries(
            (
                ResultSummary(
                    title="SEER2",
                    fields=(
                        ("SEER2", f"{summary.seer2:.3f}"),
                        ("Total Cooling [kBtu]", f"{summary.total_cooling_kbtu:.3f}"),
                        ("Total Energy [kWh]", f"{summary.total_energy_kwh:.3f}"),
                    ),
                    status="자동 계산 완료",
                ),
            )
        )
        rows = format_seer2_bin_details(summary.bin_details)
        if rows:
            self._detail_status = "상세 데이터 없음"
            self.detail_panel.set_sources(
                {"SEER2": BinDetailSource(rows=rows)},
                source_order=("SEER2",),
                panel_status=self._detail_status,
            )
        else:
            self._clear_detail("상세 데이터 없음")

    def _clear_results(self, detail_status: str = "입력 대기") -> None:
        for point in AHRI_SEER2_POINT_ORDER:
            self._set_static_cell(("eer2", point), "")
        self.result_panel.clear()
        self._clear_detail(detail_status)

    def _clear_detail(self, status: str) -> None:
        self._detail_status = status
        if hasattr(self, "detail_panel"):
            self.detail_panel.set_status(status)

    def _toggle_detail(self) -> None:
        self._detail_visible = not self._detail_visible
        if self._detail_visible:
            self.detail_panel.grid(
                row=5,
                column=0,
                sticky="ew",
                padx=0,
                pady=(0, ISO_SECTION_BLOCK_GAP),
            )
            self.detail_toggle.configure(text="상세 닫기 ↑")
        else:
            self.detail_panel.grid_remove()
            self.detail_toggle.configure(text="상세 보기 ↓")
        if self._on_detail_visibility_changed is not None:
            self._on_detail_visibility_changed()

    def _set_static_cell(self, address: tuple[str, str], value: str) -> None:
        label = self.input_table.static_cell_labels.get(address)
        if label is not None:
            label.configure(text=value)

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
            self._batch_handle.dispose()
