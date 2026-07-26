"""Model Management Qt projection and explicit action tests."""

import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from apps.common.model_lifecycle.promotion import (  # noqa: E402
    ModelPromotionService,
)
from apps.common.model_lifecycle.repository import (  # noqa: E402
    ModelLifecycleRepository,
)
from apps.train.application.model_management import (  # noqa: E402
    AdvancedSection,
    CandidateReview,
    ModelManagementService,
    ModelManagementSnapshot,
    PromotionOutcome,
    TargetMetricReview,
)
from apps.train.ui.model_management_panel import ModelManagementPanel  # noqa: E402
from apps.train.ui.model_management_text import (  # noqa: E402
    promotion_failure_message,
)
from core.data_definition.contract import bootstrap_manifest  # noqa: E402
from core.data_definition.target_registry.runtime import (  # noqa: E402
    model_registry_snapshot,
)
from tests.apps.common.model_lifecycle.conftest import (  # noqa: E402
    publish_candidate,
)


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def _candidate(
    candidate_id: str,
    *,
    active: bool = False,
    eligible: bool = True,
    comparison: str = "fair",
    promotion_status: str | None = None,
) -> CandidateReview:
    return CandidateReview(
        candidate_id=candidate_id,
        run_id=f"run-{candidate_id}",
        created_at="2026-07-25T00:00:00+00:00",
        is_active=active,
        promotion_eligible=eligible,
        blocking_reasons=() if eligible else ("required target failed",),
        targets=(
            TargetMetricReview(
                "dynamic",
                "Dynamic Target",
                "complete",
                r2=None,
                mae=1.2,
                rmse=2.3,
                comparison=comparison,
                delta_r2=None,
                unavailable_reason=(
                    "Evaluation context differs."
                    if comparison == "unfair" else ""
                ),
            ),
        ),
        baseline_kind=comparison,
        promotion_status=(
            promotion_status
            or ("active" if active else (
                "compatible" if eligible else "non-promotable"
            ))
        ),
        advanced_sections=(
            AdvancedSection("상세", (("RFECV", "used"),)),
        ),
    )


class FakeController:
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.calls = []
        self.export_calls = []

    def inspect_models(self):
        return self.snapshot

    def promote_candidate(self, candidate_id, *, expected_revision):
        self.calls.append((candidate_id, expected_revision))
        promoted = tuple(
            CandidateReview(
                **{
                    **item.__dict__,
                    "is_active": item.candidate_id == candidate_id,
                }
            )
            for item in self.snapshot.candidates
        )
        self.snapshot = ModelManagementSnapshot(
            "active",
            candidate_id,
            expected_revision + 1,
            promoted,
            "changed",
        )
        return PromotionOutcome(
            "active",
            candidate_id,
            expected_revision + 1,
            "ok",
            self.snapshot,
        )

    def export_active_model(self, destination, *, expected_revision):
        self.export_calls.append((destination, expected_revision))
        return SimpleNamespace(
            status="exported",
            message="exported",
            path=f"{destination}/export-id",
            diagnostic="",
        )


def test_active_export_action_forwards_destination_and_observed_revision(
    monkeypatch,
):
    _app()
    controller = FakeController(ModelManagementSnapshot(
        "active",
        "candidate-a",
        7,
        (_candidate("candidate-a", active=True),),
        "active",
    ))
    notifications = []
    panel = ModelManagementPanel(
        controller,
        notify=lambda title, message, success: notifications.append(
            (title, message, success)
        ),
    )
    monkeypatch.setattr(
        "apps.train.ui.model_management_panel.QFileDialog.getExistingDirectory",
        lambda *_args: "/tmp/exports",
    )

    panel.export_button.click()

    assert controller.export_calls == [("/tmp/exports", 7)]
    assert notifications == [
        ("Deployment export", "exported\n/tmp/exports/export-id", True)
    ]


def test_export_failure_ui_hides_diagnostics_and_retains_structured_outcome(
    monkeypatch,
):
    _app()
    controller = FakeController(ModelManagementSnapshot(
        "active",
        "candidate-a",
        7,
        (_candidate("candidate-a", active=True),),
        "active",
    ))
    failure = SimpleNamespace(
        status="failed",
        message=(
            "같은 export가 이미 있습니다. 기존 Active 모델은 유지됩니다. "
            "다른 위치를 선택하세요."
        ),
        path="",
        reason_code="destination_conflict",
        diagnostic="FileExistsError: secret /tmp/export candidate-a",
        diagnostic_traceback="secret traceback",
    )
    controller.export_active_model = lambda *_args, **_kwargs: failure
    notifications = []
    panel = ModelManagementPanel(
        controller,
        notify=lambda title, message, success: notifications.append(
            (title, message, success)
        ),
    )
    monkeypatch.setattr(
        "apps.train.ui.model_management_panel.QFileDialog.getExistingDirectory",
        lambda *_args: "/tmp/exports",
    )

    panel.export_button.click()

    assert notifications == [
        ("Deployment export", failure.message, False)
    ]
    assert "secret" not in notifications[0][1]
    assert panel.model_export_diagnostics is failure


