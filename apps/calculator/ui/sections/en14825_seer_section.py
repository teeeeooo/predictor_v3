"""EN14825 SEER calculation section for Tkinter."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.en14825 import (
    SeerPointInput,
    SeerPointComputed,
    SeerResultSummary,
    SeerAdapter,
    SeerTableModel,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table.roles import CellRole
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.result_panel import ResultPanel
from apps.calculator.ui.result_models import ResultSummary
from apps.calculator.ui.table_grid_model import parse_numeric_cell
from apps.calculator.ui.layout_constants import (
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
    TABLE_INVALID_BG,
    TABLE_STATIC_BG,
    TABLE_EDITABLE_BG,
    TABLE_PASS_BG,
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
    ) -> None:
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self.adapter = SeerAdapter()
        self._current_table_model: SeerTableModel | None = None

        self._frame = ttk.LabelFrame(parent, text="SEER Comparison (EN 14825)")
        self._frame.columnconfigure(0, weight=1)

        # 1. Auxiliary Parameters Frame
        self._p_design_var = tk.StringVar(value="3000")
        self._t_design_var = tk.StringVar(value="35.0")
        self._cd_var = tk.StringVar(value="0.25")
        self._p_to_var = tk.StringVar(value="0")
        self._p_sb_var = tk.StringVar(value="0")
        self._p_ck_var = tk.StringVar(value="0")
        self._p_off_var = tk.StringVar(value="0")

        aux_frame = ttk.Frame(self._frame)
        aux_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(8, ISO_SECTION_BLOCK_GAP),
        )

        # Design Specs Frame (Pdesignc, Tdesignc, Cd)
        design_frame = ttk.LabelFrame(aux_frame, text="설계 사양 (Design Specs)")
        design_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(design_frame, text="Pdesignc [W]:").grid(row=0, column=0, sticky="w", padx=(6, 4), pady=6)
        ttk.Entry(design_frame, textvariable=self._p_design_var, width=8).grid(row=0, column=1, sticky="w", padx=(0, 10), pady=6)

        ttk.Label(design_frame, text="Tdesignc [°C]:").grid(row=0, column=2, sticky="w", padx=(6, 4), pady=6)
        ttk.Entry(design_frame, textvariable=self._t_design_var, width=6).grid(row=0, column=3, sticky="w", padx=(0, 10), pady=6)

        ttk.Label(design_frame, text="Cd:").grid(row=0, column=4, sticky="w", padx=(6, 4), pady=6)
        ttk.Entry(design_frame, textvariable=self._cd_var, width=6).grid(row=0, column=5, sticky="w", padx=(0, 6), pady=6)

        # Standby/Aux power Frame (Pto, Psb, Pck, Poff)
        standby_frame = ttk.LabelFrame(aux_frame, text="대기 및 보조 전력 (Aux Power [W])")
        standby_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(standby_frame, text="Pto:").grid(row=0, column=0, sticky="w", padx=(6, 4), pady=6)
        ttk.Entry(standby_frame, textvariable=self._p_to_var, width=6).grid(row=0, column=1, sticky="w", padx=(0, 10), pady=6)

        ttk.Label(standby_frame, text="Psb:").grid(row=0, column=2, sticky="w", padx=(6, 4), pady=6)
        ttk.Entry(standby_frame, textvariable=self._p_sb_var, width=6).grid(row=0, column=3, sticky="w", padx=(0, 10), pady=6)

        ttk.Label(standby_frame, text="Pck:").grid(row=0, column=4, sticky="w", padx=(6, 4), pady=6)
        ttk.Entry(standby_frame, textvariable=self._p_ck_var, width=6).grid(row=0, column=5, sticky="w", padx=(0, 10), pady=6)

        ttk.Label(standby_frame, text="Poff:").grid(row=0, column=6, sticky="w", padx=(6, 4), pady=6)
        ttk.Entry(standby_frame, textvariable=self._p_off_var, width=6).grid(row=0, column=7, sticky="w", padx=(0, 6), pady=6)

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
        )
        self.input_table.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )

        # Hook dynamic background colors for cells based on their status
        self.input_table.default_cell_background = self._resolve_cell_bg

        # Prefill default values
        self.input_table.set_values(
            {
                "declared_capacity_A": "3600",
                "declared_capacity_B": "2650",
                "declared_capacity_C": "1700",
                "declared_capacity_D": "1200",
                "declared_eer_A": "4.00",
                "declared_eer_B": "4.60",
                "declared_eer_C": "5.40",
                "declared_eer_D": "6.20",
                "tested_capacity_A": "3600",
                "tested_capacity_B": "2650",
                "tested_capacity_C": "1700",
                "tested_capacity_D": "1200",
                "tested_power_A": "900",
                "tested_power_B": "576",
                "tested_power_C": "315",
                "tested_power_D": "194",
            }
        )

        self.input_controller = TkTableController(self.input_table)

        # 3. Result Panel
        self.result_panel = ResultPanel(self._frame, title="SEER 결과")
        self.result_panel.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )

        # 4. Debounced auto-calc scheduler
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.input_table.set_values_changed_callback(self._auto_calc.schedule)

        # Bind auxiliary changes to scheduler
        for var in (
            self._p_design_var,
            self._t_design_var,
            self._cd_var,
            self._p_to_var,
            self._p_sb_var,
            self._p_ck_var,
            self._p_off_var,
        ):
            var.trace_add("write", lambda *args: self._auto_calc.schedule())

        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._auto_calc.flush_now()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def cancel_pending(self) -> None:
        self._auto_calc.cancel()

    def recalculate_now(self) -> None:
        try:
            # 1. Read and validate text values from input matrix
            text_vals = self.input_table.get_text_values()
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
                return
            else:
                self.input_table.clear_invalid_fields()

            # Read auxiliary values
            p_design_c_w = self._parse_float_safe(self._p_design_var.get(), 0.0)
            t_design_c = self._parse_float_safe(self._t_design_var.get(), 35.0)
            cd = self._parse_float_safe(self._cd_var.get(), 0.25)
            p_to_w = self._parse_float_safe(self._p_to_var.get(), 0.0)
            p_sb_w = self._parse_float_safe(self._p_sb_var.get(), 0.0)
            p_ck_w = self._parse_float_safe(self._p_ck_var.get(), 0.0)
            p_off_w = self._parse_float_safe(self._p_off_var.get(), 0.0)

        except Exception:
            self.result_panel.clear()
            self._clear_computed_rows()
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

        is_editable = self.input_table.cell_role(position) == CellRole.EDITABLE
        if state == "invalid":
            return TABLE_INVALID_BG
        elif state == "pass":
            return TABLE_PASS_BG
        elif state == "unavailable":
            return TABLE_STATIC_BG
        else:
            return TABLE_EDITABLE_BG if is_editable else TABLE_STATIC_BG

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
