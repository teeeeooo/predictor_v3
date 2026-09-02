"""Appendix M SEER/HSPF batch sections and snapshots."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.ahri_m.batch import (
    AHRI_M_HSPF_BATCH_SPEC,
    AHRI_M_SEER_BATCH_SPEC,
    AhriMHspfBatchCommon,
    AhriMHspfBatchHandler,
    AhriMSeerBatchHandler,
)
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch.matrix_models import BatchMatrixSpec
from apps.calculator.ui.batch.matrix_table import BatchMatrixTable
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.layout_constants import (
    CONTROL_COMPACT_GAP,
    CONTROL_NUMERIC_ENTRY_WIDTH_CHARS,
    CONTROL_ROW_PADY,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
    METRIC_TABLE_POINT_DATA_COLUMN_CHARS,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table_csv_export import export_table_to_csv


@dataclass(frozen=True)
class AhriMBatchSnapshot:
    common_values: Mapping[str, str]
    cases: tuple[Mapping[str, str], ...]
class _BaseBatchSection:
    result_panel = None

    def __init__(self, parent: tk.Widget, *, spec: BatchMatrixSpec, title: str, initial_snapshot: AhriMBatchSnapshot | None = None) -> None:
        self.spec = spec
        self._frame = ttk.LabelFrame(parent, text=title)
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(1, weight=1)
        self.status_var = tk.StringVar(master=self._frame, value="")
        self._common_frame = ttk.LabelFrame(self._frame, text="Common Inputs")
        self._common_frame.grid(row=0, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(ISO_SECTION_BLOCK_GAP, 0))
        self._build_common(initial_snapshot.common_values if initial_snapshot else {})
        self.table = BatchMatrixTable(self._frame, spec)
        self.table.grid(row=1, column=0, sticky="nsew", padx=ISO_SECTION_PADX, pady=CONTROL_ROW_PADY)
        self.table.interaction_controller = TkTableController(self.table)
        if initial_snapshot and initial_snapshot.cases:
            self.table.restore_snapshot(initial_snapshot.cases)
        self._auto_calc = DebouncedAutoCalc(self._frame, self._recalculate_now, delay_ms=150)
        self.table.set_values_changed_callback(self._auto_calc.schedule)
        self._build_actions()
        self._auto_calc.flush_now()

    def _build_common(self, saved: Mapping[str, str]) -> None:
        raise NotImplementedError

    def _recalculate_now(self) -> None:
        raise NotImplementedError

    def common_values(self) -> dict[str, str]:
        raise NotImplementedError
    def _build_actions(self) -> None:
        row = ttk.Frame(self._frame)
        row.grid(row=2, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, ISO_SECTION_BLOCK_GAP))
        for label, command in (("Add Case", self.table.add_case), ("Remove Case", self.table.remove_case), ("Copy All", self.table.copy_all), ("Export CSV", self._export_csv)):
            ttk.Button(row, text=label, command=command).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Label(row, textvariable=self.status_var).pack(side=tk.LEFT, padx=(6, 0))

    def _apply_results(self, handler):
        valid = pending = errors = 0
        results = []
        for index, case in enumerate(self.table.cases):
            result = handler.calculate_row(case)
            results.append(result)
            self.table.set_result(index, result.values)
            if result.state is BatchRowState.OK:
                valid += 1
            elif result.state is BatchRowState.ERROR:
                errors += 1
            else:
                pending += 1
        self.status_var.set(f"{valid} valid / {pending} pending" + (f" / {errors} invalid" if errors else ""))
        return tuple(results)

    def _export_csv(self) -> None:
        headers, rows = self.table.table_export_data()
        common = self.common_values()
        export_table_to_csv(self._frame, f"{self.spec.profile_key}_batch.csv", (*tuple(common), *headers), tuple((*tuple(common.values()), *row) for row in rows))

    def snapshot(self) -> AhriMBatchSnapshot:
        input_keys = set(self.spec.input_keys)
        cases = tuple({key: value for key, value in case.items() if key in input_keys} for case in self.table.cases)
        return AhriMBatchSnapshot(self.common_values(), cases)

    def dispose(self) -> None:
        self._auto_calc.dispose()
class AhriMSeerBatchSection(_BaseBatchSection):
    def __init__(self, parent: tk.Widget, *, initial_snapshot: AhriMBatchSnapshot | None = None) -> None:
        super().__init__(parent, spec=AHRI_M_SEER_BATCH_SPEC, title="AHRI 210/240 M SEER Batch", initial_snapshot=initial_snapshot)

    def _build_common(self, saved: Mapping[str, str]) -> None:
        self.cd_var = tk.StringVar(master=self._frame, value=saved.get("cd", "0.25"))
        ttk.Label(self._common_frame, text="CDc").pack(side=tk.LEFT, padx=(CONTROL_ROW_PADY, CONTROL_COMPACT_GAP), pady=CONTROL_ROW_PADY)
        ttk.Entry(self._common_frame, textvariable=self.cd_var, width=CONTROL_NUMERIC_ENTRY_WIDTH_CHARS).pack(side=tk.LEFT, padx=(0, CONTROL_ROW_PADY), pady=CONTROL_ROW_PADY)
        self.cd_var.trace_add("write", lambda *_args: getattr(self, "_auto_calc", None) and self._auto_calc.schedule())

    def common_values(self) -> dict[str, str]:
        return {"cd": self.cd_var.get()}

    def _recalculate_now(self) -> None:
        self._apply_results(AhriMSeerBatchHandler(self.cd_var.get()))


class AhriMHspfBatchSection(_BaseBatchSection):
    def __init__(self, parent: tk.Widget, *, initial_snapshot: AhriMBatchSnapshot | None = None) -> None:
        super().__init__(parent, spec=AHRI_M_HSPF_BATCH_SPEC, title="AHRI 210/240 M HSPF Batch", initial_snapshot=initial_snapshot)
    def _build_common(self, saved: Mapping[str, str]) -> None:
        defaults = {
            "cd": "0.25", "defrost_test_minutes": "90", "defrost_max_minutes": "720",
            "cut_out_c": "-17.8", "cut_in_c": "-15.0",
            "h1n_same_speed": "0", "automatic_cutout": "1", "demand_defrost": "0",
        }
        defaults.update(saved)
        self._vars = {
            key: tk.StringVar(master=self._frame, value=defaults[key])
            for key in ("h1n_same_speed", "automatic_cutout", "demand_defrost")
        }
        for key, label in (("h1n_same_speed", "H1N=H32 Hz"), ("automatic_cutout", "Automatic Cutout"), ("demand_defrost", "Demand Defrost")):
            ttk.Checkbutton(self._common_frame, text=label, variable=self._vars[key], onvalue="1", offvalue="0").pack(side=tk.LEFT, padx=(CONTROL_ROW_PADY, 0), pady=CONTROL_ROW_PADY)
        self.numeric_table = MetricInputTable(
            self._common_frame,
            columns=(("cd", "CDh"), ("defrost_credit", "Defrost Credit"), ("defrost_test_minutes", "Defrost Test [min]"), ("defrost_max_minutes", "Defrost Max [min]"), ("cut_out_c", "Cut Out [°C]"), ("cut_in_c", "Cut In [°C]")),
            rows=(("value", "Value"),),
            editable_cells={("value", key): key for key in ("cd", "defrost_test_minutes", "defrost_max_minutes", "cut_out_c", "cut_in_c")},
            data_column_chars=METRIC_TABLE_POINT_DATA_COLUMN_CHARS,
            visual_style="shared",
        )
        self.numeric_table.pack(side=tk.LEFT, padx=(CONTROL_ROW_PADY, 0), pady=CONTROL_ROW_PADY)
        self.numeric_table.set_values_batch({key: defaults[key] for key in ("cd", "defrost_test_minutes", "defrost_max_minutes", "cut_out_c", "cut_in_c")})
        self.numeric_table.static_cell_labels[("value", "defrost_credit")].configure(text="1.000")
        self.numeric_table.set_values_changed_callback(lambda: getattr(self, "_auto_calc", None) and self._auto_calc.schedule())
        for variable in self._vars.values():
            variable.trace_add("write", lambda *_args: self._on_option_changed())
        self._apply_option_state()

    @staticmethod
    def _bool(value: str) -> bool:
        return value == "1"

    def common_values(self) -> dict[str, str]:
        values = self.numeric_table.get_text_values()
        values.update({key: variable.get() for key, variable in self._vars.items()})
        return values

    def _on_option_changed(self) -> None:
        self._apply_option_state()
        auto_calc = getattr(self, "_auto_calc", None)
        if auto_calc is not None:
            auto_calc.schedule()

    def _apply_option_state(self) -> None:
        readonly = []
        display_values = {}
        if not self._bool(self._vars["demand_defrost"].get()):
            for address in (("value", "defrost_test_minutes"), ("value", "defrost_max_minutes")):
                readonly.append(address)
                display_values[address] = "N/A"
        if not self._bool(self._vars["automatic_cutout"].get()):
            for address in (("value", "cut_out_c"), ("value", "cut_in_c")):
                readonly.append(address)
                display_values[address] = "No cutout"
        self.numeric_table.set_readonly_addresses(readonly, display_values=display_values)
        self.numeric_table.static_cell_labels[("value", "defrost_credit")].configure(
            text="계산 대기" if self._bool(self._vars["demand_defrost"].get()) else "1.000"
        )

    def _recalculate_now(self) -> None:
        values = self.common_values()
        common = AhriMHspfBatchCommon(
            cd=values["cd"],
            defrost_test_minutes=values["defrost_test_minutes"],
            defrost_max_minutes=values["defrost_max_minutes"],
            cut_out_c=values["cut_out_c"],
            cut_in_c=values["cut_in_c"],
            h1n_same_speed_as_h32=self._bool(values["h1n_same_speed"]),
            automatic_cutout=self._bool(values["automatic_cutout"]),
            demand_defrost=self._bool(values["demand_defrost"]),
        )
        results = self._apply_results(AhriMHspfBatchHandler(common))
        credits = [result.defrost_credit for result in results if result.defrost_credit is not None]
        if credits:
            self.numeric_table.static_cell_labels[("value", "defrost_credit")].configure(text=f"{credits[0]:.3f}")
