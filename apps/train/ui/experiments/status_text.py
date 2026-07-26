"""User-facing external Campaign status projection."""


def campaign_status_text(status: str) -> str:
    return {
        "created": "시작 준비",
        "running": "실행 중",
        "paused": "일시 중지",
        "cancelled_resumable": "취소됨 · 재개 가능",
        "failed_resumable": "실패 · 재개 가능",
        "lock_conflict": "다른 학습 실행 중",
        "blocked": "재개 차단",
        "completed": "완료",
        "paused_budget_exhausted": "예산 소진",
    }.get(status, "상태 확인 필요")
