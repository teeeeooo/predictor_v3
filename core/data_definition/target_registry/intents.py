"""Immutable Target-centered authoring intents."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AddTargetIntent:
    label: str
    column_key: str
    ml_name: str
    model_group_identity: str
    policy_mode: str
    policy_owner_identities: tuple[str, ...]
    visible: bool = True


@dataclass(frozen=True)
class EditTargetIntent:
    identity: str
    label: str
    visible: bool


@dataclass(frozen=True)
class RenameTargetIntent:
    identity: str
    label: str
    column_key: str
    ml_name: str


@dataclass(frozen=True)
class DuplicateTargetIntent:
    identity: str
    label: str
    column_key: str
    ml_name: str


@dataclass(frozen=True)
class RemoveTargetIntent:
    identity: str


@dataclass(frozen=True)
class SetTargetActiveIntent:
    identity: str
    active: bool


@dataclass(frozen=True)
class MoveTargetIntent:
    identity: str
    direction: str


@dataclass(frozen=True)
class ChangeTargetModelGroupIntent:
    identity: str
    model_group_identity: str


@dataclass(frozen=True)
class ChangeTargetPolicyIntent:
    identity: str
    mode: str
    owner_identities: tuple[str, ...]


TargetCommandIntent = (
    AddTargetIntent | EditTargetIntent | RenameTargetIntent | DuplicateTargetIntent
    | RemoveTargetIntent | SetTargetActiveIntent | MoveTargetIntent
    | ChangeTargetModelGroupIntent | ChangeTargetPolicyIntent
)

TARGET_INTENT_TYPES = (
    AddTargetIntent, EditTargetIntent, RenameTargetIntent, DuplicateTargetIntent,
    RemoveTargetIntent, SetTargetActiveIntent, MoveTargetIntent,
    ChangeTargetModelGroupIntent, ChangeTargetPolicyIntent,
)
