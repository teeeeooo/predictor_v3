"""Dual and Triple Northern HSPF2 input surface composition for Tkinter."""

from __future__ import annotations

from collections.abc import Callable, Mapping
import tkinter as tk
from tkinter import ttk

from apps.calculator.application.ahri import (
    AHRI_HSPF2_DUAL_POINT_ORDER,
    AHRI_HSPF2_TEMPERATURES_C,
    AhriHspf2Options,
)
from apps.calculator.application.ahri.product_defaults import (
    AHRI_HSPF2_COMMON_DEFAULTS,
    AHRI_HSPF2_TRIPLE_RANGE_DEFAULTS,
)
from apps.calculator.ui.layout_constants import (
    CONTROL_COMPACT_GAP,
    CONTROL_GROUP_GAP,
    CONTROL_ROW_PADY,
    METRIC_TABLE_ANCHOR_DATA_COLUMN_CHARS,
    METRIC_TABLE_COMPACT_ROW_HEADER_CHARS,
    METRIC_TABLE_DESCRIPTIVE_ROW_HEADER_CHARS,
    METRIC_TABLE_HEATING_DATA_COLUMN_CHARS,
    METRIC_TABLE_POINT_DATA_COLUMN_CHARS,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.table.controller import TkTableController

_TRIPLE_STAGE_POINTS = (
    ("Low Stage", ("H0Low", "H1Low", "H2Low", "H3Low")),
    ("Full Stage", ("H1Full", "H2Full", "H3Full")),
    ("Boost Stage", ("H2Boost", "H3Boost", "H4Boost")),
)


class AhriHspf2ProductSurface:
    """Own active multi-capacity controls, stage tables, and draft state."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        product: str,
        on_values_changed: Callable[[], None],
        snapshot: Mapping[str, object] | None = None,
    ) -> None:
        if product not in {"dual_stage", "triple_capacity_northern"}:
            raise ValueError(f"Unsupported HSPF2 product surface: {product!r}")
        self.product = product
        self._on_values_changed = on_values_changed
        self.frame = ttk.Frame(parent)
        self.frame.surface_role = "ahri_hspf2_multicapacity_surface"
        saved = snapshot or {}
        self._build_control_bar(saved)
        self.numeric_table = self._build_numeric_table(saved)
        self.a2_table = self._build_a2_table(saved)
        self.heating_tables = self._build_heating_tables(saved)
        self.heating_table = self.heating_tables[0]
        self.range_table = (
            self._build_range_table(saved)
            if product == "triple_capacity_northern"
            else None
        )
        self._tables = (
            self.numeric_table,
            self.a2_table,
            *self.heating_tables,
            *((self.range_table,) if self.range_table is not None else ()),
        )
        self._controllers = tuple(TkTableController(table) for table in self._tables)
        for table in self._tables:
            table.set_values_changed_callback(self._on_values_changed)
        self._apply_states()

    def _build_control_bar(self, snapshot: Mapping[str, object]) -> None:
        frame = ttk.LabelFrame(self.frame, text="Product Options")
        frame.grid(row=0, column=0, sticky="w", pady=(0, 6))
        flags = snapshot.get("flags")
        flags = flags if isinstance(flags, Mapping) else {}
        h2_low_default = self.product == "dual_stage"
        self.h4_full_var = tk.BooleanVar(
            master=self.frame, value=bool(flags.get("h4_full", False))
        )
        self.h2_low_var = tk.BooleanVar(
            master=self.frame, value=bool(flags.get("h2_low", h2_low_default))
        )
        self.h2_boost_var = tk.BooleanVar(
            master=self.frame, value=bool(flags.get("h2_boost", True))
        )
        self.h3_low_var = tk.BooleanVar(
            master=self.frame, value=bool(flags.get("h3_low", True))
        )
        self.low_lockout_var = tk.BooleanVar(
            master=self.frame, value=bool(flags.get("low_lockout", False))
        )
        self.defrost_mode_var = tk.StringVar(
            master=self.frame,
            value=str(flags.get("defrost_mode", "explicit_override")),
        )
        options = (
            (
                ("H4Full tested", self.h4_full_var),
                ("H2Low tested", self.h2_low_var),
                ("Low-stage lockout", self.low_lockout_var),
            )
            if self.product == "dual_stage"
            else (
                ("H2Low tested", self.h2_low_var),
                ("H2Boost tested", self.h2_boost_var),
                ("H3Low tested", self.h3_low_var),
            )
        )
        for label, variable in options:
            ttk.Checkbutton(frame, text=label, variable=variable).pack(
                side=tk.LEFT,
                padx=(CONTROL_ROW_PADY, CONTROL_COMPACT_GAP),
                pady=CONTROL_ROW_PADY,
            )
        ttk.Label(frame, text="Defrost").pack(
            side=tk.LEFT, padx=(CONTROL_GROUP_GAP, CONTROL_COMPACT_GAP)
        )
        self.defrost_selector = ttk.Combobox(
            frame,
            textvariable=self.defrost_mode_var,
            values=("none", "explicit_override", "calculated_from_timing"),
            state="readonly",
            width=22,
        )
        self.defrost_selector.pack(
            side=tk.LEFT, padx=(0, CONTROL_ROW_PADY), pady=CONTROL_ROW_PADY
        )
        for variable in (
            self.h4_full_var,
            self.h2_low_var,
            self.h2_boost_var,
            self.h3_low_var,
            self.low_lockout_var,
            self.defrost_mode_var,
        ):
            variable.trace_add("write", lambda *_args: self._on_state_changed())

    def _build_numeric_table(self, snapshot: Mapping[str, object]) -> MetricInputTable:
        columns = [
            ("cut_out_c", "Cut Out [°C]"),
            ("cut_in_c", "Cut In [°C]"),
            ("cd_low", "Cd Low"),
            ("cd_full", "Cd Full"),
        ]
        if self.product == "triple_capacity_northern":
            columns.append(("cd_boost", "Cd Boost"))
        columns.extend(
            (
                ("defrost_factor", "Fdef"),
                ("defrost_t_test_minutes", "Ttest [min]"),
                ("defrost_t_max_minutes", "Tmax [min]"),
            )
        )
        if self.product == "dual_stage":
            columns.append(("low_stage_lockout_temp_c", "Low Lockout [°C]"))
        table = MetricInputTable(
            self.frame,
            columns=tuple(columns),
            rows=(("value", "Value"),),
            editable_cells={("value", key): key for key, _label in columns},
            row_header_chars=METRIC_TABLE_COMPACT_ROW_HEADER_CHARS,
            data_column_chars=METRIC_TABLE_POINT_DATA_COLUMN_CHARS,
            visual_style="shared",
        )
        table.grid(row=1, column=0, sticky="w", pady=(0, 6))
        values = dict(AHRI_HSPF2_COMMON_DEFAULTS)
        saved = snapshot.get("numeric_values")
        if isinstance(saved, Mapping):
            values.update({key: str(value) for key, value in saved.items()})
        table.set_values_batch(
            {key: value for key, value in values.items() if key in table.field_order}
        )
        return table

    def _build_a2_table(self, snapshot: Mapping[str, object]) -> MetricInputTable:
        table = MetricInputTable(
            self.frame,
            columns=(("A2", "A2"),),
            rows=(("capacity", "Capacity [Btu/h]"),),
            editable_cells={("capacity", "A2"): "a2_capacity"},
            row_header_chars=METRIC_TABLE_DESCRIPTIVE_ROW_HEADER_CHARS,
            data_column_chars=METRIC_TABLE_ANCHOR_DATA_COLUMN_CHARS,
            visual_style="shared",
        )
        table.grid(row=2, column=0, sticky="w", pady=(0, 6))
        saved = snapshot.get("a2_values")
        if isinstance(saved, Mapping):
            table.set_values_batch(
                {key: str(value) for key, value in saved.items() if key in table.field_order}
            )
        return table

    def _build_heating_tables(
        self, snapshot: Mapping[str, object]
    ) -> tuple[MetricInputTable, ...]:
        saved = snapshot.get("heating_values")
        saved = saved if isinstance(saved, Mapping) else {}
        groups = (
            (("Dual Stage", AHRI_HSPF2_DUAL_POINT_ORDER),)
            if self.product == "dual_stage"
            else _TRIPLE_STAGE_POINTS
        )
        tables = []
        for offset, (title, points) in enumerate(groups):
            host = ttk.LabelFrame(self.frame, text=title)
            host.grid(row=3 + offset, column=0, sticky="w", pady=(0, 6))
            table = self._build_stage_table(host, points, saved)
            table.grid(row=0, column=0, sticky="w")
            tables.append(table)
        return tuple(tables)

    @staticmethod
    def _build_stage_table(
        parent: tk.Widget,
        points: tuple[str, ...],
        saved: Mapping[str, object],
    ) -> MetricInputTable:
        table = MetricInputTable(
            parent,
            columns=tuple((point, point) for point in points),
            rows=(
                ("condition_temp", "Condition / Temp"),
                ("capacity", "Capacity [Btu/h]"),
                ("power", "Power [W]"),
                ("cop", "COP"),
            ),
            editable_cells={
                (row, point): f"{row}_{point}"
                for point in points
                for row in ("capacity", "power")
            },
            row_header_chars=METRIC_TABLE_DESCRIPTIVE_ROW_HEADER_CHARS,
            data_column_chars=METRIC_TABLE_HEATING_DATA_COLUMN_CHARS,
            visual_style="shared",
        )
        for point in points:
            table.static_cell_labels[("condition_temp", point)].configure(
                text=f"Heating / {AHRI_HSPF2_TEMPERATURES_C[point]:.1f} °C"
            )
            table.static_cell_labels[("cop", point)].configure(text="")
        table.set_values_batch(
            {key: str(value) for key, value in saved.items() if key in table.field_order}
        )
        return table

    def _build_range_table(self, snapshot: Mapping[str, object]) -> MetricInputTable:
        columns = (
            ("low_min_c", "Low Min [°C]"),
            ("low_max_c", "Low Max [°C]"),
            ("full_min_c", "Full Min [°C]"),
            ("full_max_c", "Full Max [°C]"),
            ("boost_min_c", "Boost Min [°C]"),
            ("boost_max_c", "Boost Max [°C]"),
        )
        table = MetricInputTable(
            self.frame,
            columns=columns,
            rows=(("value", "Stage Range"),),
            editable_cells={("value", key): key for key, _label in columns},
            row_header_chars=METRIC_TABLE_COMPACT_ROW_HEADER_CHARS,
            data_column_chars=METRIC_TABLE_POINT_DATA_COLUMN_CHARS,
            visual_style="shared",
        )
        table.grid(row=6, column=0, sticky="w", pady=(0, 6))
        values = dict(AHRI_HSPF2_TRIPLE_RANGE_DEFAULTS)
        saved = snapshot.get("range_values")
        if isinstance(saved, Mapping):
            values.update({key: str(value) for key, value in saved.items()})
        table.set_values_batch(values)
        return table

    def _on_state_changed(self) -> None:
        self._apply_states()
        self._on_values_changed()

    def _apply_states(self) -> None:
        optional = self._optional_point_state()
        for table in self.heating_tables:
            readonly = {
                (row, point)
                for point, enabled in optional.items()
                if not enabled and point in dict(table.columns)
                for row in ("capacity", "power")
            }
            table.set_readonly_addresses(
                readonly, display_values={address: "" for address in readonly}
            )
        mode = self.defrost_mode_var.get()
        enabled_numeric = {
            "defrost_factor": mode == "explicit_override",
            "defrost_t_test_minutes": mode == "calculated_from_timing",
            "defrost_t_max_minutes": mode == "calculated_from_timing",
        }
        if self.product == "dual_stage":
            enabled_numeric["low_stage_lockout_temp_c"] = self.low_lockout_var.get()
        numeric_readonly = {
            ("value", key)
            for key, enabled in enabled_numeric.items()
            if not enabled
        }
        self.numeric_table.set_readonly_addresses(
            numeric_readonly,
            display_values={address: "" for address in numeric_readonly},
        )
        if hasattr(self, "_controllers"):
            for controller in self._controllers:
                controller.refresh()

    def _optional_point_state(self) -> dict[str, bool]:
        if self.product == "dual_stage":
            return {
                "H2Low": self.h2_low_var.get(),
                "H4Full": self.h4_full_var.get(),
            }
        return {
            "H2Low": self.h2_low_var.get(),
            "H2Boost": self.h2_boost_var.get(),
            "H3Low": self.h3_low_var.get(),
        }

    def grid(self, **kwargs: object) -> None:
        self.frame.grid(**kwargs)

    def tables(self) -> tuple[MetricInputTable, ...]:
        return self._tables

    def text_values(self) -> dict[str, str]:
        values: dict[str, str] = {}
        for table in self._tables:
            values.update(table.get_text_values())
        return values

    def options(self, *, region: str = "IV") -> AhriHspf2Options:
        return AhriHspf2Options(
            region=region,
            product_classification=self.product,
            measured_h4_full=self.h4_full_var.get(),
            measured_h2_low=self.h2_low_var.get(),
            measured_h2_boost=self.h2_boost_var.get(),
            measured_h3_low=self.h3_low_var.get(),
            low_stage_lockout_enabled=self.low_lockout_var.get(),
            defrost_mode=self.defrost_mode_var.get(),
        )

    def snapshot(self) -> dict[str, object]:
        heating_values: dict[str, str] = {}
        for table in self.heating_tables:
            heating_values.update(table.get_text_values())
        result: dict[str, object] = {
            "numeric_values": self.numeric_table.get_text_values(),
            "a2_values": self.a2_table.get_text_values(),
            "heating_values": heating_values,
            "flags": {
                "h4_full": self.h4_full_var.get(),
                "h2_low": self.h2_low_var.get(),
                "h2_boost": self.h2_boost_var.get(),
                "h3_low": self.h3_low_var.get(),
                "low_lockout": self.low_lockout_var.get(),
                "defrost_mode": self.defrost_mode_var.get(),
            },
        }
        if self.range_table is not None:
            result["range_values"] = self.range_table.get_text_values()
        return result

    def update_cop_rows(self, cops: Mapping[str, float]) -> None:
        for table in self.heating_tables:
            for point in dict(table.columns):
                table.static_cell_labels[("cop", point)].configure(
                    text=f"{cops[point]:.2f}" if point in cops else ""
                )

    def clear_results(self) -> None:
        self.update_cop_rows({})

    def clear_invalid_fields(self) -> None:
        for table in self._tables:
            table.clear_invalid_fields()

    def set_invalid_fields(self, errors: Mapping[str, str]) -> None:
        for table in self._tables:
            subset = {
                key: value for key, value in errors.items() if key in table.field_order
            }
            if subset:
                table.set_invalid_fields(subset)
