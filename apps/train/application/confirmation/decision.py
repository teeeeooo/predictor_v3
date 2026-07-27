"""Exact-evidence final user decision over the existing guarded promotion owner."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from apps.common.model_lifecycle.filesystem import LifecycleFilesystem
from apps.common.model_lifecycle.locking import lifecycle_lock
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
    """Untrusted public context. Possessing matching fields grants no authority."""

    actor_kind: str
    authority_context: str
    interactive: bool
    external_agent: bool = False


class UserAuthorityCapability:
    __slots__ = (
        "actor_kind",
        "authority_context",
        "_issuer_identity",
        "_nonce",
    )

    def __init__(
        self,
        actor_kind: str,
        authority_context: str,
        issuer_identity: object,
        nonce: object | None = None,
    ) -> None:
        self.actor_kind = actor_kind
        self.authority_context = authority_context
        self._issuer_identity = issuer_identity
        self._nonce = nonce or object()

    def __reduce__(self):  # noqa: ANN204
        raise TypeError("user authority capabilities cannot be serialized")


class TrustedUserAuthorityIssuer:
    """Process-local trusted interaction boundary shared by GUI and headless."""

    def __init__(self) -> None:
        self.__identity = object()
        self.__issued: set[object] = set()

    def issue(self, authority_context: str) -> UserAuthorityCapability:
        if type(authority_context) is not str or not authority_context:
            raise PermissionError("trusted user authority context is required")
        nonce = object()
        self.__issued.add(nonce)
        return UserAuthorityCapability(
            "user", authority_context, self.__identity, nonce
        )

    def validate(self, capability: object) -> UserAuthorityCapability:
        if (
            type(capability) is not UserAuthorityCapability
            or capability._issuer_identity is not self.__identity
            or capability._nonce not in self.__issued
            or capability.actor_kind != "user"
            or not capability.authority_context
        ):
            raise PermissionError(
                "trusted interactive user authority is required"
            )
        self.__issued.remove(capability._nonce)
        return capability


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
        authority_issuer: TrustedUserAuthorityIssuer | None = None,
        clock=None,  # noqa: ANN001
    ) -> None:
        self._repository = repository
        self._promotion = promotion
        self._store = closeout_store or LifecycleCloseoutStore(repository.root)
        self._authority_issuer = authority_issuer or TrustedUserAuthorityIssuer()
        self._filesystem = LifecycleFilesystem(repository.root)
        self._decision_lock = (
            self._filesystem.root / ".final-confirmation-decision.lock"
        )
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def decide(
        self,
        confirmation_id: str,
        *,
        approve: bool,
        authority: UserAuthorityCapability,
        expected_active_revision: int,
        decision_id: str | None = None,
        reason: str = "",
    ) -> FinalDecisionOutcome:
        trusted = self._authority_issuer.validate(authority)
        with lifecycle_lock(
            self._decision_lock, filesystem=self._filesystem
        ):
            return self._decide(
                confirmation_id,
                approve=approve,
                trusted=trusted,
                expected_active_revision=expected_active_revision,
                decision_id=decision_id,
                reason=reason,
            )

    def _decide(
        self,
        confirmation_id: str,
        *,
        approve: bool,
        trusted: UserAuthorityCapability,
        expected_active_revision: int,
        decision_id: str | None,
        reason: str,
    ) -> FinalDecisionOutcome:
        confirmation = self._store.read_confirmation(confirmation_id)
        existing = self._store.find_decision_for_confirmation(confirmation_id)
        if existing is not None:
            expected_status = "approved" if approve else "rejected"
            if existing["status"] != expected_status:
                raise ValueError("confirmation already has a conflicting decision")
            return self._resume_decision(existing, confirmation)
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
            actor_kind=trusted.actor_kind,
            authority_context=trusted.authority_context,
            reason=reason,
        )
        self._store.write_decision(decision)
        if status != "approved":
            if status == "rejected":
                self._append_decision_state(confirmation, "rejected")
            return FinalDecisionOutcome(status, decision)
        self._append_decision_state(confirmation, "approved")
        return self._promote_decision(decision)

    def _resume_decision(
        self, decision: dict[str, Any], confirmation: dict[str, Any]
    ) -> FinalDecisionOutcome:
        if decision["status"] != "approved":
            if (
                decision["status"] == "rejected"
                and confirmation["status"] != "rejected"
            ):
                self._append_decision_state(confirmation, "rejected")
            return FinalDecisionOutcome(decision["status"], decision)
        if confirmation["status"] == "promoted":
            return FinalDecisionOutcome("approved", decision)
        if confirmation["status"] == "awaiting_user_decision":
            self._append_decision_state(confirmation, "approved")
            confirmation = self._store.read_confirmation(
                decision["confirmation_id"]
            )
        active = self._repository.read_active(optional=True)
        if (
            active is not None
            and active.candidate_id == decision["candidate_id"]
            and active.revision == decision["observed_active_revision"] + 1
        ):
            self._append_decision_state(confirmation, "promoted")
            return FinalDecisionOutcome(
                "approved",
                decision,
                PromotionResult(
                    "active",
                    active.candidate_id,
                    active.revision,
                ),
            )
        return self._promote_decision(decision)

    def _promote_decision(
        self, decision: dict[str, Any]
    ) -> FinalDecisionOutcome:
        promotion = self._promotion.promote(
            decision["candidate_id"],
            expected_revision=decision["observed_active_revision"],
            source=f"final-confirmation:{decision['decision_id']}",
        )
        confirmation = self._store.read_confirmation(
            decision["confirmation_id"]
        )
        terminal = "promoted" if promotion.status == "active" else "promotion-blocked"
        if confirmation["status"] != terminal:
            self._append_decision_state(confirmation, terminal)
        return FinalDecisionOutcome("approved", decision, promotion)

    def _append_decision_state(
        self, confirmation: dict[str, Any], status: str
    ) -> None:
        from apps.common.model_lifecycle.closeout.contracts import (
            build_confirmation_record,
        )
        from .record_projection import record_arguments

        updated = build_confirmation_record(
            **{
                **record_arguments(confirmation),
                "status": status,
                "updated_at": self._clock().isoformat(),
            }
        )
        self._store.append_confirmation(
            updated, expected_status=confirmation["status"]
        )

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
