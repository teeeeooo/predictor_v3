"""Data models representing inputs, computed fields, and results for EN14825 SCOP."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ScopPointInput:
    """Raw user input values for a single SCOP heating test point in Watts (W) and dry-bulb Celsius (°C)."""
    declared_capacity: Optional[float] = None
    declared_cop: Optional[float] = None
    tested_capacity: Optional[float] = None
    tested_power: Optional[float] = None
    temp_c: Optional[float] = None  # Optional Dry-bulb outdoor temperature override


@dataclass
class ScopPointComputed:
    """Computed rows and comparison states for a single SCOP test point."""

    # Internal adapter/core-only derived value.
    # Must never be exposed as an editable or display table row.
    declared_power_w_for_core: Optional[float] = None  # W (derived from declared_capacity / declared_cop)

    # Read-only calculated table row values
    tested_cop: Optional[float] = None        # dimensionless (tested_capacity / tested_power)
    capacity_percent: Optional[float] = None  # tested_capacity / declared_capacity * 100
    cop_percent: Optional[float] = None       # tested_cop / declared_cop * 100

    # Cell states for visual tinting: "neutral", "pass", "invalid", "unavailable"
    declared_capacity_state: str = "neutral"
    declared_cop_state: str = "neutral"
    tested_capacity_state: str = "neutral"
    tested_power_state: str = "neutral"
    tested_cop_state: str = "neutral"
    capacity_percent_state: str = "neutral"
    cop_percent_state: str = "neutral"


@dataclass
class ScopResultSummary:
    """Calculated SCOP final results and summaries for a climate zone."""
    climate: Optional[str] = None
    declared_scop: Optional[float] = None
    declared_qh_kwh: Optional[float] = None
    tested_scop: Optional[float] = None
    tested_qh_kwh: Optional[float] = None
    scop_percent: Optional[float] = None

    # Annual total energy consumption
    declared_total_kwh: Optional[float] = None
    tested_total_kwh: Optional[float] = None

    # Result state tinting: "neutral", "pass", "invalid", "unavailable"
    declared_scop_state: str = "neutral"
    declared_qh_state: str = "neutral"
    tested_scop_state: str = "neutral"
    tested_qh_state: str = "neutral"
    scop_percent_state: str = "neutral"

    # SoC: status_code acts as state indicator; message is optional detail
    status_code: str = "idle"
    message: Optional[str] = None
