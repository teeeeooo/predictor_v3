from apps.train.ui.experiments.status_text import campaign_status_text


def test_external_campaign_status_is_user_facing_not_raw_contract_text():
    assert campaign_status_text("running") == "실행 중"
    assert campaign_status_text("cancelled_resumable") == "취소됨 · 재개 가능"
    assert campaign_status_text("future-status") == "상태 확인 필요"
