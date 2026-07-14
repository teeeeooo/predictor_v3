"""Service-owned Data Mapping draft and grouped command history."""

from __future__ import annotations

from core.mapping.editor_model import MappingEditorDraft


class DataMappingDraftSession:
    """Own the current draft and draft-level undo history."""

    def __init__(self, *, history_limit: int = 64) -> None:
        self._history_limit = history_limit
        self._draft: MappingEditorDraft | None = None
        self._baseline: MappingEditorDraft | None = None
        self._undo_history: list[MappingEditorDraft] = []

    @property
    def draft(self) -> MappingEditorDraft | None:
        return self._draft

    @property
    def dirty(self) -> bool:
        return self._draft is not None and self._draft != self._baseline

    @property
    def baseline(self) -> MappingEditorDraft | None:
        return self._baseline

    def project(
        self,
        draft: MappingEditorDraft,
        baseline: MappingEditorDraft | None = None,
    ) -> MappingEditorDraft:
        """Replace the current projection without creating an undo command."""
        self._draft = draft
        if self._baseline is None:
            self._baseline = baseline or draft
        elif baseline is not None:
            self._baseline = baseline
        return draft

    def reset(self, draft: MappingEditorDraft) -> MappingEditorDraft:
        """Install a newly loaded context and clear command history."""
        self._draft = draft
        self._baseline = draft
        self._undo_history.clear()
        return draft

    def store_command(
        self,
        previous: MappingEditorDraft,
        next_draft: MappingEditorDraft,
    ) -> MappingEditorDraft:
        """Store one application command when it changes the draft."""
        if next_draft == previous:
            return self._draft or next_draft
        self._undo_history.append(previous)
        if len(self._undo_history) > self._history_limit:
            del self._undo_history[0]
        self._draft = next_draft
        return next_draft

    def undo(self) -> MappingEditorDraft | None:
        """Restore the previous draft for one grouped command."""
        if not self._undo_history:
            return None
        self._draft = self._undo_history.pop()
        return self._draft

    def mark_saved(self) -> None:
        """Set the successful Save result as the new baseline."""
        self._baseline = self._draft
