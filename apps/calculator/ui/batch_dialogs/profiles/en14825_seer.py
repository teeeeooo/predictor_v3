"""EN14825 SEER batch dialog profile."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch.matrix_table import BatchMatrixTable
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.batch_dialogs.shell import BatchDialogShell
from apps.calculator.ui.en14825.seer_adapter import SeerAdapter
from apps.calculator.ui.en14825.seer_batch import (
    EN14825_SEER_BATCH_SPEC,
    En14825SeerBatchCommonInputs,
    En14825SeerBatchHandler,
)
from apps.calculator.ui.layout_constants import (
    BATCH_DIALOG_SAFETY_MIN_SIZE,
    CONTROL_APPLIANCE_TYPE_SELECTOR_WIDTH_CHARS,
    CONTROL_NUMERIC_ENTRY_WIDTH_CHARS,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table_csv_export import export_table_to_csv
from apps.calculator.ui.table_grid_model import parse_numeric_cell

__all__ = ["En14825SeerBatchDialog", "En14825SeerBatchSnapshot"]


@dataclass(frozen=True)
class En14825SeerBatchSnapshot:
    common_values: Mapping[str, str]
    cases: tuple[Mapping[str, str], ...]


_COMMON_FIELDS = (
    ("t_design_c", "Tdesignc [°C]"),
    ("cd", "Cd"),
    ("p_to_w", "Pto [W]"),
    ("p_sb_w", "Psb [W]"),
    ("p_ck_w", "Pck [W]"),
    ("p_off_w", "Poff [W]"),
)


class En14825SeerBatchSection:
    """SEER common inputs, matrix, actions, and compact status."""

    result_panel = None

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: En14825SeerBatchSnapshot | None = None,
    ) -> None:
        defaults = SeerAdapter().get_seer_defaults()
        saved = dict(initial_snapshot.common_values) if initial_snapshot else {}
        default_values = {
            "t_design_c": str(defaults["t_design_c"]),
            "cd": str(defaults["degradation_coefficient"]),
            "appliance_type": str(defaults["appliance_type"]),
            "p_to_w": "0",
            "p_sb_w": "0",
            "p_ck_w": "0",
            "p_off_w": "0",
        }
        default_values.update(saved)
        self._frame = ttk.LabelFrame(parent, text="EN14825 SEER Batch")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(1, weight=1)
        self._vars = {
            key: tk.StringVar(master=self._frame, value=default_values[key])
            for key, _label in _COMMON_FIELDS
        }
        self._vars["appliance_type"] = tk.StringVar(
            master=self._frame,
            value=default_values["appliance_type"],
        )
        self.status_var = tk.StringVar(master=self._frame, value="")
        self._build_common_inputs()
        self.table = BatchMatrixTable(self._frame, EN14825_SEER_BATCH_SPEC)
        self.table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=ISO_SECTION_PADX,
            pady=(6, 6),
        )
        self.table.interaction_controller = TkTableController(self.table)
        if initial_snapshot is not None:
            self.table.restore_snapshot(initial_snapshot.cases)
        self._auto_calc = DebouncedAutoCalc(self._frame, self._recalculate_now, delay_ms=150)
        self.table.set_values_changed_callback(self._auto_calc.schedule)
        for variable in self._vars.values():
            variable.trace_add("write", lambda *_args: self._auto_calc.schedule())
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
        for column, (key, label) in enumerate(_COMMON_FIELDS):
            ttk.Label(frame, text=label).grid(row=0, column=column, padx=3, pady=(4, 2))
            ttk.Entry(
                frame,
                textvariable=self._vars[key],
                width=CONTROL_NUMERIC_ENTRY_WIDTH_CHARS,
            ).grid(
                row=1, column=column, padx=3, pady=(0, 4)
            )
        type_column = len(_COMMON_FIELDS)
        ttk.Label(frame, text="Type").grid(row=0, column=type_column, padx=3, pady=(4, 2))
        ttk.Combobox(
            frame,
            textvariable=self._vars["appliance_type"],
            values=("reversible", "cooling_only"),
            state="readonly",
            width=CONTROL_APPLIANCE_TYPE_SELECTOR_WIDTH_CHARS,
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
            ("Add Case", self.table.add_case),
            ("Remove Case", self.table.remove_case),
            ("Copy All", self.table.copy_all),
            ("Export CSV", self._export_csv),
        ):
            ttk.Button(row, text=label, command=command).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Label(row, textvariable=self.status_var).pack(side=tk.LEFT, padx=(6, 0))

    def common_values(self) -> dict[str, str]:
        return {key: variable.get() for key, variable in self._vars.items()}

    def snapshot(self) -> En14825SeerBatchSnapshot:
        return En14825SeerBatchSnapshot(self.common_values(), self.table.snapshot())

    def dispose(self) -> None:
        self._auto_calc.dispose()

    def _common_inputs(self) -> En14825SeerBatchCommonInputs:
        values = self.common_values()
        return En14825SeerBatchCommonInputs(
            t_design_c=parse_numeric_cell(values["t_design_c"]),
            cd=parse_numeric_cell(values["cd"]),
            appliance_type=values["appliance_type"],
            p_to_w=parse_numeric_cell(values["p_to_w"]),
            p_sb_w=parse_numeric_cell(values["p_sb_w"]),
            p_ck_w=parse_numeric_cell(values["p_ck_w"]),
            p_off_w=parse_numeric_cell(values["p_off_w"]),
        )

    def _recalculate_now(self) -> None:
        try:
            handler = En14825SeerBatchHandler(self._common_inputs())
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
        self.status_var.set(
            f"{valid} valid / {pending} pending"
            + (f" / {errors} invalid" if errors else "")
        )

    def _export_csv(self) -> None:
        headers, rows = self.table.table_export_data()
        export_table_to_csv(self._frame, "en14825_seer_batch.csv", headers, rows)


class En14825SeerBatchAdapter:
    """Composition adapter for the generic batch dialog shell."""

    def __init__(self, initial_snapshot: En14825SeerBatchSnapshot | None = None) -> None:
        self.initial_snapshot = initial_snapshot
        self.section: En14825SeerBatchSection | None = None
        self.last_snapshot = initial_snapshot or En14825SeerBatchSnapshot({}, ())

    @property
    def title(self) -> str:
        return "EN14825 SEER Batch"

    @property
    def min_size(self) -> tuple[int, int]:
        return BATCH_DIALOG_SAFETY_MIN_SIZE

    def build_content(self, parent: tk.Widget) -> tk.Widget:
        self.section = En14825SeerBatchSection(parent, initial_snapshot=self.initial_snapshot)
        return self.section._frame

    def dispose(self) -> None:
        if self.section is not None:
            self.section.dispose()

    def snapshot(self) -> list[dict[str, str]]:
        if self.section is None:
            return []
        self.last_snapshot = self.section.snapshot()
        return [dict(case) for case in self.last_snapshot.cases]


class En14825SeerBatchDialog:
    """Toplevel owner for the SEER batch profile."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: En14825SeerBatchSnapshot | None = None,
        on_close: Callable[[En14825SeerBatchSnapshot], None] | None = None,
    ) -> None:
        self.adapter = En14825SeerBatchAdapter(initial_snapshot)

        def handle_close(_cases: list[dict[str, str]]) -> None:
            if on_close is not None:
                on_close(self.adapter.last_snapshot)

        self._shell = BatchDialogShell(parent, self.adapter, on_close=handle_close)
        self.section = self.adapter.section
        self.window = self._shell.window

    def close(self) -> None:
        self._shell.close()

    def snapshot(self) -> En14825SeerBatchSnapshot:
        if self.section is None:
            return En14825SeerBatchSnapshot({}, ())
        return self.section.snapshot()

    def focus(self) -> None:
        self._shell.focus()
