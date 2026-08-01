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
        self._review_revision = ""

    @property
    def active_generation_id(self) -> str:
        return self._active.manifest.generation.generation_id

    @property
    def active_snapshot(self) -> GenerationSnapshot:
        return self._active

    def revision_token(self) -> str:
        return (
            f"{self.active_generation_id}:draft={self._service.draft_revision}:"
            f"dirty={int(self._service.is_dirty)}:"
            f"{self._service.mapping_resource_revision()}"
        )

    def prepare(self, candidate: GenerationCandidate) -> PreparedParticipant:
        if self._service.is_dirty:
            self._pending = candidate
            self._refresh_review()
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
        if prepared.source_revision != self.revision_token():
            raise ParticipantPrepareError(
                "mapping_revision_stale",
                "Mapping draft or concrete provider changed after prepare.",
                "Retry Apply",
            )
        snapshot, requirements, revision = prepared.payload
        mapping_prior, _projected = self._service.commit_requirement_projection(
            requirements, expected_revision=revision
        )
        prior = self._active, mapping_prior
        self._active = snapshot
        self._pending = None
        self._review = ()
        self._review_revision = ""
        return prior

    def rollback(self, prior_state: object) -> None:
        active, mapping_prior = prior_state
        self._service.rollback_requirement_projection(mapping_prior)
        self._active = active

    def abort(self, prepared: PreparedParticipant) -> None:
        return None

    def finalize(self, prior_state: object) -> None:
        return None

    def review_update(self) -> tuple[MappingReconciliationItem, ...]:
        if self._pending is not None and self._review_revision != self.revision_token():
            self._refresh_review()
        return self._review

    def save_mapping(self) -> bool:
        result, _snapshot = self._service.save_mapping()
        if result.success and self._pending is not None:
            self._refresh_review()
        return result.success

    def discard_and_reload(self) -> None:
        self._service.discard_dirty_draft()
        if self._pending is not None:
            self._refresh_review()

    def _refresh_review(self) -> None:
        if self._pending is None:
            self._review = ()
            self._review_revision = self.revision_token()
            return
        draft, baseline = self._service.draft_baseline
        self._review = reconcile_mapping_requirements(
            self._active,
            self._pending.snapshot,
            draft=draft,
            baseline=baseline,
        )
        self._review_revision = self.revision_token()
