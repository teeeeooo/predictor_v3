"""Qt-free Active/Candidate review and explicit promotion boundary."""

from __future__ import annotations

from typing import Any, Callable

from apps.common.model_lifecycle.deployment_export import (
    DeploymentExportResult,
    DeploymentExportService,
)
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
    build_advanced_sections,
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
        deployment_export: DeploymentExportService | None = None,
    ) -> None:
        self._repository = repository
        self._promotion = promotion
        self._training_running = training_running or (lambda: False)
        self._deployment_export = deployment_export or DeploymentExportService(
            repository,
            promotion,
        )

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
                reason_code="training_running",
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
                reason_code="recovery_required",
            )
        return PromotionOutcome(
            result.status,
            result.candidate_id,
            result.revision,
            result.message,
            snapshot,
            reason_code=result.reason_code,
            diagnostic_message=result.message,
        )

    def export_active(
        self,
        destination_parent: str,
        *,
        expected_revision: int,
    ) -> DeploymentExportResult:
        if self._training_running():
            return DeploymentExportResult(
                "failed",
                message="학습 실행 중에는 deployment export를 생성할 수 없습니다.",
                diagnostic="training_running",
            )
        return self._deployment_export.export_active(
            destination_parent,
            expected_revision=expected_revision,
        )

    def _review(self, snapshot, active_candidate_id: str) -> CandidateReview:  # noqa: ANN001
        manifest = snapshot.manifest
        compatibility = self._promotion.inspect_compatibility(
            manifest.candidate_id
        )
        promotion_status = (
            "active"
            if manifest.candidate_id == active_candidate_id
            else compatibility.status
        )
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
                promotion_eligible=promotion_status == "compatible",
                blocking_reasons=tuple(reason for reason in reasons if reason),
                targets=tuple(
                    TargetMetricReview(item.identity, item.ml_name, "unavailable")
                    for item in manifest.targets
                ),
                baseline_kind="unavailable",
                promotion_status=promotion_status,
                promotion_reason_code=compatibility.reason_code,
                promotion_diagnostic=compatibility.diagnostic_message,
                analysis_status="unavailable",
                analysis_reason=analysis["reason"],
            )
        return CandidateReview(
            candidate_id=manifest.candidate_id,
            run_id=manifest.run_id,
            created_at=manifest.created_at,
            is_active=manifest.candidate_id == active_candidate_id,
            promotion_eligible=promotion_status == "compatible",
            blocking_reasons=tuple(reason for reason in reasons if reason),
            targets=tuple(
                _target_review(item, analysis.baseline)
                for item in analysis.targets
            ),
            baseline_kind=_baseline_kind(analysis.baseline),
            promotion_status=promotion_status,
            promotion_reason_code=compatibility.reason_code,
            promotion_diagnostic=compatibility.diagnostic_message,
            baseline_identity=str(analysis.baseline.get("identity", "")),
            baseline_reason=str(
                analysis.baseline.get("unavailable_reason", "")
            ),
            advanced_sections=build_advanced_sections(analysis),
        )


def _target_review(
    target: dict[str, Any],
    baseline: dict[str, Any],
) -> TargetMetricReview:
    metrics = target.get("metrics", {})
    comparison = target.get("baseline_comparison", {})
    delta = comparison.get("delta", {})
    comparison_kind = _target_comparison_kind(
        target,
        metrics,
        comparison,
        baseline,
    )
    reason = str(
        comparison.get("unavailable_reason")
        or baseline.get("unavailable_reason")
        or (
            "저장된 비교 수치를 사용할 수 없습니다."
            if comparison.get("comparable") is True
            and comparison_kind != "fair"
            else ""
        )
        or ""
    )
    return TargetMetricReview(
        identity=str(target.get("target_identity", "")),
        name=str(target.get("target_ml_name", "")),
        status=str(target.get("status", "")),
        r2=metrics.get("r2"),
        mae=metrics.get("mae"),
        rmse=metrics.get("rmse"),
        comparison=comparison_kind,
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


def _target_comparison_kind(
    target: dict[str, Any],
    metrics: dict[str, Any],
    comparison: dict[str, Any],
    baseline: dict[str, Any],
) -> str:
    metrics_available = target.get("status") == "complete" and all(
        _is_numeric(metrics.get(name)) for name in ("r2", "mae", "rmse")
    )
    delta = comparison.get("delta")
    delta_available = isinstance(delta, dict) and all(
        _is_numeric(delta.get(name)) for name in ("r2", "mae", "rmse")
    )
    if (
        comparison.get("comparable") is True
        and metrics_available
        and delta_available
    ):
        return "fair"
    if not metrics_available:
        return "unavailable"
    if baseline.get("type") == "none":
        return "no_baseline"
    if (
        baseline.get("type") == "active_candidate"
        and baseline.get("comparable") is False
    ):
        return "unfair"
    return "unavailable"


def _is_numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _baseline_kind(baseline: dict[str, Any]) -> str:
    if baseline.get("comparable") is True:
        return "fair"
    if baseline.get("type") == "none":
        return "no_baseline"
    if baseline.get("type") == "active_candidate":
        return "unfair"
    return "unavailable"
