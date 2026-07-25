"""Qt-free Train model-management projection tests."""

from dataclasses import replace
from types import SimpleNamespace

from apps.common.model_lifecycle.errors import CandidateCorruptionError
from apps.common.model_lifecycle.promotion import (
    CandidateCompatibilityReview,
    ModelPromotionService,
    PromotionResult,
)
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.common.model_lifecycle.training_result_contracts import (
    TrainingAnalysisResult,
)
from apps.train.application.model_management import ModelManagementService
from tests.apps.common.model_lifecycle.conftest import (
    incompatible_snapshot,
    publish_candidate,
)
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.target_registry.runtime import model_registry_snapshot


def _analysis(
    *,
    baseline_type: str = "none",
    comparable: bool = False,
    unavailable_reason: str = "No active model.",
    metrics: tuple[object, object, object] = (0.8, 1.5, 2.0),
    delta: tuple[object, object, object] = (None, None, None),
) -> TrainingAnalysisResult:
    comparison = (
        {
            "comparable": True,
            "delta": {"r2": delta[0], "mae": delta[1], "rmse": delta[2]},
        }
        if comparable
        else {
            "comparable": False,
            "unavailable_reason": unavailable_reason,
        }
    )
    return TrainingAnalysisResult(
        run={"run_id": "run", "candidate_id": "candidate"},
        training_context={},
        targets=(
            {
                "target_identity": "dynamic-target",
                "target_ml_name": "Dynamic Target",
                "status": "complete",
                "metrics": {
                    "r2": metrics[0],
                    "mae": metrics[1],
                    "rmse": metrics[2],
                },
                "baseline_comparison": comparison,
                "rfecv": {
                    "status": "used",
                    "features": [{"feature": "f1", "selected": True}],
                },
                "feature_importance": [{"feature": "f1"}],
                "optuna": {"status": "used"},
            },
        ),
        baseline={
            "type": baseline_type,
            "identity": "active-a" if baseline_type != "none" else "",
            "comparable": comparable,
            "unavailable_reason": unavailable_reason if not comparable else "",
        },
        preprocessing={"status": "applied", "feature_data_quality": []},
        artifacts=(),
        promotion_eligibility={"eligible": True},
    )


def _candidate(
    candidate_id: str,
    created_at: str,
    *,
    eligible: bool = True,
):
    manifest = SimpleNamespace(
        candidate_id=candidate_id,
        run_id=f"run-{candidate_id}",
        created_at=created_at,
        promotion_eligible=eligible,
        blocking_reasons=() if eligible else ("required target failed",),
        targets=(),
    )
    result = SimpleNamespace(blocking_reasons=())
    return SimpleNamespace(manifest=manifest, result=result)


class FakeRepository:
    def __init__(self, candidates=(), active=None, analyses=None):  # noqa: ANN001
        self.candidates = tuple(candidates)
        self.active = active
        self.analyses = analyses or {}
        self.error = None

    def read_active(self, *, optional=False):  # noqa: ANN001
        if self.error:
            raise self.error
        return self.active

    def list_candidates(self):
        return self.candidates

    def read_training_analysis(self, candidate_id):
        return self.analyses[candidate_id]


class FakePromotion:
    def __init__(self, compatibility=None):  # noqa: ANN001
        self.calls = []
        self.compatibility = (
            compatibility or CandidateCompatibilityReview("compatible")
        )

    def inspect_compatibility(self, candidate_id):
        return self.compatibility

    def promote(self, candidate_id, *, expected_revision):
        self.calls.append((candidate_id, expected_revision))
        return PromotionResult("active", candidate_id, expected_revision + 1, "ok")


