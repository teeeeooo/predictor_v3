"""Canonical condenser identity policy shared by mapping consumers."""

from __future__ import annotations

from typing import Any


PFC_FIN_TYPE = "PFC"


def condenser_requires_pi(fin_type: Any) -> bool:
    """Return whether a fin type requires Pi; only PFC skips it."""
    return _clean(fin_type).upper() != PFC_FIN_TYPE


def canonical_condenser_pi(fin_type: Any, pi: Any) -> str:
    """Return canonical Pi, discarding every PFC placeholder or stale value."""
    if not condenser_requires_pi(fin_type):
        return ""
    return _clean(pi)


def condenser_identity(
    odu: Any,
    fin_type: Any,
    pi: Any,
    row: Any,
) -> tuple[str, ...]:
    """Return the logical identity components for a condenser specification."""
    fin = _clean(fin_type)
    components = (_clean(odu), fin, canonical_condenser_pi(fin, pi), _clean(row))
    if condenser_requires_pi(components[1]):
        return components
    return components[0], components[1], components[3]


def condenser_spec_key(odu: Any, fin_type: Any, pi: Any, row: Any) -> str:
    """Format one logical condenser identity as the runtime mapping key."""
    return " ".join(condenser_identity(odu, fin_type, pi, row))


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
