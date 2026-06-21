"""AHRI HSPF2 detail-row formatting for the shared bin detail panel."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


def format_hspf2_bin_details(
    rows: Iterable[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    """Normalize core HSPF2 diagnostics into the compact UI schema."""
    formatted = []
    for row in rows:
        item = {
            "tj": _number(row.get("temp_F"), 1),
            "hours": _number(row.get("hours"), 1),
            "operating_case": _text(row.get("operating_case")),
            "building_load": _number(row.get("building_load"), 1),
            "q_low": _number(row.get("q_low"), 1),
            "q_int": _number(row.get("q_int"), 1),
            "q_full": _number(row.get("q_full"), 1),
            "cop_bin": _number(row.get("COP_bin"), 3),
            "q_comp": _number(row.get("q_comp"), 1),
            "e_comp": _number(row.get("e_comp"), 1),
            "q_aux": _number(row.get("q_aux"), 1),
            "e_aux": _number(row.get("e_aux"), 1),
            "q_total": _number(row.get("q_j"), 1),
            "e_total": _number(row.get("E_j"), 1),
        }
        formatted.append(item)
    return tuple(formatted)


def _number(value: object, precision: int) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.{precision}f}"
    except (TypeError, ValueError):
        return ""


def _text(value: object) -> str:
    return "" if value is None else str(value)
