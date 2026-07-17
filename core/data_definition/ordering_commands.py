"""Independent deterministic Predict and ordered-ML move commands."""

from __future__ import annotations

from dataclasses import replace

from core.data_definition.command_types import (
    DataDefinitionCommandIssue,
    DataDefinitionCommandResult,
)
from core.data_definition.feature_command_types import MoveDefinitionIntent
from core.data_definition.dependency_policy import is_supported_basic_feature
from core.data_definition.draft import DataDefinitionDraft


def apply_move_definition_command(
    draft: DataDefinitionDraft,
    intent: MoveDefinitionIntent,
) -> DataDefinitionCommandResult:
    """Move exactly one Feature in exactly one ordering contract."""
    identity = draft.resolve_identity(intent.identity)
    row = next((item for item in draft.rows if item.identity == identity), None)
    if row is None:
        return _reject(
            draft,
            "definition_not_found",
            "Feature not found.",
            "Refresh the draft and select an existing Feature.",
        )
    if not is_supported_basic_feature(row):
        return _reject(
            draft,
            "feature_authoring_deferred",
            "This Feature ordering is owned by a later authoring slice.",
            "Use the Derived, One-hot, or Target-specific ordering workflow.",
            identity,
        )
    if intent.ordering not in {"predict", "ml"}:
        return _reject(
            draft,
            "ordering_unsupported",
            "Move requires Predict display order or ordered ML contract order.",
            "Choose Predict order or ML order.",
            identity,
        )
    order = draft.predict_order if intent.ordering == "predict" else draft.ml_order
    if identity not in order:
        return _reject(
            draft,
            "ordering_membership_missing",
            f"Feature is not part of the current {intent.ordering.upper()} ordering.",
            "Enable the ML input first or choose Predict ordering.",
            identity,
        )
    index = order.index(identity)
    offset = -1 if intent.direction == "up" else 1 if intent.direction == "down" else 0
    destination = index + offset
    if offset == 0:
        return _reject(
            draft,
            "move_direction_unsupported",
            "Move direction must be Up or Down.",
            "Choose Move Up or Move Down.",
            identity,
        )
    if destination < 0 or destination >= len(order):
        return _reject(
            draft,
            "move_boundary",
            f"Feature is already at the {intent.direction} boundary.",
            "Choose the opposite direction or another Feature.",
            identity,
        )
    reordered = list(order)
    reordered[index], reordered[destination] = reordered[destination], reordered[index]
    if intent.ordering == "ml":
        updated = replace(draft, ml_order=tuple(reordered))
    else:
        display_order = {
            item: position * 10 for position, item in enumerate(reordered, 1)
        }
        updated = replace(
            draft,
            predict_order=tuple(reordered),
            rows=tuple(
                replace(item, display_order=display_order[item.identity])
                if item.identity in display_order else item
                for item in draft.rows
            ),
            controlled_field_changes=frozenset((
                *draft.controlled_field_changes,
                *((item, "display_order") for item in reordered),
            )),
        )
    return DataDefinitionCommandResult(
        updated,
        True,
        identity,
        f"Move {intent.direction.title()} ({intent.ordering.upper()} order)",
    )


def _reject(
    draft: DataDefinitionDraft,
    code: str,
    message: str,
    resolution: str,
    identity: tuple[str, str] | None = None,
) -> DataDefinitionCommandResult:
    issue = DataDefinitionCommandIssue(code, "ordering", message, resolution)
    return DataDefinitionCommandResult(draft, False, identity, "Move", (issue,))
