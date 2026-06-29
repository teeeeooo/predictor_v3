"""Outbound factory for EN14825 calculator construction."""

from __future__ import annotations

from core.calculators.standards.en14825 import EN14825Calculator


def create_en14825_calculator():
    """Create the core EN14825 calculator behind the app adapter boundary."""
    return EN14825Calculator()
