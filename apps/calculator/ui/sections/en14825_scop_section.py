"""EN14825 SCOP calculation section for Tkinter."""

from __future__ import annotations

from collections.abc import Callable, Mapping
import tkinter as tk
from tkinter import ttk

from apps.calculator.application.en14825 import ScopAdapter
from apps.calculator.application.en14825.scop_models import (
    ScopResultSummary,
)
from apps.calculator.ui.en14825 import (
    ScopTableModel,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch_dialogs.profiles.en14825_scop_dialog import (
    En14825ScopBatchDialog,
)
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.en14825.scop_batch_session import En14825ScopBatchSnapshot
from apps.calculator.ui.result_panel import ResultPanel
from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from apps.calculator.ui.sections.bin_detail_schema import (
    EN14825_SCOP_BIN_DETAIL_SCHEMA,
)
from apps.calculator.ui.sections.detail_visibility import DetailPanelVisibility
from apps.calculator.ui.sections.en14825_scop_detail import format_scop_bin_details
from apps.calculator.ui.sections.en14825_scop_input_mapper import build_scop_point_inputs
from apps.calculator.ui.sections.en14825_scop_result_formatter import (
    format_scop_climate_error_summary,
    format_scop_result_summary,
)
from apps.calculator.ui.sections.en14825_scop_result_surface import ScopResultSurface
from apps.calculator.ui.layout_constants import (
    BATCH_INPUT_BUTTON_TEXT,
    CONTROL_APPLIANCE_TYPE_SELECTOR_WIDTH_CHARS,
    CONTROL_GROUP_GAP,
    CONTROL_LABEL_GAP,
    CONTROL_ROW_PADY,
    METRIC_TABLE_COMPACT_ROW_HEADER_CHARS,
    METRIC_TABLE_DECLARED_DATA_COLUMN_CHARS,
    METRIC_TABLE_EN14825_ROW_HEADER_CHARS,
    METRIC_TABLE_STANDARD_DATA_COLUMN_CHARS,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)


class En14825ScopSection:
    """EN14825 SCOP stacked climate card tables, auxiliary inputs, and result summary panel."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_trace_visibility_changed: Callable[[], None] | None = None,
        common_input_values: Callable[[], Mapping[str, str]] | None = None,
    ) -> None:
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self._common_input_values = common_input_values or (
            lambda: {
                "p_to": "0",
                "p_sb": "0",
                "p_ck": "0",
                "p_off": "0",
            }
        )
        self.adapter = ScopAdapter()
        self._current_table_models: dict[str, ScopTableModel] = {}
        self._batch_handle: BatchDialogHandle[
            En14825ScopBatchSnapshot, En14825ScopBatchDialog
        ] = BatchDialogHandle()
        self._detail_sources: dict[str, BinDetailSource] = {}
        self._detail_status = "입력 대기"

        self._frame = ttk.LabelFrame(parent, text="SCOP")
        self._frame.columnconfigure(0, weight=1)

        # 1. Top Auxiliary Parameters Frame
        self._cd_var = tk.StringVar(master=self._frame, value="0.25")
        self._appliance_type_var = tk.StringVar(
            master=self._frame,
            value="reversible",
        )
        self._syncing_aux_inputs = False

        aux_frame = ttk.Frame(self._frame)
        aux_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, ISO_SECTION_BLOCK_GAP),
        )

        # Specs Frame (Cd)
        specs_frame = ttk.LabelFrame(aux_frame, text="설계 사양")
        specs_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, CONTROL_GROUP_GAP))
        specs_frame.columnconfigure(0, weight=0)
        self.cd_table = MetricInputTable(
            specs_frame,
            columns=(("cd", "Cd"),),
            rows=(("design", "입력값"),),
            editable_cells={("design", "cd"): "cd"},
            row_header_chars=METRIC_TABLE_COMPACT_ROW_HEADER_CHARS,
            data_column_chars=METRIC_TABLE_DECLARED_DATA_COLUMN_CHARS,
            layout_policy="content_hug",
        )
        self.cd_table.grid(
            row=0, column=0, sticky="w",
            padx=CONTROL_ROW_PADY, pady=CONTROL_ROW_PADY,
        )
        self.cd_table.set_values({"cd": self._cd_var.get()})
        self.cd_controller = TkTableController(self.cd_table)
        self.appliance_type_label = ttk.Label(specs_frame, text="Type")
        self.appliance_type_label.grid(
            row=0, column=1, sticky="w",
            padx=(CONTROL_GROUP_GAP, CONTROL_LABEL_GAP), pady=CONTROL_ROW_PADY,
        )
        self.appliance_type_selector = ttk.Combobox(
            specs_frame,
            textvariable=self._appliance_type_var,
            values=("reversible", "heating_only"),
            width=CONTROL_APPLIANCE_TYPE_SELECTOR_WIDTH_CHARS,
            state="readonly",
        )
        self.appliance_type_selector.grid(
            row=0, column=2, sticky="w",
            padx=(0, CONTROL_ROW_PADY), pady=CONTROL_ROW_PADY,
        )

        # 2. Stacked Climate Cards
        self.climates = ("average", "warmer", "colder")
        self.climate_cards: dict[str, ttk.LabelFrame] = {}
        self.climate_active_vars: dict[str, tk.BooleanVar] = {}
        self.climate_inner_frames: dict[str, ttk.Frame] = {}
        self.t_design_h_value_labels: dict[str, ttk.Label] = {}

        # Climate-specific vars
        self.p_design_h_vars: dict[str, tk.StringVar] = {
            "average": tk.StringVar(master=self._frame, value=""),
            "warmer": tk.StringVar(master=self._frame, value=""),
            "colder": tk.StringVar(master=self._frame, value=""),
        }
        self.tbiv_vars: dict[str, tk.StringVar] = {
            "average": tk.StringVar(master=self._frame, value="-10"),
            "warmer": tk.StringVar(master=self._frame, value="2"),
            "colder": tk.StringVar(master=self._frame, value="-15"),
        }
        self.tol_vars: dict[str, tk.StringVar] = {
            "average": tk.StringVar(master=self._frame, value="-11"),
            "warmer": tk.StringVar(master=self._frame, value="-11"),
            "colder": tk.StringVar(master=self._frame, value="-22"),
        }

        self.input_tables: dict[str, MetricInputTable] = {}
        self.table_controllers: dict[str, TkTableController] = {}
        self.climate_input_tables: dict[str, MetricInputTable] = {}
        self.climate_input_controllers: dict[str, TkTableController] = {}
        self._result_surfaces: dict[str, ScopResultSurface] = {}
        self._result_cards: dict[str, tk.Frame] = {}
        self._result_value_labels: dict[str, dict[tuple[str, str], tk.Label]] = {}

        card_row_start = 2
        for i, clm in enumerate(self.climates):
            # LabelFrame for climate
            card = ttk.LabelFrame(self._frame, text=f"{clm.capitalize()} 조건")
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

            active_var = tk.BooleanVar(
                master=self._frame,
                value=(clm == "average"),
            )
            self.climate_active_vars[clm] = active_var

            chk = ttk.Checkbutton(
                toggle_frame,
                text="활성화",
                variable=active_var,
                command=self._on_climate_toggle,
            )
            chk.pack(side=tk.LEFT)

            # Inner frame containing the actual tables and inputs
            inner = ttk.Frame(card)
            inner.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            self.climate_inner_frames[clm] = inner

            body = ttk.Frame(inner)
            body.pack(fill=tk.BOTH, expand=True)
            body.columnconfigure(0, weight=0)
            body.columnconfigure(1, weight=0)
            body.rowconfigure(1, weight=0)

            # Setup climate specific auxiliary inputs
            inputs_frame = ttk.Frame(body)
            inputs_frame.grid(row=0, column=0, sticky="w", pady=(0, 6))
            inputs_frame.columnconfigure(0, weight=0)

            climate_table = MetricInputTable(
                inputs_frame,
                columns=(
                    ("p_design_h", "Pdesignh [W]"),
                    ("tbiv", "Tbiv [°C]"),
                    ("tol", "TOL [°C]"),
                ),
                rows=(("design", "입력값"),),
                editable_cells={
                    ("design", "p_design_h"): "p_design_h",
                    ("design", "tbiv"): "tbiv",
                    ("design", "tol"): "tol",
                },
                row_header_chars=METRIC_TABLE_COMPACT_ROW_HEADER_CHARS,
                data_column_chars=METRIC_TABLE_STANDARD_DATA_COLUMN_CHARS,
                layout_policy="content_hug",
            )
            climate_table.grid(row=0, column=0, sticky="w", padx=(6, 10))
            climate_table.set_values(self._climate_aux_values(clm))
            self.climate_input_tables[clm] = climate_table
            self.climate_input_controllers[clm] = TkTableController(climate_table)

            ttk.Label(inputs_frame, text="Tdesignh [°C]:").grid(row=0, column=1, sticky="w", padx=(6, 4))
            t_design_label = ttk.Label(inputs_frame, text=self._format_t_design_h(clm), width=6)
            t_design_label.grid(row=0, column=2, sticky="w", padx=(0, 6))
            self.t_design_h_value_labels[clm] = t_design_label

            # Table construction
            editable_cells = {}
            for col in ScopTableModel.COL_KEYS:
                for row in ("declared_capacity", "declared_cop", "tested_capacity", "tested_power"):
                    editable_cells[(row, col)] = f"{row}_{col}"

            table = MetricInputTable(
                body,
                columns=tuple(
                    (col_key, col_key) for col_key in ScopTableModel.COL_KEYS
                ),
                rows=tuple(
                    (row_key, ScopTableModel.ROW_LABELS[row_key])
                    for row_key in ScopTableModel.ROW_KEYS
                ),
                editable_cells=editable_cells,
                row_header_chars=METRIC_TABLE_EN14825_ROW_HEADER_CHARS,
                section_break_before_rows=ScopTableModel.SECTION_BREAK_BEFORE_ROWS,
            )
            table.grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(0, 6))
            table.default_cell_background = lambda pos, c=clm: self._resolve_cell_bg(pos, c)
            self.input_tables[clm] = table

            self.table_controllers[clm] = TkTableController(table)

            result_surface = ScopResultSurface(body)
            result_surface.grid(row=1, column=1, sticky="ne", padx=(0, 2), pady=(0, 6))
            self._result_surfaces[clm] = result_surface
            self._result_cards[clm] = result_surface.frame
            self._result_value_labels[clm] = result_surface.value_labels

        # Compatibility text model for existing non-layout tests.
        self.result_panel = ResultPanel(self._frame, title="SCOP 결과")

        action_row = ttk.Frame(self._frame)
        action_row.grid(
            row=5, column=0, sticky="w", padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.batch_button = ttk.Button(
            action_row,
            text=BATCH_INPUT_BUTTON_TEXT,
            command=self._open_batch_dialog,
        )
        self.batch_button.surface_role = "en14825_scop_batch_open"
        self.batch_button.pack(side=tk.LEFT)
        self.detail_toggle = ttk.Button(
            action_row,
            text="상세 보기 ↓",
            command=self._toggle_detail,
        )
        self.detail_toggle.surface_role = "en14825_scop_detail_toggle"
        self.detail_toggle.pack(side=tk.LEFT, padx=(ISO_SECTION_BLOCK_GAP, 0))
        source_labels = tuple(
            f"{climate.capitalize()} {dataset}"
            for climate in self.climates
            for dataset in ("Declared", "Tested")
        )
        self.detail_panel = BinDetailPanel(
            self._frame,
            source_labels=source_labels,
            default_source=source_labels[0],
            csv_filename="en14825_scop_bin_detail.csv",
            schema=EN14825_SCOP_BIN_DETAIL_SCHEMA,
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
        
        # Hook table edits to recalculate
        for table in self.input_tables.values():
            table.set_values_changed_callback(self._auto_calc.schedule)
        self.cd_table.set_values_changed_callback(self._on_cd_table_values_changed)
        for clm, table in self.climate_input_tables.items():
            table.set_values_changed_callback(
                lambda clm=clm: self._on_climate_table_values_changed(clm)
            )

        # Bind auxiliary changes to scheduler
        self._cd_var.trace_add("write", lambda *args: self._on_cd_var_changed())
        self._appliance_type_var.trace_add(
            "write", lambda *args: self._auto_calc.schedule()
        )

        for d_vars in (self.p_design_h_vars, self.tbiv_vars, self.tol_vars):
            for clm, var in d_vars.items():
                var.trace_add(
                    "write",
                    lambda *args, clm=clm: self._on_climate_var_changed(clm),
                )

        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        
        # Render initial collapse state and calculate
        self._on_climate_toggle()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def cancel_pending(self) -> None:
        self._auto_calc.cancel()

    def schedule_recalculate(self) -> None:
        self._auto_calc.schedule()

    @property
    def _batch_dialog(self) -> En14825ScopBatchDialog | None:
        return self._ensure_batch_handle().dialog

    @_batch_dialog.setter
    def _batch_dialog(self, dialog: En14825ScopBatchDialog | None) -> None:
        self._ensure_batch_handle().dialog = dialog

    @property
    def _batch_snapshot(self) -> En14825ScopBatchSnapshot | None:
        return self._ensure_batch_handle().snapshot

    @_batch_snapshot.setter
    def _batch_snapshot(self, snapshot: En14825ScopBatchSnapshot | None) -> None:
        self._ensure_batch_handle().snapshot = snapshot

    def _ensure_batch_handle(
        self,
    ) -> BatchDialogHandle[En14825ScopBatchSnapshot, En14825ScopBatchDialog]:
        if not hasattr(self, "_batch_handle"):
            self._batch_handle = BatchDialogHandle()
        return self._batch_handle

    def _open_batch_dialog(self) -> None:
        self._batch_handle.open_or_focus(
            lambda: En14825ScopBatchDialog(
                self._frame.winfo_toplevel(),
                initial_snapshot=self._batch_handle.snapshot,
                on_close=self._clear_batch_dialog,
            )
        )

    def _clear_batch_dialog(
        self,
        snapshot: En14825ScopBatchSnapshot | None = None,
    ) -> None:
        self._batch_handle.clear(snapshot)

    def _climate_aux_values(self, climate: str) -> dict[str, str]:
        return {
            "p_design_h": self.p_design_h_vars[climate].get(),
            "tbiv": self.tbiv_vars[climate].get(),
            "tol": self.tol_vars[climate].get(),
        }

    def _on_cd_var_changed(self) -> None:
        if not self._syncing_aux_inputs:
            self.cd_table.set_values_batch({"cd": self._cd_var.get()})
        self._auto_calc.schedule()

    def _on_cd_table_values_changed(self) -> None:
        if self._syncing_aux_inputs:
            return
        value = self.cd_table.get_text_values().get("cd", self._cd_var.get())
        self._syncing_aux_inputs = True
        try:
            if self._cd_var.get() != value:
                self._cd_var.set(value)
        finally:
            self._syncing_aux_inputs = False
        self._auto_calc.schedule()

    def _on_climate_var_changed(self, climate: str) -> None:
        if not self._syncing_aux_inputs:
            self.climate_input_tables[climate].set_values_batch(
                self._climate_aux_values(climate)
            )
        self._auto_calc.schedule()

    def _on_climate_table_values_changed(self, climate: str) -> None:
        if self._syncing_aux_inputs:
            return
        values = self.climate_input_tables[climate].get_text_values()
        var_by_key = {
            "p_design_h": self.p_design_h_vars[climate],
            "tbiv": self.tbiv_vars[climate],
            "tol": self.tol_vars[climate],
        }
        self._syncing_aux_inputs = True
        try:
            for key, var in var_by_key.items():
                value = values.get(key, var.get())
                if var.get() != value:
                    var.set(value)
        finally:
            self._syncing_aux_inputs = False
        self._auto_calc.schedule()

    def _on_climate_toggle(self) -> None:
        """Collapse or expand inner climate tables depending on checkbutton state."""
        for clm in self.climates:
            active = self.climate_active_vars[clm].get()
            inner = self.climate_inner_frames[clm]
            if active:
                inner.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
                self._set_result_card_visible(clm, True)
            else:
                inner.pack_forget()
                self._set_result_card_visible(clm, False)

        # Re-trigger calculation and layout refit
        self._auto_calc.schedule()
        if self._on_detail_visibility_changed:
            self._on_detail_visibility_changed()

    def recalculate_now(self) -> None:
        common_inputs = self._common_input_values()
        p_to_w = self._parse_float_safe(common_inputs.get("p_to", "0"), 0.0)
        p_sb_w = self._parse_float_safe(common_inputs.get("p_sb", "0"), 0.0)
        p_ck_w = self._parse_float_safe(common_inputs.get("p_ck", "0"), 0.0)
        p_off_w = self._parse_float_safe(common_inputs.get("p_off", "0"), 0.0)
        cd = self._parse_float_safe(self._cd_var.get(), 0.25)
        appliance_type = self._appliance_type_var.get()

        summaries = []
        detail_sources: dict[str, BinDetailSource] = {}
        detail_errors: list[str] = []

        for clm in self.climates:
            table = self.input_tables[clm]
            controller = self.table_controllers[clm]
            active = self.climate_active_vars[clm].get()

            if not active:
                self._current_table_models.pop(clm, None)
                self._set_result_card_visible(clm, False)
                continue

            try:
                # Read climate-specific auxiliary values first so point availability
                # can blank/lock cells before text parsing.
                p_design_h_w = self._parse_float_safe(self.p_design_h_vars[clm].get(), 0.0)
                tbiv_temp_c = self._parse_float_safe(self.tbiv_vars[clm].get(), None)
                tol_temp_c = self._parse_float_safe(self.tol_vars[clm].get(), None)
                eff_tbiv, eff_tol = self.adapter.resolve_temperature_overrides(clm, tbiv_temp_c, tol_temp_c)
                climate_data = self.adapter.get_climate_data(clm)
                t_design_h = float(climate_data["t_design_h_c"])
                point_availability = self.adapter.resolve_point_availability(clm, eff_tbiv, eff_tol)
                if self._apply_point_availability(table, point_availability):
                    controller.refresh()

                # 1. Read and validate text values from input matrix
                input_mapping = build_scop_point_inputs(table.get_text_values())

                if input_mapping.invalid_fields:
                    table.set_invalid_fields(input_mapping.invalid_fields)
                    self._clear_computed_rows(clm)
                    self._clear_result_card(clm)
                    detail_errors.append("입력 오류: 숫자 입력을 확인하세요.")
                    continue
                else:
                    table.clear_invalid_fields()

            except Exception:
                self._clear_computed_rows(clm)
                self._clear_result_card(clm)
                detail_errors.append("입력 대기: 기류/설정을 확인하세요.")
                continue

            inputs = input_mapping.inputs

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

            model = ScopTableModel(
                inputs=inputs,
                computed=computed,
                p_design_h_w=p_design_h_w,
                climate=clm,
                t_design_h=t_design_h,
                tbiv_temp_c=eff_tbiv,
                tol_temp_c=eff_tol,
                point_availability=point_availability,
            )
            self._current_table_models[clm] = model

            # Update column headers dynamically
            for col in ScopTableModel.COL_KEYS:
                table.update_column_header(col, model.get_col_label(col))

            # Update static cells in table
            for row in ScopTableModel.ROW_KEYS:
                for col in ScopTableModel.COL_KEYS:
                    if not model.is_editable(row, col):
                        val_str = model.get_value(row, col)
                        self._set_static_cell_value(table, (row, col), val_str)

            # Repaint selections and colors
            controller._paint_selection()

            # Add to result summary list
            self._update_result_card(clm, summary)
            summaries.append(format_scop_result_summary(summary, clm))
            self._collect_detail_sources(detail_sources, clm, summary)
            if summary.status_code != "complete" and summary.message:
                detail_errors.append(summary.message)

        if not summaries:
            self.result_panel.clear()
        else:
            self.result_panel.set_summaries(summaries)
        self._set_detail_state(detail_sources, detail_errors)

    def _collect_detail_sources(
        self,
        sources: dict[str, BinDetailSource],
        climate: str,
        summary: ScopResultSummary,
    ) -> None:
        for dataset, rows in (
            ("Declared", summary.declared_bin_details),
            ("Tested", summary.tested_bin_details),
        ):
            formatted_rows = format_scop_bin_details(rows)
            if formatted_rows:
                label = f"{climate.capitalize()} {dataset}"
                sources[label] = BinDetailSource(rows=formatted_rows)

    def _set_detail_state(
        self,
        sources: dict[str, BinDetailSource],
        errors: list[str],
    ) -> None:
        self._detail_sources = dict(sources)
        if sources:
            self._detail_status = "상세 데이터 없음"
            self.detail_panel.set_sources(
                sources,
                source_order=tuple(sources),
                panel_status=self._detail_status,
            )
            return
        self._detail_status = errors[0] if errors else "입력 대기"
        self.detail_panel.set_status(self._detail_status)

    def _toggle_detail(self) -> None:
        self._detail_visibility.toggle()

    def _format_t_design_h(self, climate: str) -> str:
        try:
            return f"{float(self.adapter.get_climate_data(climate)['t_design_h_c']):.0f}"
        except Exception:
            return "-"

    def _set_result_card_visible(self, climate: str, visible: bool) -> None:
        if visible:
            self._result_surfaces[climate].show()
        else:
            self._result_surfaces[climate].hide()

    def _update_result_card(self, climate: str, summary) -> None:
        self._result_surfaces[climate].update(summary)

    def _show_result_card_error(self, climate: str, message: str) -> None:
        self._result_surfaces[climate].show_error(message)

    def _clear_result_card(self, climate: str) -> None:
        self._result_surfaces[climate].clear()

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

    def _apply_point_availability(self, table: MetricInputTable, point_availability: dict) -> bool:
        input_rows = ("declared_capacity", "declared_cop", "tested_capacity", "tested_power")
        unavailable_addresses = {
            (row, col)
            for col, meta in point_availability.get("points", {}).items()
            if meta.get("state") != "required"
            for row in input_rows
        }

        blank_values = {}
        for address in unavailable_addresses:
            field_key = table.field_key_for_address(address)
            if field_key is not None:
                blank_values[field_key] = ""
        if blank_values:
            table.set_values_batch(blank_values)

        return table.set_readonly_addresses(
            unavailable_addresses,
            display_values={address: "" for address in unavailable_addresses},
        )

    def _resolve_cell_bg(self, position: tuple[int, int], climate: str) -> str:
        table = self.input_tables[climate]
        row, col = table._address_at_position(position)
        model = self._current_table_models.get(climate)
        if model:
            state = model.get_state(row, col)
        else:
            state = "neutral"

        return table.role_cell_background(
            position,
            invalid=state == "invalid",
        )

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
            self._batch_handle.dispose()
