"""Training lifecycle wiring for the shared workspace execution lock."""

from __future__ import annotations

import json

from apps.train.application.experiments.execution_lock import (
    WorkspaceExecutionLock,
)
from apps.train.state.training_run_state import TrainingResult


class TrainingExecutionOwnership:
    def __init__(self, repository, lock_factory=None) -> None:  # noqa: ANN001
        self._repository = repository
        self._lock_factory = lock_factory
        self._lock: WorkspaceExecutionLock | None = None

    def acquire(self, request) -> None:  # noqa: ANN001
        if self._repository is None:
            return
        factory = self._lock_factory or (
            lambda current: WorkspaceExecutionLock(
                self._repository.root,
                owner=current.execution_owner,
                run_id=current.run_id,
                campaign_id=current.campaign_id,
            )
        )
        lock = factory(request)
        lock.acquire()
        self._lock = lock

    def update(self, stage: str) -> None:
        if self._lock is not None:
            self._lock.update(stage)

    def release(self) -> None:
        lock, self._lock = self._lock, None
        if lock is not None:
            lock.release()


def lock_conflict_result(request, conflict) -> TrainingResult:  # noqa: ANN001
    return TrainingResult(
        run_id=request.run_id,
        status="lock_conflict",
        model_path=request.model_output_path,
        message=str(conflict),
        generation_id=request.generation_id,
        registry_fingerprint=request.registry_fingerprint,
        candidate_id=request.candidate_id,
        summary=json.dumps(
            conflict.metadata,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
    )
