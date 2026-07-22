"""Shared runtime-generation lifecycle contracts."""

from .contracts import (
    GenerationCandidate,
    GenerationParticipant,
    GenerationTransitionStatus,
    ParticipantEvidence,
    PreparedParticipant,
)
from .errors import ParticipantPrepareError
from .repository_contract import (
    DataDefinitionGenerationRepositoryPort,
    GenerationPublishResult,
    GenerationSnapshot,
)

__all__ = [
    "GenerationCandidate",
    "GenerationParticipant",
    "GenerationTransitionStatus",
    "ParticipantEvidence",
    "ParticipantPrepareError",
    "PreparedParticipant",
    "DataDefinitionGenerationRepositoryPort",
    "GenerationPublishResult",
    "GenerationSnapshot",
]
