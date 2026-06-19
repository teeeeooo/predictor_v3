"""EN14825 SCOP dynamic batch dialog profile."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch.matrix_models import BatchMatrixSpec
from apps.calculator.ui.batch.matrix_table import BatchMatrixTable
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.en14825.scop_adapter import ScopAdapter
from apps.calculator.ui.en14825.scop_batch import (
    En14825ScopBatchCommonInputs,
    En14825ScopBatchHandler,
    build_en14825_scop_batch_spec,
)
from apps.calculator.ui.en14825.scop_batch_session import (
    En14825ScopBatchActiveConditions,
    En14825ScopBatchSessionState,
    En14825ScopBatchSnapshot,
)
from apps.calculator.ui.layout_constants import ISO_SECTION_BLOCK_GAP, ISO_SECTION_PADX
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table_csv_export import export_table_to_csv
from apps.calculator.ui.table_grid_model import parse_numeric_cell

__all__ = ["En14825ScopBatchSection"]

_DEFAULT_ACTIVE = En14825ScopBatchActiveConditions("average", -10.0, -11.0)
_DEFAULT_COMMON = {
    "climate": "average",
    "tbiv_temp_c": "-10",
    "tol_temp_c": "-11",
    "cd": "0.25",
    "appliance_type": "reversible",
    "p_to_w": "0",
    "p_sb_w": "0",
    "p_ck_w": "0",
    "p_off_w": "0",
}
_AUX_FIELDS = (
    ("cd", "Cd"),
    ("p_to_w", "Pto [W]"),
    ("p_sb_w", "Psb [W]"),
    ("p_ck_w", "Pck [W]"),
    ("p_off_w", "Poff [W]"),
)


class En14825ScopBatchSection:
    """SCOP draft conditions, dynamic matrix, actions, and compact status."""

    result_panel = None

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: En14825ScopBatchSnapshot | None = None,
        adapter: ScopAdapter | None = None,
    ) -> None:
        self._adapter = adapter if adapter is not None else ScopAdapter()
        active = initial_snapshot.active_conditions if initial_snapshot else _DEFAULT_ACTIVE
        cases = initial_snapshot.cases if initial_snapshot else ()
        self._session = En14825ScopBatchSessionState(active, cases)
        values = dict(_DEFAULT_COMMON)
        if initial_snapshot is not None:
            values.update(initial_snapshot.common_values)
        self._frame = ttk.LabelFrame(parent, text="EN14825 SCOP Batch")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(1, weight=1)
        self._vars = {
            key: tk.StringVar(master=self._frame, value=value)
            for key, value in values.items()
        }
        self.status_var = tk.StringVar(master=self._frame, value="")
        self._build_common_inputs()
        self._table_host = ttk.Frame(self._frame)
        self._table_host.grid(row=1, column=0, sticky="nsew", padx=ISO_SECTION_PADX, pady=6)
        self._table_host.columnconfigure(0, weight=1)
        self._table_host.rowconfigure(0, weight=1)
        spec = self._build_spec(active)
        self._create_table(spec)
        self._auto_calc = DebouncedAutoCalc(self._frame, self._recalculate_now, delay_ms=150)
        self.table.set_values_changed_callback(self._auto_calc.schedule)
        for key in ("climate", "tbiv_temp_c", "tol_temp_c"):
            self._vars[key].trace_add("write", self._on_condition_draft_changed)
        for key in ("cd", "appliance_type", "p_to_w", "p_sb_w", "p_ck_w", "p_off_w"):
            self._vars[key].trace_add("write", lambda *_args: self._auto_calc.schedule())
        self._build_actions()
        self._auto_calc.flush_now()

    def _build_common_inputs(self) -> None:
        frame = ttk.LabelFrame(self._frame, text="Common Inputs")
        frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 0),
        )
        condition_fields = (
            ("climate", "Climate"),
            ("tbiv_temp_c", "Tbiv [°C]"),
            ("tol_temp_c", "TOL [°C]"),
        )
        for column, (key, label) in enumerate(condition_fields):
            ttk.Label(frame, text=label).grid(row=0, column=column, padx=3, pady=(4, 2))
            if key == "climate":
                widget = ttk.Combobox(
                    frame,
                    textvariable=self._vars[key],
                    values=("average", "warmer", "colder"),
                    state="readonly",
                    width=10,
                )
            else:
                widget = ttk.Entry(frame, textvariable=self._vars[key], width=10)
            widget.grid(row=1, column=column, padx=3, pady=(0, 4))
        ttk.Button(
            frame,
            text="Apply Conditions",
            command=self._apply_conditions,
        ).grid(row=1, column=3, padx=(6, 12), pady=(0, 4))
        for offset, (key, label) in enumerate(_AUX_FIELDS, start=4):
            ttk.Label(frame, text=label).grid(row=0, column=offset, padx=3, pady=(4, 2))
            ttk.Entry(frame, textvariable=self._vars[key], width=9).grid(
                row=1,
                column=offset,
                padx=3,
                pady=(0, 4),
            )
        type_column = 4 + len(_AUX_FIELDS)
        ttk.Label(frame, text="Type").grid(row=0, column=type_column, padx=3, pady=(4, 2))
        ttk.Combobox(
            frame,
            textvariable=self._vars["appliance_type"],
            values=("reversible",),
            state="readonly",
            width=11,
        ).grid(row=1, column=type_column, padx=3, pady=(0, 4))

    def _build_actions(self) -> None:
        row = ttk.Frame(self._frame)
        row.grid(
            row=2,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        for label, command in (
            ("Add Case", self._add_case),
            ("Remove Case", self._remove_case),
            ("Copy All", self.table.copy_all),
            ("Export CSV", self._export_csv),
        ):
            ttk.Button(row, text=label, command=command).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Label(row, textvariable=self.status_var).pack(side=tk.LEFT, padx=(6, 0))

    def _build_spec(self, conditions: En14825ScopBatchActiveConditions) -> BatchMatrixSpec:
        return build_en14825_scop_batch_spec(
            conditions.climate,
            conditions.tbiv_temp_c,
            conditions.tol_temp_c,
            adapter=self._adapter,
        )

    def _create_table(self, spec: BatchMatrixSpec) -> None:
        self.table = BatchMatrixTable(self._table_host, spec)
        self.table.grid(row=0, column=0, sticky="nsew")
        self.table.interaction_controller = TkTableController(self.table)
        self.table.restore_snapshot(self._session.visible_cases(spec))

    def _replace_table(self, spec: BatchMatrixSpec) -> None:
        self.table.destroy()
        self._create_table(spec)
        self.table.set_values_changed_callback(self._auto_calc.schedule)

    def common_values(self) -> dict[str, str]:
        return {key: variable.get() for key, variable in self._vars.items()}

    def snapshot(self) -> En14825ScopBatchSnapshot:
        self._merge_visible_inputs_to_store()
        return self._session.snapshot(self.common_values())

    def dispose(self) -> None:
        self._auto_calc.dispose()

    def _draft_conditions(self) -> En14825ScopBatchActiveConditions:
        climate = self._vars["climate"].get().strip().lower()
        tbiv = parse_numeric_cell(self._vars["tbiv_temp_c"].get())
        tol = parse_numeric_cell(self._vars["tol_temp_c"].get())
        if tol > tbiv:
            raise ValueError("TOL must be less than or equal to Tbiv")
        return En14825ScopBatchActiveConditions(climate, tbiv, tol)

    def _on_condition_draft_changed(self, *_args: object) -> None:
        self._set_draft_status()

    def _set_draft_status(self) -> bool:
        try:
            changed = self._draft_conditions() != self._session.active_conditions
        except (TypeError, ValueError):
            self.status_var.set("Condition inputs invalid")
            return True
        if changed:
            self.status_var.set("Conditions changed - apply to update matrix")
        return changed

    def _apply_conditions(self) -> None:
        try:
            draft = self._draft_conditions()
        except (TypeError, ValueError):
            self.status_var.set("Condition inputs invalid")
            return
        try:
            spec = self._build_spec(draft)
        except Exception:
            self.status_var.set("Condition contract unavailable")
            return
        self._merge_visible_inputs_to_store()
        self._session.set_active_conditions(draft)
        self._replace_table(spec)
        self._auto_calc.flush_now()

    def _merge_visible_inputs_to_store(self) -> None:
        self._session.sync_visible_cases(self.table.cases, self.table.spec.input_keys)

    def _add_case(self) -> None:
        self._merge_visible_inputs_to_store()
        self._session.add_case()
        self.table.restore_snapshot(self._session.visible_cases(self.table.spec))
        self._auto_calc.schedule()

    def _remove_case(self) -> None:
        self._merge_visible_inputs_to_store()
        self._session.remove_case()
        self.table.restore_snapshot(self._session.visible_cases(self.table.spec))
        self._auto_calc.schedule()

    def _common_inputs(self) -> En14825ScopBatchCommonInputs:
        active = self._session.active_conditions
        return En14825ScopBatchCommonInputs(
            climate=active.climate,
            tbiv_temp_c=active.tbiv_temp_c,
            tol_temp_c=active.tol_temp_c,
            cd=parse_numeric_cell(self._vars["cd"].get()),
            appliance_type=self._vars["appliance_type"].get(),
            p_to_w=parse_numeric_cell(self._vars["p_to_w"].get()),
            p_sb_w=parse_numeric_cell(self._vars["p_sb_w"].get()),
            p_ck_w=parse_numeric_cell(self._vars["p_ck_w"].get()),
            p_off_w=parse_numeric_cell(self._vars["p_off_w"].get()),
        )

    def _recalculate_now(self) -> None:
        try:
            handler = En14825ScopBatchHandler(self._common_inputs(), adapter=self._adapter)
        except (TypeError, ValueError):
            self.table.clear_results()
            self.status_var.set("Common inputs invalid")
            return
        valid = pending = errors = 0
        for index, case in enumerate(self.table.cases):
            result = handler.calculate_row(case)
            self.table.set_result(index, result.values)
            if result.state is BatchRowState.OK:
                valid += 1
            elif result.state is BatchRowState.ERROR:
                errors += 1
            else:
                pending += 1
        if self._set_draft_status():
            return
        self.status_var.set(
            f"{valid} valid / {pending} pending"
            + (f" / {errors} invalid" if errors else "")
        )

    def _export_csv(self) -> None:
        headers, rows = self.table.table_export_data()
        export_table_to_csv(self._frame, "en14825_scop_batch.csv", headers, rows)
