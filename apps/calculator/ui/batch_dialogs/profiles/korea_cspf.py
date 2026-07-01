"""KOREA CSPF batch profile adapters and wrappers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
import tkinter as tk
from tkinter import ttk

from apps.calculator.application.korea import KoreaCspfUseCase
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch.controller import BatchMatrixCalculationController
from apps.calculator.ui.batch.matrix_models import (
    BatchMatrixSpec,
    MatrixMeasurementPointSpec,
    MatrixPhysicalRowType,
)
from apps.calculator.ui.batch.matrix_table import BatchMatrixTable
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.batch_dialogs.shell import BatchDialogShell
from apps.calculator.ui.layout_constants import (
    BATCH_DIALOG_SAFETY_MIN_SIZE,
    BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS,
    BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table_csv_export import export_table_to_csv

DECLARED_CAPACITY = "declared_capacity"
FULL_CAPACITY = "full_capacity"
FULL_POWER = "full_power"
HALF_CAPACITY = "half_capacity"
HALF_POWER = "half_power"
MIN_CAPACITY = "min_capacity"
MIN_POWER = "min_power"
CSPF = "cspf"
CSEC = "csec"
_REQUIRED_INPUT_KEYS = (
    DECLARED_CAPACITY,
    FULL_CAPACITY,
    FULL_POWER,
    HALF_CAPACITY,
    HALF_POWER,
    MIN_CAPACITY,
    MIN_POWER,
)

KOREA_CSPF_MATRIX_SPEC = BatchMatrixSpec(
    profile_key="korea_cspf",
    title="KOREA CSPF Batch Matrix",
    physical_rows=(MatrixPhysicalRowType.CAPACITY, MatrixPhysicalRowType.POWER),
    row_type_labels=MappingProxyType(
        {
            MatrixPhysicalRowType.CAPACITY: "Capacity",
            MatrixPhysicalRowType.POWER: "Power",
        }
    ),
    measurement_points=(
        MatrixMeasurementPointSpec(
            "declared",
            "Declared",
            MappingProxyType({MatrixPhysicalRowType.CAPACITY: DECLARED_CAPACITY}),
        ),
        MatrixMeasurementPointSpec(
            "35_full",
            "35 Full",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: FULL_CAPACITY,
                    MatrixPhysicalRowType.POWER: FULL_POWER,
                }
            ),
        ),
        MatrixMeasurementPointSpec(
            "35_half",
            "35 Half",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: HALF_CAPACITY,
                    MatrixPhysicalRowType.POWER: HALF_POWER,
                }
            ),
        ),
        MatrixMeasurementPointSpec(
            "29_min",
            "29 Min",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: MIN_CAPACITY,
                    MatrixPhysicalRowType.POWER: MIN_POWER,
                }
            ),
        ),
    ),
    result_metrics=(
        (CSPF, "CSPF", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        (CSEC, "CSEC", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
    ),
    default_cases=({}, {}, {}, {}, {}),
)


@dataclass(frozen=True)
class KoreaCspfBatchResult:
    values: dict[str, str]
    state: BatchRowState


class KoreaCspfBatchHandler:
    """Calculate KOREA CSPF matrix batch cases."""

    spec = KOREA_CSPF_MATRIX_SPEC

    def __init__(self) -> None:
        self._usecase = KoreaCspfUseCase()

    def calculate_row(self, row: Mapping[str, str]) -> KoreaCspfBatchResult:
        if not all(str(row.get(key, "")).strip() for key in _REQUIRED_INPUT_KEYS):
            return _blank_result()
        try:
            result = self._usecase.calculate(row)
            if not result.is_ok:
                return _blank_result(BatchRowState.ERROR)
            fields = dict(result.summary_fields)
            return KoreaCspfBatchResult(
                values={
                    CSPF: fields.get("CSPF", "-"),
                    CSEC: fields.get("CSEC [kWh]", "-"),
                },
                state=BatchRowState.OK,
            )
        except Exception:
            return _blank_result(BatchRowState.ERROR)


class KoreaCspfBatchSection:
    """Two-row matrix batch surface for KOREA CSPF cases."""

    result_panel = None

    def __init__(self, parent: tk.Widget, *, initial_snapshot: object | None = None) -> None:
        self._frame = ttk.LabelFrame(parent, text="CSPF Batch (KOREA)")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(0, weight=1)
        self.status_var = tk.StringVar(master=self._frame, value="")
        self.table = BatchMatrixTable(self._frame, KOREA_CSPF_MATRIX_SPEC)
        self.table.grid(row=0, column=0, sticky="nsew", padx=ISO_SECTION_PADX, pady=(ISO_SECTION_BLOCK_GAP, 6))
        self.table.interaction_controller = TkTableController(self.table)
        self.controller = BatchMatrixCalculationController(self.table, KoreaCspfBatchHandler())
        self._auto_calc = DebouncedAutoCalc(self._frame, self._recalculate_now, delay_ms=150)
        self.table.set_values_changed_callback(self._auto_calc.schedule)
        if initial_snapshot is not None:
            self.table.restore_snapshot(initial_snapshot)
        action_row = ttk.Frame(self._frame)
        action_row.grid(row=1, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, ISO_SECTION_BLOCK_GAP))
        ttk.Button(action_row, text="Add Case", command=self.table.add_case).pack(side=tk.LEFT)
        ttk.Button(action_row, text="Remove Case", command=self.table.remove_case).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(action_row, text="Copy All", command=self.table.copy_all).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(action_row, text="Export CSV", command=self._export_csv).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Label(action_row, textvariable=self.status_var).pack(side=tk.LEFT, padx=(12, 0))
        self._auto_calc.flush_now()

    def dispose(self) -> None:
        self._auto_calc.dispose()

    def _recalculate_now(self) -> None:
        summary = self.controller.recalculate()
        self.status_var.set(f"{summary.valid_rows} valid / {summary.blank_rows} blank" + (f" / {summary.error_rows} invalid" if summary.error_rows else ""))

    def _export_csv(self) -> None:
        headers, rows = self.table.table_export_data()
        export_table_to_csv(self._frame, "korea_cspf_batch.csv", headers, rows)


class KoreaCspfBatchAdapter:
    def __init__(self, initial_snapshot: object | None = None) -> None:
        self.initial_snapshot = initial_snapshot
        self.section: KoreaCspfBatchSection | None = None

    @property
    def title(self) -> str:
        return "CSPF Batch (KOREA)"

    @property
    def min_size(self) -> tuple[int, int]:
        return BATCH_DIALOG_SAFETY_MIN_SIZE

    def build_content(self, parent: tk.Widget) -> tk.Widget:
        self.section = KoreaCspfBatchSection(parent, initial_snapshot=self.initial_snapshot)
        return self.section._frame

    def dispose(self) -> None:
        if self.section is not None:
            self.section.dispose()

    def snapshot(self) -> list[dict[str, str]]:
        if self.section is None:
            return []
        raw_snapshot = self.section.table.snapshot()
        return [dict(row) for row in raw_snapshot if isinstance(row, dict)]


class KoreaCspfBatchDialog:
    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: object | None = None,
        on_close: Callable[[list[dict[str, str]]], None] | None = None,
    ) -> None:
        self.adapter = KoreaCspfBatchAdapter(initial_snapshot=initial_snapshot)
        self._shell = BatchDialogShell(parent, self.adapter, on_close=on_close)
        self.section = self.adapter.section
        self.window = self._shell.window

    def close(self) -> None:
        self._shell.close()

    def snapshot(self) -> list[dict[str, str]]:
        return self._shell.snapshot()

    def focus(self) -> None:
        self._shell.focus()


def _blank_result(state: BatchRowState = BatchRowState.PENDING) -> KoreaCspfBatchResult:
    return KoreaCspfBatchResult(values={CSPF: "", CSEC: ""}, state=state)
