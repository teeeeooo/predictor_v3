"""User-facing external Campaign status projection."""


def campaign_status_text(status: str) -> str:
    return {
        "created": "시작 준비",
        "awaiting_proposal": "다음 제안 대기",
        "proposal_rejected": "제안 거절",
        "ready_to_execute": "실행 준비",
        "running": "실행 중",
        "paused": "일시 중지",
        "budget_exhausted": "예산 소진",
        "no_valid_candidate": "유효 후보 없음",
        "recommendation_ready": "추천 검토 준비",
        "completed_without_recommendation": "추천 없이 완료",
        "cancelled_resumable": "취소됨 · 재개 가능",
        "failed_resumable": "실패 · 재개 가능",
        "lock_conflict": "다른 학습 실행 중",
        "blocked": "재개 차단",
        "completed": "완료",
        "paused_budget_exhausted": "예산 소진",
    }.get(status, "상태 확인 필요")


def campaign_summary_text(campaign: dict) -> str:
    parts = [f"외부 Campaign: {campaign_status_text(campaign.get('status', ''))}"]
    budget = campaign.get("budget", {})
    maximum = budget.get("max_iterations", budget.get("configured_iterations"))
    consumed = budget.get("consumed_iterations")
    remaining = budget.get("remaining_iterations")
    if maximum is not None and consumed is not None:
        text = f"예산 {consumed}/{maximum}"
        if remaining is not None:
            text += f" · 남음 {remaining}"
        parts.append(text)
    incumbent = campaign.get("incumbent_candidate_id")
    parts.append(f"내부 최우수 후보 {incumbent or '없음'}")
    recommendation = campaign.get("recommendation_status")
    if recommendation:
        parts.append(
            "추천 검토 준비" if recommendation == "recommendation_ready"
            else "추천 미생성"
        )
    if campaign.get("approval_required"):
        parts.append("사용자 승인 필요")
    failure = campaign.get("failure") or {}
    reason = failure.get("code")
    if reason:
        parts.append(f"차단 사유 {campaign_reason_text(reason)}")
    return " · ".join(parts)


def campaign_reason_text(code: str) -> str:
    return {
        "proposal_delta_forbidden": "허용되지 않은 변경",
        "proposal_category_forbidden": "허용되지 않은 실험 범주",
        "proposal_baseline_stale": "기준 후보가 변경됨",
        "campaign_budget_exhausted": "실험 예산 소진",
        "execution_lock_conflict": "다른 학습 실행 중",
        "training_preflight_failed": "학습 사전 점검 실패",
        "training_start_failed": "학습 시작 전 실패",
        "resume_contract_changed": "실행 계약 변경",
    }.get(code, "상세 진단 확인 필요")
