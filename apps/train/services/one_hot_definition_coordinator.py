"""Application coordination for One-hot commands and vocabulary snapshots."""

from __future__ import annotations

from core.data_definition import DataDefinitionCommandResult, DataDefinitionDraft
from core.data_definition.one_hot.category_commands import apply_category_command
from core.data_definition.one_hot.group_commands import apply_group_command
from core.data_definition.one_hot.intents import (
    ONE_HOT_CATEGORY_INTENT_TYPES,
    ONE_HOT_GROUP_INTENT_TYPES,
    OneHotCommandIntent,
)
from core.data_definition.one_hot.model import VocabularySnapshot


class OneHotDefinitionCoordinator:
    """Apply pure domain transitions with one immutable source observation set."""

    def __init__(self, snapshots: tuple[VocabularySnapshot, ...]) -> None:
        self.snapshots = tuple(snapshots)

    def apply(
        self,
        draft: DataDefinitionDraft,
        intent: OneHotCommandIntent,
    ) -> DataDefinitionCommandResult:
        if isinstance(intent, ONE_HOT_GROUP_INTENT_TYPES):
            return apply_group_command(draft, intent, self.snapshots)
        if isinstance(intent, ONE_HOT_CATEGORY_INTENT_TYPES):
            return apply_category_command(draft, intent, self.snapshots)
        raise TypeError(f"Unsupported One-hot command intent: {type(intent).__name__}")
