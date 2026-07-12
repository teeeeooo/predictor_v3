"""Product-aware AHRI 210/240 SEER2 batch dialog profile."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
import tkinter as tk
from tkinter import ttk

from apps.calculator.application.ahri import AhriSeer2Options
from apps.calculator.application.ahri.seer2_adapter import AHRI_SEER2_DUAL_DEFAULTS
from apps.calculator.ui.ahri.seer2_batch import (
    AhriSeer2BatchCommonInputs,
    AhriSeer2BatchHandler,
    build_ahri_seer2_batch_spec,
)
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch.matrix_table import BatchMatrixTable
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.batch_dialogs.shell import BatchDialogShell
from apps.calculator.ui.layout_constants import (
    BATCH_DIALOG_SAFETY_MIN_SIZE,
    CONTROL_EQUIPMENT_TYPE_SELECTOR_WIDTH_CHARS,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table_csv_export import export_table_to_csv

__all__ = ["AhriSeer2BatchDialog", "AhriSeer2BatchSnapshot"]

_PRODUCT_LABELS = {
    "Variable Capacity": "variable_capacity",
    "Dual Stage": "dual_stage",
}


@dataclass(frozen=True)
class AhriSeer2BatchSnapshot:
    common_values: Mapping[str, str]
    cases: tuple[Mapping[str, str], ...]
    product_cases: Mapping[str, tuple[Mapping[str, str], ...]] = field(default_factory=dict)


class AhriSeer2BatchSection:
    """Product/common options, active matrix, actions, and automatic results."""

    result_panel = None

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: AhriSeer2BatchSnapshot | None = None,
    ) -> None:
        saved = dict(initial_snapshot.common_values) if initial_snapshot else {}
        self._product_cases = {
            key: tuple(dict(case) for case in cases)
            for key, cases in (initial_snapshot.product_cases.items() if initial_snapshot else ())
        }
        initial_product = saved.get("product", "variable_capacity")
        if initial_snapshot and not self._product_cases:
            self._product_cases[initial_product] = initial_snapshot.cases
        self._frame = ttk.LabelFrame(parent, text="AHRI 210/240 SEER2 Batch")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(1, weight=1)
        self.product_var = tk.StringVar(
            master=self._frame,
            value=next(
                (label for label, value in _PRODUCT_LABELS.items() if value == initial_product),
                "Variable Capacity",
            ),
        )
        self.type_var = tk.StringVar(master=self._frame, value=saved.get("type", "HP"))
        self.cd_low_var = tk.StringVar(
            master=self._frame, value=saved.get("cd_low", AHRI_SEER2_DUAL_DEFAULTS["cd_low"])
        )
        self.cd_full_var = tk.StringVar(
            master=self._frame, value=saved.get("cd_full", AHRI_SEER2_DUAL_DEFAULTS["cd_full"])
        )
        self.lockout_var = tk.BooleanVar(
            master=self._frame, value=saved.get("low_stage_lockout_enabled", "False") == "True"
        )
        self.lockout_temp_var = tk.StringVar(
            master=self._frame,
            value=saved.get(
                "low_stage_lockout_temp_f",
                AHRI_SEER2_DUAL_DEFAULTS["low_stage_lockout_temp_f"],
            ),
        )
        self.status_var = tk.StringVar(master=self._frame, value="")
        self._build_common_inputs()
        self.table: BatchMatrixTable
        self._build_table(self.product_classification)
        self._auto_calc = DebouncedAutoCalc(self._frame, self._recalculate_now, delay_ms=150)
        self.table.set_values_changed_callback(self._auto_calc.schedule)
        for variable in (
            self.type_var,
            self.cd_low_var,
            self.cd_full_var,
            self.lockout_var,
            self.lockout_temp_var,
        ):
            variable.trace_add("write", lambda *_args: self._auto_calc.schedule())
        self.product_var.trace_add("write", lambda *_args: self._on_product_changed())
        self._build_actions()
        self._apply_product_controls()
        self._auto_calc.flush_now()

    @property
    def product_classification(self) -> str:
        return _PRODUCT_LABELS[self.product_var.get()]

    def _build_common_inputs(self) -> None:
        frame = ttk.LabelFrame(self._frame, text="Common Inputs")
        frame.grid(
            row=0,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 0),
        )
        ttk.Label(frame, text="Product").pack(side=tk.LEFT, padx=(6, 4), pady=6)
        self.product_selector = ttk.Combobox(
            frame,
            textvariable=self.product_var,
            values=tuple(_PRODUCT_LABELS),
            state="readonly",
            width=22,
        )
        self.product_selector.pack(side=tk.LEFT, padx=(0, 6), pady=6)
        ttk.Label(frame, text="Type").pack(side=tk.LEFT, padx=(6, 4), pady=6)
        self.type_selector = ttk.Combobox(
            frame,
            textvariable=self.type_var,
            values=("HP", "AC"),
            state="readonly",
            width=CONTROL_EQUIPMENT_TYPE_SELECTOR_WIDTH_CHARS,
        )
        self.type_selector.pack(side=tk.LEFT, padx=(0, 6), pady=6)
        self._dual_controls = ttk.Frame(frame)
        ttk.Checkbutton(
            self._dual_controls,
            text="Low lockout",
            variable=self.lockout_var,
        ).pack(side=tk.LEFT, padx=(6, 2))
        for label, variable, width in (
            ("Lockout °F", self.lockout_temp_var, 7),
            ("Cd Low", self.cd_low_var, 6),
            ("Cd Full", self.cd_full_var, 6),
        ):
            ttk.Label(self._dual_controls, text=label).pack(side=tk.LEFT, padx=(4, 2))
            ttk.Entry(self._dual_controls, textvariable=variable, width=width).pack(side=tk.LEFT)

    def _build_table(self, product: str) -> None:
        self.table = BatchMatrixTable(
            self._frame,
            build_ahri_seer2_batch_spec(product),
        )
        self.table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=ISO_SECTION_PADX,
            pady=(6, 6),
        )
        self.table.interaction_controller = TkTableController(self.table)
        saved_cases = self._product_cases.get(product, ())
        if saved_cases:
            self.table.restore_snapshot(saved_cases)

    def _on_product_changed(self) -> None:
        if not hasattr(self, "table"):
            return
        old_product = self.table.spec.profile_key.removeprefix("ahri_seer2_")
        self._product_cases[old_product] = self._input_cases()
        self.table.destroy()
        self._build_table(self.product_classification)
        self.table.set_values_changed_callback(self._auto_calc.schedule)
        self._apply_product_controls()
        self.status_var.set("0 valid / 1 pending")
        self._auto_calc.flush_now()

    def _apply_product_controls(self) -> None:
        if self.product_classification == "dual_stage":
            self._dual_controls.pack(side=tk.LEFT)
        else:
            self._dual_controls.pack_forget()

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
            ("Add Case", self.table.add_case),
            ("Remove Case", self.table.remove_case),
            ("Copy All", self.table.copy_all),
            ("Export CSV", self._export_csv),
        ):
            ttk.Button(row, text=label, command=command).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Label(row, textvariable=self.status_var).pack(side=tk.LEFT, padx=(6, 0))

    def _options(self) -> AhriSeer2Options | None:
        if self.product_classification == "variable_capacity":
            return None
        return AhriSeer2Options(
            product_classification="dual_stage",
            low_stage_lockout_enabled=self.lockout_var.get(),
            low_stage_lockout_temp_f=(
                float(self.lockout_temp_var.get()) if self.lockout_var.get() else None
            ),
            cd_low=float(self.cd_low_var.get()),
            cd_full=float(self.cd_full_var.get()),
        )

    def common_values(self) -> dict[str, str]:
        return {
            "product": self.product_classification,
            "type": self.type_var.get(),
            "cd_low": self.cd_low_var.get(),
            "cd_full": self.cd_full_var.get(),
            "low_stage_lockout_enabled": str(self.lockout_var.get()),
            "low_stage_lockout_temp_f": self.lockout_temp_var.get(),
        }

    def _input_cases(self) -> tuple[Mapping[str, str], ...]:
        input_keys = set(self.table.spec.input_keys)
        return tuple(
            {key: value for key, value in case.items() if key in input_keys}
            for case in self.table.cases
        )

    def snapshot(self) -> AhriSeer2BatchSnapshot:
        self._product_cases[self.product_classification] = self._input_cases()
        return AhriSeer2BatchSnapshot(
            self.common_values(),
            self._input_cases(),
            dict(self._product_cases),
        )

    def dispose(self) -> None:
        self._auto_calc.dispose()

    def _recalculate_now(self) -> None:
        try:
            options = self._options()
        except ValueError:
            for index in range(len(self.table.cases)):
                self.table.set_result(
                    index,
                    {key: "" for key, _label, _width in self.table.spec.result_metrics},
                )
            self.status_var.set(f"0 valid / 0 pending / {len(self.table.cases)} invalid")
            return
        handler = AhriSeer2BatchHandler(
            AhriSeer2BatchCommonInputs(
                system_type=self.type_var.get(),
                product_classification=self.product_classification,
                options=options,
            )
        )
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
        self.status_var.set(
            f"{valid} valid / {pending} pending"
            + (f" / {errors} invalid" if errors else "")
        )

    def _export_csv(self) -> None:
        headers, rows = self.table.table_export_data()
        common = self.common_values()
        common_headers = tuple(common)
        extended_headers = (*common_headers, *headers)
        common_values = tuple(common[key] for key in common_headers)
        extended_rows = tuple((*common_values, *row) for row in rows)
        export_table_to_csv(
            self._frame,
            f"ahri_seer2_{self.product_classification}_batch.csv",
            extended_headers,
            extended_rows,
        )


class AhriSeer2BatchAdapter:
    def __init__(self, initial_snapshot: AhriSeer2BatchSnapshot | None = None) -> None:
        self.initial_snapshot = initial_snapshot
        self.section: AhriSeer2BatchSection | None = None
        self.last_snapshot = initial_snapshot or AhriSeer2BatchSnapshot({}, ())

    @property
    def title(self) -> str:
        return "AHRI 210/240 SEER2 Batch"

    @property
    def min_size(self) -> tuple[int, int]:
        return BATCH_DIALOG_SAFETY_MIN_SIZE

    def build_content(self, parent: tk.Widget) -> tk.Widget:
        self.section = AhriSeer2BatchSection(parent, initial_snapshot=self.initial_snapshot)
        return self.section._frame

    def dispose(self) -> None:
        if self.section is not None:
            self.section.dispose()

    def snapshot(self) -> list[dict[str, str]]:
        if self.section is None:
            return []
        self.last_snapshot = self.section.snapshot()
        return [dict(case) for case in self.last_snapshot.cases]


class AhriSeer2BatchDialog:
    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: AhriSeer2BatchSnapshot | None = None,
        on_close: Callable[[AhriSeer2BatchSnapshot], None] | None = None,
    ) -> None:
        self.adapter = AhriSeer2BatchAdapter(initial_snapshot)

        def handle_close(_cases: list[dict[str, str]]) -> None:
            if on_close is not None:
                on_close(self.adapter.last_snapshot)

        self._shell = BatchDialogShell(parent, self.adapter, on_close=handle_close)
        self.section = self.adapter.section
        self.window = self._shell.window

    def close(self) -> None:
        self._shell.close()

    def snapshot(self) -> AhriSeer2BatchSnapshot:
        if self.section is None:
            return AhriSeer2BatchSnapshot({}, ())
        return self.section.snapshot()

    def focus(self) -> None:
        self._shell.focus()
