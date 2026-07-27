"""Exact-evidence final user decision over the existing guarded promotion owner."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from apps.common.model_lifecycle.closeout.canonical import file_sha256
from apps.common.model_lifecycle.closeout.contracts import build_final_decision
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.common.model_lifecycle.promotion import (
    ModelPromotionService,
    PromotionResult,
)
from apps.common.model_lifecycle.repository import ModelLifecycleRepository


@dataclass(frozen=True)
class UserAuthorityContext:
    actor_kind: str
    authority_context: str
    interactive: bool
    external_agent: bool = False

    def require_user(self) -> None:
        if (
            self.actor_kind != "user"
            or not self.authority_context
            or not self.interactive
            or self.external_agent
        ):
            raise PermissionError(
                "explicit interactive user authority is required"
            )


@dataclass(frozen=True)
class FinalDecisionOutcome:
    status: str
    decision: dict[str, Any]
    promotion: PromotionResult | None = None


class FinalDecisionApplicationService:
    def __init__(
        self,
        repository: ModelLifecycleRepository,
        promotion: ModelPromotionService,
        *,
        closeout_store: LifecycleCloseoutStore | None = None,
        clock=None,  # noqa: ANN001
    ) -> None:
        self._repository = repository
        self._promotion = promotion
        self._store = closeout_store or LifecycleCloseoutStore(repository.root)
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def decide(
        self,
        confirmation_id: str,
        *,
        approve: bool,
        authority: UserAuthorityContext,
        expected_active_revision: int,
        decision_id: str | None = None,
        reason: str = "",
    ) -> FinalDecisionOutcome:
        authority.require_user()
        confirmation = self._store.read_confirmation(confirmation_id)
        identity = decision_id or f"decision-{uuid4().hex}"
        status = "approved" if approve else "rejected"
        stale_reason = self._stale_reason(
            confirmation, expected_active_revision=expected_active_revision
        )
        if stale_reason:
            status = "stale"
            reason = stale_reason
        candidate_id = confirmation.get("confirmation_candidate_id")
        candidate_hash = confirmation.get(
            "confirmation_candidate_manifest_sha256"
        )
        if not candidate_id or not candidate_hash:
            raise ValueError("confirmation has no final Candidate evidence")
        decision = build_final_decision(
            decision_id=identity,
            status=status,
            snapshot_id=confirmation["snapshot_id"],
            confirmation_id=confirmation_id,
            candidate_id=candidate_id,
            candidate_manifest_sha256=candidate_hash,
            observed_active_revision=expected_active_revision,
            created_at=self._clock().isoformat(),
            actor_kind=authority.actor_kind,
            authority_context=authority.authority_context,
            reason=reason,
        )
        self._store.write_decision(decision)
        if status != "approved":
            return FinalDecisionOutcome(status, decision)
        promotion = self._promotion.promote(
            candidate_id,
            expected_revision=expected_active_revision,
            source=f"final-confirmation:{identity}",
        )
        return FinalDecisionOutcome(status, decision, promotion)

    def inspect(self, decision_id: str) -> dict[str, Any]:
        return self._store.read_decision(decision_id)

    def _stale_reason(
        self,
        confirmation: dict[str, Any],
        *,
        expected_active_revision: int,
    ) -> str:
        if confirmation["status"] != "awaiting_user_decision":
            return "confirmation is no longer awaiting an exact user decision"
        snapshot = self._store.read_snapshot(confirmation["snapshot_id"])
        if snapshot["status"] != "frozen":
            return "confirmation snapshot is no longer frozen"
        candidate_id = confirmation["confirmation_candidate_id"]
        candidate = self._repository.read_candidate(candidate_id)
        current_hash = file_sha256(candidate.path / "manifest.json")
        if current_hash != confirmation["confirmation_candidate_manifest_sha256"]:
            return "confirmation Candidate manifest changed"
        active = self._repository.read_active(optional=True)
        current_revision = active.revision if active else 0
        if current_revision != expected_active_revision:
            return "Active revision changed after evidence review"
        return ""
