"""Loaded-model identity, Active observation, and atomic Predict reload."""

from __future__ import annotations

from threading import Lock
import traceback
from typing import Callable

from apps.common.model_lifecycle import ActiveModelResolver, ModelLifecycleRepository
from apps.common.model_lifecycle.errors import StaleActiveRevisionError
from apps.predict.application.model_lifecycle_models import (
    LoadedModelIdentity,
    ModelReloadOutcome,
    PredictModelLifecycleStatus,
    observed_model_status,
    reload_failure_guidance,
)
from apps.predict.application.model_reload_preparation import (
    ReloadPreparationFailure,
    prepare_model_replacement,
)
from apps.predict.application.runtime_snapshot import PredictRuntimeSnapshot
from apps.predict.ports.prediction_workflow_ports import PredictionServicePort


class PredictModelLifecycleService:
    """Keep a usable loaded bundle while observing and reloading Active."""
    def __init__(
        self,
        repository: ModelLifecycleRepository,
        runtime_snapshot: PredictRuntimeSnapshot,
        service_factory: Callable[[str, PredictRuntimeSnapshot], PredictionServicePort],
    ) -> None:
        self._repository = repository
        self._runtime_snapshot = runtime_snapshot
        self._service_factory = service_factory
        self._operation_lock = Lock()
        self._next_operation_id = 0
        self._current_operation_id = 0
        self._loaded = LoadedModelIdentity()
        self._last_status = PredictModelLifecycleStatus(
            "startup-failed",
            self._loaded,
            message="사용할 수 있는 모델이 아직 로드되지 않았습니다.",
        )

    @property
    def loaded(self) -> LoadedModelIdentity:
        with self._operation_lock:
            return self._loaded

    @property
    def status(self) -> PredictModelLifecycleStatus:
        with self._operation_lock:
            return self._last_status

    def is_operation_current(self, operation_id: int) -> bool:
        with self._operation_lock:
            return operation_id == self._current_operation_id

    def set_runtime_snapshot(self, snapshot: PredictRuntimeSnapshot) -> None:
        self._runtime_snapshot = snapshot

    def initialize_loaded(
        self,
        service: PredictionServicePort,
        *,
        candidate_id: str,
        active_revision: int,
    ) -> None:
        service.prepare_model()
        with self._operation_lock:
            self._loaded = LoadedModelIdentity(
                candidate_id,
                active_revision,
                self._runtime_snapshot.generation_id,
            )
        self.refresh()

    def record_startup_failure(self, message: str) -> None:
        operation_id = self._begin_status_operation()
        status = PredictModelLifecycleStatus(
            "startup-failed",
            self.loaded,
            message="현재 Active 모델을 시작할 수 없습니다.",
            diagnostic=message,
            operation_id=operation_id,
        )
        self._publish_status(status, operation_id=operation_id)

    def refresh(self) -> PredictModelLifecycleStatus:
        operation_id = self._begin_status_operation()
        observed = self._observe_status(operation_id=operation_id)
        self._publish_status(observed, operation_id=operation_id)
        return observed

    def _observe_status(self, *, operation_id: int) -> PredictModelLifecycleStatus:
        resolution = ActiveModelResolver(self._repository).resolve()
        return observed_model_status(
            resolution,
            self.loaded,
            operation_id=operation_id,
        )

    def reload(
        self,
        *,
        prediction_running: bool,
        swap_service: Callable[[PredictionServicePort], None],
    ) -> ModelReloadOutcome:
        operation_id = self._begin_status_operation()
        if prediction_running:
            return self._reload_failure(
                "blocked",
                operation_id,
                "prediction_running",
                "Prediction is running.",
            )
        resolution = ActiveModelResolver(self._repository).resolve()
        if resolution.status != "resolved":
            return self._reload_failure(
                "failed",
                operation_id,
                (
                    "recovery_required"
                    if resolution.status == "recovery-required"
                    else "missing_active"
                    if resolution.status == "missing-active"
                    else "corrupt_active"
                ),
                resolution.message,
                resolution.diagnostic_traceback,
            )
        try:
            prepared = prepare_model_replacement(
                self._repository,
                candidate_id=resolution.candidate_id,
                runtime=self._runtime_snapshot,
                service_factory=self._service_factory,
            )
            with self._repository.guard_active(
                resolution.candidate_id,
                resolution.revision,
            ):
                with self._operation_lock:
                    if operation_id != self._current_operation_id:
                        raise StaleActiveRevisionError("reload operation was superseded")
                    swap_service(prepared)
                    self._loaded = LoadedModelIdentity(
                        resolution.candidate_id,
                        resolution.revision,
                        self._runtime_snapshot.generation_id,
                    )
        except StaleActiveRevisionError as exc:
            return self._reload_failure(
                "failed",
                operation_id,
                "stale_active_revision",
                str(exc),
                traceback.format_exc(),
            )
        except ReloadPreparationFailure as exc:
            return self._reload_failure(
                "failed",
                operation_id,
                exc.reason_code,
                exc.diagnostic,
                exc.diagnostic_traceback,
            )
        except Exception as exc:
            return self._reload_failure(
                "failed",
                operation_id,
                "internal_failure",
                f"{type(exc).__name__}: {str(exc)}",
                traceback.format_exc(),
            )
        status = self._observe_status(operation_id=operation_id)
        published = self._publish_status(status, operation_id=operation_id)
        applied = published is status
        return ModelReloadOutcome(
            "reloaded",
            published,
            "새 Active 모델을 안전하게 다시 불러왔습니다.",
            preserved_loaded_model=False,
            operation_id=operation_id,
            applied_to_shared_state=applied,
        )

    def _begin_status_operation(self) -> int:
        with self._operation_lock:
            self._next_operation_id += 1
            self._current_operation_id = self._next_operation_id
            return self._current_operation_id

    def _publish_status(
        self,
        status: PredictModelLifecycleStatus,
        *,
        operation_id: int,
    ) -> PredictModelLifecycleStatus:
        with self._operation_lock:
            if operation_id != self._current_operation_id:
                return self._last_status
            self._last_status = status
            return status

    def _reload_failure(
        self,
        outcome_status: str,
        operation_id: int,
        reason_code: str,
        diagnostic: str,
        diagnostic_traceback: str = "",
    ) -> ModelReloadOutcome:
        observed = self._observe_status(operation_id=operation_id)
        loaded = observed.loaded
        message, action = reload_failure_guidance(
            reason_code,
            loaded_model_exists=bool(loaded.candidate_id),
        )
        failure_status = PredictModelLifecycleStatus(
            "reload-failed" if loaded.candidate_id else "startup-failed",
            loaded,
            observed.active_candidate_id,
            observed.active_revision,
            message,
            diagnostic,
            diagnostic_traceback,
            reason_code,
            action,
            operation_id,
        )
        published = self._publish_status(
            failure_status,
            operation_id=operation_id,
        )
        applied = published is failure_status
        return ModelReloadOutcome(
            outcome_status,
            published,
            message,
            reason_code,
            preserved_loaded_model=bool(loaded.candidate_id),
            recommended_action=action,
            diagnostic=diagnostic,
            diagnostic_traceback=diagnostic_traceback,
            operation_id=operation_id,
            applied_to_shared_state=applied,
        )
