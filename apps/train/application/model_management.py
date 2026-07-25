"""Qt-free Active/Candidate review and explicit promotion boundary."""

from __future__ import annotations

from typing import Any, Callable

from apps.common.model_lifecycle.errors import ModelLifecycleError
from apps.common.model_lifecycle.promotion import ModelPromotionService
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.common.model_lifecycle.training_result_contracts import (
    TrainingAnalysisResult,
)
from .model_management_models import (
    AdvancedSection,
    CandidateReview,
    TargetMetricReview,
)
from .model_management_state import (
    ModelManagementSnapshot,
    PromotionOutcome,
)


class ModelManagementService:
    """Project persisted lifecycle/result contracts for Train UI consumers."""

    def __init__(
        self,
        repository: ModelLifecycleRepository,
        promotion: ModelPromotionService,
        *,
        training_running: Callable[[], bool] | None = None,
    ) -> None:
        self._repository = repository
        self._promotion = promotion
        self._training_running = training_running or (lambda: False)

    def inspect(self) -> ModelManagementSnapshot:
        try:
            active = self._repository.read_active(optional=True)
            candidates = tuple(
                self._review(item, active.candidate_id if active else "")
                for item in sorted(
                    self._repository.list_candidates(),
                    key=lambda item: (
                        item.manifest.created_at,
                        item.manifest.candidate_id,
                    ),
                    reverse=True,
                )
            )
            if active is not None and all(
                item.candidate_id != active.candidate_id
                for item in candidates
            ):
                raise ModelLifecycleError(
                    "Active reference points to a missing Candidate."
                )
        except (ModelLifecycleError, FileNotFoundError, OSError) as exc:
            return ModelManagementSnapshot(
                status="corrupt",
                message=str(exc).splitlines()[0],
            )
        if active is None and not candidates:
            status = "empty"
            message = "현재 사용 모델과 학습 결과가 없습니다."
        elif active is None:
            status = "bootstrap"
            message = "아직 사용 모델을 선택하지 않았습니다."
        else:
            status = "active"
            message = "현재 사용 모델을 확인하고 학습 결과를 비교하세요."
        return ModelManagementSnapshot(
            status=status,
            active_candidate_id=active.candidate_id if active else "",
            active_revision=active.revision if active else 0,
            candidates=candidates,
            message=message,
        )

    def promote(
        self,
        candidate_id: str,
        *,
        expected_revision: int,
    ) -> PromotionOutcome:
        if self._training_running():
            snapshot = self.inspect()
            return PromotionOutcome(
                "blocked",
                candidate_id,
                snapshot.active_revision,
                "학습 실행 중에는 사용 모델을 변경할 수 없습니다.",
                snapshot,
            )
        result = self._promotion.promote(
            candidate_id,
            expected_revision=expected_revision,
        )
        snapshot = self.inspect()
        if result.status == "active" and (
            snapshot.status != "active"
            or snapshot.active_candidate_id != candidate_id
        ):
            return PromotionOutcome(
                "recovery-required",
                candidate_id,
                snapshot.active_revision,
                "모델 변경 후 Active 상태를 안전하게 다시 읽을 수 없습니다.",
                snapshot,
            )
        return PromotionOutcome(
            result.status,
            result.candidate_id,
            result.revision,
            result.message,
            snapshot,
        )

    def _review(self, snapshot, active_candidate_id: str) -> CandidateReview:  # noqa: ANN001
        manifest = snapshot.manifest
        analysis = self._repository.read_training_analysis(
            manifest.candidate_id
        )
        analysis_reasons = (
            tuple(
                item.get("reason", "")
                for item in analysis.blocking_reasons
            )
            if isinstance(analysis, TrainingAnalysisResult)
            else ()
        )
        reasons = tuple(
            dict.fromkeys(
                (
                    *manifest.blocking_reasons,
                    *snapshot.result.blocking_reasons,
                    *analysis_reasons,
                )
            )
        )
        if not isinstance(analysis, TrainingAnalysisResult):
            return CandidateReview(
                candidate_id=manifest.candidate_id,
                run_id=manifest.run_id,
                created_at=manifest.created_at,
                is_active=manifest.candidate_id == active_candidate_id,
                promotion_eligible=manifest.promotion_eligible,
                blocking_reasons=tuple(reason for reason in reasons if reason),
                targets=tuple(
                    TargetMetricReview(item.identity, item.ml_name, "unavailable")
                    for item in manifest.targets
                ),
                baseline_kind="unavailable",
                analysis_status="unavailable",
                analysis_reason=analysis["reason"],
            )
        return CandidateReview(
            candidate_id=manifest.candidate_id,
            run_id=manifest.run_id,
            created_at=manifest.created_at,
            is_active=manifest.candidate_id == active_candidate_id,
            promotion_eligible=manifest.promotion_eligible,
            blocking_reasons=tuple(reason for reason in reasons if reason),
            targets=tuple(
                _target_review(item, analysis.baseline)
                for item in analysis.targets
            ),
            baseline_kind=_baseline_kind(analysis.baseline),
            baseline_identity=str(analysis.baseline.get("identity", "")),
            baseline_reason=str(
                analysis.baseline.get("unavailable_reason", "")
            ),
            advanced_sections=_advanced_sections(analysis),
        )


