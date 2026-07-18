"""Definition intents for controlled One-hot groups."""

from dataclasses import dataclass

from core.data_definition.one_hot.group_intent_types import SelectorDisposition, SourceMode


@dataclass(frozen=True)
class AddOneHotGroupIntent:
    group_key: str
    selector_feature_identity: str
    source_mode: SourceMode
    source_binding: str = ""
    unknown_policy: str = ""
    missing_policy: str = ""
    active: bool = False


@dataclass(frozen=True)
class EditOneHotGroupIntent:
    group_identity: str
    unknown_policy: str
    missing_policy: str
    source_binding: str | None = None


@dataclass(frozen=True)
class RenameOneHotGroupIntent:
    group_identity: str
    group_key: str


@dataclass(frozen=True)
class AssignOneHotSelectorIntent:
    group_identity: str
    selector_feature_identity: str
    previous_selector_disposition: SelectorDisposition = "detach"
