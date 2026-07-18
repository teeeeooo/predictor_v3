"""Lifecycle and order intents for controlled One-hot categories."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class DuplicateOneHotCategoryIntent:
    category_identity: str
    source_value: str
    emitted_ml_name: str
    provider_category_identity: str = ""
    position: int | None = None


@dataclass(frozen=True)
class RemoveOneHotCategoryIntent:
    category_identity: str


@dataclass(frozen=True)
class SetOneHotCategoryActiveIntent:
    category_identity: str
    active: bool


@dataclass(frozen=True)
class MoveOneHotCategoryIntent:
    category_identity: str
    direction: Literal["up", "down"]
