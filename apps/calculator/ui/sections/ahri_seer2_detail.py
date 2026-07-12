"""AHRI SEER2 detail-row formatting for variable and dual-stage products."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from apps.calculator.ui.sections.detail_formatting import (
    optional_fixed_number,
    optional_text,
)


def _first(row: Mapping[str, object], *keys: str) -> object:
    for key in keys:
        value = row.get(key)
        if value is not None:
            return value
    return None


def format_seer2_bin_details(
    rows: Iterable[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    """Normalize product-specific core diagnostics into detail schemas."""
    formatted = []
    for row in rows:
        q_low = _first(row, "q_Low", "q_low")
        p_low = _first(row, "p_Low", "p_low")
        q_full = _first(row, "q_Full", "q_full")
        p_full = _first(row, "p_Full", "p_full")
        formatted.append(
            {
                "bin_no": optional_fixed_number(_first(row, "bin", "bin_no"), 0),
                "tj": optional_fixed_number(row.get("temp_F"), 1),
                "hours": optional_fixed_number(row.get("fractional_hours"), 3),
                "operating_case": optional_text(
                    _first(row, "operating_case", "case")
                ),
                "building_load": optional_fixed_number(
                    _first(row, "BL", "building_load"), 1
                ),
                "q_low": optional_fixed_number(q_low, 1),
                "p_low": optional_fixed_number(p_low, 1),
                "q_int": optional_fixed_number(row.get("q_Int"), 1),
                "q_full": optional_fixed_number(q_full, 1),
                "p_full": optional_fixed_number(p_full, 1),
                "low_permitted": optional_text(row.get("low_permitted")),
                "clf_low": optional_fixed_number(
                    _first(row, "CLF_low", "clf_low"), 4
                ),
                "clf_full": optional_fixed_number(
                    _first(row, "CLF_full", "clf_full"), 4
                ),
                "plf": optional_fixed_number(_first(row, "PLF", "plf"), 4),
                "eer_low": optional_fixed_number(
                    _first(row, "EER_Low")
                    if row.get("EER_Low") is not None
                    else (float(q_low) / float(p_low) if q_low and p_low else None),
                    3,
                ),
                "eer_int": optional_fixed_number(row.get("EER_Int"), 3),
                "eer_full": optional_fixed_number(
                    _first(row, "EER_Full")
                    if row.get("EER_Full") is not None
                    else (
                        float(q_full) / float(p_full)
                        if q_full and p_full
                        else None
                    ),
                    3,
                ),
                "eer_bin": optional_fixed_number(_first(row, "EER_IntBin"), 3),
                "q_total": optional_fixed_number(row.get("q_j"), 1),
                "e_total": optional_fixed_number(row.get("E_j"), 1),
            }
        )
    return tuple(formatted)
