"""Data Definition runtime-generation participant."""

from apps.common.runtime_generation import GenerationCandidate, PreparedParticipant
from apps.common.runtime_generation import GenerationSnapshot

from .errors import ParticipantPrepareError


class DefinitionRuntimeParticipant:
    name = "Data Definition"

    def __init__(self, active: GenerationSnapshot) -> None:
        self._active = active

    @property
    def active_generation_id(self) -> str:
        return self._active.manifest.generation.generation_id

    @property
    def active_snapshot(self) -> GenerationSnapshot:
        return self._active

    def revision_token(self) -> str:
        return self.active_generation_id

    def prepare(self, candidate: GenerationCandidate) -> PreparedParticipant:
        snapshot = candidate.snapshot
        if snapshot.manifest.generation.generation_id != candidate.persisted_generation:
            raise ParticipantPrepareError(
                "definition_candidate_mismatch", "Saved candidate identity mismatch."
            )
        return PreparedParticipant(
            self.name, candidate.generation_id, self.revision_token(), snapshot
        )

    def commit(self, prepared: PreparedParticipant) -> GenerationSnapshot:
        prior = self._active
        self._active = prepared.payload
        return prior

    def rollback(self, prior_state: GenerationSnapshot) -> None:
        self._active = prior_state

    def abort(self, prepared: PreparedParticipant) -> None:
        return None
