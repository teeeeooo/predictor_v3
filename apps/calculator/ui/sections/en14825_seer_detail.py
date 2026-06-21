"""EN14825 SEER detail-row formatting for the shared bin detail panel."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


def format_seer_bin_details(
    rows: Iterable[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    """Normalize core SEER diagnostics into the UI schema and rounding policy."""
    return tuple(
        {
            "tj": _number(row.get("temp_c"), 1),
            "hours": _number(row.get("hours"), 1),
            "cooling_load": _number(row.get("pc"), 3),
            "eer_pl": _number(row.get("eer_pl"), 3),
            "energy_contribution": _number(
                row.get("energy_contribution"), 3
            ),
            "source": _text(row.get("interpolation")),
        }
        for row in rows
    )


def _number(value: object, precision: int) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.{precision}f}"
    except (TypeError, ValueError):
        return ""


def _text(value: object) -> str:
    return "" if value is None else str(value)
