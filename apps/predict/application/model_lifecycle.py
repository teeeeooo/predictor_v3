"""Loaded-model identity, Active observation, and atomic Predict reload."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from apps.common.model_lifecycle import ActiveModelResolver, ModelLifecycleRepository
from apps.common.model_lifecycle.errors import StaleActiveRevisionError
from apps.predict.application.runtime_snapshot import PredictRuntimeSnapshot
from apps.predict.ports.prediction_workflow_ports import PredictionServicePort


@dataclass(frozen=True)
class LoadedModelIdentity:
    candidate_id: str = ""
    active_revision: int = 0
    generation_id: str = ""


@dataclass(frozen=True)
class PredictModelLifecycleStatus:
    status: str
    loaded: LoadedModelIdentity
    active_candidate_id: str = ""
    active_revision: int = 0
    message: str = ""
    diagnostic: str = ""

    @property
    def reload_required(self) -> bool:
        return self.status in {"reload-required", "reload-failed"}


@dataclass(frozen=True)
class ModelReloadOutcome:
    status: str
    model_status: PredictModelLifecycleStatus
    message: str


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
        self._loaded = LoadedModelIdentity()
        self._last_status = PredictModelLifecycleStatus(
            "startup-failed",
            self._loaded,
            message="사용할 수 있는 모델이 아직 로드되지 않았습니다.",
        )

    @property
    def loaded(self) -> LoadedModelIdentity:
        return self._loaded

    @property
    def status(self) -> PredictModelLifecycleStatus:
        return self._last_status

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
        self._loaded = LoadedModelIdentity(
            candidate_id,
            active_revision,
            self._runtime_snapshot.generation_id,
        )
        self.refresh()

    def record_startup_failure(self, message: str) -> None:
        self._last_status = PredictModelLifecycleStatus(
            "startup-failed",
            self._loaded,
            message="현재 Active 모델을 시작할 수 없습니다.",
            diagnostic=message,
        )

    def refresh(self) -> PredictModelLifecycleStatus:
        resolution = ActiveModelResolver(self._repository).resolve()
        if resolution.status != "resolved":
            status = "active-unavailable" if self._loaded.candidate_id else "startup-failed"
            message = (
                "Active 상태를 확인할 수 없지만 기존에 로드된 모델을 계속 사용합니다."
                if self._loaded.candidate_id
                else "사용할 수 있는 Active 모델이 없습니다."
            )
            self._last_status = PredictModelLifecycleStatus(
                status,
                self._loaded,
                message=message,
                diagnostic=resolution.message,
            )
            return self._last_status
        differs = (
            resolution.candidate_id != self._loaded.candidate_id
            or resolution.revision != self._loaded.active_revision
        )
        self._last_status = PredictModelLifecycleStatus(
            "reload-required" if differs else "current",
            self._loaded,
            resolution.candidate_id,
            resolution.revision,
            (
                "새 Active 모델이 있습니다. 현재 모델을 계속 사용 중이며 다시 불러오기가 필요합니다."
                if differs
                else "현재 Active 모델을 사용 중입니다."
            ),
        )
        return self._last_status

    def reload(
        self,
        *,
        prediction_running: bool,
        swap_service: Callable[[PredictionServicePort], None],
    ) -> ModelReloadOutcome:
        if prediction_running:
            status = self.refresh()
            return ModelReloadOutcome(
                "blocked",
                status,
                "예측 실행 중에는 모델을 다시 불러올 수 없습니다.",
            )
        resolution = ActiveModelResolver(self._repository).resolve()
        if resolution.status != "resolved":
            return self._reload_failure(
                "Active 모델을 안전하게 읽을 수 없어 기존 모델을 계속 사용합니다.",
                resolution.message,
            )
        try:
            candidate = self._repository.read_candidate(resolution.candidate_id)
            self._validate_compatibility(candidate.manifest)
            prepared = self._service_factory(
                str(candidate.model_path),
                self._runtime_snapshot,
            )
            prepared.prepare_model()
            with self._repository.guard_active(
                resolution.candidate_id,
                resolution.revision,
            ):
                swap_service(prepared)
                self._loaded = LoadedModelIdentity(
                    resolution.candidate_id,
                    resolution.revision,
                    self._runtime_snapshot.generation_id,
                )
        except StaleActiveRevisionError as exc:
            return self._reload_failure(
                "준비 중 Active 모델이 변경되어 다시 불러오기를 적용하지 않았습니다.",
                str(exc),
            )
        except Exception as exc:
            return self._reload_failure(
                "새 모델을 불러오지 못했습니다. 기존 모델을 계속 사용합니다.",
                f"{type(exc).__name__}: {str(exc)}",
            )
        status = self.refresh()
        return ModelReloadOutcome(
            "reloaded",
            status,
            "새 Active 모델을 안전하게 다시 불러왔습니다.",
        )

    def _reload_failure(self, message: str, diagnostic: str) -> ModelReloadOutcome:
        observed = self.refresh()
        self._last_status = PredictModelLifecycleStatus(
            "reload-failed" if self._loaded.candidate_id else "startup-failed",
            self._loaded,
            observed.active_candidate_id,
            observed.active_revision,
            message,
            diagnostic,
        )
        return ModelReloadOutcome("failed", self._last_status, message)

    def _validate_compatibility(self, manifest) -> None:  # noqa: ANN001
        runtime = self._runtime_snapshot
        checks = {
            "generation": (manifest.definition_generation_id, runtime.generation_id),
            "registry": (manifest.registry_fingerprint, runtime.target_registry_fingerprint),
            "feature order": (manifest.ordered_ml_fingerprint, runtime.ordered_ml_fingerprint),
            "derived semantics": (
                manifest.derived_semantics_fingerprint,
                runtime.derived_fingerprint,
            ),
            "one-hot": (manifest.one_hot_fingerprint, runtime.one_hot_fingerprint),
            "preprocessing": (
                manifest.preprocessing_version,
                runtime.preprocessing_version,
            ),
        }
        mismatched = tuple(name for name, values in checks.items() if values[0] != values[1])
        if mismatched:
            raise ValueError("Active Candidate compatibility differs: " + ", ".join(mismatched))
        if tuple(item.ml_name for item in manifest.targets) != runtime.active_targets:
            raise ValueError("Active Candidate production targets are incomplete")
        ordered = runtime.ordered_input_ml_names
        for target in manifest.targets:
            positions = [ordered.index(name) for name in target.feature_names if name in ordered]
            if len(positions) != len(target.feature_names) or positions != sorted(positions):
                raise ValueError(f"Active Candidate feature order is incompatible: {target.ml_name}")
