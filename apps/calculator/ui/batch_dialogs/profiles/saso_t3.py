"""SASO T3 batch profile adapters and wrappers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
import tkinter as tk
from tkinter import ttk

from core.calculator_dispatcher import create_calculator_for_profile
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
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
from apps.calculator.ui.profile_resolver import MODE_SASO_T3, resolve_calculation_mode_profile_id
from apps.calculator.ui.sections.result_formatting import kwh_value, metric_value
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table_csv_export import export_table_to_csv
from apps.calculator.ui.table_grid_model import parse_numeric_cell
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
class _MatrixCalculationSummary:
    valid_rows: int
    blank_rows: int
    error_rows: int


@dataclass(frozen=True)
class BatchCalculationResult:
    values: dict[str, str]
    state: BatchRowState


class SasoT3BatchHandler:
    """Calculates row cases for SASO T3 batch."""

    spec = SASO_T3_MATRIX_SPEC

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
            full_46_cap = parse_numeric_cell(str(row.get("full_46_capacity", "")))
            full_46_pw = parse_numeric_cell(str(row.get("full_46_power", "")))
            full_35_cap = parse_numeric_cell(str(row.get("full_35_capacity", "")))
            full_35_pw = parse_numeric_cell(str(row.get("full_35_power", "")))
            half_35_cap = parse_numeric_cell(str(row.get("half_35_capacity", "")))
            half_35_pw = parse_numeric_cell(str(row.get("half_35_power", "")))

            # Positivity check
            for val in (full_46_cap, full_46_pw, full_35_cap, full_35_pw, half_35_cap, half_35_pw):
                if val <= 0:
                    raise ValueError("positivity check failed")

            required_measured = {
                "46_full": {
                    "capacity": full_46_cap,
                    "power": full_46_pw,
                },
                "35_full": {
                    "capacity": full_35_cap,
                    "power": full_35_pw,
                },
                "35_half": {
                    "capacity": half_35_cap,
                    "power": half_35_pw,
                },
            }

            # Calculate Required-only (3-point)
            calc = create_calculator_for_profile(
                profile_id=resolve_calculation_mode_profile_id(MODE_SASO_T3)
            )
            calc.config["cspf_test_profile"]["test_selection"] = "required_only"
            req_res = calc.calculate_cspf(required_measured)
            req_cspf_val = metric_value(req_res, "cspf")
            req_cstl_val = kwh_value(req_res, ("annual_cooling_kwh", "cstl_kwh", "cstl"))
            req_csec_val = kwh_value(req_res, ("annual_power_kwh", "csec_kwh", "csec"))

            # Check optional inputs
            opt_cap_str = str(row.get("min_35_capacity", "")).strip()
            opt_pw_str = str(row.get("min_35_power", "")).strip()

            opt_cspf_val = ""
            opt_cstl_val = ""
            opt_csec_val = ""
            has_optional_error = False
            has_optional = False

            if not opt_cap_str and not opt_pw_str:
                # Both blank: OK, no optional calculation
                pass
            elif opt_cap_str and opt_pw_str:
                # Both present: try calculating 4pt
                has_optional = True
            else:
                # One present, one blank: error
                has_optional_error = True

            if has_optional and not has_optional_error:
                try:
                    min_35_cap = parse_numeric_cell(opt_cap_str)
                    min_35_pw = parse_numeric_cell(opt_pw_str)

                    if min_35_cap <= 0 or min_35_pw <= 0:
                        raise ValueError("positivity check failed")

                    optional_measured = {
                        "46_full": {
                            "capacity": full_46_cap,
                            "power": full_46_pw,
                        },
                        "35_full": {
                            "capacity": full_35_cap,
                            "power": full_35_pw,
                        },
                        "35_half": {
                            "capacity": half_35_cap,
                            "power": half_35_pw,
                        },
                        "35_min": {
                            "capacity": min_35_cap,
                            "power": min_35_pw,
                        },
                    }

                    # Calculate With 35 Min (4-point)
                    opt_calc = create_calculator_for_profile(
                        profile_id=resolve_calculation_mode_profile_id(MODE_SASO_T3)
                    )
                    opt_calc.config["cspf_test_profile"]["test_selection"] = "with_optional_test"
                    opt_res = opt_calc.calculate_cspf(optional_measured)
                    opt_cspf_val = metric_value(opt_res, "cspf")
                    opt_cstl_val = kwh_value(opt_res, ("annual_cooling_kwh", "cstl_kwh", "cstl"))
                    opt_csec_val = kwh_value(opt_res, ("annual_power_kwh", "csec_kwh", "csec"))
                except Exception:
                    has_optional_error = True

            state = BatchRowState.OK
            if has_optional_error:
                state = BatchRowState.ERROR

            return BatchCalculationResult(
                values={
                    "req_cspf": req_cspf_val,
                    "req_cstl": req_cstl_val,
                    "req_csec": req_csec_val,
                    "opt_cspf": opt_cspf_val,
                    "opt_cstl": opt_cstl_val,
                    "opt_csec": opt_csec_val,
                },
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


class SasoT3MatrixController:
    """Batch matrix calculation adapter for SASO T3."""

    def __init__(self, table: BatchMatrixTable, handler: SasoT3BatchHandler) -> None:
        self._table = table
        self._handler = handler

    def recalculate(self) -> _MatrixCalculationSummary:
        valid = 0
        blank = 0
        error = 0
        for index, case in enumerate(self._table.cases):
            result = self._handler.calculate_row(case)
            self._table.set_result(index, result.values)
            if result.state is BatchRowState.OK:
                valid += 1
            elif result.state is BatchRowState.ERROR:
                error += 1
            else:
                blank += 1
        return _MatrixCalculationSummary(valid, blank, error)


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
        self.controller = SasoT3MatrixController(
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
