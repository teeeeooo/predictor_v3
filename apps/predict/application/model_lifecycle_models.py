"""Structured Predict model-lifecycle status and reload outcomes."""

from __future__ import annotations

from dataclasses import dataclass


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
    diagnostic_traceback: str = ""
    reason_code: str = ""
    recommended_action: str = ""
    operation_id: int = 0

    @property
    def reload_required(self) -> bool:
        if self.active_candidate_id and self.active_revision:
            return (
                self.active_candidate_id != self.loaded.candidate_id
                or self.active_revision != self.loaded.active_revision
            )
        return self.status in {"reload-required", "reload-failed"}


@dataclass(frozen=True)
class ModelReloadOutcome:
    status: str
    model_status: PredictModelLifecycleStatus
    message: str
    reason_code: str = ""
    preserved_loaded_model: bool = False
    recommended_action: str = ""
    diagnostic: str = ""
    diagnostic_traceback: str = ""
    operation_id: int = 0
    applied_to_shared_state: bool = True


_RELOAD_GUIDANCE = {
    "prediction_running": (
        "현재 예측이 실행 중이라 새 모델을 불러올 수 없습니다.",
        "예측이 끝난 뒤 다시 시도하세요.",
    ),
    "missing_active": (
        "현재 사용할 Active 모델이 선택되지 않았습니다.",
        "Train에서 사용할 모델을 먼저 선택한 뒤 다시 시도하세요.",
    ),
    "stale_active_revision": (
        "모델을 준비하는 동안 Active 모델이 변경되었습니다.",
        "상태를 새로고침한 뒤 다시 시도하세요.",
    ),
    "recovery_required": (
        "모델 lifecycle 복구가 필요해 새 모델을 불러올 수 없습니다.",
        "복구가 완료된 뒤 다시 시도하세요.",
    ),
    "corrupt_active": (
        "현재 Active 모델을 안전하게 읽을 수 없습니다.",
        "Train에서 다른 정상 모델을 선택하거나 다시 학습하세요.",
    ),
    "incompatible_active": (
        "현재 Active 모델이 현재 정의와 호환되지 않습니다.",
        "현재 정의로 다시 학습하거나 호환되는 모델을 선택하세요.",
    ),
    "replacement_preparation_failed": (
        "새 모델의 실행 준비를 완료하지 못했습니다.",
        "진단 정보를 확인한 뒤 다시 시도하거나 다른 모델을 선택하세요.",
    ),
    "internal_failure": (
        "예상하지 못한 오류로 새 모델을 불러오지 못했습니다.",
        "진단 정보를 확인한 뒤 다시 시도하세요.",
    ),
}


def reload_failure_guidance(
    reason_code: str,
    *,
    loaded_model_exists: bool,
) -> tuple[str, str]:
    problem, action = _RELOAD_GUIDANCE[reason_code]
    preservation = (
        "기존에 로드된 모델은 그대로 유지됩니다."
        if loaded_model_exists
        else "사용 가능한 기존 모델이 없어 예측을 시작할 수 없습니다."
    )
    return f"{problem} {preservation} {action}", action


def observed_model_status(
    resolution,
    loaded: LoadedModelIdentity,
    *,
    operation_id: int = 0,
) -> PredictModelLifecycleStatus:  # noqa: ANN001
    if resolution.status != "resolved":
        status = "active-unavailable" if loaded.candidate_id else "startup-failed"
        message = (
            "Active 상태를 확인할 수 없지만 기존에 로드된 모델을 계속 사용합니다."
            if loaded.candidate_id
            else "사용할 수 있는 Active 모델이 없습니다."
        )
        reason_code = (
            "recovery_required"
            if resolution.status == "recovery-required"
            else "missing_active"
            if resolution.status == "missing-active"
            else "corrupt_active"
        )
        return PredictModelLifecycleStatus(
            status,
            loaded,
            message=message,
            diagnostic=resolution.message,
            diagnostic_traceback=resolution.diagnostic_traceback,
            reason_code=reason_code,
            operation_id=operation_id,
        )
    differs = (
        resolution.candidate_id != loaded.candidate_id
        or resolution.revision != loaded.active_revision
    )
    return PredictModelLifecycleStatus(
        "reload-required" if differs else "current",
        loaded,
        resolution.candidate_id,
        resolution.revision,
        (
            "새 Active 모델이 있습니다. 현재 모델을 계속 사용 중이며 다시 불러오기가 필요합니다."
            if differs
            else "현재 Active 모델을 사용 중입니다."
        ),
        operation_id=operation_id,
    )
