"""View-side intent collection for the table-first Basic Feature Manager."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QWidget

from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.ui.data_definition.command_preview_dialog import FeatureCommandPreviewDialog
from apps.train.ui.data_definition.feature_mutation_dialogs import (
    DuplicateFeatureDialog,
    RenameFeatureDialog,
)
from core.data_definition import (
    DuplicateDefinitionIntent,
    FeatureCommandIntent,
    MoveDefinitionIntent,
    RemoveDefinitionIntent,
    RenameDefinitionIntent,
    SetDefinitionActiveIntent,
)

SelectedFeature = tuple[tuple[str, str], dict[str, str]] | None


class FeatureManagerActions:
    """Collect command intent and show the application-owned impact preview."""

    def __init__(
        self,
        controller: DataDefinitionController,
        selected: Callable[[], SelectedFeature],
        apply_state: Callable[[object], None],
        parent: QWidget,
    ) -> None:
        self._controller = controller
        self._selected = selected
        self._apply_state = apply_state
        self._parent = parent

    def rename(self) -> bool:
        selected = self._selected()
        if selected is None:
            return False
        identity, values = selected
        return bool(RenameFeatureDialog(
            identity,
            values,
            self._preview_and_apply,
            self._parent,
        ).exec())

    def duplicate(self) -> bool:
        selected = self._selected()
        if selected is None:
            return False
        identity, values = selected
        return bool(DuplicateFeatureDialog(
            identity,
            values,
            self._preview_and_apply,
            self._parent,
        ).exec())

    def remove(self) -> bool:
        selected = self._selected()
        return bool(selected and self._preview_and_apply(
            RemoveDefinitionIntent(selected[0])
        )[0])

    def toggle_active(self) -> bool:
        selected = self._selected()
        if selected is None:
            return False
        identity, values = selected
        active = values.get("active", "false").casefold() == "true"
        return self._preview_and_apply(SetDefinitionActiveIntent(identity, not active))[0]

    def move(self, ordering: str, direction: str) -> bool:
        selected = self._selected()
        if selected is None:
            return False
        return self._preview_and_apply(MoveDefinitionIntent(
            selected[0],
            ordering,  # type: ignore[arg-type]
            direction,  # type: ignore[arg-type]
        ))[0]

    def _preview_and_apply(
        self,
        intent: FeatureCommandIntent,
    ) -> tuple[bool, str]:
        prepared = self._controller.preview_feature_command(intent)
        if not prepared.command_accepted:
            FeatureCommandPreviewDialog(prepared.preview, self._parent).exec()
            state = self._controller.apply_prepared_feature_command(prepared)
            self._apply_state(state)
            return False, state.message
        if not FeatureCommandPreviewDialog(prepared.preview, self._parent).exec():
            return False, "Command cancelled after Impact Preview."
        state = self._controller.apply_prepared_feature_command(prepared)
        self._apply_state(state)
        return state.last_action_ok, state.message
