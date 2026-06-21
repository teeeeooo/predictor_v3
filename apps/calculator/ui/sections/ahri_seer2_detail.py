"""AHRI SEER2 detail-row formatting for the shared bin detail panel."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


def format_seer2_bin_details(
    rows: Iterable[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    """Normalize core SEER2 bin diagnostics into the UI-owned schema."""

    formatted = []
    for row in rows:
        formatted.append(
            {
                "bin_no": _number(row.get("bin"), 0),
                "tj": _number(row.get("temp_F"), 1),
                "operating_case": _text(row.get("case")),
                "building_load": _number(row.get("BL"), 1),
                "q_low": _number(row.get("q_Low"), 1),
                "q_int": _number(row.get("q_Int"), 1),
                "q_full": _number(row.get("q_Full"), 1),
                "eer_low": _number(row.get("EER_Low"), 3),
                "eer_int": _number(row.get("EER_Int"), 3),
                "eer_full": _number(row.get("EER_Full"), 3),
                "eer_bin": _number(row.get("EER_IntBin"), 3),
                "q_total": _number(row.get("q_j"), 1),
                "e_total": _number(row.get("E_j"), 1),
            }
        )
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
