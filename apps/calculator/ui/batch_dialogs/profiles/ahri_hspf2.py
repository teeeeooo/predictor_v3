"""Product-aware AHRI HSPF2 dynamic batch dialog profile section."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.application.ahri.product_defaults import (
    AHRI_HSPF2_COMMON_DEFAULTS,
    AHRI_HSPF2_TRIPLE_RANGE_DEFAULTS,
)
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
from apps.calculator.ui.layout_constants import (
    CONTROL_NUMERIC_ENTRY_WIDTH_CHARS,
    CONTROL_REGION_CODE_SELECTOR_WIDTH_CHARS,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table_csv_export import export_table_to_csv

_PRODUCT_LABELS = {
    "Variable Capacity": "variable_capacity",
    "Dual Stage": "dual_stage",
    "Triple Stage Northern": "triple_capacity_northern",
}
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
    "h4_full_enabled": "0",
    "h2_low_enabled": "1",
    "h2_boost_enabled": "1",
    "h3_low_enabled": "1",
    "low_stage_lockout_enabled": "0",
    "defrost_mode": "explicit_override",
    **AHRI_HSPF2_COMMON_DEFAULTS,
    **AHRI_HSPF2_TRIPLE_RANGE_DEFAULTS,
}
_VARIABLE_NUMERIC_FIELDS = (
    ("cd", "Cd"),
    ("defrost_credit", "Defrost Credit"),
    ("cut_out_c", "Cut Out [°C]"),
    ("cut_in_c", "Cut In [°C]"),
)
_MULTI_NUMERIC_FIELDS = (
    ("cut_out_c", "Cut Out [°C]"),
    ("cut_in_c", "Cut In [°C]"),
    ("cd_low", "Cd Low"),
    ("cd_full", "Cd Full"),
    ("cd_boost", "Cd Boost"),
    ("defrost_factor", "Fdef"),
    ("defrost_t_test_minutes", "Ttest"),
    ("defrost_t_max_minutes", "Tmax"),
    ("low_stage_lockout_temp_c", "Lockout [°C]"),
    ("low_min_c", "Low Min"),
    ("low_max_c", "Low Max"),
    ("full_min_c", "Full Min"),
    ("full_max_c", "Full Max"),
    ("boost_min_c", "Boost Min"),
    ("boost_max_c", "Boost Max"),
)


class AhriHspf2BatchSection:
    """Product/common options, isolated draft matrices, and automatic results."""

    result_panel = None

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: AhriHspf2BatchSnapshot | None = None,
    ) -> None:
        active = initial_snapshot.active_options if initial_snapshot else _DEFAULT_ACTIVE
        cases = initial_snapshot.cases if initial_snapshot else ()
        product_cases = initial_snapshot.product_cases if initial_snapshot else None
        self._session = AhriHspf2BatchSessionState(active, cases, product_cases)
        values = dict(_DEFAULT_COMMON)
        if initial_snapshot is not None:
            values.update(initial_snapshot.common_values)
        self._frame = ttk.LabelFrame(parent, text="AHRI 210/240 HSPF2 Batch")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(1, weight=1)
        self.product_var = tk.StringVar(
            master=self._frame,
            value=next(
                (
                    label
                    for label, value in _PRODUCT_LABELS.items()
                    if value == active.product_classification
                ),
                "Variable Capacity",
            ),
        )
        self._vars = {
            key: tk.StringVar(master=self._frame, value=value)
            for key, value in values.items()
        }
        self.status_var = tk.StringVar(master=self._frame, value="")
        self._build_common_inputs()
        self._table_host = ttk.Frame(self._frame)
        self._table_host.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=ISO_SECTION_PADX,
            pady=6,
        )
        self._table_host.columnconfigure(0, weight=1)
        self._table_host.rowconfigure(0, weight=1)
        self._create_table(build_ahri_hspf2_batch_spec(active))
        self._auto_calc = DebouncedAutoCalc(
            self._frame,
            self._recalculate_now,
            delay_ms=150,
        )
        self.table.set_values_changed_callback(self._auto_calc.schedule)
        self.product_var.trace_add("write", lambda *_args: self._on_product_changed())
        for key in (
            "region",
            "h42_enabled",
            "h12_enabled",
            "h22_enabled",
            "h4_full_enabled",
            "h2_low_enabled",
            "h2_boost_enabled",
            "h3_low_enabled",
        ):
            self._vars[key].trace_add("write", self._on_option_draft_changed)
        for key in (
            "h1n_h32_same_hz",
            "min_spd",
            "low_stage_lockout_enabled",
            "defrost_mode",
            *dict(_VARIABLE_NUMERIC_FIELDS),
            *dict(_MULTI_NUMERIC_FIELDS),
        ):
            self._vars[key].trace_add(
                "write", lambda *_args: self._auto_calc.schedule()
            )
        self._build_actions()
        self._show_product_controls()
        self._auto_calc.flush_now()

    @property
    def product_classification(self) -> str:
        return _PRODUCT_LABELS[self.product_var.get()]

    def _build_common_inputs(self) -> None:
        frame = ttk.LabelFrame(self._frame, text="Common Inputs")
        frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 0),
        )
        ttk.Label(frame, text="Product").grid(
            row=0, column=0, padx=3, pady=(4, 2)
        )
        ttk.Combobox(
            frame,
            textvariable=self.product_var,
            values=tuple(_PRODUCT_LABELS),
            state="readonly",
            width=22,
        ).grid(row=1, column=0, padx=3, pady=(0, 4))
        ttk.Label(frame, text="Region").grid(
            row=0, column=1, padx=3, pady=(4, 2)
        )
        ttk.Combobox(
            frame,
            textvariable=self._vars["region"],
            values=("IV",),
            state="readonly",
            width=CONTROL_REGION_CODE_SELECTOR_WIDTH_CHARS,
        ).grid(row=1, column=1, padx=3, pady=(0, 4))
        self._variable_controls = ttk.Frame(frame)
        self._variable_controls.grid(row=0, column=2, rowspan=2, sticky="w")
        self._build_variable_controls(self._variable_controls)
        self._multi_controls = ttk.Frame(frame)
        self._multi_controls.grid(row=0, column=2, rowspan=2, sticky="w")
        self._build_multi_controls(self._multi_controls)
        self.apply_button = ttk.Button(
            frame,
            text="Apply Options",
            command=self._apply_options,
        )
        self.apply_button.grid(row=1, column=20, padx=(6, 12), pady=(0, 4))

    def _build_variable_controls(self, frame: ttk.Frame) -> None:
        column = 0
        for key, label in (
            ("h42_enabled", "H42"),
            ("h12_enabled", "H12"),
            ("h22_enabled", "H22"),
            ("h1n_h32_same_hz", "H1N=H32 Hz"),
            ("min_spd", "MinSpd"),
        ):
            ttk.Checkbutton(
                frame,
                text=label,
                variable=self._vars[key],
                onvalue="1",
                offvalue="0",
            ).grid(row=1, column=column, padx=3, pady=(0, 4))
            column += 1
        for key, label in _VARIABLE_NUMERIC_FIELDS:
            self._numeric_entry(frame, key, label, column)
            column += 1

    def _build_multi_controls(self, frame: ttk.Frame) -> None:
        column = 0
        for key, label in (
            ("h4_full_enabled", "H4Full"),
            ("h2_low_enabled", "H2Low"),
            ("h2_boost_enabled", "H2Boost"),
            ("h3_low_enabled", "H3Low"),
            ("low_stage_lockout_enabled", "Low Lockout"),
        ):
            ttk.Checkbutton(
                frame,
                text=label,
                variable=self._vars[key],
                onvalue="1",
                offvalue="0",
            ).grid(row=1, column=column, padx=3, pady=(0, 4))
            column += 1
        ttk.Label(frame, text="Defrost Mode").grid(
            row=0,
            column=column,
            padx=3,
            pady=(4, 2),
        )
        ttk.Combobox(
            frame,
            textvariable=self._vars["defrost_mode"],
            values=("none", "explicit_override", "calculated_from_timing"),
            state="readonly",
            width=22,
        ).grid(row=1, column=column, padx=3, pady=(0, 4))
        column += 1
        for key, label in _MULTI_NUMERIC_FIELDS:
            self._numeric_entry(frame, key, label, column)
            column += 1

    def _numeric_entry(
        self,
        frame: ttk.Frame,
        key: str,
        label: str,
        column: int,
    ) -> None:
        ttk.Label(frame, text=label).grid(
            row=0,
            column=column,
            padx=3,
            pady=(4, 2),
        )
        ttk.Entry(
            frame,
            textvariable=self._vars[key],
            width=CONTROL_NUMERIC_ENTRY_WIDTH_CHARS,
        ).grid(row=1, column=column, padx=3, pady=(0, 4))

    def _show_product_controls(self) -> None:
        if self.product_classification == "variable_capacity":
            self._multi_controls.grid_remove()
            self._variable_controls.grid()
        else:
            self._variable_controls.grid_remove()
            self._multi_controls.grid()

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
            ("Copy All", self._copy_all),
            ("Export CSV", self._export_csv),
        ):
            ttk.Button(row, text=label, command=command).pack(
                side=tk.LEFT,
                padx=(0, 6),
            )
        ttk.Label(row, textvariable=self.status_var).pack(
            side=tk.LEFT,
            padx=(6, 0),
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
        values = {key: variable.get() for key, variable in self._vars.items()}
        values["product"] = self.product_classification
        return values

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
            product_classification=self.product_classification,
            h4_full_enabled=self._parse_bool(
                self._vars["h4_full_enabled"].get()
            ),
            h2_low_enabled=self._parse_bool(
                self._vars["h2_low_enabled"].get()
            ),
            h2_boost_enabled=self._parse_bool(
                self._vars["h2_boost_enabled"].get()
            ),
            h3_low_enabled=self._parse_bool(
                self._vars["h3_low_enabled"].get()
            ),
        )

    def _on_product_changed(self) -> None:
        if not hasattr(self, "table"):
            return
        self._show_product_controls()
        self._apply_options()

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
        self._session.sync_visible_cases(
            self.table.cases,
            self.table.spec.input_keys,
        )

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

    def _copy_all(self) -> str:
        return self.table.copy_all()

    def _numeric_values(self) -> dict[str, str]:
        fields = (
            _VARIABLE_NUMERIC_FIELDS
            if self.product_classification == "variable_capacity"
            else _MULTI_NUMERIC_FIELDS
        )
        return {key: self._vars[key].get() for key, _label in fields}

    def _common_inputs(self) -> AhriHspf2BatchCommonInputs:
        return AhriHspf2BatchCommonInputs(
            active=self._session.active_options,
            h1n_h32_same_hz=self._parse_bool(
                self._vars["h1n_h32_same_hz"].get()
            ),
            min_spd=self._parse_bool(self._vars["min_spd"].get()),
            numeric_values=self._numeric_values(),
            low_stage_lockout_enabled=self._parse_bool(
                self._vars["low_stage_lockout_enabled"].get()
            ),
            defrost_mode=self._vars["defrost_mode"].get(),
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
        self.status_var.set(
            f"{valid} valid / {pending} pending"
            + (f" / {errors} invalid" if errors else "")
        )

    def _export_csv(self) -> None:
        headers, rows = self.table.table_export_data()
        common = self.common_values()
        common_headers = tuple(common)
        common_values = tuple(common[key] for key in common_headers)
        export_table_to_csv(
            self._frame,
            f"ahri_hspf2_{self.product_classification}_batch.csv",
            (*common_headers, *headers),
            tuple((*common_values, *row) for row in rows),
        )
