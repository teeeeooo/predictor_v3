"""View-side Derived intent routing through prepared Preview/Apply."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QInputDialog, QWidget

from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.ui.data_definition.command_preview_dialog import FeatureCommandPreviewDialog
from apps.train.ui.data_definition.derived_dialogs import DerivedDefinitionDialog
from core.data_definition import (
    DuplicateDerivedIntent,
    RemoveDerivedIntent,
    RenameDerivedIntent,
    SetDerivedActiveIntent,
)


class DerivedManagerActions:
    def __init__(
        self,
        controller: DataDefinitionController,
        selected: Callable[[], tuple[tuple[str, str], dict[str, str]] | None],
        apply_state: Callable[[object], None],
        parent: QWidget,
    ) -> None:
        self._controller = controller
        self._selected = selected
        self._apply_state = apply_state
        self._parent = parent

    def add(self) -> bool:
        return bool(DerivedDefinitionDialog(
            self._preview_and_apply,
            self._controller.derived_operand_options(),
            parent=self._parent,
        ).exec())

    def edit(self) -> bool:
        selected = self._selected()
        if selected is None:
            return False
        identity, values = selected
        return bool(DerivedDefinitionDialog(
            self._preview_and_apply,
            self._controller.derived_operand_options(identity[1]),
            identity=identity,
            values=values,
            parent=self._parent,
        ).exec())

    def rename(self) -> bool:
        selected = self._selected()
        if selected is None:
            return False
        identity, values = selected
        name, ok = QInputDialog.getText(
            self._parent, "Rename Derived", "Output ML name", text=values.get("ml_name", "")
        )
        return bool(ok and self._preview_and_apply(RenameDerivedIntent(identity, name))[0])

    def duplicate(self) -> bool:
        selected = self._selected()
        if selected is None:
            return False
        identity, values = selected
        name, ok = QInputDialog.getText(
            self._parent,
            "Duplicate Derived",
            "New output ML name",
            text=f"{values.get('ml_name', '')}_copy",
        )
        return bool(ok and self._preview_and_apply(DuplicateDerivedIntent(identity, name))[0])

    def remove(self) -> bool:
        selected = self._selected()
        return bool(selected and self._preview_and_apply(RemoveDerivedIntent(selected[0]))[0])

    def toggle_active(self) -> bool:
        selected = self._selected()
        if selected is None:
            return False
        identity, values = selected
        active = values.get("active", "false").casefold() == "true"
        return self._preview_and_apply(SetDerivedActiveIntent(identity, not active))[0]

    def _preview_and_apply(self, intent) -> tuple[bool, str]:  # noqa: ANN001
        prepared = self._controller.preview_derived_command(intent)
        if not prepared.command_accepted:
            FeatureCommandPreviewDialog(prepared.preview, self._parent).exec()
            state = self._controller.apply_prepared_derived_command(prepared)
            self._apply_state(state)
            return False, state.message
        if not FeatureCommandPreviewDialog(prepared.preview, self._parent).exec():
            return False, "Command cancelled after Impact Preview."
        state = self._controller.apply_prepared_derived_command(prepared)
        self._apply_state(state)
        return state.last_action_ok, state.message


class DefinitionManagerActions:
    """Route selected identity to Basic Feature or Derived action owners."""

    def __init__(self, feature, derived, selected, edit_feature) -> None:  # noqa: ANN001
        self._feature = feature
        self._derived = derived
        self._selected = selected
        self._edit_feature = edit_feature

    def edit(self) -> None:
        (self._derived.edit if self._is_derived() else self._edit_feature)()

    def rename(self) -> None:
        (self._derived.rename if self._is_derived() else self._feature.rename)()

    def duplicate(self) -> None:
        (self._derived.duplicate if self._is_derived() else self._feature.duplicate)()

    def remove(self) -> None:
        (self._derived.remove if self._is_derived() else self._feature.remove)()

    def toggle_active(self) -> None:
        (self._derived.toggle_active if self._is_derived() else self._feature.toggle_active)()

    def _is_derived(self) -> bool:
        selected = self._selected()
        return bool(selected and selected[1].get("source_kind") == "derived_policy")
