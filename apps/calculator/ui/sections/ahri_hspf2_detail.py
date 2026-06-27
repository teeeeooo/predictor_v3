"""AHRI HSPF2 detail-row formatting for the shared bin detail panel."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from apps.calculator.ui.sections.detail_formatting import (
    optional_fixed_number,
    optional_text,
)


def format_hspf2_bin_details(
    rows: Iterable[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    """Normalize core HSPF2 diagnostics into the compact UI schema."""
    formatted = []
    for row in rows:
        item = {
            "tj": optional_fixed_number(row.get("temp_F"), 1),
            "hours": optional_fixed_number(row.get("hours"), 1),
            "operating_case": optional_text(row.get("operating_case")),
            "building_load": optional_fixed_number(row.get("building_load"), 1),
            "q_low": optional_fixed_number(row.get("q_low"), 1),
            "q_int": optional_fixed_number(row.get("q_int"), 1),
            "q_full": optional_fixed_number(row.get("q_full"), 1),
            "cop_bin": optional_fixed_number(row.get("COP_bin"), 3),
            "q_comp": optional_fixed_number(row.get("q_comp"), 1),
            "e_comp": optional_fixed_number(row.get("e_comp"), 1),
            "q_aux": optional_fixed_number(row.get("q_aux"), 1),
            "e_aux": optional_fixed_number(row.get("e_aux"), 1),
            "q_total": optional_fixed_number(row.get("q_j"), 1),
            "e_total": optional_fixed_number(row.get("E_j"), 1),
        }
        formatted.append(item)
    return tuple(formatted)
