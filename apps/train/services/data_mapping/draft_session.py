"""Service-owned Data Mapping draft and grouped command history."""

from __future__ import annotations

from core.mapping.editor_model import MappingEditorDraft


class DataMappingDraftSession:
    """Own the current draft and draft-level undo history."""

    def __init__(self, *, history_limit: int = 64) -> None:
        self._history_limit = history_limit
        self._draft: MappingEditorDraft | None = None
        self._dirty = False
        self._undo_history: list[MappingEditorDraft] = []

    @property
    def draft(self) -> MappingEditorDraft | None:
        return self._draft

    @property
    def dirty(self) -> bool:
        return self._dirty

    def project(self, draft: MappingEditorDraft) -> MappingEditorDraft:
        """Replace the current projection without creating an undo command."""
        self._draft = draft
        return draft

    def reset(self, draft: MappingEditorDraft) -> MappingEditorDraft:
        """Install a newly loaded context and clear command history."""
        self._draft = draft
        self._dirty = False
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
        self._dirty = True
        return next_draft

    def undo(self) -> MappingEditorDraft | None:
        """Restore the previous draft for one grouped command."""
        if not self._undo_history:
            return None
        self._draft = self._undo_history.pop()
        self._dirty = True
        return self._draft

    def mark_clean(self) -> None:
        """Mark the current draft saved without discarding undo history."""
        self._dirty = False
