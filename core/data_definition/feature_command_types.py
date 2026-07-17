"""Intent DTOs for Phase 4C Basic Feature lifecycle commands."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.data_definition.command_types import AddDefinitionIntent, EditDefinitionIntent

FeatureOrderingKind = Literal["predict", "ml"]
MoveDirection = Literal["up", "down"]


@dataclass(frozen=True)
class RenameDefinitionIntent:
    identity: tuple[str, str]
    label: str | None = None
    column_key: str | None = None
    ml_name: str | None = None


@dataclass(frozen=True)
class DuplicateDefinitionIntent:
    identity: tuple[str, str]
    label: str
    column_key: str
    ml_name: str = ""


@dataclass(frozen=True)
class RemoveDefinitionIntent:
    identity: tuple[str, str]


@dataclass(frozen=True)
class SetDefinitionActiveIntent:
    identity: tuple[str, str]
    active: bool


@dataclass(frozen=True)
class MoveDefinitionIntent:
    identity: tuple[str, str]
    ordering: FeatureOrderingKind
    direction: MoveDirection


FeatureCommandIntent = (
    AddDefinitionIntent
    | EditDefinitionIntent
    | RenameDefinitionIntent
    | DuplicateDefinitionIntent
    | RemoveDefinitionIntent
    | SetDefinitionActiveIntent
    | MoveDefinitionIntent
)
