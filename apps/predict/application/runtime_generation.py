"""Standalone Predict generation drift detection and reload boundary."""

from __future__ import annotations

from uuid import uuid4

from apps.common.runtime_generation import GenerationCandidate


class StandalonePredictGenerationGuard:
    """Reload latest persisted generation or block prediction without data loss."""

    def __init__(self, repository, participant) -> None:  # noqa: ANN001
        self._repository = repository
        self._participant = participant
        self.status = "Up to date"
        self.blocker_code = ""
        self.recommended_action = ""

    @property
    def active_generation_id(self) -> str:
        return self._participant.active_generation_id

    def ensure_current(self) -> bool:
        """Check the pointer at startup, explicit refresh, or prediction boundary."""
        try:
            snapshot = self._repository.read_active()
        except Exception:
            return self._block("Reload failed", "candidate_generation_load_failed", "Retry Reload")
        persisted = snapshot.manifest.generation.generation_id
        if persisted == self._participant.active_generation_id:
            compatibility = self._participant.model_compatibility
            if compatibility.status != "compatible":
                return self._block(
                    "Retraining required", "model_incompatible",
                    "Retrain or reload a compatible model",
                )
            self.status = "Up to date"
            self.blocker_code = ""
            self.recommended_action = ""
            return True
        revision = self._participant.revision_token()
        candidate = GenerationCandidate(
            snapshot, persisted, ((self._participant.name, revision),), uuid4().hex
        )
        try:
            prepared = self._participant.prepare(candidate)
            if prepared.compatibility != "compatible":
                self._participant.abort(prepared)
                return self._block(
                    "Retraining required",
                    "model_incompatible",
                    "Retrain or reload a compatible model",
                )
            if (
                self._repository.read_active().manifest.generation.generation_id != persisted
                or self._participant.revision_token() != revision
            ):
                self._participant.abort(prepared)
                return self._block("Reload failed", "stale_candidate", "Retry Reload")
            prior = self._participant.commit(prepared)
            if self._participant.active_generation_id != persisted:
                self._participant.rollback(prior)
                return self._block("Restart required", "mixed_generation_detected", "Restart Required")
            self._participant.finalize(prior)
        except Exception:
            if "prepared" in locals():
                try:
                    self._participant.abort(prepared)
                except Exception:
                    return self._block(
                        "Restart required", "predict_abort_failed", "Restart Required"
                    )
            return self._block("Reload failed", "predict_reload_failed", "Retry Reload")
        self.status = "Up to date"
        self.blocker_code = ""
        self.recommended_action = ""
        return True

    def _block(self, status: str, blocker: str, action: str) -> bool:
        self.status = status
        self.blocker_code = blocker
        self.recommended_action = action
        return False
