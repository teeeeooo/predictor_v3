"""Outbound port for canonical Data Definition generation persistence."""

from __future__ import annotations

from apps.common.runtime_generation.repository_contract import (
    DataDefinitionGenerationRepositoryPort,
    GenerationPublishResult,
    GenerationSnapshot,
)

__all__ = [
    "DataDefinitionGenerationRepositoryPort",
    "GenerationPublishResult",
    "GenerationSnapshot",
]
