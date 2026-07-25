"""Korean formatting for persisted model-management projections."""

from __future__ import annotations

from apps.train.application.model_management import CandidateReview, PromotionOutcome


def display_value(value: object) -> str:
    if value is None or value == "":
        return "값 없음"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def comparison_value(target) -> str:  # noqa: ANN001
    if target.comparison == "fair":
        return (
            f"ΔR² {display_value(target.delta_r2)} / "
            f"ΔMAE {display_value(target.delta_mae)} / "
            f"ΔRMSE {display_value(target.delta_rmse)}"
        )
    if target.comparison == "no_baseline":
        return "비교 기준 없음"
    return "비교 불가"


def candidate_status_text(candidate: CandidateReview) -> str:
    return {
        "active": "사용 중",
        "compatible": "사용 가능",
        "incompatible": "현재 환경과 맞지 않음",
        "non-promotable": "학습 결과 사용 불가",
        "corrupt": "학습 결과 손상",
        "recovery-required": "상태 복구 필요",
    }.get(candidate.promotion_status, "상태 확인 필요")


def candidate_availability_message(candidate: CandidateReview) -> str:
    if candidate.is_active or candidate.promotion_status == "active":
        return "현재 사용 중인 모델입니다."
    return {
        "incompatible": (
            "현재 모델 정의와 맞지 않아 사용할 수 없습니다. "
            "현재 정의로 다시 학습하거나, 현재 정의와 맞는 학습 결과를 선택하세요."
        ),
        "non-promotable": (
            "학습 결과가 사용 조건을 충족하지 못했습니다. "
            "학습 결과의 차단 사유를 확인한 뒤 다시 학습하세요."
        ),
        "corrupt": (
            "학습 결과를 안전하게 읽을 수 없어 사용할 수 없습니다. "
            "진단 로그를 확인하고 정상인 다른 학습 결과를 선택하세요."
        ),
        "recovery-required": (
            "모델 상태 복구가 필요해 변경할 수 없습니다. "
            "기존 복구 절차를 완료한 뒤 새로고침하세요."
        ),
    }.get(
        candidate.promotion_status,
        "현재 상태를 확인할 수 없어 사용할 수 없습니다. 진단 로그를 확인하세요.",
    )


def promotion_blocked_message(reason_code: str) -> str:
    return {
        "current_contract_incompatible": (
            "현재 모델 정의와 맞지 않아 변경하지 못했습니다. 기존 사용 모델은 "
            "유지됩니다. 현재 정의로 다시 학습하거나 맞는 학습 결과를 선택하세요."
        ),
        "candidate_corrupt": (
            "선택한 학습 결과를 안전하게 읽을 수 없어 변경하지 못했습니다. "
            "기존 사용 모델은 유지됩니다. 진단 로그를 확인하고 정상인 결과를 선택하세요."
        ),
        "training_result_not_promotable": (
            "선택한 학습 결과가 사용 조건을 충족하지 못했습니다. 기존 사용 모델은 "
            "유지됩니다. 학습 차단 사유를 확인한 뒤 다시 학습하세요."
        ),
        "stale_active_revision": (
            "다른 작업에서 현재 사용 모델이 변경되었습니다. 새로 확인된 사용 모델은 "
            "그대로 유지됩니다. 새로고침 후 다시 확인하세요."
        ),
        "recovery_required": (
            "모델 상태 복구가 필요해 변경을 완료할 수 없습니다. 안전하게 확인된 "
            "사용 모델 상태는 유지됩니다. 기존 복구 절차를 완료한 뒤 새로고침하세요."
        ),
        "training_running": (
            "학습 실행 중이라 모델을 변경하지 않았습니다. 기존 사용 모델은 "
            "유지됩니다. 학습이 끝난 뒤 다시 시도하세요."
        ),
    }.get(
        reason_code,
        "모델을 안전하게 변경하지 못했습니다. 기존 사용 모델은 유지됩니다. "
        "진단 로그를 확인한 뒤 새로고침하세요.",
    )


def promotion_failure_message(outcome: PromotionOutcome) -> str:
    return promotion_blocked_message(outcome.reason_code)
