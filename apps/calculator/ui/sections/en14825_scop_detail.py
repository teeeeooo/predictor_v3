"""EN14825 SCOP detail-row formatting for the shared bin detail panel."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


def format_scop_bin_details(
    rows: Iterable[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    """Normalize core SCOP diagnostics into the UI schema and rounding policy."""
    return tuple(
        {
            "tj": _number(row.get("temp_c"), 1),
            "hours": _number(row.get("hours"), 1),
            "heating_load": _number(row.get("ph"), 3),
            "heat_pump_capacity": _number(row.get("pdh"), 3),
            "cop_pl": _number(row.get("cop_pl"), 3),
            "equivalent_power": _number(row.get("equivalent_power"), 3),
            "backup_load": _number(row.get("elbu"), 3),
            "operating_case": _text(row.get("operating_case")),
            "capacity_source": _text(row.get("capacity_source")),
            "cop_source": _text(row.get("cop_source")),
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