def test_unexpected_export_ui_exception_is_contained_and_redacted(monkeypatch):
    _app()
    controller = FakeController(ModelManagementSnapshot(
        "active",
        "candidate-a",
        7,
        (_candidate("candidate-a", active=True),),
        "active",
    ))
    controller.export_active_model = lambda *_args, **_kwargs: (
        (_ for _ in ()).throw(
            RuntimeError("secret /tmp/export candidate-a fingerprint-value")
        )
    )
    notifications = []
    panel = ModelManagementPanel(
        controller,
        notify=lambda title, message, success: notifications.append(
            (title, message, success)
        ),
    )
    monkeypatch.setattr(
        "apps.train.ui.model_management_panel.QFileDialog.getExistingDirectory",
        lambda *_args: "/tmp/exports",
    )

    panel.export_button.click()

    assert len(notifications) == 1
    title, message, success = notifications[0]
    assert title == "Deployment export"
    assert not success
    assert "예상하지 못한 오류" in message
    assert "기존 Active 모델" in message
    assert "이미 생성된 export" in message
    assert "대상 위치와 진단 정보" in message
    assert "secret" not in message
    assert "/tmp" not in message
    assert "RuntimeError" not in message
    assert "secret /tmp/export" in panel.model_export_diagnostics.diagnostic
    assert "RuntimeError" in (
        panel.model_export_diagnostics.diagnostic_traceback
    )


def test_empty_corrupt_and_candidate_metric_states_are_explicit():
    _app()
    controller = FakeController(ModelManagementSnapshot(
        "empty", message="현재 사용 모델과 학습 결과가 없습니다."
    ))
    panel = ModelManagementPanel(controller)
    assert panel.active_label.text().endswith("선택되지 않음")
    assert "없습니다" in panel.state_label.text()
    assert panel.candidate_table.model().rowCount() == 0

    controller.snapshot = ModelManagementSnapshot(
        "corrupt", message="invalid active reference"
    )
    panel.refresh()
    assert "안전하게 읽을 수 없습니다" in panel.state_label.text()

    controller.snapshot = ModelManagementSnapshot(
        "bootstrap",
        candidates=(
            _candidate("candidate-a", comparison="no_baseline"),
            _candidate("candidate-b", eligible=False, comparison="unfair"),
        ),
        message="아직 사용 모델을 선택하지 않았습니다.",
    )
    panel.refresh()
    metrics = panel.metrics_table.model()
    assert metrics.data(metrics.index(0, 1)) == "값 없음"
    assert metrics.data(metrics.index(0, 4)) == "비교 기준 없음"
    assert panel.advanced_text.isHidden()
    panel.advanced_button.click()
    assert not panel.advanced_text.isHidden()

    panel.candidate_table.selectRow(1)
    assert panel.promote_button.isHidden()
    assert "사용 조건" in panel.promotion_message.text()


def test_populated_empty_error_and_populated_transition_has_safe_stale_headers():
    _app()
    controller = FakeController(ModelManagementSnapshot(
        "bootstrap",
        candidates=(_candidate("candidate-a"),),
        message="아직 사용 모델을 선택하지 않았습니다.",
    ))
    panel = ModelManagementPanel(controller)
    old_candidates = panel.candidate_table.model()
    old_metrics = panel.metrics_table.model()

    controller.snapshot = ModelManagementSnapshot(
        "corrupt", message="fingerprint internal-detail"
    )
    panel.refresh()
    assert panel.candidate_table.model().rowCount() == 0
    assert panel.metrics_table.model().columnCount() == 0
    assert panel.candidate_table.model().headerData(0, 1) is None
    assert panel.metrics_table.model().headerData(5, 1) is None
    assert old_candidates.headerData(99, 1) is None
    assert old_metrics.headerData(99, 1) is None
    assert "fingerprint internal-detail" not in panel.state_label.text()

    controller.snapshot = ModelManagementSnapshot(
        "bootstrap",
        candidates=(_candidate("candidate-b"),),
        message="다시 읽었습니다.",
    )
    panel.refresh()
    assert panel.candidate_table.model().rowCount() == 1
    assert panel.metrics_table.model().rowCount() == 1


