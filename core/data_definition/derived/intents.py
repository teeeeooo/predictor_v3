"""Immutable intents for restricted Derived authoring."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AddDerivedIntent:
    ml_name: str
    numerator_identity: str
    denominator_identity: str
    operation: str = "safe_ratio"
    zero_denominator_policy: str = "constant"
    zero_value: object = 0.0
    active: bool = False


@dataclass(frozen=True)
class EditDerivedIntent:
    identity: tuple[str, str]
    numerator_identity: str
    denominator_identity: str
    operation: str = "safe_ratio"
    zero_denominator_policy: str = "constant"
    zero_value: object = 0.0
    active: bool | None = None


@dataclass(frozen=True)
class RenameDerivedIntent:
    identity: tuple[str, str]
    ml_name: str


@dataclass(frozen=True)
class DuplicateDerivedIntent:
    identity: tuple[str, str]
    ml_name: str


@dataclass(frozen=True)
class RemoveDerivedIntent:
    identity: tuple[str, str]


@dataclass(frozen=True)
class SetDerivedActiveIntent:
    identity: tuple[str, str]
    active: bool


DerivedCommandIntent = (
    AddDerivedIntent
    | EditDerivedIntent
    | RenameDerivedIntent
    | DuplicateDerivedIntent
    | RemoveDerivedIntent
    | SetDerivedActiveIntent
)

DERIVED_INTENT_TYPES = (
    AddDerivedIntent,
    EditDerivedIntent,
    RenameDerivedIntent,
    DuplicateDerivedIntent,
    RemoveDerivedIntent,
    SetDerivedActiveIntent,
)
