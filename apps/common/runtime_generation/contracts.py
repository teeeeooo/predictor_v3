"""UI-neutral contracts for one immutable runtime generation transition."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from .repository_contract import GenerationSnapshot


@dataclass(frozen=True)
class GenerationCandidate:
    """One repository snapshot plus evidence frozen before participant prepare."""

    snapshot: GenerationSnapshot
    persisted_generation: str
    participant_revisions: tuple[tuple[str, str], ...]
    transition_id: str

    @property
    def generation_id(self) -> str:
        return self.snapshot.manifest.generation.generation_id


@dataclass(frozen=True)
class PreparedParticipant:
    """Opaque staged participant state; active state must still be unchanged."""

    participant: str
    generation_id: str
    source_revision: str
    payload: Any = field(repr=False, compare=False)
    warnings: tuple[str, ...] = ()
    compatibility: str = "compatible"


@dataclass(frozen=True)
class ParticipantEvidence:
    """Bounded diagnostics for one required participant."""

    participant: str
    active_generation: str
    prepared_generation: str = ""
    stage: str = "active"
    blocker_code: str = ""
    summary: str = ""


@dataclass(frozen=True)
class GenerationTransitionStatus:
    """Concise status plus bounded recovery evidence."""

    code: str
    message: str
    active_generation: str
    persisted_generation: str
    pending_generation: str = ""
    failed_stage: str = ""
    blocker_code: str = ""
    recommended_action: str = ""
    participants: tuple[ParticipantEvidence, ...] = ()
    model_compatibility: str = ""
    mapping_conflicts: tuple[str, ...] = ()


class GenerationParticipant(Protocol):
    """Equal staged lifecycle implemented by every in-process consumer."""

    name: str

    @property
    def active_generation_id(self) -> str: ...

    def revision_token(self) -> str: ...

    def prepare(self, candidate: GenerationCandidate) -> PreparedParticipant: ...

    def commit(self, prepared: PreparedParticipant) -> Any: ...

    def rollback(self, prior_state: Any) -> None: ...

    def abort(self, prepared: PreparedParticipant) -> None: ...
