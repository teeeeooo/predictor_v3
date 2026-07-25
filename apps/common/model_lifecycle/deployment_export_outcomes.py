"""Structured deployment-export failure contracts and user guidance."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeploymentExportResult:
    status: str
    export_id: str = ""
    path: str = ""
    candidate_id: str = ""
    active_revision: int = 0
    message: str = ""
    reason_code: str = ""
    preserved_active: bool = True
    recommended_action: str = ""
    diagnostic: str = ""
    diagnostic_traceback: str = ""


_EXPORT_GUIDANCE = {
    "training_running": (
        "학습이 실행 중이라 deployment export를 생성할 수 없습니다.",
        "학습이 끝난 뒤 모델 상태를 확인하고 다시 시도하세요.",
    ),
    "missing_active": (
        "현재 사용할 Active 모델이 선택되지 않아 export할 수 없습니다.",
        "Train에서 사용할 모델을 먼저 선택한 뒤 다시 시도하세요.",
    ),
    "stale_active_revision": (
        "확인한 뒤 Active 모델이 변경되어 export를 중단했습니다.",
        "모델 상태를 새로고침한 뒤 다시 시도하세요.",
    ),
    "recovery_required": (
        "모델 lifecycle 복구가 필요해 export할 수 없습니다.",
        "복구가 완료된 뒤 다시 시도하세요.",
    ),
    "incompatible_active": (
        "현재 Active 모델이 현재 정의와 호환되지 않습니다.",
        "현재 정의로 다시 학습하거나 호환되는 모델을 선택하세요.",
    ),
    "corrupt_active": (
        "현재 Active 모델을 안전하게 읽을 수 없습니다.",
        "다른 정상 모델을 선택하거나 다시 학습하세요.",
    ),
    "partial_non_promotable_active": (
        "현재 Active 모델은 production export 요건을 모두 충족하지 않습니다.",
        "모든 필수 Target이 완료된 호환 모델을 선택하세요.",
    ),
    "destination_conflict": (
        "같은 export identity가 대상 위치에 이미 존재합니다.",
        "다른 export 위치를 선택하거나 새 Active revision에서 다시 시도하세요.",
    ),
    "publication_filesystem_failure": (
        "대상 위치에 export를 안전하게 게시하지 못했습니다.",
        "대상 위치와 쓰기 가능 상태를 확인한 뒤 다시 시도하세요.",
    ),
    "internal_failure": (
        "예상하지 못한 오류로 export를 완료하지 못했습니다.",
        "진단 정보를 확인한 뒤 다시 시도하세요.",
    ),
}


def deployment_export_failure(
    reason_code: str,
    *,
    diagnostic: str,
    diagnostic_traceback: str = "",
) -> DeploymentExportResult:
    problem, action = _EXPORT_GUIDANCE[reason_code]
    return DeploymentExportResult(
        "failed",
        message=(
            f"{problem} 기존 Active 모델과 Candidate는 변경되지 않았습니다. {action}"
        ),
        reason_code=reason_code,
        preserved_active=True,
        recommended_action=action,
        diagnostic=diagnostic,
        diagnostic_traceback=diagnostic_traceback,
    )
