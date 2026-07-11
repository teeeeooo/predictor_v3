"""Brazil CSPF batch matrix profile and dialog wrapper."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

import tkinter as tk
from tkinter import ttk

from apps.calculator.application.brazil_cspf import BrazilCspfUseCase
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


FULL_CAPACITY = "full_capacity"
FULL_POWER = "full_power"
HALF_CAPACITY = "half_capacity"
HALF_POWER = "half_power"
HALF_29_CAPACITY = "half_29_capacity"
HALF_29_POWER = "half_29_power"
THREE_POINT_CSPF = "three_point_cspf"
THREE_POINT_CSTL = "three_point_cstl"
THREE_POINT_CSEC = "three_point_csec"
TWO_POINT_CSPF = "two_point_cspf"
TWO_POINT_CSTL = "two_point_cstl"
TWO_POINT_CSEC = "two_point_csec"
RULE_1 = "rule_1"
MEASURED_29_HALF_EER = "measured_29_half_eer"
CALCULATED_29_BIN_EER = "calculated_29_bin_eer"
RULE_2 = "rule_2"
FINAL = "final"
ROW_STATUS = "row_status"

_REQUIRED_INPUT_KEYS = (
    FULL_CAPACITY,
    FULL_POWER,
    HALF_CAPACITY,
    HALF_POWER,
    HALF_29_CAPACITY,
    HALF_29_POWER,
)


BRAZIL_CSPF_MATRIX_SPEC = BatchMatrixSpec(
    profile_key="brazil_cspf_compliance",
    title="Brazil CSPF Compliance Batch Matrix",
    physical_rows=(MatrixPhysicalRowType.CAPACITY, MatrixPhysicalRowType.POWER),
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
            "29_half",
            "29 Half",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: HALF_29_CAPACITY,
                    MatrixPhysicalRowType.POWER: HALF_29_POWER,
                }
            ),
        ),
    ),
    result_metrics=(
        (THREE_POINT_CSPF, "3-point CSPF", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        (THREE_POINT_CSTL, "3-point CSTL", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
        (THREE_POINT_CSEC, "3-point CSEC", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
        (TWO_POINT_CSPF, "2-point CSPF", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        (TWO_POINT_CSTL, "2-point CSTL", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
        (TWO_POINT_CSEC, "2-point CSEC", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
        (RULE_1, "Rule 1", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        (MEASURED_29_HALF_EER, "Measured 29 Half EER", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
        (CALCULATED_29_BIN_EER, "Calculated 29°C Bin EER", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
        (RULE_2, "Rule 2", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        (FINAL, "Final", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        (ROW_STATUS, "Row Status", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
    ),
    default_cases=({}, {}, {}, {}, {}),
)


@dataclass(frozen=True)
class BrazilCspfBatchCalculationResult:
    values: dict[str, str]
    state: BatchRowState


class BrazilCspfBatchHandler:
    spec = BRAZIL_CSPF_MATRIX_SPEC

    def __init__(self, usecase: BrazilCspfUseCase | None = None) -> None:
        self._usecase = usecase or BrazilCspfUseCase()

    def calculate_row(
        self, row: Mapping[str, str]
    ) -> BrazilCspfBatchCalculationResult:
        if not _has_complete_inputs(row):
            return _blank_result(BatchRowState.PENDING, "PENDING")
        result = self._usecase.calculate(
            {key: str(row.get(key, "")) for key in _REQUIRED_INPUT_KEYS}
        )
        if not result.is_ok or len(result.rows) != 2 or len(result.rules) != 2:
            return _blank_result(BatchRowState.ERROR, "ERROR")
        three_point, two_point = result.rows
        rule_1, rule_2 = result.rules
        return BrazilCspfBatchCalculationResult(
            values={
                THREE_POINT_CSPF: three_point[1],
                THREE_POINT_CSTL: three_point[2],
                THREE_POINT_CSEC: three_point[3],
                TWO_POINT_CSPF: two_point[1],
                TWO_POINT_CSTL: two_point[2],
                TWO_POINT_CSEC: two_point[3],
                RULE_1: rule_1.status_text,
                MEASURED_29_HALF_EER: rule_2.left_value_text,
                CALCULATED_29_BIN_EER: rule_2.right_value_text,
                RULE_2: rule_2.status_text,
                FINAL: result.final_status or "",
                ROW_STATUS: "OK",
            },
            state=BatchRowState.OK,
        )


def _has_complete_inputs(row: Mapping[str, str]) -> bool:
    return all(str(row.get(key, "")).strip() for key in _REQUIRED_INPUT_KEYS)


def _blank_result(
    state: BatchRowState,
    row_status: str,
) -> BrazilCspfBatchCalculationResult:
    return BrazilCspfBatchCalculationResult(
        values={key: "" for key in BRAZIL_CSPF_MATRIX_SPEC.result_keys[:-1]}
        | {ROW_STATUS: row_status},
        state=state,
    )


class BrazilCspfBatchSection:
    """Two-row matrix batch surface for Brazil CSPF compliance cases."""

    result_panel = None

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: object | None = None,
    ) -> None:
        self._frame = ttk.LabelFrame(parent, text="Brazil CSPF Compliance Batch")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(0, weight=1)
        self.status_var = tk.StringVar(master=self._frame, value="")
        self.table = BatchMatrixTable(self._frame, BRAZIL_CSPF_MATRIX_SPEC)
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
            BrazilCspfBatchHandler(),
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
            side=tk.LEFT, padx=(6, 0)
        )
        ttk.Button(action_row, text="Copy All", command=self.table.copy_all).pack(
            side=tk.LEFT, padx=(6, 0)
        )
        ttk.Button(action_row, text="Export CSV", command=self._export_csv).pack(
            side=tk.LEFT, padx=(6, 0)
        )
        ttk.Label(action_row, textvariable=self.status_var).pack(
            side=tk.LEFT, padx=(12, 0)
        )
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
        export_table_to_csv(self._frame, "brazil_cspf_batch.csv", headers, rows)


class BrazilCspfBatchAdapter:
    """Composition adapter implementing the common batch dialog protocol."""

    def __init__(self, initial_snapshot: object | None = None) -> None:
        self.initial_snapshot = initial_snapshot
        self.section: BrazilCspfBatchSection | None = None

    @property
    def title(self) -> str:
        return "Brazil CSPF Compliance Batch"

    @property
    def min_size(self) -> tuple[int, int]:
        return BATCH_DIALOG_SAFETY_MIN_SIZE

    def build_content(self, parent: tk.Widget) -> tk.Widget:
        self.section = BrazilCspfBatchSection(
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


class BrazilCspfBatchDialog:
    """Toplevel wrapper using the shared hidden-first batch shell."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        initial_snapshot: object | None = None,
        on_close: Callable[[list[dict[str, str]]], None] | None = None,
    ) -> None:
        self.adapter = BrazilCspfBatchAdapter(initial_snapshot=initial_snapshot)
        self._shell = BatchDialogShell(parent, self.adapter, on_close=on_close)
        self.section = self.adapter.section
        self.window = self._shell.window

    def close(self) -> None:
        self._shell.close()

    def snapshot(self) -> list[dict[str, str]]:
        return self._shell.snapshot()

    def focus(self) -> None:
        self._shell.focus()
