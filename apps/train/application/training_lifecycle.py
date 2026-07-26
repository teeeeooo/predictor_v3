"""Qt-free training request, execution, and Candidate publication boundary."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from apps.common.model_lifecycle.resolver import ActiveModelResolver
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.common.model_lifecycle.publication_errors import (
    CandidatePublicationValidationError,
)
from apps.common.model_lifecycle.durability_errors import (
    LifecycleRecoveryRequiredError,
)
from apps.train.application.candidate_publication import (
    CandidateArtifactGenerationError,
    CandidatePublicationPort,
)
from apps.train.application.experiments.execution_lock import (
    ExecutionLockConflict,
)
from apps.train.application.experiments.execution_owner import (
    TrainingExecutionOwnership,
    lock_conflict_result,
)
from apps.train.application.experiments.terminal_policy import (
    apply_exploratory_terminal_policy,
)
from apps.train.ports.training_execution_port import (
    TrainingExecutionCallbacks,
    TrainingExecutionFactory,
    TrainingExecutionPort,
)
from apps.train.services.training_service import TrainingService
from apps.train.state.training_run_state import (
    TrainingLogEvent,
    TrainingProgress,
    TrainingRequest,
    TrainingResourceStatus,
    TrainingResult,
)
from core.data_definition.target_registry.runtime import ModelRegistrySnapshot
from core.ml.artifacts import MODEL_FILE, TRAIN_DATA_FILE


class TrainingLifecycleService:
    """Coordinate one immutable request through execution and publication."""

    def __init__(
        self,
        *,
        validation: TrainingService | None = None,
        execution: TrainingExecutionPort | None = None,
        execution_factory: TrainingExecutionFactory | None = None,
        registry_provider: Callable[[], ModelRegistrySnapshot] | None = None,
        repository: ModelLifecycleRepository | None = None,
        publisher: CandidatePublicationPort | None = None,
        execution_lock_factory=None,  # noqa: ANN001
    ) -> None:
        self._validation = validation or TrainingService()
        self._execution = execution
        self._execution_factory = execution_factory
        self._registry_provider = registry_provider
        self._repository = repository
        self._publisher = publisher
        self._execution_ownership = TrainingExecutionOwnership(
            repository, execution_lock_factory
        )
        self._is_running = False
        self._last_result: TrainingResult | None = None
        self._active_request: TrainingRequest | None = None
        self._staging: Path | None = None
        self._callbacks: dict[str, Callable | None] = {}

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def last_result(self) -> TrainingResult | None:
        return self._last_result

    @property
    def active_request(self) -> TrainingRequest | None:
        return self._active_request

    def registry_snapshot(self) -> ModelRegistrySnapshot:
        from core.ml.registry import compatibility_registry_snapshot

        return (
            self._registry_provider()
            if self._registry_provider else compatibility_registry_snapshot()
        )

    def resource_status(
        self,
        data_path: str | None = None,
        model_output_path: str | None = None,
    ) -> TrainingResourceStatus:
        if self._repository is None:
            return self._validation.resource_status(data_path, model_output_path)
        resolution = ActiveModelResolver(self._repository).resolve()
        base = self._validation.resource_status(
            data_path,
            resolution.model_path or str(self._repository.root / ".missing-active-model.pkl"),
        )
        lifecycle_message = "" if resolution.status == "resolved" else resolution.message
        return replace(
            base,
            model_path=resolution.model_path,
            model_status=(
                "exists" if resolution.status == "resolved" else resolution.status
            ),
            message="; ".join(
                item for item in (base.message, lifecycle_message) if item
            ),
        )

    def start(
        self,
        request: TrainingRequest | str | None = None,
        *,
        data_path: str | None = None,
        model_output_path: str | None = None,
        **callbacks,
    ) -> TrainingResult | None:
        if self._is_running:
            raise RuntimeError("Training run already in progress.")
        resolved = self._freeze_request(request, data_path, model_output_path)
        invalid = self._validation.validate_request(resolved)
        if invalid is not None:
            self._last_result = invalid
            _notify(callbacks.get("status_callback"), invalid.message)
            _notify(callbacks.get("failed_callback"), invalid)
            return invalid
        if self._repository is not None:
            try:
                self._execution_ownership.acquire(resolved)
            except ExecutionLockConflict as exc:
                result = lock_conflict_result(resolved, exc)
                self._last_result = result
                _notify(callbacks.get("status_callback"), result.message)
                _notify(callbacks.get("failed_callback"), result)
                return result
        if self._repository is not None:
            try:
                self._staging = self._repository.create_staging(resolved.candidate_id)
            except Exception as exc:
                self._release_execution_lock()
                result = _error_result(resolved, str(exc).splitlines()[0])
                self._last_result = result
                _notify(callbacks.get("status_callback"), result.message)
                _notify(callbacks.get("failed_callback"), result)
                return result
            resolved = replace(
                resolved, model_output_path=str(self._staging / "model.pkl")
            )
        self._active_request = resolved
        self._callbacks = callbacks
        self._update_execution_stage("training_starting")
        _notify(callbacks.get("status_callback"), "Training run starting.")
        try:
            _notify(callbacks.get("accepted_callback"), resolved)
        except Exception as exc:
            result = _error_result(
                resolved,
                "Training preflight persistence failed: "
                f"{str(exc).splitlines()[0]}",
            )
            self._discard_staging()
            self._release_execution_lock()
            self._active_request = None
            self._callbacks = {}
            self._last_result = result
            _notify(callbacks.get("failed_callback"), result)
            return result
        return self._start_execution(resolved)

    def cancel(self) -> bool:
        return self._execution.cancel() if self._execution is not None else False

    def _freeze_request(
        self,
        request: TrainingRequest | str | None,
        data_path: str | None,
        model_output_path: str | None,
    ) -> TrainingRequest:
        if isinstance(request, TrainingRequest):
            resolved = request
        else:
            resolved = TrainingRequest(
                run_id=f"train-{uuid4().hex}",
                data_path=str(data_path or request or TRAIN_DATA_FILE),
                model_output_path=str(model_output_path or MODEL_FILE),
            )
        if not resolved.candidate_id:
            resolved = replace(resolved, candidate_id=f"candidate-{resolved.run_id}")
        if resolved.registry_payload_json or self._registry_provider is None:
            return resolved
        snapshot = self._registry_provider()
        return replace(
            resolved,
            preprocess_version=snapshot.preprocessing_version,
            generation_id=snapshot.generation_id,
            registry_fingerprint=snapshot.registry_fingerprint,
            ordered_ml_fingerprint=snapshot.ordered_ml_fingerprint,
            derived_semantics_fingerprint=snapshot.derived_semantics_fingerprint,
            one_hot_fingerprint=snapshot.one_hot_fingerprint,
            registry_payload_json=json.dumps(
                snapshot.to_payload(), ensure_ascii=False, separators=(",", ":")
            ),
        )

    def _start_execution(self, request: TrainingRequest) -> TrainingResult | None:
        if self._execution is None and self._execution_factory is not None:
            self._execution = self._execution_factory()
        if self._execution is None:
            result = replace(
                _error_result(request, "Training execution adapter is not configured."),
                candidate_id=request.candidate_id,
            )
            self._finish("failed", result)
            return result
        self._is_running = True
        try:
            self._execution.start(request, TrainingExecutionCallbacks(
                log=lambda event: _notify(self._callbacks.get("log_callback"), event),
                progress=self._handle_progress,
                finished=lambda result: self._finish("finished", result),
                failed=lambda result: self._finish("failed", result),
                cancelled=lambda result: self._finish("cancelled", result),
            ))
        except Exception as exc:
            result = _error_result(request, str(exc).splitlines()[0])
            self._finish("failed", result)
            return result
        return None

    def _handle_progress(self, progress: TrainingProgress) -> None:
        self._update_execution_stage("training")
        _notify(self._callbacks.get("progress_callback"), progress)
        if progress.message:
            _notify(self._callbacks.get("status_callback"), progress.message)

    def _finish(self, terminal: str, result: TrainingResult) -> None:
        request = self._active_request
        failure_stage = (
            "training_execution" if terminal != "finished" else ""
        )
        failure_reason = result.message if failure_stage else ""
        terminal, result, failure_stage, failure_reason = (
            apply_exploratory_terminal_policy(
                request, terminal, result, failure_stage, failure_reason
            )
        )
        if terminal == "finished" and request is not None and self._repository is not None:
            self._update_execution_stage("candidate_publication")
            try:
                assert self._publisher is not None and self._staging is not None
                result = self._publisher.publish(request, result, self._staging)
                self._staging = None
            except CandidateArtifactGenerationError as exc:
                terminal = "failed"
                failure_stage = "artifact_generation_or_validation"
                failure_reason = str(exc).splitlines()[0]
                result = replace(
                    result,
                    status="error",
                    message=(
                        "Candidate artifact generation failed: "
                        f"{str(exc).splitlines()[0]}"
                    ),
                    candidate_id=request.candidate_id,
                    publication_outcome="artifact_generation_failed",
                )
            except CandidatePublicationValidationError as exc:
                terminal = "failed"
                failure_stage = "lifecycle_validation"
                failure_reason = str(exc).splitlines()[0]
                result = replace(
                    result,
                    status="error",
                    message=failure_reason,
                    candidate_id=request.candidate_id,
                    publication_outcome="failed",
                )
            except LifecycleRecoveryRequiredError as exc:
                terminal = "failed"
                failure_stage = "candidate_publication_durability"
                failure_reason = str(exc).splitlines()[0]
                result = replace(
                    result,
                    status="error",
                    message=f"Candidate publication recovery required: {str(exc).splitlines()[0]}",
                    candidate_id=request.candidate_id,
                    publication_outcome="recovery-required",
                )
            except Exception as exc:
                terminal = "failed"
                failure_stage = "candidate_publication"
                failure_reason = str(exc).splitlines()[0]
                result = replace(
                    result,
                    status="error",
                    message=f"Candidate publication failed: {str(exc).splitlines()[0]}",
                    candidate_id=request.candidate_id,
                    publication_outcome="failed",
                )
        if (
            terminal != "finished"
            and request is not None
            and self._repository is not None
            and self._publisher is not None
            and self._staging is not None
        ):
            outcome = _terminal_publication_outcome(terminal, result)
            try:
                result = self._publisher.preserve_terminal_evidence(
                    request,
                    result,
                    self._staging,
                    publication_outcome=outcome,
                    failure_stage=failure_stage,
                    failure_reason=failure_reason,
                )
                self._staging = None
            except Exception as evidence_exc:
                result = replace(
                    result,
                    message=(
                        f"{result.message}; terminal evidence preservation failed: "
                        f"{str(evidence_exc).splitlines()[0]}"
                    ).strip("; "),
                )
        if terminal != "finished":
            self._discard_staging()
        self._is_running = False
        self._active_request = None
        self._last_result = result
        messages = {
            "finished": "Training run finished; Candidate published.",
            "failed": f"Training run failed: {result.message}",
            "cancelled": "Training run cancelled.",
        }
        _notify(self._callbacks.get("status_callback"), messages[terminal])
        _notify(self._callbacks.get(f"{terminal}_callback"), result)
        execution, self._execution = self._execution, None
        if execution is not None:
            execution.dispose()
        self._release_execution_lock()
        self._callbacks = {}

    def _discard_staging(self) -> None:
        if self._staging is not None:
            assert self._repository is not None
            self._repository.discard_staging(self._staging)
            self._staging = None

    def _update_execution_stage(self, stage: str) -> None:
        self._execution_ownership.update(stage)

    def _release_execution_lock(self) -> None:
        self._execution_ownership.release()


def _error_result(request: TrainingRequest, message: str) -> TrainingResult:
    return TrainingResult(
        request.run_id, "error", model_path=request.model_output_path,
        message=message, generation_id=request.generation_id,
        registry_fingerprint=request.registry_fingerprint,
        candidate_id=request.candidate_id,
    )


def _terminal_publication_outcome(
    terminal: str,
    result: TrainingResult,
) -> str:
    if result.publication_outcome in {
        "artifact_generation_failed",
        "recovery-required",
        "failed",
    }:
        return result.publication_outcome
    if terminal == "cancelled":
        return "cancelled"
    if result.status == "partial":
        return "partial"
    return "failed"


def _notify(callback, payload) -> None:  # noqa: ANN001
    if callback is not None:
        callback(payload)