def _target_review(
    target: dict[str, Any],
    baseline: dict[str, Any],
) -> TargetMetricReview:
    metrics = target.get("metrics", {})
    comparison = target.get("baseline_comparison", {})
    delta = comparison.get("delta", {})
    reason = str(
        comparison.get("unavailable_reason")
        or baseline.get("unavailable_reason")
        or ""
    )
    return TargetMetricReview(
        identity=str(target.get("target_identity", "")),
        name=str(target.get("target_ml_name", "")),
        status=str(target.get("status", "")),
        r2=metrics.get("r2"),
        mae=metrics.get("mae"),
        rmse=metrics.get("rmse"),
        comparison=(
            "fair"
            if comparison.get("comparable") is True
            else _baseline_kind(baseline)
        ),
        delta_r2=delta.get("r2"),
        delta_mae=delta.get("mae"),
        delta_rmse=delta.get("rmse"),
        unavailable_reason=reason,
        blocking_reason=str(
            target.get("blocking_reason")
            or target.get("failure_reason")
            or ""
        ),
    )


def _baseline_kind(baseline: dict[str, Any]) -> str:
    if baseline.get("comparable") is True:
        return "fair"
    if baseline.get("type") == "none":
        return "no_baseline"
    if baseline.get("type") == "active_candidate":
        return "unfair"
    return "unavailable"


def _advanced_sections(
    result: TrainingAnalysisResult,
) -> tuple[AdvancedSection, ...]:
    rows: list[tuple[str, str]] = []
    for target in result.targets:
        target_name = str(target.get("target_ml_name", ""))
        rfecv = target.get("rfecv", {})
        rfecv_status = str(rfecv.get("status", "unavailable"))
        selected = [
            str(item.get("feature", ""))
            for item in rfecv.get("features", ())
            if item.get("selected")
        ]
        selected_text = (
            rfecv_status
            if rfecv_status in {"unavailable", "failed"}
            else ", ".join(selected) or "저장된 항목 없음"
        )
        rows.extend((
            (f"{target_name} · RFECV", rfecv_status),
            (f"{target_name} · 선택 특성", selected_text),
            (
                f"{target_name} · Feature importance",
                ", ".join(
                    str(item.get("feature", ""))
                    for item in target.get("feature_importance", ())
                ) or "저장된 항목 없음",
            ),
            (
                f"{target_name} · Optuna",
                str(target.get("optuna", {}).get("status", "unavailable")),
            ),
        ))
    rows.extend((
        ("전처리 상태", str(result.preprocessing.get("status", "unavailable"))),
        (
            "데이터 품질",
            ", ".join(
                str(item.get("feature", ""))
                for item in result.preprocessing.get(
                    "feature_data_quality", ()
                )
            ) or "저장된 항목 없음",
        ),
        ("Result contract", result.schema_version),
    ))
    return (AdvancedSection("학습 상세 정보", tuple(rows)),)
