"""ISO/India ISEER 2-point batch profile adapters and wrappers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
import tkinter as tk
from tkinter import ttk

from apps.calculator.application.iso_iseer_2point.usecase import IsoIseer2PointUseCase
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


ISO_ISEER_2POINT_MATRIX_SPEC = BatchMatrixSpec(
    profile_key="iso_iseer_2point",
    title="ISO / India ISEER 2-point Batch Matrix",
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
            "35_full",
            "35 Full",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: "full_capacity",
                    MatrixPhysicalRowType.POWER: "full_power",
                }
            ),
        ),
        MatrixMeasurementPointSpec(
            "35_half",
            "35 Half",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: "half_capacity",
                    MatrixPhysicalRowType.POWER: "half_power",
                }
            ),
        ),
    ),
    result_metrics=(
        ("iso_cspf", "ISO CSPF", 9),
        ("iso_cstl", "ISO CSTL", 10),
        ("iso_csec", "ISO CSEC", 10),
        ("iseer", "ISEER", 9),
        ("iseer_cstl", "ISEER CSTL", 10),
        ("iseer_csec", "ISEER CSEC", 10),
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


class IsoIseer2PointBatchHandler:
    """Calculates row cases for ISO/India ISEER 2-point batch."""

    spec = ISO_ISEER_2POINT_MATRIX_SPEC

    def __init__(self, usecase: IsoIseer2PointUseCase | None = None) -> None:
        self._usecase = usecase or IsoIseer2PointUseCase()

    def calculate_row(self, row: Mapping[str, str]) -> BatchCalculationResult:
        required_keys = ("full_capacity", "full_power", "half_capacity", "half_power")
        if not all(str(row.get(k, "")).strip() for k in required_keys):
            return self._blank_result(BatchRowState.PENDING)

        result = self._usecase.calculate(
            {key: str(row.get(key, "")) for key in required_keys}
        )
        if not result.is_ok:
            return self._blank_result(BatchRowState.ERROR)

        rows_by_label = {values[0]: values for values in result.rows}
        iso_row = rows_by_label["ISO 16358-1"]
        iseer_row = rows_by_label["India ISEER"]
        return BatchCalculationResult(
            values={
                "iso_cspf": iso_row[3],
                "iso_cstl": iso_row[4],
                "iso_csec": iso_row[5],
                "iseer": iseer_row[3],
                "iseer_cstl": iseer_row[4],
                "iseer_csec": iseer_row[5],
            },
            state=BatchRowState.OK,
        )

    def _blank_result(self, state: BatchRowState) -> BatchCalculationResult:
        return BatchCalculationResult(
            values={
                "iso_cspf": "",
                "iso_cstl": "",
                "iso_csec": "",
                "iseer": "",
                "iseer_cstl": "",
                "iseer_csec": "",
            },
            state=state,
        )


class IsoIseer2PointBatchSection:
    """Two-row matrix batch surface for ISO/India ISEER 2-point cases."""

    result_panel = None

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: object | None = None,
    ) -> None:
        self._frame = ttk.LabelFrame(parent, text="ISO / India ISEER 2-point Batch")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(0, weight=1)
        self.status_var = tk.StringVar(master=self._frame, value="")
        self.table = BatchMatrixTable(self._frame, ISO_ISEER_2POINT_MATRIX_SPEC)
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
            IsoIseer2PointBatchHandler(),
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
        export_table_to_csv(self._frame, "iso_iseer_2point_batch.csv", headers, rows)


class IsoIseer2PointBatchAdapter:
    """Composition adapter implementing BatchProfileAdapter for ISO/India ISEER 2-point."""

    def __init__(self, initial_snapshot: object | None = None) -> None:
        self.initial_snapshot = initial_snapshot
        self.section: IsoIseer2PointBatchSection | None = None

    @property
    def title(self) -> str:
        return "ISO / India ISEER 2-point Batch"

    @property
    def min_size(self) -> tuple[int, int]:
        return BATCH_DIALOG_SAFETY_MIN_SIZE

    def build_content(self, parent: tk.Widget) -> tk.Widget:
        self.section = IsoIseer2PointBatchSection(
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


class IsoIseer2PointBatchDialog:
    """Toplevel owner wrapper for ISO/India ISEER 2-point batch dialog, utilizing BatchDialogShell."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: object | None = None,
        on_close: Callable[[list[dict[str, str]]], None] | None = None,
    ) -> None:
        self.adapter = IsoIseer2PointBatchAdapter(initial_snapshot=initial_snapshot)
        self._shell = BatchDialogShell(parent, self.adapter, on_close=on_close)
        self.section = self.adapter.section
        self.window = self._shell.window

    def close(self) -> None:
        self._shell.close()

    def snapshot(self) -> list[dict[str, str]]:
        return self._shell.snapshot()

    def focus(self) -> None:
        self._shell.focus()
