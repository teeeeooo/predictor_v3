"""EN14825 SCOP detail-row formatting for the shared bin detail panel."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from apps.calculator.ui.sections.detail_formatting import (
    optional_fixed_number,
    optional_text,
)


def format_scop_bin_details(
    rows: Iterable[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    """Normalize core SCOP diagnostics into the UI schema and rounding policy."""
    return tuple(
        {
            "tj": optional_fixed_number(row.get("temp_c"), 1),
            "hours": optional_fixed_number(row.get("hours"), 1),
            "heating_load": optional_fixed_number(row.get("ph"), 3),
            "heat_pump_capacity": optional_fixed_number(row.get("pdh"), 3),
            "cop_pl": optional_fixed_number(row.get("cop_pl"), 3),
            "equivalent_power": optional_fixed_number(row.get("equivalent_power"), 3),
            "backup_load": optional_fixed_number(row.get("elbu"), 3),
            "operating_case": optional_text(row.get("operating_case")),
            "capacity_source": optional_text(row.get("capacity_source")),
            "cop_source": optional_text(row.get("cop_source")),
        }
        for row in rows
    )
