"""Application contracts for canonical Data Definition persistence."""

from apps.train.application.data_definition.ports import (
    DataDefinitionGenerationRepositoryPort,
    GenerationPublishResult,
    GenerationSnapshot,
)

__all__ = [
    "DataDefinitionGenerationRepositoryPort",
    "GenerationPublishResult",
    "GenerationSnapshot",
]
