"""Immutable input/output types for controlled Data Definition commands."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.data_definition.draft import DataDefinitionDraft

DefinitionIntentKind = Literal[
    "manual_predict",
    "mapping_predict",
    "mapping_attribute",
    "predict_only",
    "ml_only",
    "mapping_backed",
    "helper_hidden",
]


@dataclass(frozen=True)
class AddDefinitionIntent:
    """Constrained user intent for one complete schema-row addition."""

    kind: DefinitionIntentKind
    label: str
    column_key: str
    data_type: str
    visible: bool = True
    required: bool = False
    mapping_entity: str = ""
    mapping_attribute: str = ""
    trigger_column: str = ""
    rule_id: str = ""
    notes: str = ""
    model_input_enabled: bool = False
    ml_name: str = ""
    active: bool = True


@dataclass(frozen=True)
class EditDefinitionIntent:
    """One atomic set of schema-backed metadata updates."""

    identity: tuple[str, str]
    updates: tuple[tuple[str, object], ...]




@dataclass(frozen=True)
class DataDefinitionCommandIssue:
    """User-understandable command validation issue."""

    code: str
    field_name: str
    message: str
    resolution: str = ""


@dataclass(frozen=True)
class DataDefinitionCommandResult:
    """Outcome of one non-persisting controlled draft transition."""

    draft: DataDefinitionDraft
    accepted: bool
    identity: tuple[str, str] | None
    action: str
    issues: tuple[DataDefinitionCommandIssue, ...] = ()
    affected_identities: tuple[tuple[str, str], ...] = ()

    @property
    def message(self) -> str:
        if self.accepted:
            return f"{self.action} command applied to the unsaved draft."
        return self.issues[0].message if self.issues else f"{self.action} command was blocked."
