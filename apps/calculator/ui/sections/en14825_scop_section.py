"""EN14825 SCOP calculation section for Tkinter."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.en14825 import (
    ScopPointInput,
    ScopPointComputed,
    ScopResultSummary,
    ScopAdapter,
    ScopTableModel,
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
    "invalid_design_load": "설계 난방 부하 오류 (0 초과 필요)",
    "invalid_t_design": "설계 온도 오류 (16°C 불가)",
    "invalid_climate": "기후 선택 오류",
    "invalid_temp_override": "TOL/Tbiv 범위 오류 (TOL <= Tbiv 필요)",
    "input_incomplete": "입력 대기 중 (Declared 또는 Tested 데이터 입력 필요)",
    "declared_error": "Declared 계산 오류",
    "tested_error": "Tested 계산 오류",
}


class En14825ScopSection:
    """EN14825 SCOP stacked climate card tables, auxiliary inputs, and result summary panel."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_trace_visibility_changed: Callable[[], None] | None = None,
    ) -> None:
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self.adapter = ScopAdapter()
        self._current_table_models: dict[str, ScopTableModel] = {}

        self._frame = ttk.LabelFrame(parent, text="SCOP Comparison (EN 14825)")
        self._frame.columnconfigure(0, weight=1)

        # 1. Top Auxiliary Parameters Frame (Standby and Cd)
        self._cd_var = tk.StringVar(value="0.25")
        self._p_to_var = tk.StringVar(value="0")
        self._p_sb_var = tk.StringVar(value="0")
        self._p_ck_var = tk.StringVar(value="0")
        self._p_off_var = tk.StringVar(value="0")
        self._appliance_type_var = tk.StringVar(value="reversible")

        aux_frame = ttk.Frame(self._frame)
        aux_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(8, ISO_SECTION_BLOCK_GAP),
        )

        # Specs Frame (Cd, Appliance Type)
        specs_frame = ttk.LabelFrame(aux_frame, text="기본 사양 (Base Specs)")
        specs_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(specs_frame, text="Cd:").grid(row=0, column=0, sticky="w", padx=(6, 4), pady=6)
        ttk.Entry(specs_frame, textvariable=self._cd_var, width=6).grid(row=0, column=1, sticky="w", padx=(0, 10), pady=6)

        ttk.Label(specs_frame, text="기기 유형:").grid(row=0, column=2, sticky="w", padx=(6, 4), pady=6)
        appliance_combo = ttk.Combobox(
            specs_frame,
            textvariable=self._appliance_type_var,
            values=("reversible", "heating_only"),
            width=12,
            state="readonly",
        )
        appliance_combo.grid(row=0, column=3, sticky="w", padx=(0, 6), pady=6)

        # Standby power Frame
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

        # 2. Stacked Climate Cards
        self.climates = ("average", "warmer", "colder")
        self.climate_cards: dict[str, ttk.LabelFrame] = {}
        self.climate_active_vars: dict[str, tk.BooleanVar] = {}
        self.climate_inner_frames: dict[str, ttk.Frame] = {}

        # Climate-specific vars
        self.p_design_h_vars: dict[str, tk.StringVar] = {
            "average": tk.StringVar(value="3000"),
            "warmer": tk.StringVar(value="3000"),
            "colder": tk.StringVar(value="3000"),
        }
        self.tbiv_vars: dict[str, tk.StringVar] = {
            "average": tk.StringVar(value="-10"),
            "warmer": tk.StringVar(value="2"),
            "colder": tk.StringVar(value="-15"),
        }
        self.tol_vars: dict[str, tk.StringVar] = {
            "average": tk.StringVar(value="-11"),
            "warmer": tk.StringVar(value="-11"),
            "colder": tk.StringVar(value="-22"),
        }

        self.input_tables: dict[str, MetricInputTable] = {}
        self.table_controllers: dict[str, TkTableController] = {}

        card_row_start = 2
        for i, clm in enumerate(self.climates):
            # LabelFrame for climate
            card = ttk.LabelFrame(self._frame, text=f"{clm.capitalize()} 기후 조건 ({clm.capitalize()} Climate)")
            card.grid(
                row=card_row_start + i,
                column=0,
                sticky="ew",
                padx=ISO_SECTION_PADX,
                pady=(0, 10),
            )
            self.climate_cards[clm] = card

            # Climate toggle checkbox in the header area of card (simulated by top frame)
            toggle_frame = ttk.Frame(card)
            toggle_frame.pack(fill=tk.X, padx=6, pady=4)

            active_var = tk.BooleanVar(value=(clm == "average"))
            self.climate_active_vars[clm] = active_var

            chk = ttk.Checkbutton(
                toggle_frame,
                text="기후 활성화 (Activate Climate)",
                variable=active_var,
                command=self._on_climate_toggle,
            )
            chk.pack(side=tk.LEFT)

            # Inner frame containing the actual tables and inputs
            inner = ttk.Frame(card)
            inner.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            self.climate_inner_frames[clm] = inner

            # Setup climate specific auxiliary inputs
            inputs_frame = ttk.Frame(inner)
            inputs_frame.pack(anchor="w", pady=(0, 6))

            ttk.Label(inputs_frame, text="Pdesignh [W]:").grid(row=0, column=0, sticky="w", padx=(6, 4))
            ttk.Entry(inputs_frame, textvariable=self.p_design_h_vars[clm], width=8).grid(row=0, column=1, sticky="w", padx=(0, 10))

            ttk.Label(inputs_frame, text="Tbiv [°C]:").grid(row=0, column=2, sticky="w", padx=(6, 4))
            ttk.Entry(inputs_frame, textvariable=self.tbiv_vars[clm], width=6).grid(row=0, column=3, sticky="w", padx=(0, 10))

            ttk.Label(inputs_frame, text="TOL [°C]:").grid(row=0, column=4, sticky="w", padx=(6, 4))
            ttk.Entry(inputs_frame, textvariable=self.tol_vars[clm], width=6).grid(row=0, column=5, sticky="w", padx=(0, 6))

            # Table construction
            editable_cells = {}
            for col in ScopTableModel.COL_KEYS:
                for row in ("declared_capacity", "declared_cop", "tested_capacity", "tested_power"):
                    editable_cells[(row, col)] = f"{row}_{col}"

            table = MetricInputTable(
                inner,
                columns=tuple(
                    (col_key, col_key) for col_key in ScopTableModel.COL_KEYS
                ),
                rows=tuple(
                    (row_key, ScopTableModel.ROW_LABELS[row_key])
                    for row_key in ScopTableModel.ROW_KEYS
                ),
                editable_cells=editable_cells,
                section_break_before_rows=ScopTableModel.SECTION_BREAK_BEFORE_ROWS,
            )
            table.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
            table.default_cell_background = lambda pos, c=clm: self._resolve_cell_bg(pos, c)
            self.input_tables[clm] = table

            # Prefill sensible default values
            table.set_values(
                {
                    "declared_capacity_A": "3000",
                    "declared_capacity_B": "3000",
                    "declared_capacity_C": "3000",
                    "declared_capacity_D": "3000",
                    "declared_capacity_TOL": "3000",
                    "declared_capacity_Tbiv": "3000",
                    "declared_cop_A": "2.80",
                    "declared_cop_B": "3.20",
                    "declared_cop_C": "3.60",
                    "declared_cop_D": "4.00",
                    "declared_cop_TOL": "2.20",
                    "declared_cop_Tbiv": "2.80",
                    "tested_capacity_A": "3000",
                    "tested_capacity_B": "3000",
                    "tested_capacity_C": "3000",
                    "tested_capacity_D": "3000",
                    "tested_capacity_TOL": "3000",
                    "tested_capacity_Tbiv": "3000",
                    "tested_power_A": "1070",
                    "tested_power_B": "938",
                    "tested_power_C": "833",
                    "tested_power_D": "750",
                    "tested_power_TOL": "1360",
                    "tested_power_Tbiv": "1070",
                }
            )

            self.table_controllers[clm] = TkTableController(table)

        # 3. Bottom Result Summary Panel
        self.result_panel = ResultPanel(self._frame, title="SCOP 결과")
        self.result_panel.grid(
            row=card_row_start + len(self.climates),
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )

        # 4. Debounced auto-calc scheduler
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        
        # Hook table edits to recalculate
        for table in self.input_tables.values():
            table.set_values_changed_callback(self._auto_calc.schedule)

        # Bind auxiliary changes to scheduler
        for var in (
            self._cd_var,
            self._p_to_var,
            self._p_sb_var,
            self._p_ck_var,
            self._p_off_var,
            self._appliance_type_var,
        ):
            var.trace_add("write", lambda *args: self._auto_calc.schedule())

        for d_vars in (self.p_design_h_vars, self.tbiv_vars, self.tol_vars):
            for var in d_vars.values():
                var.trace_add("write", lambda *args: self._auto_calc.schedule())

        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        
        # Render initial collapse state and calculate
        self._on_climate_toggle()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def cancel_pending(self) -> None:
        self._auto_calc.cancel()

    def _on_climate_toggle(self) -> None:
        """Collapse or expand inner climate tables depending on checkbutton state."""
        for clm in self.climates:
            active = self.climate_active_vars[clm].get()
            inner = self.climate_inner_frames[clm]
            if active:
                inner.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            else:
                inner.pack_forget()

        # Re-trigger calculation and layout refit
        self._auto_calc.schedule()
        if self._on_detail_visibility_changed:
            self._on_detail_visibility_changed()

    def recalculate_now(self) -> None:
        p_to_w = self._parse_float_safe(self._p_to_var.get(), 0.0)
        p_sb_w = self._parse_float_safe(self._p_sb_var.get(), 0.0)
        p_ck_w = self._parse_float_safe(self._p_ck_var.get(), 0.0)
        p_off_w = self._parse_float_safe(self._p_off_var.get(), 0.0)
        cd = self._parse_float_safe(self._cd_var.get(), 0.25)
        appliance_type = self._appliance_type_var.get()

        summaries = []

        for clm in self.climates:
            table = self.input_tables[clm]
            controller = self.table_controllers[clm]
            active = self.climate_active_vars[clm].get()

            if not active:
                self._current_table_models.pop(clm, None)
                continue

            try:
                # 1. Read and validate text values from input matrix
                text_vals = table.get_text_values()
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
                    table.set_invalid_fields(invalid_fields)
                    self._clear_computed_rows(clm)
                    continue
                else:
                    table.clear_invalid_fields()

                # Read climate-specific auxiliary values
                p_design_h_w = self._parse_float_safe(self.p_design_h_vars[clm].get(), 0.0)
                tbiv_temp_c = self._parse_float_safe(self.tbiv_vars[clm].get(), None)
                tol_temp_c = self._parse_float_safe(self.tol_vars[clm].get(), None)

            except Exception:
                self._clear_computed_rows(clm)
                continue

            # Build point inputs
            inputs = {}
            for col in ScopTableModel.COL_KEYS:
                inputs[col] = ScopPointInput(
                    declared_capacity=parsed_vals[f"declared_capacity_{col}"],
                    declared_cop=parsed_vals[f"declared_cop_{col}"],
                    tested_capacity=parsed_vals[f"tested_capacity_{col}"],
                    tested_power=parsed_vals[f"tested_power_{col}"],
                )

            # Resolve effective temperatures
            try:
                eff_tbiv, eff_tol = self.adapter.resolve_temperature_overrides(clm, tbiv_temp_c, tol_temp_c)
                climate_data = self.adapter.get_climate_data(clm)
                t_design_h = float(climate_data["t_design_h_c"])
            except Exception as exc:
                self._clear_computed_rows(clm)
                # Show climate-local status
                summaries.append(
                    ResultSummary(
                        title=f"{clm.upper()} SCOP 결과",
                        fields=(("Climate", clm.capitalize()),),
                        status=f"기류/설정 오류: {str(exc)}",
                    )
                )
                continue

            # Perform calculation
            computed = self.adapter.compute_points(inputs)
            summary = self.adapter.calculate(
                inputs=inputs,
                p_design_h_w=p_design_h_w,
                climate=clm,
                p_to_w=p_to_w,
                p_sb_w=p_sb_w,
                p_ck_w=p_ck_w,
                p_off_w=p_off_w,
                cd=cd,
                appliance_type=appliance_type,
                tbiv_temp_c=tbiv_temp_c,
                tol_temp_c=tol_temp_c,
            )

            # Update column headers dynamically
            table.update_column_header("TOL", f"TOL ({eff_tol:.0f}°C)")
            table.update_column_header("Tbiv", f"Tbiv ({eff_tbiv:.0f}°C)")

            model = ScopTableModel(
                inputs=inputs,
                computed=computed,
                p_design_h_w=p_design_h_w,
                climate=clm,
                t_design_h=t_design_h,
                tbiv_temp_c=eff_tbiv,
                tol_temp_c=eff_tol,
            )
            self._current_table_models[clm] = model

            # Update static cells in table
            for row in ScopTableModel.ROW_KEYS:
                for col in ScopTableModel.COL_KEYS:
                    if not model.is_editable(row, col):
                        val_str = model.get_value(row, col)
                        self._set_static_cell_value(table, (row, col), val_str)

            # Repaint selections and colors
            controller._paint_selection()

            # Add to result summary list
            status_text = STATUS_MAPPINGS.get(summary.status_code, "계산 완료")
            fields = (
                ("기후 (Climate)", clm.capitalize()),
                ("Declared SCOP", f"{summary.declared_scop:.2f}" if summary.declared_scop is not None else "-"),
                ("Tested SCOP", f"{summary.tested_scop:.2f}" if summary.tested_scop is not None else "-"),
                ("SCOP %", f"{summary.scop_percent:.1f}%" if summary.scop_percent is not None else "-"),
                ("Declared QH [kWh]", f"{summary.declared_qh_kwh:.1f}" if summary.declared_qh_kwh is not None else "-"),
                ("Tested QH [kWh]", f"{summary.tested_qh_kwh:.1f}" if summary.tested_qh_kwh is not None else "-"),
                ("Declared Total [kWh]", f"{summary.declared_total_kwh:.1f}" if summary.declared_total_kwh is not None else "-"),
                ("Tested Total [kWh]", f"{summary.tested_total_kwh:.1f}" if summary.tested_total_kwh is not None else "-"),
            )
            summaries.append(
                ResultSummary(
                    title=f"EN14825 SCOP - {clm.capitalize()}",
                    fields=fields,
                    status=status_text,
                )
            )

        if not summaries:
            self.result_panel.clear()
        else:
            self.result_panel.set_summaries(summaries)

    def _parse_float_safe(self, text: str, default: float | None) -> float | None:
        try:
            return float(text.strip().replace(",", ""))
        except ValueError:
            return default

    def _clear_computed_rows(self, climate: str) -> None:
        self._current_table_models.pop(climate, None)
        table = self.input_tables[climate]
        controller = self.table_controllers[climate]
        for row in ScopTableModel.ROW_KEYS:
            for col in ScopTableModel.COL_KEYS:
                is_editable = row in (
                    "declared_capacity",
                    "declared_cop",
                    "tested_capacity",
                    "tested_power",
                )
                if not is_editable:
                    self._set_static_cell_value(table, (row, col), "-")
        controller._paint_selection()

    def _set_static_cell_value(self, table: MetricInputTable, address: tuple[str, str], value: str) -> None:
        label = table.static_cell_labels.get(address)
        if label:
            label.configure(text=value)

    def _resolve_cell_bg(self, position: tuple[int, int], climate: str) -> str:
        table = self.input_tables[climate]
        row, col = table._address_at_position(position)
        model = self._current_table_models.get(climate)
        if model:
            state = model.get_state(row, col)
        else:
            state = "neutral"

        is_editable = table.cell_role(position) == CellRole.EDITABLE
        if state == "invalid":
            return TABLE_INVALID_BG
        elif state == "pass":
            return TABLE_PASS_BG
        elif state == "unavailable":
            return TABLE_STATIC_BG
        else:
            return TABLE_EDITABLE_BG if is_editable else TABLE_STATIC_BG

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
