"""Headless table model containing SCOP row/column structure, cell values, and state metadata."""

from typing import Dict, Tuple
from apps.calculator.ui.en14825.scop_models import ScopPointInput, ScopPointComputed
from apps.calculator.ui.en14825.scop_adapter import ScopAdapter


class ScopTableModel:
    """Headless table model to feed data and cell metadata into UI widgets for SCOP."""

    ROW_KEYS = (
        "condition_temp",
        "part_load_ratio",
        "part_load_w",
        "declared_capacity",
        "declared_cop",
        "tested_capacity",
        "tested_power",
        "tested_cop",
        "capacity_percent",
        "cop_percent",
    )

    COL_KEYS = ("A", "B", "C", "D", "TOL", "Tbiv")

    ROW_LABELS = {
        "condition_temp": "Condition / Temp",
        "part_load_ratio": "Part load %",
        "part_load_w": "Part load [W]",
        "declared_capacity": "Declared capacity [W]",
        "declared_cop": "Declared COP",
        "tested_capacity": "Tested capacity [W]",
        "tested_power": "Tested power [W]",
        "tested_cop": "Tested COP",
        "capacity_percent": "Capacity %",
        "cop_percent": "COP %",
    }

    OUTDOOR_TEMPS = {
        "A": -7.0,
        "B": 2.0,
        "C": 7.0,
        "D": 12.0,
    }

    # Grouping break rows for MetricInputTable rendering
    SECTION_BREAK_BEFORE_ROWS = (
        "declared_capacity",
        "tested_capacity",
        "capacity_percent",
    )

    def __init__(
        self,
        inputs: Dict[str, ScopPointInput],
        computed: Dict[str, ScopPointComputed],
        p_design_h_w: float,
        climate: str,
        t_design_h: float,
        tbiv_temp_c: float,
        tol_temp_c: float,
    ) -> None:
        self.inputs = inputs
        self.computed = computed
        self.p_design_h_w = p_design_h_w
        self.climate = climate
        self.t_design_h = t_design_h
        self.tbiv_temp_c = tbiv_temp_c
        self.tol_temp_c = tol_temp_c

    def get_row_keys(self) -> Tuple[str, ...]:
        """Return table row keys in visual order."""
        return self.ROW_KEYS

    def get_col_keys(self) -> Tuple[str, ...]:
        """Return table column keys."""
        return self.COL_KEYS

    def get_row_label(self, row_key: str) -> str:
        """Return the user-facing label for a row key."""
        return self.ROW_LABELS.get(row_key, row_key)

    def get_col_label(self, col_key: str) -> str:
        """Return the user-facing label for a column key, incorporating active temperatures."""
        if col_key in self.OUTDOOR_TEMPS:
            temp = self.OUTDOOR_TEMPS[col_key]
            return f"{col_key} ({temp:.0f}°C)"
        if col_key == "TOL":
            return f"TOL ({self.tol_temp_c:.0f}°C)"
        if col_key == "Tbiv":
            return f"Tbiv ({self.tbiv_temp_c:.0f}°C)"
        return col_key

    def is_editable(self, row_key: str, col_key: str) -> bool:
        """Return True if the specified cell is user-editable."""
        return row_key in (
            "declared_capacity",
            "declared_cop",
            "tested_capacity",
            "tested_power",
        )

    def get_value(self, row_key: str, col_key: str) -> str:
        """Return the formatted string representation of the cell value."""
        inp = self.inputs.get(col_key)
        comp = self.computed.get(col_key)

        # 1. Condition Temperature (fixed DB or TOL/Tbiv active temperature)
        if row_key == "condition_temp":
            if col_key in self.OUTDOOR_TEMPS:
                temp = self.OUTDOOR_TEMPS[col_key]
                return f"{temp:.0f}°C"
            if col_key == "TOL":
                return f"{self.tol_temp_c:.0f}°C"
            if col_key == "Tbiv":
                return f"{self.tbiv_temp_c:.0f}°C"
            return ""

        # 2. Part Load Ratio (%) and Part Load (W)
        if row_key in ("part_load_ratio", "part_load_w"):
            if col_key in self.OUTDOOR_TEMPS:
                temp = self.OUTDOOR_TEMPS[col_key]
            elif col_key == "TOL":
                temp = self.tol_temp_c
            elif col_key == "Tbiv":
                temp = self.tbiv_temp_c
            else:
                return ""

            ratio_pct, load_w = ScopAdapter.get_part_load_info(temp, self.p_design_h_w, self.t_design_h)
            if row_key == "part_load_ratio":
                return f"{ratio_pct:.0f}%"
            else:
                return f"{load_w:.0f}"

        # 3. Editable Input Fields
        if row_key == "declared_capacity":
            val = inp.declared_capacity if inp else None
            return f"{val:.0f}" if val is not None else ""
        if row_key == "declared_cop":
            val = inp.declared_cop if inp else None
            return f"{val:.2f}" if val is not None else ""
        if row_key == "tested_capacity":
            val = inp.tested_capacity if inp else None
            return f"{val:.0f}" if val is not None else ""
        if row_key == "tested_power":
            val = inp.tested_power if inp else None
            return f"{val:.0f}" if val is not None else ""

        # 4. Computed Fields
        if row_key == "tested_cop":
            val = comp.tested_cop if comp else None
            return f"{val:.2f}" if val is not None else ""
        if row_key == "capacity_percent":
            val = comp.capacity_percent if comp else None
            return f"{val:.1f}%" if val is not None else ""
        if row_key == "cop_percent":
            val = comp.cop_percent if comp else None
            return f"{val:.1f}%" if val is not None else ""

        return ""

    def get_state(self, row_key: str, col_key: str) -> str:
        """Return the visual state of the cell ("neutral", "pass", "invalid", "unavailable")."""
        comp = self.computed.get(col_key)
        if not comp:
            return "unavailable"

        if row_key == "condition_temp":
            return "neutral"
        if row_key in ("part_load_ratio", "part_load_w"):
            return "neutral" if self.p_design_h_w > 0 else "unavailable"

        if row_key == "declared_capacity":
            return comp.declared_capacity_state
        if row_key == "declared_cop":
            return comp.declared_cop_state
        if row_key == "tested_capacity":
            return comp.tested_capacity_state
        if row_key == "tested_power":
            return comp.tested_power_state
        if row_key == "tested_cop":
            return comp.tested_cop_state
        if row_key == "capacity_percent":
            return comp.capacity_percent_state
        if row_key == "cop_percent":
            return comp.cop_percent_state

        return "unavailable"
