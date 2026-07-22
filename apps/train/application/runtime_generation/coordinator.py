"""Atomic staged cutover coordinator for TrainShell generation consumers."""

from __future__ import annotations

from uuid import uuid4

from apps.common.runtime_generation import (
    GenerationCandidate,
    GenerationParticipant,
    GenerationTransitionStatus,
    ParticipantEvidence,
)
from apps.common.runtime_generation import DataDefinitionGenerationRepositoryPort


class RuntimeGenerationCoordinator:
    """Prepare all required participants, then commit or restore them as one unit."""

    def __init__(self, repository: DataDefinitionGenerationRepositoryPort, participants) -> None:  # noqa: ANN001
        self._repository = repository
        self._participants: tuple[GenerationParticipant, ...] = tuple(participants)
        self._prepared_candidate: GenerationCandidate | None = None
        self._prepared_tokens = ()
        names = tuple(item.name for item in self._participants)
        if len(names) != len(set(names)) or not names:
            raise ValueError("runtime generation participants must be non-empty and unique")
        active = self._common_active_generation()
        persisted = self._repository.read_active().manifest.generation.generation_id
        self._status = GenerationTransitionStatus(
            "current" if active == persisted else "pending",
            "Up to date" if active == persisted else "Saved; update pending",
            active,
            persisted,
            "" if active == persisted else persisted,
            recommended_action="Retry Apply" if active != persisted else "",
            participants=self._evidence(),
        )

    def inspect_status(self) -> GenerationTransitionStatus:
        return self._status

    def request_cutover(self) -> GenerationTransitionStatus:
        """Read the latest persisted snapshot once and attempt one atomic cutover."""
        status = self.prepare_all()
        return self.commit_all() if status.code == "prepared" else status

    def retry_pending_generation(self) -> GenerationTransitionStatus:
        """Retry from a newly read immutable candidate, never an old prepare token."""
        return self.request_cutover()

    def prepare_all(self) -> GenerationTransitionStatus:
        """Prepare a newly read candidate without changing any active participant."""
        self.abort_prepared_candidate()
        try:
            snapshot = self._repository.read_active()
        except Exception:
            return self._failed(
                "candidate_load_failed", "Saved; update pending", "candidate-load",
                "candidate_generation_load_failed", "Retry Apply",
            )
        persisted = snapshot.manifest.generation.generation_id
        if all(item.active_generation_id == persisted for item in self._participants):
            self._status = GenerationTransitionStatus(
                "current", "Up to date", persisted, persisted,
                participants=self._evidence(),
            )
            return self._status
        candidate = GenerationCandidate(
            snapshot,
            persisted,
            tuple((item.name, item.revision_token()) for item in self._participants),
            uuid4().hex,
        )
        prepared = []
        try:
            for participant in self._participants:
                prepared.append(participant.prepare(candidate))
        except Exception as exc:
            abort_failed = self._abort_tokens(tuple(prepared))
            code = "abort_failed" if abort_failed else getattr(exc, "code", "participant_prepare_failed")
            action = "Restart Required" if abort_failed else getattr(exc, "recommended_action", "Retry Apply")
            message = (
                "Restart required" if abort_failed
                else "Mapping review required" if code == "mapping_reconciliation_required"
                else "Saved; update pending"
            )
            return self._failed(
                code, message, "abort" if abort_failed else "prepare", code, action,
                candidate.generation_id, tuple(prepared),
                mapping_conflicts=getattr(exc, "details", ()),
            )
        self._prepared_candidate = candidate
        self._prepared_tokens = tuple(prepared)
        self._status = GenerationTransitionStatus(
            "prepared", "Update prepared", self._common_active_generation(),
            candidate.persisted_generation, candidate.generation_id,
            participants=self._evidence(self._prepared_tokens),
            model_compatibility=next(
                (item.compatibility for item in prepared if item.compatibility != "compatible"),
                "compatible",
            ),
        )
        return self._status

    def commit_all(self) -> GenerationTransitionStatus:
        """Commit the currently prepared candidate after all stale guards pass."""
        if self._prepared_candidate is None:
            return self._failed(
                "prepare_required", "Saved; update pending", "commit",
                "prepare_required", "Retry Apply",
            )
        candidate = self._prepared_candidate
        prepared = self._prepared_tokens
        if not self._candidate_is_current(candidate):
            abort_failed = self._abort_tokens(prepared)
            self._clear_prepared()
            return self._failed(
                "abort_failed" if abort_failed else "stale",
                "Restart required" if abort_failed else "Saved; update pending",
                "abort" if abort_failed else "stale-guard",
                "abort_failed" if abort_failed else "stale_candidate",
                "Restart Required" if abort_failed else "Retry Apply",
                candidate.generation_id, prepared,
            )
        status = self._commit(candidate, prepared)
        self._clear_prepared()
        return status

    def abort_prepared_candidate(self) -> GenerationTransitionStatus:
        """Abort staged state explicitly while leaving active state unchanged."""
        if not self._prepared_tokens:
            return self._status
        failed = self._abort_tokens(self._prepared_tokens)
        pending = self._prepared_candidate.generation_id if self._prepared_candidate else ""
        self._clear_prepared()
        if failed:
            return self._failed(
                "abort_failed", "Restart required", "abort", "abort_failed",
                "Restart Required", pending,
            )
        return self._failed(
            "aborted", "Saved; update pending", "abort", "transition_aborted",
            "Retry Apply", pending,
        )

    def _commit(self, candidate: GenerationCandidate, prepared) -> GenerationTransitionStatus:  # noqa: ANN001
        prior_states = []
        try:
            for participant, token in zip(self._participants, prepared):
                prior_states.append((participant, participant.commit(token)))
        except Exception:
            rollback_failed = False
            for participant, prior in reversed(prior_states):
                try:
                    participant.rollback(prior)
                except Exception:
                    rollback_failed = True
            code = "rollback_failed" if rollback_failed else "participant_commit_failed"
            message = "Restart required" if rollback_failed else "Saved; update pending"
            return self._failed(
                code, message, "rollback" if rollback_failed else "commit", code,
                "Restart Required" if rollback_failed else "Retry Apply",
                candidate.generation_id,
            )
        if any(item.active_generation_id != candidate.generation_id for item in self._participants):
            rollback_failed = False
            for participant, prior in reversed(prior_states):
                try:
                    participant.rollback(prior)
                except Exception:
                    rollback_failed = True
            return self._failed(
                "rollback_failed" if rollback_failed else "mixed_generation",
                "Restart required",
                "rollback" if rollback_failed else "post-commit",
                "rollback_failed" if rollback_failed else "mixed_generation_detected",
                "Restart Required",
                candidate.generation_id,
            )
        compatibility = next(
            (item.compatibility for item in prepared if item.compatibility != "compatible"),
            "compatible",
        )
        message = "Retraining required" if compatibility != "compatible" else "Saved and applied"
        self._status = GenerationTransitionStatus(
            "retraining_required" if compatibility != "compatible" else "applied",
            message,
            candidate.generation_id,
            candidate.persisted_generation,
            participants=self._evidence(),
            model_compatibility=compatibility,
            recommended_action="Retrain model" if compatibility != "compatible" else "",
        )
        return self._status

    def _candidate_is_current(self, candidate: GenerationCandidate) -> bool:
        try:
            persisted = self._repository.read_active().manifest.generation.generation_id
        except Exception:
            return False
        return (
            persisted == candidate.persisted_generation == candidate.generation_id
            and tuple((item.name, item.revision_token()) for item in self._participants)
            == candidate.participant_revisions
        )

    def _common_active_generation(self) -> str:
        generations = {item.active_generation_id for item in self._participants}
        return next(iter(generations)) if len(generations) == 1 else "mixed"

    def _evidence(self, prepared=()) -> tuple[ParticipantEvidence, ...]:  # noqa: ANN001
        by_name = {item.participant: item for item in prepared}
        return tuple(
            ParticipantEvidence(
                item.name,
                item.active_generation_id,
                by_name[item.name].generation_id if item.name in by_name else "",
                "prepared" if item.name in by_name else "active",
            )
            for item in self._participants
        )

    def _abort_tokens(self, prepared) -> bool:  # noqa: ANN001
        failed = False
        for participant, token in reversed(list(zip(self._participants, prepared))):
            try:
                participant.abort(token)
            except Exception:
                failed = True
        return failed

    def _clear_prepared(self) -> None:
        self._prepared_candidate = None
        self._prepared_tokens = ()

    def _failed(
        self, code: str, message: str, stage: str, blocker: str, action: str,
        pending: str = "",
        prepared=(),  # noqa: ANN001
        mapping_conflicts: tuple[str, ...] = (),
    ) -> GenerationTransitionStatus:
        persisted = pending
        if not persisted:
            try:
                persisted = self._repository.read_active().manifest.generation.generation_id
            except Exception:
                persisted = self._status.persisted_generation
        self._status = GenerationTransitionStatus(
            code, message, self._common_active_generation(), persisted, persisted,
            stage, blocker, action, self._evidence(prepared),
            mapping_conflicts=mapping_conflicts,
        )
        return self._status
