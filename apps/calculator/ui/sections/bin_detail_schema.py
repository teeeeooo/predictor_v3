"""Bin detail schema definitions for configurable trace tables and graphs.

Schemas separate UI shell responsibility (display/copy/export) from
domain-specific column/key/series definitions. No calculator core imports.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BinDetailSchema:
    """Immutable schema for a bin-detail trace table and its graph series."""

    column_labels: tuple[str, ...]
    column_keys: tuple[str, ...]
    graph_series: tuple[tuple[str, str], ...]
    table_title: str = "상세 표"

    def __post_init__(self) -> None:
        if len(self.column_labels) != len(self.column_keys):
            raise ValueError(
                f"column_labels ({len(self.column_labels)}) and column_keys "
                f"({len(self.column_keys)}) must have the same length"
            )
        if not self.column_labels:
            raise ValueError("column_labels must not be empty")
        if not self.graph_series:
            raise ValueError("graph_series must not be empty")


# ---------------------------------------------------------------------------
# Cooling default schema (preserves existing CSPF/SASO/ISEER behavior)
# ---------------------------------------------------------------------------
COOLING_BIN_DETAIL_SCHEMA = BinDetailSchema(
    column_labels=(
        "Bin No",
        "Temp [°C]",
        "Hours",
        "Load [W]",
        "Capacity [W]",
        "Power [W]",
        "EER",
        "CSTL [Wh]",
        "CSEC [Wh]",
    ),
    column_keys=(
        "bin_no",
        "tj",
        "nj",
        "lc",
        "capacity",
        "power",
        "eer",
        "cstl_bin",
        "csec_bin",
    ),
    graph_series=(
        ("Bin Hours [h]", "nj"),
        ("Load [W]", "lc"),
        ("Capacity [W]", "capacity"),
        ("Power [W]", "power"),
        ("EER [W/W]", "eer"),
        ("CSTL [Wh]", "cstl_bin"),
        ("CSEC [Wh]", "csec_bin"),
    ),
    table_title="상세 표",
)

# ---------------------------------------------------------------------------
# Heating schema candidate for HSPF detail/bin trace (not wired yet)
# ---------------------------------------------------------------------------
HEATING_HSPF_BIN_DETAIL_SCHEMA = BinDetailSchema(
    column_labels=(
        "Bin No",
        "Temp [°C]",
        "Hours",
        "Load [W]",
        "Delivered [W]",
        "Power [W]",
        "Case",
        "Heat Pump [Wh]",
        "Auxiliary [Wh]",
        "Total [Wh]",
    ),
    column_keys=(
        "bin_no",
        "tj",
        "nj",
        "bl_h",
        "pi_j",
        "P_j",
        "case",
        "heat_pump_energy",
        "auxiliary_energy",
        "E_j",
    ),
    graph_series=(
        ("Bin Hours [h]", "nj"),
        ("Load [W]", "bl_h"),
        ("Delivered [W]", "pi_j"),
        ("Power [W]", "P_j"),
        ("Heat Pump [Wh]", "heat_pump_energy"),
        ("Auxiliary [Wh]", "auxiliary_energy"),
        ("Total [Wh]", "E_j"),
    ),
    table_title="난방 상세 표",
)


# EN14825 SCOP uses profile-specific normalized keys; raw core diagnostics are
# converted by the SCOP detail formatter before reaching the shared panel.
EN14825_SCOP_BIN_DETAIL_SCHEMA = BinDetailSchema(
    column_labels=(
        "Tj [°C]",
        "Hours",
        "Heating Load Ph [kW]",
        "HP Capacity Pdh [kW]",
        "COPpl",
        "Equivalent Power [kW]",
        "Backup/ELBU [kW]",
        "Operating Case",
        "Capacity Source",
        "COP Source",
    ),
    column_keys=(
        "tj",
        "hours",
        "heating_load",
        "heat_pump_capacity",
        "cop_pl",
        "equivalent_power",
        "backup_load",
        "operating_case",
        "capacity_source",
        "cop_source",
    ),
    graph_series=(
        ("Bin Hours [h]", "hours"),
        ("Heating Load Ph [kW]", "heating_load"),
        ("HP Capacity Pdh [kW]", "heat_pump_capacity"),
        ("Equivalent Power [kW]", "equivalent_power"),
        ("Backup/ELBU [kW]", "backup_load"),
        ("COPpl", "cop_pl"),
    ),
    table_title="EN14825 SCOP Bin Detail",
)


EN14825_SEER_BIN_DETAIL_SCHEMA = BinDetailSchema(
    column_labels=(
        "Tj [°C]",
        "Hours",
        "Cooling Load Pc [kW]",
        "EERpl",
        "Energy Contribution [kWh]",
        "Source",
    ),
    column_keys=(
        "tj",
        "hours",
        "cooling_load",
        "eer_pl",
        "energy_contribution",
        "source",
    ),
    graph_series=(
        ("Bin Hours [h]", "hours"),
        ("Cooling Load Pc [kW]", "cooling_load"),
        ("EERpl", "eer_pl"),
        ("Energy Contribution [kWh]", "energy_contribution"),
    ),
    table_title="EN14825 SEER Bin Detail",
)
