"""AHRI HSPF2 dynamic batch dialog profile section."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.ahri.hspf2_batch import (
    AhriHspf2BatchActiveOptions,
    AhriHspf2BatchCommonInputs,
    AhriHspf2BatchHandler,
    build_ahri_hspf2_batch_spec,
)
from apps.calculator.ui.ahri.hspf2_batch_session import (
    AhriHspf2BatchSessionState,
    AhriHspf2BatchSnapshot,
)
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch.matrix_models import BatchMatrixSpec
from apps.calculator.ui.batch.matrix_table import BatchMatrixTable
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.layout_constants import ISO_SECTION_BLOCK_GAP, ISO_SECTION_PADX
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table_csv_export import export_table_to_csv

_DEFAULT_ACTIVE = AhriHspf2BatchActiveOptions()
_DEFAULT_COMMON = {
    "region": "IV",
    "h42_enabled": "1",
    "h12_enabled": "0",
    "h22_enabled": "0",
    "h1n_h32_same_hz": "0",
    "min_spd": "1",
    "cd": "0.25",
    "defrost_credit": "1.0",
    "cut_out_c": "-40.0",
    "cut_in_c": "-40.0",
}
_NUMERIC_FIELDS = (
    ("cd", "Cd"),
    ("defrost_credit", "Defrost Credit"),
    ("cut_out_c", "Cut Out [°C]"),
    ("cut_in_c", "Cut In [°C]"),
)


class AhriHspf2BatchSection:
    """Draft options, dynamic matrix, superset state, and automatic results."""

    result_panel = None

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: AhriHspf2BatchSnapshot | None = None,
    ) -> None:
        active = initial_snapshot.active_options if initial_snapshot else _DEFAULT_ACTIVE
        cases = initial_snapshot.cases if initial_snapshot else ()
        self._session = AhriHspf2BatchSessionState(active, cases)
        values = dict(_DEFAULT_COMMON)
        if initial_snapshot is not None:
            values.update(initial_snapshot.common_values)
        self._frame = ttk.LabelFrame(parent, text="AHRI 210/240 HSPF2 Batch")
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
        self._create_table(build_ahri_hspf2_batch_spec(active))
        self._auto_calc = DebouncedAutoCalc(self._frame, self._recalculate_now, delay_ms=150)
        self.table.set_values_changed_callback(self._auto_calc.schedule)
        for key in ("region", "h42_enabled", "h12_enabled", "h22_enabled"):
            self._vars[key].trace_add("write", self._on_option_draft_changed)
        for key in ("h1n_h32_same_hz", "min_spd", *dict(_NUMERIC_FIELDS)):
            self._vars[key].trace_add("write", lambda *_args: self._auto_calc.schedule())
        self._build_actions()
        self._auto_calc.flush_now()

    def _build_common_inputs(self) -> None:
        frame = ttk.LabelFrame(self._frame, text="Common Inputs")
        frame.grid(row=0, column=0, sticky="ew", padx=ISO_SECTION_PADX,
                   pady=(ISO_SECTION_BLOCK_GAP, 0))
        ttk.Label(frame, text="Region").grid(row=0, column=0, padx=3, pady=(4, 2))
        ttk.Combobox(frame, textvariable=self._vars["region"], values=("IV",),
                     state="readonly", width=5).grid(row=1, column=0, padx=3, pady=(0, 4))
        column = 1
        for key, label in (
            ("h42_enabled", "H42"), ("h12_enabled", "H12"),
            ("h22_enabled", "H22"), ("h1n_h32_same_hz", "H1N=H32 Hz"),
            ("min_spd", "MinSpd"),
        ):
            ttk.Checkbutton(frame, text=label, variable=self._vars[key],
                            onvalue="1", offvalue="0").grid(
                row=1, column=column, padx=3, pady=(0, 4)
            )
            column += 1
        ttk.Button(frame, text="Apply Options", command=self._apply_options).grid(
            row=1, column=column, padx=(6, 12), pady=(0, 4)
        )
        column += 1
        for key, label in _NUMERIC_FIELDS:
            ttk.Label(frame, text=label).grid(row=0, column=column, padx=3, pady=(4, 2))
            ttk.Entry(frame, textvariable=self._vars[key], width=10).grid(
                row=1, column=column, padx=3, pady=(0, 4)
            )
            column += 1

    def _build_actions(self) -> None:
        row = ttk.Frame(self._frame)
        row.grid(row=2, column=0, sticky="w", padx=ISO_SECTION_PADX,
                 pady=(0, ISO_SECTION_BLOCK_GAP))
        for label, command in (
            ("Add Case", self._add_case), ("Remove Case", self._remove_case),
            ("Copy All", self.table.copy_all), ("Export CSV", self._export_csv),
        ):
            ttk.Button(row, text=label, command=command).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Label(row, textvariable=self.status_var).pack(side=tk.LEFT, padx=(6, 0))

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

    def snapshot(self) -> AhriHspf2BatchSnapshot:
        self._merge_visible_inputs_to_store()
        return self._session.snapshot(self.common_values())

    def dispose(self) -> None:
        self._auto_calc.dispose()

    @staticmethod
    def _parse_bool(value: str) -> bool:
        if value == "1":
            return True
        if value == "0":
            return False
        raise ValueError("boolean option must be 0 or 1")

    def _draft_active_options(self) -> AhriHspf2BatchActiveOptions:
        region = self._vars["region"].get().strip()
        if region != "IV":
            raise ValueError("Region IV required")
        return AhriHspf2BatchActiveOptions(
            region=region,
            h42_enabled=self._parse_bool(self._vars["h42_enabled"].get()),
            h12_enabled=self._parse_bool(self._vars["h12_enabled"].get()),
            h22_enabled=self._parse_bool(self._vars["h22_enabled"].get()),
        )

    def _on_option_draft_changed(self, *_args: object) -> None:
        self._set_draft_status()

    def _set_draft_status(self) -> bool:
        try:
            changed = self._draft_active_options() != self._session.active_options
        except ValueError:
            self.status_var.set("Option inputs invalid")
            return True
        if changed:
            self.status_var.set("Options changed - apply to update matrix")
        return changed

    def _apply_options(self) -> None:
        try:
            draft = self._draft_active_options()
            spec = build_ahri_hspf2_batch_spec(draft)
        except (TypeError, ValueError):
            self.status_var.set("Option inputs invalid")
            return
        self._merge_visible_inputs_to_store()
        self._session.set_active_options(draft)
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

    def _common_inputs(self) -> AhriHspf2BatchCommonInputs:
        numeric = {key: self._vars[key].get() for key, _label in _NUMERIC_FIELDS}
        return AhriHspf2BatchCommonInputs(
            active=self._session.active_options,
            h1n_h32_same_hz=self._parse_bool(self._vars["h1n_h32_same_hz"].get()),
            min_spd=self._parse_bool(self._vars["min_spd"].get()),
            numeric_values=numeric,
        )

    def _recalculate_now(self) -> None:
        try:
            handler = AhriHspf2BatchHandler(self._common_inputs())
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
        self.status_var.set(f"{valid} valid / {pending} pending" +
                            (f" / {errors} invalid" if errors else ""))

    def _export_csv(self) -> None:
        headers, rows = self.table.table_export_data()
        export_table_to_csv(self._frame, "ahri_hspf2_batch.csv", headers, rows)
