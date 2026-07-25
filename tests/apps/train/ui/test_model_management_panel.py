"""Model Management Qt projection and explicit action tests."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from apps.train.application.model_management import (  # noqa: E402
    AdvancedSection,
    CandidateReview,
    ModelManagementSnapshot,
    PromotionOutcome,
    TargetMetricReview,
)
from apps.train.ui.model_management_panel import ModelManagementPanel  # noqa: E402


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def _candidate(
    candidate_id: str,
    *,
    active: bool = False,
    eligible: bool = True,
    comparison: str = "fair",
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
        advanced_sections=(
            AdvancedSection("상세", (("RFECV", "used"),)),
        ),
    )


class FakeController:
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.calls = []

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
    assert "적용할 수 없습니다" in panel.promotion_message.text()


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
