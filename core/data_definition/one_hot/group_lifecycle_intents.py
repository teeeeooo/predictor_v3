"""Lifecycle intents for controlled One-hot groups."""

from dataclasses import dataclass

from core.data_definition.one_hot.group_intent_types import SelectorDisposition, SourceMode


@dataclass(frozen=True)
class DuplicateOneHotGroupIntent:
    group_identity: str
    group_key: str
    selector_feature_identity: str
    emitted_name_suffix: str = "_copy"


@dataclass(frozen=True)
class RemoveOneHotGroupIntent:
    group_identity: str
    selector_disposition: SelectorDisposition


@dataclass(frozen=True)
class SetOneHotGroupActiveIntent:
    group_identity: str
    active: bool


@dataclass(frozen=True)
class ChangeOneHotSourceModeIntent:
    group_identity: str
    source_mode: SourceMode
    source_binding: str
    provider_categories: tuple[tuple[str, str], ...] = ()