def test_empty_bootstrap_active_and_dynamic_target_projection():
    promotion = FakePromotion()
    empty = ModelManagementService(FakeRepository(), promotion).inspect()
    assert (empty.status, empty.active_candidate_id, empty.candidates) == (
        "empty", "", (),
    )

    candidates = (
        _candidate("older", "2026-07-24T00:00:00+00:00"),
        _candidate("newer", "2026-07-25T00:00:00+00:00"),
    )
    repository = FakeRepository(
        candidates,
        analyses={
            "older": _analysis(),
            "newer": _analysis(
                baseline_type="active_candidate",
                comparable=True,
                unavailable_reason="",
                delta=(0.1, -0.2, -0.3),
            ),
        },
    )
    bootstrap = ModelManagementService(repository, promotion).inspect()
    assert bootstrap.status == "bootstrap"
    assert [item.candidate_id for item in bootstrap.candidates] == [
        "newer", "older",
    ]
    target = bootstrap.candidates[0].targets[0]
    assert (target.identity, target.name, target.comparison) == (
        "dynamic-target", "Dynamic Target", "fair",
    )
    assert (target.delta_r2, target.delta_mae, target.delta_rmse) == (
        0.1, -0.2, -0.3,
    )

    repository.active = SimpleNamespace(candidate_id="older", revision=4)
    active = ModelManagementService(repository, promotion).inspect()
    assert active.status == "active"
    assert active.active_candidate_id == "older"
    assert next(
        item for item in active.candidates if item.candidate_id == "older"
    ).is_active


def test_unfair_no_baseline_and_unavailable_values_are_preserved():
    candidates = (
        _candidate("no-baseline", "2026-07-25T00:00:00+00:00"),
        _candidate("unfair", "2026-07-24T00:00:00+00:00"),
    )
    repository = FakeRepository(
        candidates,
        analyses={
            "no-baseline": _analysis(metrics=(None, None, None)),
            "unfair": _analysis(
                baseline_type="active_candidate",
                unavailable_reason="Evaluation context differs.",
            ),
        },
    )
    snapshot = ModelManagementService(repository, FakePromotion()).inspect()
    by_id = {item.candidate_id: item for item in snapshot.candidates}

    assert by_id["no-baseline"].baseline_kind == "no_baseline"
    assert by_id["no-baseline"].targets[0].r2 is None
    assert by_id["unfair"].baseline_kind == "unfair"
    assert (
        by_id["unfair"].targets[0].unavailable_reason
        == "Evaluation context differs."
    )
    assert by_id["no-baseline"].targets[0].comparison == "unavailable"


def test_target_comparison_never_promotes_global_fair_or_missing_delta():
    candidate = _candidate("candidate-a", "2026-07-25T00:00:00+00:00")
    target_unavailable = _analysis(
        baseline_type="active_candidate",
        comparable=True,
        unavailable_reason="",
        delta=(0.1, -0.2, -0.3),
    )
    target_unavailable.targets[0]["baseline_comparison"] = {
        "comparable": False,
        "unavailable_reason": "Baseline target is unavailable.",
    }
    repository = FakeRepository(
        (candidate,),
        analyses={"candidate-a": target_unavailable},
    )
    review = ModelManagementService(
        repository, FakePromotion()
    ).inspect().candidates[0].targets[0]
    assert review.comparison == "unavailable"
    assert review.unavailable_reason == "Baseline target is unavailable."

    missing_delta = _analysis(
        baseline_type="active_candidate",
        comparable=True,
        unavailable_reason="",
    )
    review = ModelManagementService(
        FakeRepository(
            (candidate,),
            analyses={"candidate-a": missing_delta},
        ),
        FakePromotion(),
    ).inspect().candidates[0].targets[0]
    assert review.comparison == "unavailable"
    assert review.unavailable_reason == "저장된 비교 수치를 사용할 수 없습니다."

    non_numeric = _analysis(
        baseline_type="active_candidate",
        comparable=True,
        unavailable_reason="",
        metrics=("not-a-number", 1.0, 2.0),
        delta=(0.1, -0.2, -0.3),
    )
    non_numeric.targets[0]["baseline_comparison"][
        "unavailable_reason"
    ] = "R² is not numeric."
    review = ModelManagementService(
        FakeRepository(
            (candidate,),
            analyses={"candidate-a": non_numeric},
        ),
        FakePromotion(),
    ).inspect().candidates[0].targets[0]
    assert review.comparison == "unavailable"
    assert review.unavailable_reason == "R² is not numeric."


