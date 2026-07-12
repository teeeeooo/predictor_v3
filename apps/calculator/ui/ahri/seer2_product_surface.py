"""Product-specific SEER2 input surface composition for Tkinter."""

from __future__ import annotations

from collections.abc import Callable, Mapping
import tkinter as tk
from tkinter import ttk

from apps.calculator.application.ahri import (
    AHRI_SEER2_DUAL_POINT_ORDER,
    AHRI_SEER2_POINT_ORDER,
    AHRI_SEER2_TEMPERATURES_C,
    AhriSeer2Options,
)
from apps.calculator.application.ahri.seer2_adapter import (
    AHRI_SEER2_DUAL_DEFAULTS,
)
from apps.calculator.ui.layout_constants import (
    CONTROL_COMPACT_GAP,
    CONTROL_ROW_PADY,
    METRIC_TABLE_COMPACT_ROW_HEADER_CHARS,
    METRIC_TABLE_DESCRIPTIVE_ROW_HEADER_CHARS,
    METRIC_TABLE_POINT_DATA_COLUMN_CHARS,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.table.controller import TkTableController


class AhriSeer2ProductSurface:
    """Own the active product table, product-only options, and draft values."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        product: str,
        on_values_changed: Callable[[], None],
        snapshot: Mapping[str, object] | None = None,
    ) -> None:
        self.product = product
        self._on_values_changed = on_values_changed
        self.frame = ttk.Frame(parent)
        self.frame.surface_role = "ahri_seer2_product_surface"
        self.options_table: MetricInputTable | None = None
        self.lockout_var: tk.BooleanVar | None = None
        self._build(snapshot or {})

    def _build(self, snapshot: Mapping[str, object]) -> None:
        if self.product == "dual_stage":
            self._build_dual_options(snapshot)
        point_order = (
            AHRI_SEER2_POINT_ORDER
            if self.product == "variable_capacity"
            else AHRI_SEER2_DUAL_POINT_ORDER
        )
        editable = {
            (row, point): f"{row}_{point}"
            for point in point_order
            for row in ("capacity", "power")
        }
        self.input_table = MetricInputTable(
            self.frame,
            columns=tuple((point, point) for point in point_order),
            rows=(
                ("condition_temp", "Condition / Temp"),
                ("capacity", "Capacity [Btu/h]"),
                ("power", "Power [W]"),
                ("eer2", "EER2"),
            ),
            editable_cells=editable,
            row_header_chars=METRIC_TABLE_DESCRIPTIVE_ROW_HEADER_CHARS,
            data_column_chars=METRIC_TABLE_POINT_DATA_COLUMN_CHARS,
            layout_policy="content_hug",
            values_changed_callback=self._on_values_changed,
            visual_style="shared",
        )
        table_row = 1 if self.options_table is not None else 0
        self.input_table.grid(row=table_row, column=0, sticky="w")
        self.controller = TkTableController(self.input_table)
        for point in point_order:
            self.input_table.static_cell_labels[
                ("condition_temp", point)
            ].configure(
                text=f"Cooling / {AHRI_SEER2_TEMPERATURES_C[point]:.1f} °C"
            )
            self.input_table.static_cell_labels[("eer2", point)].configure(
                text=""
            )
        table_values = snapshot.get("table_values", snapshot)
        if isinstance(table_values, Mapping):
            values = {
                key: str(value)
                for key, value in table_values.items()
                if key in self.input_table.field_order
            }
            if values:
                self.input_table.set_values_batch(values)

    def _build_dual_options(self, snapshot: Mapping[str, object]) -> None:
        option_frame = ttk.LabelFrame(self.frame, text="Dual-stage Options")
        option_frame.grid(row=0, column=0, sticky="w", pady=(0, 6))
        saved_lockout = bool(
            snapshot.get("low_stage_lockout_enabled", False)
        )
        self.lockout_var = tk.BooleanVar(
            master=self.frame, value=saved_lockout
        )
        ttk.Checkbutton(
            option_frame,
            text="Low-stage lockout",
            variable=self.lockout_var,
            command=self._on_values_changed,
        ).pack(
            side=tk.LEFT,
            padx=(CONTROL_ROW_PADY, CONTROL_COMPACT_GAP),
            pady=CONTROL_ROW_PADY,
        )
        self.options_table = MetricInputTable(
            option_frame,
            columns=(
                ("cd_low", "Cd Low"),
                ("cd_full", "Cd Full"),
                ("low_stage_lockout_temp_f", "Lockout [°F]"),
            ),
            rows=(("value", "Value"),),
            editable_cells={
                ("value", "cd_low"): "cd_low",
                ("value", "cd_full"): "cd_full",
                (
                    "value",
                    "low_stage_lockout_temp_f",
                ): "low_stage_lockout_temp_f",
            },
            row_header_chars=METRIC_TABLE_COMPACT_ROW_HEADER_CHARS,
            data_column_chars=METRIC_TABLE_POINT_DATA_COLUMN_CHARS,
            values_changed_callback=self._on_values_changed,
            visual_style="shared",
        )
        self.options_table.pack(
            side=tk.LEFT,
            padx=(0, CONTROL_ROW_PADY),
            pady=CONTROL_ROW_PADY,
        )
        defaults = dict(AHRI_SEER2_DUAL_DEFAULTS)
        saved_options = snapshot.get("option_values")
        if isinstance(saved_options, Mapping):
            defaults.update(
                {key: str(value) for key, value in saved_options.items()}
            )
        self.options_table.set_values_batch(defaults)
        self.options_controller = TkTableController(self.options_table)
        self._apply_lockout_state()
        self.lockout_var.trace_add(
            "write", lambda *_args: self._apply_lockout_state()
        )

    def _apply_lockout_state(self) -> None:
        if self.options_table is None or self.lockout_var is None:
            return
        address = ("value", "low_stage_lockout_temp_f")
        if self.lockout_var.get():
            self.options_table.set_readonly_addresses(())
        else:
            self.options_table.set_readonly_addresses(
                (address,),
                display_values={address: ""},
            )
        self.options_controller.refresh()

    def grid(self, **kwargs: object) -> None:
        self.frame.grid(**kwargs)

    def snapshot(self) -> dict[str, object]:
        result: dict[str, object] = {
            "table_values": self.input_table.get_text_values(),
        }
        if self.options_table is not None:
            result["option_values"] = self.options_table.get_text_values()
        if self.lockout_var is not None:
            result["low_stage_lockout_enabled"] = self.lockout_var.get()
        return result

    def text_values(self) -> dict[str, str]:
        values = dict(self.input_table.get_text_values())
        if self.options_table is not None:
            values.update(self.options_table.get_text_values())
        return values

    def options(self) -> AhriSeer2Options:
        if self.product == "variable_capacity":
            return AhriSeer2Options()
        return AhriSeer2Options(
            product_classification="dual_stage",
            low_stage_lockout_enabled=bool(
                self.lockout_var and self.lockout_var.get()
            ),
        )

    def set_result_eer2(self, values: Mapping[str, float]) -> None:
        for point, value in values.items():
            label = self.input_table.static_cell_labels.get(("eer2", point))
            if label is not None:
                label.configure(text=f"{value:.2f}")

    def clear_result_eer2(self) -> None:
        for point in dict(self.input_table.columns):
            label = self.input_table.static_cell_labels.get(("eer2", point))
            if label is not None:
                label.configure(text="")

    def set_invalid_fields(self, errors: Mapping[str, str]) -> None:
        table_errors = {
            key: value
            for key, value in errors.items()
            if key in self.input_table.field_order
        }
        self.input_table.set_invalid_fields(table_errors)
        if self.options_table is not None:
            option_errors = {
                key: value
                for key, value in errors.items()
                if key in self.options_table.field_order
            }
            self.options_table.set_invalid_fields(option_errors)

    def clear_invalid_fields(self) -> None:
        self.input_table.clear_invalid_fields()
        if self.options_table is not None:
            self.options_table.clear_invalid_fields()
