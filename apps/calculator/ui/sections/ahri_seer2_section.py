"""Product-aware AHRI 210/240 SEER2 calculation section for Tkinter."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from apps.calculator.application.ahri import AhriSeer2Adapter, AhriSeer2InputError
from apps.calculator.ui.ahri.seer2_product_surface import AhriSeer2ProductSurface
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.batch_dialogs.profiles.ahri_seer2 import (
    AhriSeer2BatchDialog,
    AhriSeer2BatchSnapshot,
)
from apps.calculator.ui.layout_constants import (
    BATCH_INPUT_BUTTON_TEXT,
    CONTROL_EQUIPMENT_TYPE_SELECTOR_WIDTH_CHARS,
    CONTROL_LABEL_GAP,
    CONTROL_ROW_PADY,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.result_actions import add_result_actions
from apps.calculator.ui.result_models import ResultSummary
from apps.calculator.ui.result_panel import ResultPanel
from apps.calculator.ui.sections.ahri_multicapacity_detail_schema import (
    AHRI_DUAL_SEER2_BIN_DETAIL_SCHEMA,
)
from apps.calculator.ui.sections.ahri_seer2_detail import format_seer2_bin_details
from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from apps.calculator.ui.sections.bin_detail_schema import AHRI_SEER2_BIN_DETAIL_SCHEMA
from apps.calculator.ui.sections.detail_visibility import DetailPanelVisibility

_PRODUCT_LABELS = {
    "Variable Capacity": "variable_capacity",
    "Dual Stage": "dual_stage",
}


class AhriSeer2Section:
    """Stable metric shell with product-specific input and detail composition."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        adapter: AhriSeer2Adapter | None = None,
        on_trace_visibility_changed: Callable[[], None] | None = None,
    ) -> None:
        self.adapter = adapter or AhriSeer2Adapter()
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self._detail_status = "입력 대기"
        self._product_snapshots: dict[str, dict[str, object]] = {}
        self._batch_handle: BatchDialogHandle[
            AhriSeer2BatchSnapshot, AhriSeer2BatchDialog
        ] = BatchDialogHandle()
        self._frame = ttk.LabelFrame(parent, text="SEER2")
        self._frame.columnconfigure(0, weight=1)
        self._build_option_bar()
        self._surface_host = ttk.Frame(self._frame)
        self._surface_host.grid(
            row=1,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self._surface: AhriSeer2ProductSurface
        self._build_product_surface("variable_capacity")
        self.result_panel = ResultPanel(self._frame, title="AHRI 210/240 SEER2 결과")
        self.result_panel.grid(
            row=2,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        action_row = ttk.Frame(self._frame)
        action_row.grid(
            row=3,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.batch_button = ttk.Button(
            action_row,
            text=BATCH_INPUT_BUTTON_TEXT,
            command=self._open_batch_dialog,
        )
        self.batch_button.pack(side=tk.LEFT)
        self.detail_toggle = ttk.Button(
            action_row,
            text="상세 보기 ↓",
            command=self._toggle_detail,
        )
        self.detail_toggle.surface_role = "ahri_seer2_detail_toggle"
        self.detail_toggle.pack(side=tk.LEFT, padx=(6, 0))
        self.result_actions = add_result_actions(
            action_row,
            parent=self._frame,
            result_owner=self.result_panel,
            csv_filename="ahri_seer2_result.csv",
            surface_prefix="ahri_seer2_result",
        )
        self.copy_button = self.result_actions.copy_button
        self.export_button = self.result_actions.export_button
        self._build_detail_panel(AHRI_SEER2_BIN_DETAIL_SCHEMA)
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.type_var.trace_add("write", lambda *_args: self._on_input_changed())
        self.product_var.trace_add("write", lambda *_args: self._on_product_changed())
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self.recalculate_now()

    def _build_option_bar(self) -> None:
        frame = ttk.LabelFrame(self._frame, text="Options")
        frame.grid(
            row=0,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, ISO_SECTION_BLOCK_GAP),
        )
        ttk.Label(frame, text="Product").pack(
            side=tk.LEFT,
            padx=(CONTROL_ROW_PADY, CONTROL_LABEL_GAP),
            pady=CONTROL_ROW_PADY,
        )
        self.product_var = tk.StringVar(master=self._frame, value="Variable Capacity")
        self.product_selector = ttk.Combobox(
            frame,
            textvariable=self.product_var,
            values=tuple(_PRODUCT_LABELS),
            state="readonly",
            width=22,
        )
        self.product_selector.pack(
            side=tk.LEFT,
            padx=(0, CONTROL_ROW_PADY),
            pady=CONTROL_ROW_PADY,
        )
        ttk.Label(frame, text="Type").pack(
            side=tk.LEFT,
            padx=(CONTROL_ROW_PADY, CONTROL_LABEL_GAP),
            pady=CONTROL_ROW_PADY,
        )
        self.type_var = tk.StringVar(master=self._frame, value="HP")
        self.type_selector = ttk.Combobox(
            frame,
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

    @property
    def product_classification(self) -> str:
        return _PRODUCT_LABELS[self.product_var.get()]

    def _build_product_surface(self, product: str) -> None:
        if hasattr(self, "_surface"):
            self._surface.frame.destroy()
        self._surface = AhriSeer2ProductSurface(
            self._surface_host,
            product=product,
            on_values_changed=self._on_input_changed,
            snapshot=self._product_snapshots.get(product),
        )
        self._surface.grid(row=0, column=0, sticky="w")
        self.input_table = self._surface.input_table
        self.input_controller = self._surface.controller

    def _build_detail_panel(self, schema) -> None:
        self.detail_panel = BinDetailPanel(
            self._frame,
            source_labels=("SEER2",),
            default_source="SEER2",
            csv_filename="ahri_seer2_bin_detail.csv",
            show_source_selector=False,
            schema=schema,
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
            on_change=(
                self._on_detail_visibility_changed
                if self._on_detail_visibility_changed is not None
                else None
            ),
        )

    def _replace_detail_panel(self, schema) -> None:
        was_visible = self._detail_visibility.visible
        self.detail_panel._frame.destroy()
        self._build_detail_panel(schema)
        if was_visible:
            self._detail_visibility.toggle()

    def _on_product_changed(self) -> None:
        if not hasattr(self, "_surface"):
            return
        self._product_snapshots[self._surface.product] = self._surface.snapshot()
        product = self.product_classification
        self._build_product_surface(product)
        self._replace_detail_panel(
            AHRI_SEER2_BIN_DETAIL_SCHEMA
            if product == "variable_capacity"
            else AHRI_DUAL_SEER2_BIN_DETAIL_SCHEMA
        )
        self._clear_results("입력 대기")
        self.schedule_recalculate()
        self._request_refit()

    def _request_refit(self) -> None:
        if self._on_detail_visibility_changed is not None:
            self._frame.after_idle(self._on_detail_visibility_changed)

    def pack(self, **kwargs: object) -> None:
        self._frame.pack(**kwargs)

    def schedule_recalculate(self) -> None:
        if hasattr(self, "_auto_calc"):
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

    def _initial_batch_snapshot(self) -> AhriSeer2BatchSnapshot:
        snapshot = self._batch_handle.snapshot
        if snapshot is not None:
            return snapshot
        product = self.product_classification
        return AhriSeer2BatchSnapshot(
            {
                "product": product,
                "type": self.type_var.get(),
            },
            (),
            {product: ()},
        )

    def _open_batch_dialog(self) -> None:
        self._batch_handle.open_or_focus(
            lambda: AhriSeer2BatchDialog(
                self._frame.winfo_toplevel(),
                initial_snapshot=self._initial_batch_snapshot(),
                on_close=self._clear_batch_dialog,
            )
        )

    def _clear_batch_dialog(
        self, snapshot: AhriSeer2BatchSnapshot | None = None
    ) -> None:
        self._batch_handle.clear(snapshot)

    def recalculate_now(self) -> None:
        try:
            options = self._surface.options()
            summary = self.adapter.calculate(
                self._surface.text_values(),
                system_type=self.type_var.get(),
                product_classification=self.product_classification,
                options=options,
            )
        except AhriSeer2InputError as exc:
            self._surface.set_invalid_fields(exc.field_errors)
            self._clear_results("입력 오류: 숫자 입력을 확인하세요.")
            return
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            self._clear_results("계산 오류")
            return
        self._surface.clear_invalid_fields()
        if summary is None:
            self._clear_results("입력 대기")
            return
        self._surface.set_result_eer2(summary.eer2_by_point)
        if summary.product_classification == "dual_stage":
            fields = (
                ("SEER2 Raw", f"{summary.raw_seer2:.6f}"),
                ("SEER2 Published", f"{summary.published_seer2:.2f}"),
                ("Total Cooling [kBtu]", f"{summary.total_cooling_kbtu:.3f}"),
                ("Total Energy [kWh]", f"{summary.total_energy_kwh:.3f}"),
            )
        else:
            fields = (
                ("SEER2", f"{summary.seer2:.3f}"),
                ("Total Cooling [kBtu]", f"{summary.total_cooling_kbtu:.3f}"),
                ("Total Energy [kWh]", f"{summary.total_energy_kwh:.3f}"),
            )
        self.result_panel.set_summaries(
            (ResultSummary("SEER2", fields, "자동 계산 완료"),)
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
        if hasattr(self, "_surface"):
            self._surface.clear_result_eer2()
        if hasattr(self, "result_panel"):
            self.result_panel.clear()
        self._clear_detail(detail_status)

    def _clear_detail(self, status: str) -> None:
        self._detail_status = status
        if hasattr(self, "detail_panel"):
            self.detail_panel.set_status(status)

    def _toggle_detail(self) -> None:
        self._detail_visibility.toggle()

    def _set_static_cell(self, address: tuple[str, str], value: str) -> None:
        label = self.input_table.static_cell_labels.get(address)
        if label is not None:
            label.configure(text=value)

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
            self._batch_handle.dispose()
