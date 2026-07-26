from apps.train.ui.experiments.status_text import (
    campaign_status_text,
    campaign_summary_text,
)


def test_external_campaign_status_is_user_facing_not_raw_contract_text():
    assert campaign_status_text("running") == "실행 중"
    assert campaign_status_text("cancelled_resumable") == "취소됨 · 재개 가능"
    assert campaign_status_text("future-status") == "상태 확인 필요"


def test_agent_campaign_summary_is_read_only_and_shows_shared_store_state():
    summary = campaign_summary_text({
        "status": "proposal_rejected",
        "budget": {
            "max_iterations": 5,
            "consumed_iterations": 1,
            "remaining_iterations": 4,
        },
        "incumbent_candidate_id": "candidate-a",
        "recommendation_status": "recommendation_ready",
        "approval_required": True,
        "failure": {"code": "proposal_delta_forbidden"},
    })

    assert "제안 거절" in summary
    assert "예산 1/5 · 남음 4" in summary
    assert "candidate-a" in summary
    assert "추천 검토 준비" in summary
    assert "사용자 승인 필요" in summary
    assert "허용되지 않은 변경" in summary
    assert "proposal_delta_forbidden" not in summary
