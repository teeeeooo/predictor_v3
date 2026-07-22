"""Data Mapping runtime-generation participant and reconciliation actions."""

from apps.common.runtime_generation import GenerationCandidate, PreparedParticipant
from apps.common.runtime_generation import GenerationSnapshot
from apps.train.services.data_mapping_service import DataMappingService

from .errors import ParticipantPrepareError
from .reconciliation import MappingReconciliationItem, reconcile_mapping_requirements


class MappingRuntimeParticipant:
    name = "Data Mapping"

    def __init__(self, active: GenerationSnapshot, service: DataMappingService) -> None:
        self._active = active
        self._service = service
        self._service.activate_initial_requirements(active.projections.mapping_requirements)
        self._pending: GenerationCandidate | None = None
        self._review: tuple[MappingReconciliationItem, ...] = ()

    @property
    def active_generation_id(self) -> str:
        return self._active.manifest.generation.generation_id

    def revision_token(self) -> str:
        return f"{self.active_generation_id}:{self._service.draft_revision}"

    def prepare(self, candidate: GenerationCandidate) -> PreparedParticipant:
        if self._service.is_dirty:
            self._pending = candidate
            self._review = reconcile_mapping_requirements(
                self._active.manifest, candidate.snapshot.manifest
            )
            self._review += tuple(
                MappingReconciliationItem(
                    item.identity,
                    "dirty column removal",
                    item.summary,
                    True,
                )
                for item in self._review
                if item.classification == "removed requirement"
            )
            raise ParticipantPrepareError(
                "mapping_reconciliation_required",
                "Dirty Mapping draft preserved; review the pending requirement generation.",
                "Review Mapping Update",
                tuple(item.classification for item in self._review[:12]),
            )
        preview = self._service.preview_requirement_projection(
            candidate.snapshot.projections.mapping_requirements
        )
        if preview.mapping_requirement_conflicts:
            raise ParticipantPrepareError(
                "mapping_requirement_conflict",
                "Candidate Mapping requirements conflict.",
                "Review Mapping Update",
                tuple(item.message for item in preview.mapping_requirement_conflicts[:12]),
            )
        blocking = tuple(
            item for item in preview.validation_errors if item.severity == "error"
        )
        if blocking:
            raise ParticipantPrepareError(
                "mapping_coverage_insufficient",
                "Candidate Mapping coverage is insufficient for required runtime values.",
                "Review Mapping Update",
                tuple(item.message for item in blocking[:12]),
            )
        payload = (
            candidate.snapshot,
            candidate.snapshot.projections.mapping_requirements,
            self._service.draft_revision,
        )
        return PreparedParticipant(
            self.name, candidate.generation_id, self.revision_token(), payload
        )

    def commit(self, prepared: PreparedParticipant) -> object:
        snapshot, requirements, revision = prepared.payload
        mapping_prior, _projected = self._service.commit_requirement_projection(
            requirements, expected_revision=revision
        )
        prior = self._active, mapping_prior
        self._active = snapshot
        self._pending = None
        self._review = ()
        return prior

    def rollback(self, prior_state: object) -> None:
        active, mapping_prior = prior_state
        self._service.rollback_requirement_projection(mapping_prior)
        self._active = active

    def abort(self, prepared: PreparedParticipant) -> None:
        return None

    def review_update(self) -> tuple[MappingReconciliationItem, ...]:
        return self._review

    def save_mapping(self) -> bool:
        result, _snapshot = self._service.save_mapping()
        return result.success

    def discard_and_reload(self) -> None:
        self._service.discard_dirty_draft()
