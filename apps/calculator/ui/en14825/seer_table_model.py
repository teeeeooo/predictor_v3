"""Headless table model containing SEER row/column structure, cell values, and state metadata."""

from typing import Dict, Tuple
from core.calculator_en14825 import T_DESIGN_C
from apps.calculator.ui.en14825.seer_models import SeerPointInput, SeerPointComputed
from apps.calculator.ui.en14825.seer_adapter import SeerAdapter

class SeerTableModel:
    """Headless table model to feed data and cell metadata into UI widgets."""

    # Note: declared_power_w_for_core is adapter/core only and must never be exposed here as a table row.
    ROW_KEYS = (
        "condition_temp",
        "part_load_ratio",
        "part_load_w",
        "declared_capacity",
        "declared_eer",
        "tested_capacity",
        "tested_power",
        "tested_eer",
        "capacity_percent",
        "eer_percent",
    )

    COL_KEYS = ("A", "B", "C", "D")

    ROW_LABELS = {
        "condition_temp": "Condition / Temp",
        "part_load_ratio": "Part load %",
        "part_load_w": "Part load [W]",
        "declared_capacity": "Declared capacity [W]",
        "declared_eer": "Declared EER",
        "tested_capacity": "Tested capacity [W]",
        "tested_power": "Tested power [W]",
        "tested_eer": "Tested EER",
        "capacity_percent": "Capacity %",
        "eer_percent": "EER %",
    }

    COL_LABELS = {
        "A": "A (35°C)",
        "B": "B (30°C)",
        "C": "C (25°C)",
        "D": "D (20°C)",
    }

    # Outdoor temperatures mapping for A, B, C, D
    OUTDOOR_TEMPS = {
        "A": 35.0,
        "B": 30.0,
        "C": 25.0,
        "D": 20.0,
    }

    def __init__(
        self,
        inputs: Dict[str, SeerPointInput],
        computed: Dict[str, SeerPointComputed],
        p_design_c_w: float,
        t_design_c: float = T_DESIGN_C,
    ) -> None:
        self.inputs = inputs
        self.computed = computed
        self.p_design_c_w = p_design_c_w
        self.t_design_c = t_design_c

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
        """Return the user-facing label for a column key."""
        return self.COL_LABELS.get(col_key, col_key)

    def is_editable(self, row_key: str, col_key: str) -> bool:
        """Return True if the specified cell is user-editable."""
        return row_key in (
            "declared_capacity",
            "declared_eer",
            "tested_capacity",
            "tested_power",
        )

    def get_value(self, row_key: str, col_key: str) -> str:
        """Return the formatted string representation of the cell value."""
        inp = self.inputs.get(col_key)
        comp = self.computed.get(col_key)

        # 1. Condition Temperature (fixed DB)
        if row_key == "condition_temp":
            temp = self.OUTDOOR_TEMPS.get(col_key)
            return f"{temp:.0f}°C" if temp is not None else ""

        # 2. Part Load Ratio (%) and Part Load (W)
        if row_key in ("part_load_ratio", "part_load_w"):
            temp = self.OUTDOOR_TEMPS.get(col_key)
            if temp is not None:
                ratio_pct, load_w = SeerAdapter.get_part_load_info(temp, self.p_design_c_w, self.t_design_c)
                if row_key == "part_load_ratio":
                    return f"{ratio_pct:.0f}%"
                else:
                    return f"{load_w:.0f}"
            return ""

        # 3. Editable Input Fields
        if row_key == "declared_capacity":
            val = inp.declared_capacity if inp else None
            return f"{val:.0f}" if val is not None else ""
        if row_key == "declared_eer":
            val = inp.declared_eer if inp else None
            return f"{val:.2f}" if val is not None else ""
        if row_key == "tested_capacity":
            val = inp.tested_capacity if inp else None
            return f"{val:.0f}" if val is not None else ""
        if row_key == "tested_power":
            val = inp.tested_power if inp else None
            return f"{val:.0f}" if val is not None else ""

        # 4. Computed Fields
        if row_key == "tested_eer":
            val = comp.tested_eer if comp else None
            return f"{val:.2f}" if val is not None else ""
        if row_key == "capacity_percent":
            val = comp.capacity_percent if comp else None
            return f"{val:.1f}%" if val is not None else ""
        if row_key == "eer_percent":
            val = comp.eer_percent if comp else None
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
            return "neutral" if self.p_design_c_w > 0 else "unavailable"

        if row_key == "declared_capacity":
            return comp.declared_capacity_state
        if row_key == "declared_eer":
            return comp.declared_eer_state
        if row_key == "tested_capacity":
            return comp.tested_capacity_state
        if row_key == "tested_power":
            return comp.tested_power_state
        if row_key == "tested_eer":
            return comp.tested_eer_state
        if row_key == "capacity_percent":
            return comp.capacity_percent_state
        if row_key == "eer_percent":
            return comp.eer_percent_state

        return "unavailable"
