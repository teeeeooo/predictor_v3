"""AHRI 210/240 SEER2 batch dialog profile."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.ahri.seer2_batch import (
    AHRI_SEER2_BATCH_SPEC,
    AhriSeer2BatchCommonInputs,
    AhriSeer2BatchHandler,
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


@dataclass(frozen=True)
class AhriSeer2BatchSnapshot:
    common_values: Mapping[str, str]
    cases: tuple[Mapping[str, str], ...]


class AhriSeer2BatchSection:
    """Type option, two-row matrix, actions, and automatic results."""

    result_panel = None

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: AhriSeer2BatchSnapshot | None = None,
    ) -> None:
        saved = dict(initial_snapshot.common_values) if initial_snapshot else {}
        self._frame = ttk.LabelFrame(parent, text="AHRI 210/240 SEER2 Batch")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(1, weight=1)
        self.type_var = tk.StringVar(
            master=self._frame,
            value=saved.get("type", "HP"),
        )
        self.status_var = tk.StringVar(master=self._frame, value="")
        self._build_common_inputs()
        self.table = BatchMatrixTable(self._frame, AHRI_SEER2_BATCH_SPEC)
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
        self._auto_calc = DebouncedAutoCalc(
            self._frame,
            self._recalculate_now,
            delay_ms=150,
        )
        self.table.set_values_changed_callback(self._auto_calc.schedule)
        self.type_var.trace_add("write", lambda *_args: self._auto_calc.schedule())
        self._build_actions()
        self._auto_calc.flush_now()

    def _build_common_inputs(self) -> None:
        frame = ttk.LabelFrame(self._frame, text="Common Inputs")
        frame.grid(
            row=0,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 0),
        )
        ttk.Label(frame, text="Type").pack(side=tk.LEFT, padx=(6, 4), pady=6)
        self.type_selector = ttk.Combobox(
            frame,
            textvariable=self.type_var,
            values=("HP", "AC"),
            state="readonly",
            width=CONTROL_EQUIPMENT_TYPE_SELECTOR_WIDTH_CHARS,
        )
        self.type_selector.pack(side=tk.LEFT, padx=(0, 6), pady=6)

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
            ttk.Button(row, text=label, command=command).pack(
                side=tk.LEFT,
                padx=(0, 6),
            )
        ttk.Label(row, textvariable=self.status_var).pack(side=tk.LEFT, padx=(6, 0))

    def common_values(self) -> dict[str, str]:
        return {"type": self.type_var.get()}

    def snapshot(self) -> AhriSeer2BatchSnapshot:
        input_keys = set(AHRI_SEER2_BATCH_SPEC.input_keys)
        cases = tuple(
            {key: value for key, value in case.items() if key in input_keys}
            for case in self.table.cases
        )
        return AhriSeer2BatchSnapshot(self.common_values(), cases)

    def dispose(self) -> None:
        self._auto_calc.dispose()

    def _recalculate_now(self) -> None:
        handler = AhriSeer2BatchHandler(
            AhriSeer2BatchCommonInputs(system_type=self.type_var.get())
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
        export_table_to_csv(self._frame, "ahri_seer2_batch.csv", headers, rows)


class AhriSeer2BatchAdapter:
    """Composition adapter for the generic batch dialog shell."""

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
        self.section = AhriSeer2BatchSection(
            parent,
            initial_snapshot=self.initial_snapshot,
        )
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
    """Toplevel owner for the AHRI SEER2 batch profile."""

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
