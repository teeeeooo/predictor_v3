"""EN14825 SEER calculation section for Tkinter."""

from __future__ import annotations

from collections.abc import Callable, Mapping
import tkinter as tk
from tkinter import ttk

from apps.calculator.application.en14825 import SeerAdapter
from apps.calculator.application.en14825.seer_models import (
    SeerPointInput,
    SeerPointComputed,
    SeerResultSummary,
)
from apps.calculator.ui.en14825 import (
    SeerTableModel,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch_dialogs.profiles.en14825_seer import (
    En14825SeerBatchDialog,
    En14825SeerBatchSnapshot,
)
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.result_panel import ResultPanel
from apps.calculator.ui.result_actions import add_result_actions
from apps.calculator.ui.result_models import ResultSummary
from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from apps.calculator.ui.sections.bin_detail_schema import (
    EN14825_SEER_BIN_DETAIL_SCHEMA,
)
from apps.calculator.ui.sections.detail_visibility import DetailPanelVisibility
from apps.calculator.ui.sections.en14825_seer_detail import format_seer_bin_details
from apps.calculator.ui.table_grid_model import parse_numeric_cell
from apps.calculator.ui.layout_constants import (
    BATCH_INPUT_BUTTON_TEXT,
    CONTROL_APPLIANCE_TYPE_SELECTOR_WIDTH_CHARS,
    CONTROL_GROUP_GAP,
    CONTROL_LABEL_GAP,
    CONTROL_ROW_PADY,
    METRIC_TABLE_COMPACT_ROW_HEADER_CHARS,
    METRIC_TABLE_EN14825_ROW_HEADER_CHARS,
    METRIC_TABLE_STANDARD_DATA_COLUMN_CHARS,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)

STATUS_MAPPINGS = {
    "idle": "대기 중",
    "complete": "자동 계산 완료",
    "invalid_design_load": "설계 냉방 부하 오류 (0 초과 필요)",
    "invalid_t_design": "설계 온도 오류 (16°C 불가)",
    "input_incomplete": "입력 대기 중 (Declared 또는 Tested 데이터 입력 필요)",
    "declared_error": "Declared 계산 오류",
    "tested_error": "Tested 계산 오류",
}


class En14825SeerSection:
    """EN14825 SEER input table, auxiliary inputs, and result summary panel."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_trace_visibility_changed: Callable[[], None] | None = None,
        common_input_values: Callable[[], Mapping[str, str]] | None = None,
    ) -> None:
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self._common_input_values = common_input_values or (
            lambda: {"p_to": "0", "p_sb": "0", "p_ck": "0", "p_off": "0"}
        )
        self.adapter = SeerAdapter()
        self._seer_defaults = self.adapter.get_seer_defaults()
        self._current_table_model: SeerTableModel | None = None
        self._batch_handle: BatchDialogHandle[
            En14825SeerBatchSnapshot, En14825SeerBatchDialog
        ] = BatchDialogHandle()
        self._detail_sources: dict[str, BinDetailSource] = {}
        self._detail_status = "입력 대기"

        self._frame = ttk.LabelFrame(parent, text="SEER")
        self._frame.columnconfigure(0, weight=1)

        # 1. Auxiliary Parameters Frame
        self._p_design_var = tk.StringVar(master=self._frame, value="")
        self._t_design_var = tk.StringVar(
            master=self._frame,
            value=str(self._seer_defaults["t_design_c"]),
        )
        self._cd_var = tk.StringVar(
            master=self._frame,
            value=str(self._seer_defaults["degradation_coefficient"]),
        )
        self._appliance_type_var = tk.StringVar(
            master=self._frame,
            value=self._seer_defaults["appliance_type"],
        )
        self._syncing_design_inputs = False

        aux_frame = ttk.Frame(self._frame)
        aux_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, ISO_SECTION_BLOCK_GAP),
        )

        # Design Specs Frame (Pdesignc, Tdesignc, Cd)
        design_frame = ttk.LabelFrame(aux_frame, text="설계 사양 (Design Specs)")
        design_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, CONTROL_GROUP_GAP))
        design_frame.columnconfigure(0, weight=0)
        self.design_table = MetricInputTable(
            design_frame,
            columns=(
                ("p_design_c", "Pdesignc [W]"),
                ("t_design_c", "Tdesignc [°C]"),
                ("cd", "Cd"),
            ),
            rows=(("design", "입력값"),),
            editable_cells={
                ("design", "p_design_c"): "p_design_c",
                ("design", "t_design_c"): "t_design_c",
                ("design", "cd"): "cd",
            },
            row_header_chars=METRIC_TABLE_COMPACT_ROW_HEADER_CHARS,
            data_column_chars=METRIC_TABLE_STANDARD_DATA_COLUMN_CHARS,
            layout_policy="content_hug",
            visual_style="shared",
        )
        self.design_table.grid(
            row=0, column=0, sticky="w",
            padx=CONTROL_ROW_PADY, pady=CONTROL_ROW_PADY,
        )
        self.design_table.set_values(self._design_input_values())
        self.design_table.set_values_changed_callback(
            self._on_design_table_values_changed
        )
        self.design_controller = TkTableController(self.design_table)
        self.appliance_type_label = ttk.Label(design_frame, text="Type")
        self.appliance_type_label.grid(
            row=0, column=1, sticky="w",
            padx=(CONTROL_GROUP_GAP, CONTROL_LABEL_GAP), pady=CONTROL_ROW_PADY,
        )
        self.appliance_type_selector = ttk.Combobox(
            design_frame,
            textvariable=self._appliance_type_var,
            values=("reversible", "cooling_only"),
            width=CONTROL_APPLIANCE_TYPE_SELECTOR_WIDTH_CHARS,
            state="readonly",
        )
        self.appliance_type_selector.grid(
            row=0, column=2, sticky="w",
            padx=(0, CONTROL_ROW_PADY), pady=CONTROL_ROW_PADY,
        )

        # 2. Main Matrix Table
        ttk.Label(self._frame, text="SEER Test Conditions & Data").grid(
            row=2,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 4),
        )

        editable_cells = {}
        for col in ("A", "B", "C", "D"):
            for row in ("declared_capacity", "declared_eer", "tested_capacity", "tested_power"):
                editable_cells[(row, col)] = f"{row}_{col}"

        self.input_table = MetricInputTable(
            self._frame,
            columns=(
                ("A", "A (35°C)"),
                ("B", "B (30°C)"),
                ("C", "C (25°C)"),
                ("D", "D (20°C)"),
            ),
            rows=tuple(
                (row_key, SeerTableModel.ROW_LABELS[row_key])
                for row_key in SeerTableModel.ROW_KEYS
            ),
            editable_cells=editable_cells,
            row_header_chars=METRIC_TABLE_EN14825_ROW_HEADER_CHARS,
            section_break_before_rows=(
                "declared_capacity",
                "tested_capacity",
                "capacity_percent",
            ),
            visual_style="shared",
        )
        self.input_table.grid(
            row=3,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )

        # Hook dynamic background colors for cells based on their status
        self.input_table.default_cell_background = self._resolve_cell_bg

        self.input_controller = TkTableController(self.input_table)

        # 3. Result Panel
        self.result_panel = ResultPanel(self._frame, title="SEER 결과")
        self.result_panel.grid(
            row=4,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )

        action_row = ttk.Frame(self._frame)
        action_row.grid(
            row=5,
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
        self.batch_button.surface_role = "en14825_seer_batch_open"
        self.batch_button.pack(side=tk.LEFT)
        self.detail_toggle = ttk.Button(
            action_row,
            text="상세 보기 ↓",
            command=self._toggle_detail,
        )
        self.detail_toggle.surface_role = "en14825_seer_detail_toggle"
        self.detail_toggle.pack(side=tk.LEFT, padx=(ISO_SECTION_BLOCK_GAP, 0))
        self.result_actions = add_result_actions(
            action_row,
            parent=self._frame,
            result_owner=self.result_panel,
            csv_filename="en14825_seer_result.csv",
            surface_prefix="en14825_seer_result",
        )
        self.copy_button = self.result_actions.copy_button
        self.export_button = self.result_actions.export_button
        self.detail_panel = BinDetailPanel(
            self._frame,
            source_labels=("Declared", "Tested"),
            default_source="Declared",
            csv_filename="en14825_seer_bin_detail.csv",
            schema=EN14825_SEER_BIN_DETAIL_SCHEMA,
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
            on_change=lambda: self._on_detail_visibility_changed()
            if self._on_detail_visibility_changed is not None
            else None,
        )

        # 4. Debounced auto-calc scheduler
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.input_table.set_values_changed_callback(self._auto_calc.schedule)

        # Bind auxiliary changes to scheduler
        for var in (
            self._p_design_var,
            self._t_design_var,
            self._cd_var,
        ):
            var.trace_add("write", lambda *args: self._on_design_var_changed())
        self._appliance_type_var.trace_add(
            "write", lambda *args: self._auto_calc.schedule()
        )

        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._auto_calc.flush_now()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def cancel_pending(self) -> None:
        self._auto_calc.cancel()

    def schedule_recalculate(self) -> None:
        self._auto_calc.schedule()

    @property
    def _batch_dialog(self) -> En14825SeerBatchDialog | None:
        return self._batch_handle.dialog

    @_batch_dialog.setter
    def _batch_dialog(self, dialog: En14825SeerBatchDialog | None) -> None:
        self._batch_handle.dialog = dialog

    @property
    def _batch_snapshot(self) -> En14825SeerBatchSnapshot | None:
        return self._batch_handle.snapshot

    @_batch_snapshot.setter
    def _batch_snapshot(self, snapshot: En14825SeerBatchSnapshot | None) -> None:
        self._batch_handle.snapshot = snapshot

    def _open_batch_dialog(self) -> None:
        self._batch_handle.open_or_focus(
            lambda: En14825SeerBatchDialog(
                self._frame.winfo_toplevel(),
                initial_snapshot=self._batch_handle.snapshot,
                on_close=self._clear_batch_dialog,
            )
        )

    def _clear_batch_dialog(
        self,
        snapshot: En14825SeerBatchSnapshot | None = None,
    ) -> None:
        self._batch_handle.clear(snapshot)

    def _design_input_values(self) -> dict[str, str]:
        return {
            "p_design_c": self._p_design_var.get(),
            "t_design_c": self._t_design_var.get(),
            "cd": self._cd_var.get(),
        }

    def _on_design_var_changed(self) -> None:
        if not self._syncing_design_inputs:
            self.design_table.set_values_batch(self._design_input_values())
        self._auto_calc.schedule()

    def _on_design_table_values_changed(self) -> None:
        if self._syncing_design_inputs:
            return
        values = self.design_table.get_text_values()
        var_by_key = {
            "p_design_c": self._p_design_var,
            "t_design_c": self._t_design_var,
            "cd": self._cd_var,
        }
        self._syncing_design_inputs = True
        try:
            for key, var in var_by_key.items():
                value = values.get(key, var.get())
                if var.get() != value:
                    var.set(value)
        finally:
            self._syncing_design_inputs = False
        self._auto_calc.schedule()

    def recalculate_now(self) -> None:
        try:
            # 1. Read and validate text values from input matrix
            text_vals = self.input_table.get_text_values()
            if (
                not self._p_design_var.get().strip()
                and not any(value.strip() for value in text_vals.values())
            ):
                self.input_table.clear_invalid_fields()
                self.result_panel.clear()
                self._clear_computed_rows()
                self._clear_detail("\uc785\ub825 \ub300\uae30")
                return
            invalid_fields = {}
            parsed_vals = {}
            for field_key, raw_val in text_vals.items():
                stripped = raw_val.strip()
                if not stripped:
                    parsed_vals[field_key] = None
                else:
                    try:
                        parsed_vals[field_key] = parse_numeric_cell(raw_val)
                    except ValueError:
                        invalid_fields[field_key] = "숫자 입력 필요"

            if invalid_fields:
                self.input_table.set_invalid_fields(invalid_fields)
                self.result_panel.clear()
                self._clear_computed_rows()
                self._clear_detail("입력 오류: 숫자 입력을 확인하세요.")
                return
            else:
                self.input_table.clear_invalid_fields()

            # Read auxiliary values
            p_design_c_w = self._parse_float_safe(self._p_design_var.get(), 0.0)
            t_design_c = self._parse_float_safe(self._t_design_var.get(), self._seer_defaults["t_design_c"])
            cd = self._parse_float_safe(self._cd_var.get(), self._seer_defaults["degradation_coefficient"])
            appliance_type = self._appliance_type_var.get()
            common_inputs = self._common_input_values()
            p_to_w = self._parse_float_safe(common_inputs.get("p_to", "0"), 0.0)
            p_sb_w = self._parse_float_safe(common_inputs.get("p_sb", "0"), 0.0)
            p_ck_w = self._parse_float_safe(common_inputs.get("p_ck", "0"), 0.0)
            p_off_w = self._parse_float_safe(common_inputs.get("p_off", "0"), 0.0)

        except Exception:
            self.result_panel.clear()
            self._clear_computed_rows()
            self._clear_detail("입력 대기: 설계 조건을 확인하세요.")
            return

        # 2. Build point inputs
        inputs = {}
        for col in ("A", "B", "C", "D"):
            inputs[col] = SeerPointInput(
                declared_capacity=parsed_vals[f"declared_capacity_{col}"],
                declared_eer=parsed_vals[f"declared_eer_{col}"],
                tested_capacity=parsed_vals[f"tested_capacity_{col}"],
                tested_power=parsed_vals[f"tested_power_{col}"],
            )

        # 3 & 4. Compute points and final results
        computed = self.adapter.compute_points(inputs)
        summary = self.adapter.calculate(
            inputs=inputs,
            p_design_c_w=p_design_c_w,
            p_to_w=p_to_w,
            p_sb_w=p_sb_w,
            p_ck_w=p_ck_w,
            p_off_w=p_off_w,
            t_design_c=t_design_c,
            cd=cd,
            appliance_type=appliance_type,
        )

        self._current_table_model = SeerTableModel(
            inputs=inputs,
            computed=computed,
            p_design_c_w=p_design_c_w,
            t_design_c=t_design_c,
        )

        # 5. Update display / computed rows in table
        for row in SeerTableModel.ROW_KEYS:
            for col in SeerTableModel.COL_KEYS:
                if not self._current_table_model.is_editable(row, col):
                    val_str = self._current_table_model.get_value(row, col)
                    self._set_static_cell_value((row, col), val_str)

        # Repaint selection backgrounds (respects new cell states)
        self.input_controller._paint_selection()

        # 6. Update result summaries
        self._update_result_summary(summary)
        self._update_detail(summary)

    def _update_detail(self, summary: SeerResultSummary) -> None:
        sources: dict[str, BinDetailSource] = {}
        for label, rows in (
            ("Declared", summary.declared_bin_details),
            ("Tested", summary.tested_bin_details),
        ):
            formatted_rows = format_seer_bin_details(rows)
            if formatted_rows:
                sources[label] = BinDetailSource(rows=formatted_rows)
        self._detail_sources = sources
        if sources:
            self._detail_status = "상세 데이터 없음"
            self.detail_panel.set_sources(
                sources,
                source_order=tuple(sources),
                panel_status=self._detail_status,
            )
            return
        self._clear_detail(
            STATUS_MAPPINGS.get(summary.status_code, "상세 데이터 없음")
        )

    def _clear_detail(self, status: str) -> None:
        self._detail_sources = {}
        self._detail_status = status
        self.detail_panel.set_status(status)

    def _toggle_detail(self) -> None:
        self._detail_visibility.toggle()

    def _parse_float_safe(self, text: str, default: float) -> float:
        try:
            return float(text.strip().replace(",", ""))
        except ValueError:
            return default

    def _clear_computed_rows(self) -> None:
        self._current_table_model = None
        for row in SeerTableModel.ROW_KEYS:
            for col in SeerTableModel.COL_KEYS:
                is_editable = row in (
                    "declared_capacity",
                    "declared_eer",
                    "tested_capacity",
                    "tested_power",
                )
                if not is_editable:
                    self._set_static_cell_value((row, col), "-")
        self.input_controller._paint_selection()

    def _set_static_cell_value(self, address: tuple[str, str], value: str) -> None:
        label = self.input_table.static_cell_labels.get(address)
        if label:
            label.configure(text=value)

    def _resolve_cell_bg(self, position: tuple[int, int]) -> str:
        row, col = self.input_table._address_at_position(position)
        if self._current_table_model:
            state = self._current_table_model.get_state(row, col)
        else:
            state = "neutral"

        return self.input_table.role_cell_background(
            position,
            invalid=state == "invalid",
        )

    def _update_result_summary(self, summary: SeerResultSummary) -> None:
        status_text = STATUS_MAPPINGS.get(summary.status_code, "계산 완료")

        fields = (
            ("Declared SEER", f"{summary.declared_seer:.2f}" if summary.declared_seer is not None else "-"),
            ("Tested SEER", f"{summary.tested_seer:.2f}" if summary.tested_seer is not None else "-"),
            ("SEER %", f"{summary.seer_percent:.1f}%" if summary.seer_percent is not None else "-"),
            ("Declared QC [kWh]", f"{summary.declared_qc_kwh:.1f}" if summary.declared_qc_kwh is not None else "-"),
            ("Tested QC [kWh]", f"{summary.tested_qc_kwh:.1f}" if summary.tested_qc_kwh is not None else "-"),
        )

        self.result_panel.set_summaries(
            [
                ResultSummary(
                    title="EN14825 SEER 결과",
                    fields=fields,
                    status=status_text,
                )
            ]
        )

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
            self._batch_handle.dispose()