def test_current_compatibility_controls_availability_and_final_race_guard(
    tmp_path,
):
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    registry_snapshot = model_registry_snapshot(bootstrap_manifest())
    publish_candidate(repository, registry_snapshot, "candidate-a")
    current = {"value": registry_snapshot}
    service = ModelManagementService(
        repository,
        ModelPromotionService(repository, lambda: current["value"]),
    )

    initial = service.inspect().candidates[0]
    assert initial.promotion_status == "compatible"
    assert initial.promotion_eligible is True

    current["value"] = incompatible_snapshot(
        registry_snapshot, "generation_id", "new-generation"
    )
    incompatible = service.inspect().candidates[0]
    assert incompatible.promotion_status == "incompatible"
    assert incompatible.promotion_eligible is False

    outcome = service.promote("candidate-a", expected_revision=0)
    assert outcome.status == "blocked"
    assert outcome.reason_code == "current_contract_incompatible"
    assert repository.read_active(optional=True) is None


def test_advanced_projection_preserves_all_stored_evidence():
    candidate = _candidate("candidate-a", "2026-07-25T00:00:00+00:00")
    analysis = _analysis()
    analysis.targets[0]["rfecv"] = {
        "status": "used",
        "feature_count_before": 3,
        "feature_count_after": 1,
        "score_context": "cv-r2",
        "features": (
            {
                "feature": "f1",
                "selected": True,
                "rank": 1,
                "evaluation_score": 0.91,
            },
            {
                "feature": "f2",
                "selected": False,
                "rank": 2,
                "evaluation_score": None,
            },
        ),
    }
    analysis.targets[0]["feature_importance"] = (
        {
            "feature": "f1",
            "method": "native",
            "raw_value": 0.75,
            "normalized_value": 1.0,
            "rank": 1,
        },
    )
    analysis.targets[0]["optuna"] = {
        "status": "used",
        "best_score": 0.88,
        "selected_parameters": {"max_depth": 0},
        "trials": (
            {"trial_number": 2, "status": "complete", "score": 0.88},
        ),
    }
    analysis = replace(
        analysis,
        preprocessing={
            "status": "applied",
            "steps": (
                {
                    "name": "impute",
                    "status": "applied",
                    "details": {"fill": 0},
                },
            ),
            "feature_data_quality": (
                {
                    "feature": "f1",
                    "missing_rate": 0.0,
                    "unique_count": 12,
                    "variance": 1.25,
                    "outlier_count": 2,
                    "unavailable_reason": None,
                },
            ),
        },
    )
    candidate_review = ModelManagementService(
        FakeRepository(
            (candidate,), analyses={"candidate-a": analysis}
        ),
        FakePromotion(),
    ).inspect().candidates[0]
    projected = "\n".join(
        f"{section.title}\n"
        + "\n".join(f"{name}={value}" for name, value in section.rows)
        for section in candidate_review.advanced_sections
    )

    for stored_value in (
        "feature_count_before=3",
        "feature_count_after=1",
        "score_context=cv-r2",
        "rank=1",
        "evaluation_score=0.91",
        "method=native",
        "raw_value=0.75",
        "normalized_value=1.0",
        "best_score=0.88",
        "max_depth=0",
        "Trial 2",
        "missing_rate=0.0",
        "unique_count=12",
        "variance=1.25",
        "outlier_count=2",
        "unavailable_reason=저장되지 않음",
    ):
        assert stored_value in projected


