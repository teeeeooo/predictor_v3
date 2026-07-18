"""Facade and dispatch groups for controlled One-hot intents."""

from core.data_definition.one_hot.category_intents import (
    AddOneHotCategoryIntent,
    DuplicateOneHotCategoryIntent,
    EditOneHotCategoryIntent,
    MoveOneHotCategoryIntent,
    RemoveOneHotCategoryIntent,
    RenameOneHotEmittedFeatureIntent,
    SetOneHotCategoryActiveIntent,
)
from core.data_definition.one_hot.group_intents import (
    AddOneHotGroupIntent,
    AssignOneHotSelectorIntent,
    ChangeOneHotSourceModeIntent,
    DuplicateOneHotGroupIntent,
    EditOneHotGroupIntent,
    RemoveOneHotGroupIntent,
    RenameOneHotGroupIntent,
    SelectorDisposition,
    SetOneHotGroupActiveIntent,
    SourceMode,
)

OneHotGroupIntent = (
    AddOneHotGroupIntent | EditOneHotGroupIntent | RenameOneHotGroupIntent
    | DuplicateOneHotGroupIntent | RemoveOneHotGroupIntent
    | SetOneHotGroupActiveIntent | ChangeOneHotSourceModeIntent
    | AssignOneHotSelectorIntent
)
OneHotCategoryIntent = (
    AddOneHotCategoryIntent | EditOneHotCategoryIntent
    | RenameOneHotEmittedFeatureIntent | DuplicateOneHotCategoryIntent
    | RemoveOneHotCategoryIntent | SetOneHotCategoryActiveIntent
    | MoveOneHotCategoryIntent
)
OneHotCommandIntent = OneHotGroupIntent | OneHotCategoryIntent

ONE_HOT_GROUP_INTENT_TYPES = (
    AddOneHotGroupIntent, EditOneHotGroupIntent, RenameOneHotGroupIntent,
    DuplicateOneHotGroupIntent, RemoveOneHotGroupIntent,
    SetOneHotGroupActiveIntent, ChangeOneHotSourceModeIntent,
    AssignOneHotSelectorIntent,
)
ONE_HOT_CATEGORY_INTENT_TYPES = (
    AddOneHotCategoryIntent, EditOneHotCategoryIntent,
    RenameOneHotEmittedFeatureIntent, DuplicateOneHotCategoryIntent,
    RemoveOneHotCategoryIntent, SetOneHotCategoryActiveIntent,
    MoveOneHotCategoryIntent,
)
ONE_HOT_INTENT_TYPES = (*ONE_HOT_GROUP_INTENT_TYPES, *ONE_HOT_CATEGORY_INTENT_TYPES)

__all__ = [name for name in globals() if name.endswith("Intent") or name.startswith("ONE_HOT")]
