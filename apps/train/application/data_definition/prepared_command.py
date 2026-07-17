"""Application-owned prepared Feature command transition."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.command_types import DataDefinitionCommandResult
from core.data_definition.draft import DataDefinitionDraft
from core.data_definition.impact_preview import FeatureImpactPreview


@dataclass(frozen=True)
class PreparedFeatureCommand:
    """One command execution and its exact side-effect-free candidate evidence."""

    source_revision: int
    source_generation_id: str
    source_draft: DataDefinitionDraft
    result: DataDefinitionCommandResult
    preview: FeatureImpactPreview

    def __getattr__(self, name: str):  # noqa: ANN204
        """Keep the existing read-only Preview surface source-compatible."""
        return getattr(self.preview, name)
