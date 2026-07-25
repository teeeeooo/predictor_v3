"""Controlled Predict startup resolution for one immutable Active Candidate."""

from __future__ import annotations

from .active_contracts import ModelResolution
from .durability_errors import LifecycleRecoveryRequiredError
from .errors import ModelLifecycleError
from .repository import ModelLifecycleRepository


class ActiveModelResolver:
    def __init__(self, repository: ModelLifecycleRepository) -> None:
        self._repository = repository

    def resolve(self) -> ModelResolution:
        try:
            reference = self._repository.read_active(optional=True)
            if reference is None:
                return ModelResolution(
                    "missing-active",
                    message="No Active model has been selected. Training can continue in Bootstrap mode.",
                )
            candidate = self._repository.read_candidate(reference.candidate_id)
        except LifecycleRecoveryRequiredError as exc:
            return ModelResolution(
                "recovery-required",
                message=f"Active model recovery is required: {str(exc).splitlines()[0]}",
            )
        except (OSError, ModelLifecycleError) as exc:
            return ModelResolution(
                "invalid-active",
                message=f"Active model is unavailable: {str(exc).splitlines()[0]}",
            )
        return ModelResolution(
            "resolved",
            str(candidate.model_path),
            candidate.manifest.candidate_id,
            reference.revision,
            "Active model resolved.",
        )
