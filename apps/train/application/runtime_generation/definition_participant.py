"""Data Definition runtime-generation participant."""

from apps.common.runtime_generation import GenerationCandidate, PreparedParticipant
from apps.common.runtime_generation import GenerationSnapshot

from .errors import ParticipantPrepareError
from apps.train.controllers.data_definition_controller import DataDefinitionController


class DefinitionRuntimeParticipant:
    name = "Data Definition"

    def __init__(
        self,
        active: GenerationSnapshot,
        controller: DataDefinitionController,
    ) -> None:
        self._active = active
        self._controller = controller
        self._controller.bind_runtime_generation(active)

    @property
    def active_generation_id(self) -> str:
        return self._controller.runtime_generation_id

    @property
    def active_snapshot(self) -> GenerationSnapshot:
        return self._active

    @property
    def controller_state(self):  # noqa: ANN201
        return self._controller.runtime_controller_state

    def revision_token(self) -> str:
        return self._controller.runtime_revision_token()

    def prepare(self, candidate: GenerationCandidate) -> PreparedParticipant:
        snapshot = candidate.snapshot
        if snapshot.manifest.generation.generation_id != candidate.persisted_generation:
            raise ParticipantPrepareError(
                "definition_candidate_mismatch", "Saved candidate identity mismatch."
            )
        try:
            controller_candidate = self._controller.prepare_runtime_generation(snapshot)
        except RuntimeError as exc:
            if str(exc) == "definition_draft_reconciliation_required":
                raise ParticipantPrepareError(
                    "definition_draft_reconciliation_required",
                    "Dirty Data Definition draft preserved; resolve it before apply.",
                    "Save Definition or Reset Draft, then Retry Apply.",
                ) from exc
            raise
        return PreparedParticipant(
            self.name,
            candidate.generation_id,
            self.revision_token(),
            (snapshot, controller_candidate),
        )

    def commit(self, prepared: PreparedParticipant) -> GenerationSnapshot:
        if prepared.source_revision != self.revision_token():
            raise ParticipantPrepareError(
                "definition_runtime_revision_stale",
                "Data Definition draft changed after prepare.",
                "Retry Apply",
            )
        snapshot, controller_candidate = prepared.payload
        controller_prior = self._controller.commit_runtime_generation(
            controller_candidate
        )
        prior = self._active, controller_prior
        self._active = snapshot
        return prior

    def rollback(self, prior_state: object) -> None:
        self._active, controller_prior = prior_state
        self._controller.rollback_runtime_generation(controller_prior)

    def abort(self, prepared: PreparedParticipant) -> None:
        return None
