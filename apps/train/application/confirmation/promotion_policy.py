"""Promotion authorization policy for recommendation/confirmation Candidates."""

from __future__ import annotations

from pathlib import Path

from apps.common.model_lifecycle.closeout.canonical import file_sha256
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.train.application.experiments.store import ExperimentStore


class RecommendationPromotionAuthorization:
    """Keep ordinary Candidates compatible while closing recommendation bypasses."""

    def __init__(self, lifecycle_root: str | Path) -> None:
        self._experiments = ExperimentStore(lifecycle_root)
        self._closeout = LifecycleCloseoutStore(lifecycle_root)
        self._repository = ModelLifecycleRepository(lifecycle_root)

    def review(
        self,
        candidate_id: str,
        source: str,
        expected_active_revision: int,
    ) -> tuple[bool, str]:
        if source.startswith("final-confirmation:"):
            decision_id = source.split(":", 1)[1]
            try:
                decision = self._closeout.read_decision(decision_id)
                confirmation = self._closeout.read_confirmation(
                    decision["confirmation_id"]
                )
                candidate = self._repository.read_candidate(candidate_id)
            except (FileNotFoundError, OSError, TypeError, ValueError):
                return False, "final_confirmation_authorization_invalid"
            if (
                decision["status"] != "approved"
                or decision["candidate_id"] != candidate_id
                or decision["observed_active_revision"]
                != expected_active_revision
                or candidate.manifest.source != "confirmation"
                or confirmation.get("confirmation_candidate_id")
                != candidate_id
                or confirmation.get(
                    "confirmation_candidate_manifest_sha256"
                ) != file_sha256(candidate.path / "manifest.json")
                or confirmation["status"] not in {
                    "approved",
                    "promotion-blocked",
                    "promoted",
                }
            ):
                return False, "final_confirmation_authorization_invalid"
            return True, ""
        recommendation_link = self._is_recommendation_candidate(candidate_id)
        confirmation_link = self._is_confirmation_candidate(candidate_id)
        if recommendation_link is None or confirmation_link is None:
            return False, "promotion_authorization_evidence_incomplete"
        if recommendation_link:
            return False, "confirmation_required"
        if confirmation_link:
            return False, "final_user_approval_required"
        try:
            candidate = self._repository.read_candidate(candidate_id)
        except (FileNotFoundError, OSError, TypeError, ValueError):
            return False, "promotion_authorization_evidence_incomplete"
        if candidate.manifest.source == "confirmation":
            return False, "confirmation_linkage_incomplete"
        return True, ""

    def _is_recommendation_candidate(self, candidate_id: str) -> bool | None:
        try:
            campaigns = self._experiments.list_campaigns()
        except (FileNotFoundError, OSError, TypeError, ValueError):
            return None
        return any(
            item.get("recommended_candidate", {}).get("candidate_id")
            == candidate_id
            for campaign in campaigns
            for item in campaign.get("recommendations", ())
            if isinstance(item, dict)
            and isinstance(item.get("recommended_candidate"), dict)
        )

    def _is_confirmation_candidate(self, candidate_id: str) -> bool | None:
        try:
            records = self._closeout.list_records(
                self._closeout.confirmations, "confirmation.json"
            )
        except (FileNotFoundError, OSError, TypeError, ValueError):
            return None
        for initial in records:
            try:
                current = self._closeout.read_confirmation(
                    initial["confirmation_id"]
                )
            except (FileNotFoundError, OSError, TypeError, ValueError):
                return None
            if current.get("confirmation_candidate_id") == candidate_id:
                return current["status"] in {
                    "awaiting_user_decision",
                    "approved",
                    "rejected",
                    "promoted",
                    "promotion-blocked",
                }
        return False