def test_legacy_analysis_and_corruption_fail_closed():
    candidate = _candidate("legacy", "2026-07-25T00:00:00+00:00")
    repository = FakeRepository(
        (candidate,),
        analyses={
            "legacy": {
                "status": "unavailable",
                "reason": "Candidate predates the training analysis contract.",
            }
        },
    )
    snapshot = ModelManagementService(repository, FakePromotion()).inspect()
    assert snapshot.candidates[0].analysis_status == "unavailable"
    assert "predates" in snapshot.candidates[0].analysis_reason

    repository.error = CandidateCorruptionError("candidate corrupt")
    corrupt = ModelManagementService(repository, FakePromotion()).inspect()
    assert corrupt.status == "corrupt"
    assert corrupt.candidates == ()

    repository.error = None
    repository.active = SimpleNamespace(candidate_id="missing", revision=1)
    missing_active = ModelManagementService(
        repository, FakePromotion()
    ).inspect()
    assert missing_active.status == "corrupt"
    assert "missing Candidate" in missing_active.message


def test_guarded_promotion_uses_revision_and_training_blocks_command():
    candidate = _candidate("candidate-a", "2026-07-25T00:00:00+00:00")
    repository = FakeRepository(
        (candidate,),
        active=SimpleNamespace(candidate_id="active-a", revision=7),
        analyses={"candidate-a": _analysis()},
    )
    class UpdatingPromotion(FakePromotion):
        def promote(self, candidate_id, *, expected_revision):
            result = super().promote(
                candidate_id,
                expected_revision=expected_revision,
            )
            repository.active = SimpleNamespace(
                candidate_id=candidate_id,
                revision=result.revision,
            )
            return result

    promotion = UpdatingPromotion()
    running = {"value": False}
    service = ModelManagementService(
        repository,
        promotion,
        training_running=lambda: running["value"],
    )

    outcome = service.promote("candidate-a", expected_revision=7)
    assert outcome.status == "active"
    assert promotion.calls == [("candidate-a", 7)]

    running["value"] = True
    blocked = service.promote("candidate-a", expected_revision=7)
    assert blocked.status == "blocked"
    assert promotion.calls == [("candidate-a", 7)]


def test_promotion_success_requires_confirming_reloaded_active():
    candidate = _candidate("candidate-a", "2026-07-25T00:00:00+00:00")
    repository = FakeRepository(
        (candidate,),
        analyses={"candidate-a": _analysis()},
    )

    class UnreadableAfterPromotion(FakePromotion):
        def promote(self, candidate_id, *, expected_revision):
            result = super().promote(
                candidate_id,
                expected_revision=expected_revision,
            )
            repository.error = CandidateCorruptionError("active unreadable")
            return result

    outcome = ModelManagementService(
        repository,
        UnreadableAfterPromotion(),
    ).promote("candidate-a", expected_revision=0)

    assert outcome.status == "recovery-required"
    assert outcome.snapshot.status == "corrupt"
    assert "다시 읽을 수 없습니다" in outcome.message


def test_real_lifecycle_stale_guard_and_rollback_by_repromotion(
    tmp_path,
):
    repository = ModelLifecycleRepository(tmp_path / "lifecycle")
    registry_snapshot = model_registry_snapshot(bootstrap_manifest())
    publish_candidate(repository, registry_snapshot, "candidate-a")
    publish_candidate(repository, registry_snapshot, "candidate-b")
    service = ModelManagementService(
        repository,
        ModelPromotionService(repository, lambda: registry_snapshot),
    )

    first = service.promote("candidate-a", expected_revision=0)
    stale = service.promote("candidate-b", expected_revision=0)
    second = service.promote("candidate-b", expected_revision=1)
    rollback = service.promote("candidate-a", expected_revision=2)

    assert (first.status, first.snapshot.active_candidate_id) == (
        "active", "candidate-a",
    )
    assert (stale.status, stale.snapshot.active_candidate_id) == (
        "blocked", "candidate-a",
    )
    assert (second.status, second.snapshot.active_candidate_id) == (
        "active", "candidate-b",
    )
    assert (rollback.status, rollback.snapshot.active_candidate_id) == (
        "active", "candidate-a",
    )
    active = repository.read_active()
    assert active.revision == 3
    assert [item.candidate_id for item in active.history] == [
        "candidate-a", "candidate-b", "candidate-a",
    ]
