"""Definition intents for controlled One-hot categories."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AddOneHotCategoryIntent:
    group_identity: str
    source_value: str
    emitted_ml_name: str
    provider_category_identity: str = ""
    position: int | None = None
    active: bool = False


@dataclass(frozen=True)
class EditOneHotCategoryIntent:
    category_identity: str
    source_value: str | None = None
    emitted_ml_name: str | None = None
    provider_category_identity: str | None = None
    active: bool | None = None


@dataclass(frozen=True)
class RenameOneHotEmittedFeatureIntent:
    category_identity: str
    emitted_ml_name: str
