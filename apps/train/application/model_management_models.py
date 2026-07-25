"""Immutable Candidate review and persisted evidence projections."""

from dataclasses import dataclass
from typing import Any

from apps.common.model_lifecycle.training_result_contracts import (
    TrainingAnalysisResult,
)


@dataclass(frozen=True)
class TargetMetricReview:
    identity: str
    name: str
    status: str
    r2: object = None
    mae: object = None
    rmse: object = None
    comparison: str = "unavailable"
    delta_r2: object = None
    delta_mae: object = None
    delta_rmse: object = None
    unavailable_reason: str = ""
    blocking_reason: str = ""


@dataclass(frozen=True)
class AdvancedSection:
    title: str
    rows: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class CandidateReview:
    candidate_id: str
    run_id: str
    created_at: str
    is_active: bool
    promotion_eligible: bool
    blocking_reasons: tuple[str, ...]
    targets: tuple[TargetMetricReview, ...]
    baseline_kind: str
    promotion_status: str = "compatible"
    promotion_reason_code: str = ""
    promotion_diagnostic: str = ""
    baseline_identity: str = ""
    baseline_reason: str = ""
    analysis_status: str = "available"
    analysis_reason: str = ""
    advanced_sections: tuple[AdvancedSection, ...] = ()


def build_advanced_sections(
    result: TrainingAnalysisResult,
) -> tuple[AdvancedSection, ...]:
    """Project persisted Phase 5C Advanced evidence without deriving values."""
    sections: list[AdvancedSection] = []
    for target in result.targets:
        target_name = str(target.get("target_ml_name", ""))
        rfecv = target.get("rfecv", {})
        features = tuple(rfecv.get("features", ()))
        sections.extend((
            AdvancedSection(
                f"{target_name} · RFECV",
                _summary_rows(rfecv, excluded={"features"}),
            ),
            AdvancedSection(
                f"{target_name} · 선택 특성",
                tuple(
                    (
                        str(item.get("feature", "저장되지 않음")),
                        _mapping_details(item, excluded={"feature"}),
                    )
                    for item in features
                    if item.get("selected") is True
                ) or (("선택 결과", "저장된 항목 없음"),),
            ),
            AdvancedSection(
                f"{target_name} · RFECV 순위",
                tuple(
                    (
                        str(item.get("feature", "저장되지 않음")),
                        _mapping_details(item, excluded={"feature"}),
                    )
                    for item in features
                ) or (("순위", "저장된 항목 없음"),),
            ),
            AdvancedSection(
                f"{target_name} · Feature importance",
                tuple(
                    (
                        str(item.get("feature", "저장되지 않음")),
                        _mapping_details(item, excluded={"feature"}),
                    )
                    for item in target.get("feature_importance", ())
                ) or (("중요도", "저장된 항목 없음"),),
            ),
            _optuna_section(target_name, target.get("optuna", {})),
        ))
    sections.extend((
        _preprocessing_section(result.preprocessing),
        _data_quality_section(result.preprocessing),
        AdvancedSection(
            "Contract",
            (("training result schema", result.schema_version),),
        ),
    ))
    return tuple(sections)


def _optuna_section(
    target_name: str,
    optuna: dict[str, Any],
) -> AdvancedSection:
    rows = list(_summary_rows(
        optuna,
        excluded={"selected_parameters", "trials"},
    ))
    rows.extend(
        (
            f"선택 parameter · {name}",
            _stored_value(value),
        )
        for name, value in optuna.get("selected_parameters", {}).items()
    )
    rows.extend(
        (
            f"Trial {item.get('trial_number', '저장되지 않음')}",
            _mapping_details(item, excluded={"trial_number"}),
        )
        for item in optuna.get("trials", ())
    )
    return AdvancedSection(
        f"{target_name} · Optuna",
        tuple(rows) or (("상태", "저장된 항목 없음"),),
    )


def _preprocessing_section(
    preprocessing: dict[str, Any],
) -> AdvancedSection:
    rows = list(_summary_rows(
        preprocessing,
        excluded={"steps", "feature_data_quality"},
    ))
    rows.extend(
        (
            f"Step {index}",
            _mapping_details(item),
        )
        for index, item in enumerate(preprocessing.get("steps", ()), start=1)
    )
    return AdvancedSection(
        "Preprocessing",
        tuple(rows) or (("상태", "저장된 항목 없음"),),
    )


def _data_quality_section(
    preprocessing: dict[str, Any],
) -> AdvancedSection:
    rows = tuple(
        (
            str(item.get("feature", "저장되지 않음")),
            _mapping_details(item, excluded={"feature"}),
        )
        for item in preprocessing.get("feature_data_quality", ())
    )
    return AdvancedSection(
        "Data quality",
        rows or (("품질 evidence", "저장된 항목 없음"),),
    )


def _summary_rows(
    payload: dict[str, Any],
    *,
    excluded: set[str],
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (str(name), _stored_value(value))
        for name, value in payload.items()
        if name not in excluded
    )


def _mapping_details(
    payload: dict[str, Any],
    *,
    excluded: set[str] | None = None,
) -> str:
    excluded = excluded or set()
    return " · ".join(
        f"{name}={_stored_value(value)}"
        for name, value in payload.items()
        if name not in excluded
    ) or "저장된 상세 값 없음"


def _stored_value(value: object) -> str:
    if value is None:
        return "저장되지 않음"
    if isinstance(value, dict):
        return "{" + ", ".join(
            f"{name}: {_stored_value(item)}"
            for name, item in value.items()
        ) + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_stored_value(item) for item in value) + "]"
    return str(value)
