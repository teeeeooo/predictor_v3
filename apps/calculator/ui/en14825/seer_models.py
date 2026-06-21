"""Data models representing inputs, computed fields, and results for EN14825 SEER."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Optional

@dataclass
class SeerPointInput:
    """Raw user input values for a single SEER test point in Watts (W)."""
    declared_capacity: Optional[float] = None
    declared_eer: Optional[float] = None
    tested_capacity: Optional[float] = None
    tested_power: Optional[float] = None


@dataclass
class SeerPointComputed:
    """Computed rows and comparison states for a single SEER test point."""

    # Internal adapter/core-only derived value.
    # Must never be exposed as an editable or display table row.
    declared_power_w_for_core: Optional[float] = None  # W (derived from declared_capacity / declared_eer)

    tested_eer: Optional[float] = None      # dimensionless (tested_capacity / tested_power)
    capacity_percent: Optional[float] = None # tested_capacity / declared_capacity * 100
    eer_percent: Optional[float] = None      # tested_eer / declared_eer * 100

    # Cell states for visual tinting: "neutral", "pass", "invalid", "unavailable"
    declared_capacity_state: str = "neutral"
    declared_eer_state: str = "neutral"
    tested_capacity_state: str = "neutral"
    tested_power_state: str = "neutral"
    tested_eer_state: str = "neutral"
    capacity_percent_state: str = "neutral"
    eer_percent_state: str = "neutral"


@dataclass
class SeerResultSummary:
    """Calculated SEER final results and summaries."""
    declared_seer: Optional[float] = None
    declared_qc_kwh: Optional[float] = None
    tested_seer: Optional[float] = None
    tested_qc_kwh: Optional[float] = None
    seer_percent: Optional[float] = None

    # Additive UI diagnostics preserved from each completed core calculation.
    declared_bin_details: tuple[Mapping[str, object], ...] = ()
    tested_bin_details: tuple[Mapping[str, object], ...] = ()

    # Result state tinting: "neutral", "pass", "invalid", "unavailable"
    declared_seer_state: str = "neutral"
    declared_qc_state: str = "neutral"
    tested_seer_state: str = "neutral"
    tested_qc_state: str = "neutral"
    seer_percent_state: str = "neutral"

    # SoC: status_code acts as state indicator; message is optional detail
    status_code: str = "idle"
    message: Optional[str] = None
