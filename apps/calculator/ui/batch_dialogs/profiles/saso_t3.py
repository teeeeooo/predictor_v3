"""SASO T3 batch profile adapters and wrappers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
import tkinter as tk
from tkinter import ttk

from apps.calculator.application.saso_t3 import SasoT3UseCase
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch.controller import BatchMatrixCalculationController
from apps.calculator.ui.batch.matrix_models import (
    BatchMatrixSpec,
    MatrixMeasurementPointSpec,
    MatrixPhysicalRowType,
)
from apps.calculator.ui.batch.matrix_table import BatchMatrixTable
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.layout_constants import (
    BATCH_DIALOG_SAFETY_MIN_SIZE,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table_csv_export import export_table_to_csv
from apps.calculator.ui.batch_dialogs.shell import BatchDialogShell


SASO_T3_MATRIX_SPEC = BatchMatrixSpec(
    profile_key="saso_t3",
    title="SASO T3 Batch Matrix",
    physical_rows=(
        MatrixPhysicalRowType.CAPACITY,
        MatrixPhysicalRowType.POWER,
    ),
    row_type_labels=MappingProxyType(
        {
            MatrixPhysicalRowType.CAPACITY: "Capacity",
            MatrixPhysicalRowType.POWER: "Power",
        }
    ),
    measurement_points=(
        MatrixMeasurementPointSpec(
            "46_full",
            "46 Full",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: "full_46_capacity",
                    MatrixPhysicalRowType.POWER: "full_46_power",
                }
            ),
        ),
        MatrixMeasurementPointSpec(
            "35_full",
            "35 Full",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: "full_35_capacity",
                    MatrixPhysicalRowType.POWER: "full_35_power",
                }
            ),
        ),
        MatrixMeasurementPointSpec(
            "35_half",
            "35 Half",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: "half_35_capacity",
                    MatrixPhysicalRowType.POWER: "half_35_power",
                }
            ),
        ),
        MatrixMeasurementPointSpec(
            "35_min",
            "35 Min",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: "min_35_capacity",
                    MatrixPhysicalRowType.POWER: "min_35_power",
                }
            ),
        ),
    ),
    result_metrics=(
        ("opt_cspf", "4pt CSPF", 9),
        ("opt_cstl", "4pt CSTL", 10),
        ("opt_csec", "4pt CSEC", 10),
        ("req_cspf", "3pt CSPF", 9),
        ("req_cstl", "3pt CSTL", 10),
        ("req_csec", "3pt CSEC", 10),
    ),
    default_cases=(
        {},
        {},
        {},
        {},
        {},
    ),
)


@dataclass(frozen=True)
class BatchCalculationResult:
    values: dict[str, str]
    state: BatchRowState


class SasoT3BatchHandler:
    """Calculates row cases for SASO T3 batch."""

    spec = SASO_T3_MATRIX_SPEC

    def __init__(self) -> None:
        self._usecase = SasoT3UseCase()

    def calculate_row(self, row: Mapping[str, str]) -> BatchCalculationResult:
        required_keys = (
            "full_46_capacity",
            "full_46_power",
            "full_35_capacity",
            "full_35_power",
            "half_35_capacity",
            "half_35_power",
        )
        if not all(str(row.get(k, "")).strip() for k in required_keys):
            return self._blank_result(BatchRowState.PENDING)

        try:
            result = self._usecase.calculate_batch_row(row)
            state = BatchRowState.OK if result.status == "ok" else BatchRowState.ERROR
            return BatchCalculationResult(
                values=dict(result.values),
                state=state,
            )

        except Exception:
            return self._blank_result(BatchRowState.ERROR)

    def _blank_result(self, state: BatchRowState) -> BatchCalculationResult:
        return BatchCalculationResult(
            values={
                "req_cspf": "",
                "req_cstl": "",
                "req_csec": "",
                "opt_cspf": "",
                "opt_cstl": "",
                "opt_csec": "",
            },
            state=state,
        )


class SasoT3BatchSection:
    """Two-row matrix batch surface for SASO T3 cases."""

    result_panel = None

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: object | None = None,
    ) -> None:
        self._frame = ttk.LabelFrame(parent, text="SASO T3 Batch")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(0, weight=1)
        self.status_var = tk.StringVar(master=self._frame, value="")
        self.table = BatchMatrixTable(self._frame, SASO_T3_MATRIX_SPEC)
        self.table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 6),
        )
        self.table.interaction_controller = TkTableController(self.table)
        self.controller = BatchMatrixCalculationController(
            self.table,
            SasoT3BatchHandler(),
        )
        self._auto_calc = DebouncedAutoCalc(
            self._frame,
            self._recalculate_now,
            delay_ms=150,
        )
        self.table.set_values_changed_callback(self._auto_calc.schedule)
        if initial_snapshot is not None:
            self.table.restore_snapshot(initial_snapshot)
        action_row = ttk.Frame(self._frame)
        action_row.grid(
            row=1,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        ttk.Button(action_row, text="Add Case", command=self.table.add_case).pack(side=tk.LEFT)
        ttk.Button(action_row, text="Remove Case", command=self.table.remove_case).pack(
            side=tk.LEFT,
            padx=(6, 0),
        )
        ttk.Button(action_row, text="Copy All", command=self.table.copy_all).pack(
            side=tk.LEFT, padx=(6, 0)
        )
        ttk.Button(action_row, text="Export CSV", command=self._export_csv).pack(
            side=tk.LEFT, padx=(6, 0)
        )
        ttk.Label(action_row, textvariable=self.status_var).pack(side=tk.LEFT, padx=(12, 0))
        self._auto_calc.flush_now()

    def pack(self, **kwargs: object) -> None:
        self._frame.pack(**kwargs)

    def dispose(self) -> None:
        self._auto_calc.dispose()

    def _recalculate_now(self) -> None:
        summary = self.controller.recalculate()
        self.status_var.set(
            f"{summary.valid_rows} valid / {summary.blank_rows} blank"
            + (f" / {summary.error_rows} invalid" if summary.error_rows else "")
        )

    def _export_csv(self) -> None:
        headers, rows = self.table.table_export_data()
        export_table_to_csv(self._frame, "saso_t3_batch.csv", headers, rows)


class SasoT3BatchAdapter:
    """Composition adapter implementing BatchProfileAdapter for SASO T3."""

    def __init__(self, initial_snapshot: object | None = None) -> None:
        self.initial_snapshot = initial_snapshot
        self.section: SasoT3BatchSection | None = None

    @property
    def title(self) -> str:
        return "SASO T3 Batch"

    @property
    def min_size(self) -> tuple[int, int]:
        return BATCH_DIALOG_SAFETY_MIN_SIZE

    def build_content(self, parent: tk.Widget) -> tk.Widget:
        self.section = SasoT3BatchSection(
            parent,
            initial_snapshot=self.initial_snapshot,
        )
        return self.section._frame

    def dispose(self) -> None:
        if self.section is not None:
            self.section.dispose()

    def snapshot(self) -> list[dict[str, str]]:
        if self.section is not None:
            raw_snapshot = self.section.table.snapshot()
            if isinstance(raw_snapshot, (tuple, list)):
                return [dict(row) for row in raw_snapshot if isinstance(row, dict)]
        return []


class SasoT3BatchDialog:
    """Toplevel owner wrapper for SASO T3 batch dialog, utilizing BatchDialogShell."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: object | None = None,
        on_close: Callable[[list[dict[str, str]]], None] | None = None,
    ) -> None:
        self.adapter = SasoT3BatchAdapter(initial_snapshot=initial_snapshot)
        self._shell = BatchDialogShell(parent, self.adapter, on_close=on_close)
        self.section = self.adapter.section
        self.window = self._shell.window

    def close(self) -> None:
        self._shell.close()

    def snapshot(self) -> list[dict[str, str]]:
        return self._shell.snapshot()

    def focus(self) -> None:
        self._shell.focus()
