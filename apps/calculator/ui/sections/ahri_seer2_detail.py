"""AHRI SEER2 detail-row formatting for the shared bin detail panel."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from apps.calculator.ui.sections.detail_formatting import (
    optional_fixed_number,
    optional_text,
)


def format_seer2_bin_details(
    rows: Iterable[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    """Normalize core SEER2 bin diagnostics into the UI-owned schema."""

    formatted = []
    for row in rows:
        formatted.append(
            {
                "bin_no": optional_fixed_number(row.get("bin"), 0),
                "tj": optional_fixed_number(row.get("temp_F"), 1),
                "operating_case": optional_text(row.get("case")),
                "building_load": optional_fixed_number(row.get("BL"), 1),
                "q_low": optional_fixed_number(row.get("q_Low"), 1),
                "q_int": optional_fixed_number(row.get("q_Int"), 1),
                "q_full": optional_fixed_number(row.get("q_Full"), 1),
                "eer_low": optional_fixed_number(row.get("EER_Low"), 3),
                "eer_int": optional_fixed_number(row.get("EER_Int"), 3),
                "eer_full": optional_fixed_number(row.get("EER_Full"), 3),
                "eer_bin": optional_fixed_number(row.get("EER_IntBin"), 3),
                "q_total": optional_fixed_number(row.get("q_j"), 1),
                "e_total": optional_fixed_number(row.get("E_j"), 1),
            }
        )
    return tuple(formatted)
