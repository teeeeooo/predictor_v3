"""Hong Kong HSPF batch profile adapters and wrappers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

from core.calculators.dispatcher import create_calculator_for_profile
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch.controller import BatchMatrixCalculationController
from apps.calculator.ui.batch.matrix_models import (
    FULL_CAPACITY,
    FULL_POWER,
    HALF_CAPACITY,
    HALF_POWER,
    HONG_KONG_HSPF_MATRIX_SPEC,
    HSEC,
    HSPF,
    HSTL,
)
from apps.calculator.ui.batch.matrix_table import BatchMatrixTable
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.batch_dialogs.shell import BatchDialogShell
from apps.calculator.ui.layout_constants import (
    BATCH_DIALOG_SAFETY_MIN_SIZE,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.profile_resolver import resolve_profile_id
from apps.calculator.ui.sections.iso16358_helpers import build_hspf_input
from apps.calculator.ui.sections.result_formatting import summarize_hspf_result
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table_csv_export import export_table_to_csv
from apps.calculator.ui.table_grid_model import parse_numeric_cell

_REQUIRED_INPUT_KEYS = (FULL_CAPACITY, FULL_POWER, HALF_CAPACITY, HALF_POWER)


@dataclass(frozen=True)
class HongKongHspfBatchResult:
    values: dict[str, str]
    state: BatchRowState


class HongKongHspfBatchHandler:
    """Calculate Hong Kong HSPF matrix batch cases."""

    spec = HONG_KONG_HSPF_MATRIX_SPEC

    def __init__(self, region_label: str = "Hong Kong") -> None:
        self._region_label = region_label

    def calculate_row(self, row: Mapping[str, str]) -> HongKongHspfBatchResult:
        if not _has_complete_required_inputs(row):
            return _blank_result()
        try:
            measured = build_hspf_input(
                full_capacity=_required_number(row, FULL_CAPACITY, "7 Full Capacity"),
                full_power=_required_number(row, FULL_POWER, "7 Full Power"),
                half_capacity=_required_number(row, HALF_CAPACITY, "7 Half Capacity"),
                half_power=_required_number(row, HALF_POWER, "7 Half Power"),
            )
            profile_id = resolve_profile_id(self._region_label, "HSPF")
            calc = create_calculator_for_profile(profile_id=profile_id)
            result = calc.calculate_hspf(measured)
            fields = dict(summarize_hspf_result(result).fields)
            return HongKongHspfBatchResult(
                values={
                    HSPF: fields.get("HSPF", "-"),
                    HSTL: fields.get("HSTL [kWh]", "-"),
                    HSEC: fields.get("HSEC [kWh]", "-"),
                },
                state=BatchRowState.OK,
            )
        except Exception:
            return _blank_result(BatchRowState.ERROR)


class HongKongHspfBatchSection:
    """Two-row matrix batch surface for Hong Kong HSPF cases."""

    result_panel = None

    def __init__(
        self,
        parent: tk.Widget,
        region_label: str,
        *,
        initial_snapshot: object | None = None,
    ) -> None:
        self._frame = ttk.LabelFrame(parent, text=f"HSPF Batch ({region_label})")
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(0, weight=1)
        self.status_var = tk.StringVar(master=self._frame, value="")
        self.table = BatchMatrixTable(self._frame, HONG_KONG_HSPF_MATRIX_SPEC)
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
            HongKongHspfBatchHandler(region_label),
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
        ttk.Button(action_row, text="Add Case", command=self.table.add_case).pack(
            side=tk.LEFT
        )
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
        export_table_to_csv(self._frame, "hong_kong_hspf_batch.csv", headers, rows)


class HongKongHspfBatchAdapter:
    """Composition adapter implementing BatchProfileAdapter for Hong Kong HSPF."""

    def __init__(self, region_label: str, initial_snapshot: object | None = None) -> None:
        self.region_label = region_label
        self.initial_snapshot = initial_snapshot
        self.section: HongKongHspfBatchSection | None = None

    @property
    def title(self) -> str:
        return f"HSPF Batch ({self.region_label})"

    @property
    def min_size(self) -> tuple[int, int]:
        return BATCH_DIALOG_SAFETY_MIN_SIZE

    def build_content(self, parent: tk.Widget) -> tk.Widget:
        self.section = HongKongHspfBatchSection(
            parent,
            self.region_label,
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


class HongKongHspfBatchDialog:
    """Toplevel owner wrapper for Hong Kong HSPF batch dialog."""

    def __init__(
        self,
        parent: tk.Widget,
        region_label: str,
        *,
        initial_snapshot: object | None = None,
        on_close: Callable[[list[dict[str, str]]], None] | None = None,
    ) -> None:
        self.adapter = HongKongHspfBatchAdapter(
            region_label,
            initial_snapshot=initial_snapshot,
        )
        self._shell = BatchDialogShell(parent, self.adapter, on_close=on_close)
        self.section = self.adapter.section
        self.window = self._shell.window

    def close(self) -> None:
        self._shell.close()

    def snapshot(self) -> list[dict[str, str]]:
        return self._shell.snapshot()

    def focus(self) -> None:
        self._shell.focus()


def _required_number(row: Mapping[str, str], key: str, label: str) -> float:
    try:
        return parse_numeric_cell(str(row.get(key, "")))
    except ValueError as exc:
        raise ValueError(f"{label}: {exc}") from exc


def _has_complete_required_inputs(row: Mapping[str, str]) -> bool:
    return all(str(row.get(key, "")).strip() for key in _REQUIRED_INPUT_KEYS)


def _blank_result(
    state: BatchRowState = BatchRowState.PENDING,
) -> HongKongHspfBatchResult:
    return HongKongHspfBatchResult(
        values={HSPF: "", HSTL: "", HSEC: ""},
        state=state,
    )
