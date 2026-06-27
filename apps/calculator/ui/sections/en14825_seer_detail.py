"""EN14825 SEER detail-row formatting for the shared bin detail panel."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from apps.calculator.ui.sections.detail_formatting import (
    optional_fixed_number,
    optional_text,
)


def format_seer_bin_details(
    rows: Iterable[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    """Normalize core SEER diagnostics into the UI schema and rounding policy."""
    return tuple(
        {
            "tj": optional_fixed_number(row.get("temp_c"), 1),
            "hours": optional_fixed_number(row.get("hours"), 1),
            "cooling_load": optional_fixed_number(row.get("pc"), 3),
            "eer_pl": optional_fixed_number(row.get("eer_pl"), 3),
            "energy_contribution": optional_fixed_number(
                row.get("energy_contribution"), 3
            ),
            "source": optional_text(row.get("interpolation")),
        }
        for row in rows
    )
