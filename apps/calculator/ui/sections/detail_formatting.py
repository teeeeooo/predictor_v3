"""Shared primitive coercion helpers for calculator detail formatters."""

from __future__ import annotations


def optional_fixed_number(value: object, precision: int) -> str:
    """Return a fixed-precision number string or blank for missing/invalid input."""
    if value is None:
        return ""
    try:
        return f"{float(value):.{precision}f}"
    except (TypeError, ValueError):
        return ""


def optional_text(value: object) -> str:
    """Return string display text or blank for missing input."""
    return "" if value is None else str(value)
