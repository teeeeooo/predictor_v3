"""Immutable Candidate review projections for Train adapters."""

from dataclasses import dataclass


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
    baseline_identity: str = ""
    baseline_reason: str = ""
    analysis_status: str = "available"
    analysis_reason: str = ""
    advanced_sections: tuple[AdvancedSection, ...] = ()
