"""Korean formatting for persisted model-management projections."""

from __future__ import annotations

from apps.train.application.model_management import PromotionOutcome


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


def promotion_failure_message(outcome: PromotionOutcome) -> str:
    if "stale Active reference revision" in outcome.message:
        return "다른 작업에서 현재 사용 모델이 변경되었습니다. 새로고침 후 다시 확인하세요."
    if outcome.status == "recovery-required":
        return "모델 상태 복구가 필요합니다. 기존 진단 절차를 확인하세요."
    return f"모델을 변경하지 못했습니다. {outcome.message}"
