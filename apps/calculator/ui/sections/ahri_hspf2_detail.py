"""AHRI HSPF2 detail-row formatting across supported product classes."""

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


def _common_values(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "tj": optional_fixed_number(row.get("temp_F"), 1),
        "hours": optional_fixed_number(
            _first(row, "hours", "fractional_hours"), 3
        ),
        "operating_case": optional_text(
            _first(row, "operating_case", "case")
        ),
        "building_load": optional_fixed_number(row.get("building_load"), 1),
        "q_low": optional_fixed_number(row.get("q_low"), 1),
        "q_full": optional_fixed_number(row.get("q_full"), 1),
        "q_comp": optional_fixed_number(row.get("q_comp"), 1),
        "e_comp": optional_fixed_number(row.get("e_comp"), 1),
        "q_aux": optional_fixed_number(row.get("q_aux"), 1),
        "e_aux": optional_fixed_number(row.get("e_aux"), 1),
        "q_total": optional_fixed_number(row.get("q_j"), 1),
        "e_total": optional_fixed_number(row.get("E_j"), 1),
    }


def format_hspf2_bin_details(
    rows: Iterable[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    """Normalize rows while preserving the active product schema exactly."""
    formatted = []
    for row in rows:
        values = _common_values(row)
        is_triple = any(
            key in row for key in ("q_boost", "boost_permitted", "delta_boost")
        )
        is_dual = is_triple or any(
            key in row
            for key in (
                "low_permitted",
                "delta_low",
                "compressor_availability",
            )
        )
        if is_triple:
            formatted.append(
                {
                    "tj": values["tj"],
                    "hours": values["hours"],
                    "operating_case": values["operating_case"],
                    "availability": optional_text(
                        row.get("compressor_availability")
                    ),
                    "building_load": values["building_load"],
                    "q_low": values["q_low"],
                    "q_full": values["q_full"],
                    "q_boost": optional_fixed_number(row.get("q_boost"), 1),
                    "low_permitted": optional_text(row.get("low_permitted")),
                    "full_permitted": optional_text(row.get("full_permitted")),
                    "boost_permitted": optional_text(
                        row.get("boost_permitted")
                    ),
                    "q_comp": values["q_comp"],
                    "e_comp": values["e_comp"],
                    "q_aux": values["q_aux"],
                    "e_aux": values["e_aux"],
                    "q_total": values["q_total"],
                    "e_total": values["e_total"],
                }
            )
        elif is_dual:
            formatted.append(
                {
                    "tj": values["tj"],
                    "hours": values["hours"],
                    "operating_case": values["operating_case"],
                    "availability": optional_text(
                        row.get("compressor_availability")
                    ),
                    "building_load": values["building_load"],
                    "q_low": values["q_low"],
                    "q_full": values["q_full"],
                    "low_permitted": optional_text(row.get("low_permitted")),
                    "q_comp": values["q_comp"],
                    "e_comp": values["e_comp"],
                    "q_aux": values["q_aux"],
                    "e_aux": values["e_aux"],
                    "q_total": values["q_total"],
                    "e_total": values["e_total"],
                }
            )
        else:
            formatted.append(
                {
                    "tj": values["tj"],
                    "hours": values["hours"],
                    "operating_case": values["operating_case"],
                    "building_load": values["building_load"],
                    "q_low": values["q_low"],
                    "q_int": optional_fixed_number(row.get("q_int"), 1),
                    "q_full": values["q_full"],
                    "cop_bin": optional_fixed_number(
                        _first(row, "COP_bin", "cop_bin"), 3
                    ),
                    "q_comp": values["q_comp"],
                    "e_comp": values["e_comp"],
                    "q_aux": values["q_aux"],
                    "e_aux": values["e_aux"],
                    "q_total": values["q_total"],
                    "e_total": values["e_total"],
                }
            )
    return tuple(formatted)
