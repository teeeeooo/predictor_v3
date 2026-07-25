"""Query and command state returned by Train model management."""

from dataclasses import dataclass

from .model_management_models import CandidateReview


@dataclass(frozen=True)
class ModelManagementSnapshot:
    status: str
    active_candidate_id: str = ""
    active_revision: int = 0
    candidates: tuple[CandidateReview, ...] = ()
    message: str = ""


@dataclass(frozen=True)
class PromotionOutcome:
    status: str
    candidate_id: str
    revision: int
    message: str
    snapshot: ModelManagementSnapshot
