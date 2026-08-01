"""Immutable contracts exposed by the Result Review projection."""

from __future__ import annotations

from dataclasses import dataclass

from apps.predict.application.result_contract import PredictionExecutionContext
from apps.predict.application.result_enrichment import DerivedMetricOutcome
from apps.predict.application.target_outcome import TargetOutcome


@dataclass(frozen=True)
class ResultReviewColumn:
    key: str
    header: str


RESULT_REVIEW_COLUMNS = (
    ResultReviewColumn("case_ordinal", "Case"),
    ResultReviewColumn("status", "상태"),
    ResultReviewColumn("cooling_capacity", "냉방능력"),
    ResultReviewColumn("heating_capacity", "난방능력"),
    ResultReviewColumn("specification_summary", "사양 요약"),
    ResultReviewColumn("eer", "EER"),
    ResultReviewColumn("cop", "COP"),
    ResultReviewColumn("cooling_frequency", "냉방 주파수"),
    ResultReviewColumn("heating_frequency", "난방 주파수"),
    ResultReviewColumn("refrigerant_quantity", "냉매량"),
)


@dataclass(frozen=True)
class ReviewSourceValue:
    """A value plus the stable source association used by the projection."""

    feature_identity: str
    current_key: str
    current_label: str
    semantic_unit: str
    source_kind: str
    raw_value: object | None = None
    available: bool = False


@dataclass(frozen=True)
class ResultReviewIssue:
    owner: str
    reason_code: str
    message: str


@dataclass(frozen=True)
class ResultReviewRow:
    """One immutable view of a canonical session row and its typed evidence."""

    case_ordinal: int
    case_id: str
    status: str
    freshness: str
    message: str
    stale_reason: str
    cooling_capacity: ReviewSourceValue
    heating_capacity: ReviewSourceValue
    specification_summary: str
    eer: DerivedMetricOutcome | None
    cop: DerivedMetricOutcome | None
    cooling_frequency: TargetOutcome | None
    heating_frequency: TargetOutcome | None
    refrigerant_quantity: TargetOutcome | None
    target_outcomes: tuple[TargetOutcome, ...]
    derived_metrics: tuple[DerivedMetricOutcome, ...]
    execution_context: PredictionExecutionContext | None
    issues: tuple[ResultReviewIssue, ...]

    @property
    def has_executed_evidence(self) -> bool:
        return self.execution_context is not None