def test_incompatible_candidate_is_not_available_and_has_safe_guidance():
    _app()
    controller = FakeController(ModelManagementSnapshot(
        "bootstrap",
        candidates=(_candidate(
            "candidate-a",
            promotion_status="incompatible",
        ),),
    ))
    panel = ModelManagementPanel(controller)

    assert panel.candidate_table.model().data(
        panel.candidate_table.model().index(0, 3)
    ) == "현재 환경과 맞지 않음"
    assert panel.promote_button.isHidden()
    assert "다시 학습" in panel.promotion_message.text()


def test_structured_promotion_failures_hide_internal_diagnostics():
    snapshot = ModelManagementSnapshot("active", active_candidate_id="active-a")
    cases = {
        "current_contract_incompatible": "현재 모델 정의",
        "candidate_corrupt": "안전하게 읽을 수 없어",
        "training_result_not_promotable": "사용 조건",
        "stale_active_revision": "새로고침",
        "recovery_required": "복구",
        "training_running": "학습이 끝난 뒤",
    }
    for reason_code, expected in cases.items():
        outcome = PromotionOutcome(
            "blocked",
            "internal-candidate-id",
            3,
            "registry_fingerprint stack internal-candidate-id",
            snapshot,
            reason_code=reason_code,
            diagnostic_message="raw diagnostics",
        )
        message = promotion_failure_message(outcome)
        assert expected in message
        assert "유지" in message
        assert "registry_fingerprint" not in message
        assert "internal-candidate-id" not in message


def test_promotion_rollback_then_candidate_corruption_refresh_is_fail_closed(
    tmp_path,
):
    _app()
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    registry = model_registry_snapshot(bootstrap_manifest())
    first = publish_candidate(repository, registry, "candidate-a")
    second = publish_candidate(repository, registry, "candidate-b")
    service = ModelManagementService(
        repository,
        ModelPromotionService(repository, lambda: registry),
    )

    class Controller:
        def inspect_models(self):
            return service.inspect()

        def promote_candidate(self, candidate_id, *, expected_revision):
            return service.promote(
                candidate_id, expected_revision=expected_revision
            )

    assert service.promote("candidate-a", expected_revision=0).status == "active"
    assert service.promote("candidate-b", expected_revision=1).status == "active"
    assert service.promote("candidate-a", expected_revision=2).status == "active"
    panel = ModelManagementPanel(Controller())
    assert panel.candidate_table.model().rowCount() == 2

    (second.path / "manifest.json").write_text("{", encoding="utf-8")
    panel.refresh()

    assert panel.candidate_table.model().rowCount() == 0
    assert panel.metrics_table.model().columnCount() == 0
    assert "안전하게 읽을 수 없습니다" in panel.state_label.text()
    active = repository.read_active()
    assert (active.candidate_id, active.revision) == ("candidate-a", 3)
    assert first.path.exists()


def test_promotion_confirmation_uses_selected_and_current_revision():
    _app()
    confirmations = []
    notifications = []
    controller = FakeController(ModelManagementSnapshot(
        "active",
        active_candidate_id="active-a",
        active_revision=3,
        candidates=(
            _candidate("candidate-new"),
            _candidate("active-a", active=True),
        ),
    ))
    panel = ModelManagementPanel(
        controller,
        confirm=lambda selected, active: (
            confirmations.append((selected, active)) or True
        ),
        notify=lambda title, message, success: notifications.append(
            (title, message, success)
        ),
    )

    assert not panel.promote_button.isHidden()
    panel.set_training_running(True)
    assert not panel.promote_button.isEnabled()
    assert panel.promotion_message.text() == (
        "학습 실행 중이라 모델을 변경하지 않았습니다. 기존 사용 모델은 "
        "유지됩니다. 학습이 끝난 뒤 다시 시도하세요."
    )
    assert controller.calls == []
    panel.set_training_running(False)
    panel.promote_button.click()

    assert confirmations == [("candidate-new", "active-a")]
    assert controller.calls == [("candidate-new", 3)]
    assert panel.active_label.text().endswith("candidate-new")
    assert panel.promote_button.isHidden()
    assert notifications[-1][2] is True


def test_model_management_surface_remains_usable_at_compact_size():
    _app()
    controller = FakeController(ModelManagementSnapshot(
        "bootstrap",
        candidates=(_candidate("candidate-a"),),
        message="아직 사용 모델을 선택하지 않았습니다.",
    ))
    panel = ModelManagementPanel(controller)
    panel.resize(820, 560)
    panel.show()
    QApplication.processEvents()

    assert panel.candidate_table.viewport().height() > 0
    assert panel.metrics_table.viewport().height() > 0
    assert not panel.promote_button.isHidden()
    assert panel.refresh_button.isEnabled()
