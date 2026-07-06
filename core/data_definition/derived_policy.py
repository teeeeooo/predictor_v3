"""Explicit Arc 15A derived feature policy.

Derived calculation logic remains in the ML preprocessing owner. This module
only names current compatibility rows that are not represented by schema rows.
"""

from __future__ import annotations

from core.data_definition.model import DerivedFeatureDefinition

CURRENT_DERIVED_FEATURES: tuple[DerivedFeatureDefinition, ...] = (
    DerivedFeatureDefinition("Cool_Capa_per_EER"),
    DerivedFeatureDefinition("Cool_Capa_per_CondArea"),
    DerivedFeatureDefinition("Cool_Capa_per_EvapArea"),
    DerivedFeatureDefinition("Cool_Capa_per_cc"),
    DerivedFeatureDefinition("Heat_Capa_per_EER"),
    DerivedFeatureDefinition("Heat_Capa_per_CondArea"),
    DerivedFeatureDefinition("Heat_Capa_per_EvapArea"),
    DerivedFeatureDefinition("Heat_Capa_per_cc"),
)


def load_current_derived_feature_policy() -> tuple[DerivedFeatureDefinition, ...]:
    """Return the current derived feature policy used for parity projection."""
    return CURRENT_DERIVED_FEATURES
