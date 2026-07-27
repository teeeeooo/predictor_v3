from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from apps.common.model_lifecycle.closeout.canonical import file_sha256
from apps.common.model_lifecycle.closeout.contracts import (
    build_confirmation_record,
    build_snapshot_record,
)
from apps.common.model_lifecycle.closeout.contracts import build_final_decision
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.common.model_lifecycle.promotion import PromotionResult
from apps.train.application.confirmation.decision import (
    FinalDecisionApplicationService,
    TrustedUserAuthorityIssuer,
    UserAuthorityCapability,
    UserAuthorityContext,
)
from apps.train.application.confirmation.execution import (
    ConfirmationApplicationService,
    ConfirmationExecutionResult,
)
from apps.train.application.confirmation.promotion_policy import (
    RecommendationPromotionAuthorization,
)

HASH = "a" * 64
NOW = "2026-07-27T00:00:00+00:00"
TARGETS = ("target-a", "target-b")


class _Repository:
    def __init__(self, root: Path, candidates: dict, active=None) -> None:
        self.root = root
        self.candidates = candidates
        self.active = active

    def read_candidate(self, candidate_id: str):
        return self.candidates[candidate_id]

    def read_active(self, *, optional: bool = False):
        return self.active


class _Generations:
    def active_generation_id(self) -> str:
        return "generation-1"

    def read_generation(self, generation_id: str):
        assert generation_id == "generation-1"
        return {"generation_id": generation_id}


class _Promotion:
    def __init__(self) -> None:
        self.calls = []

    def inspect_compatibility(self, candidate_id: str):
        return SimpleNamespace(status="compatible", reason_code="")

    def promote(self, candidate_id: str, *, expected_revision: int, source: str):
        self.calls.append((candidate_id, expected_revision, source))
        return PromotionResult("active", candidate_id, expected_revision + 1)


class _Execution:
    def __init__(self, result: ConfirmationExecutionResult) -> None:
        self.result = result
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return self.result


class _Integrity:
    def validate(self, meaning):
        return None


def _candidate(root: Path, candidate_id: str, source: str):
    path = root / "candidates" / candidate_id
    path.mkdir(parents=True)
    (path / "manifest.json").write_text(
        f'{{"candidate_id":"{candidate_id}","source":"{source}"}}',
        encoding="utf-8",
    )
    return SimpleNamespace(
        path=path,
        manifest=SimpleNamespace(
            candidate_id=candidate_id,
            source=source,
            targets=tuple(SimpleNamespace(identity=value) for value in TARGETS),
        ),
    )


def _snapshot(store: LifecycleCloseoutStore, selected) -> dict:
    meaning = {
        "recommendation": {"recommendation_id": "recommendation-1"},
        "campaign": {"campaign_id": "campaign-1"},
        "selected_candidate": {
            "candidate_id": selected.manifest.candidate_id,
            "manifest_sha256": file_sha256(selected.path / "manifest.json"),
        },
        "source_run": {"run_id": "run-1"},
        "candidate_artifacts": {
            "manifest.json": {
                "sha256": file_sha256(selected.path / "manifest.json"),
                "size_bytes": (selected.path / "manifest.json").stat().st_size,
            },
        },
        "resolved_specification": {
            "features": {"experimental_derived": []},
        },
        "specification_fingerprint": HASH,
        "definition_runtime": {"generation_id": "generation-1"},
        "target_roles": {
            "production_required": list(TARGETS),
            "primary": ["target-a"],
            "guardrail": ["target-b"],
        },
        "feature_contract": {"ordered": ["feature-a"]},
        "evaluation_contract": {"metric": "r2", "seed": 42},
        "training_configuration": {
            "selected_parameters": {
                "target-a": {"depth": 3},
                "target-b": {"depth": 4},
            },
            "search_disabled_for_confirmation": True,
        },
        "baseline": {"active_revision": 0},
        "build_identity": {"training_semantic": "build-1"},
        "training_semantic_identity": HASH,
        "training_data": {
            "materialization_kind": "owned_source_bytes",
            "materialized_identity": f"sha256:{HASH}",
            "content_sha256": HASH,
            "ordered_row_set_sha256": HASH,
            "row_count": 2,
            "column_count": 2,
        },
    }
    snapshot = build_snapshot_record(
        meaning, created_at=NOW, actor_kind="user"
    )
    store.write_snapshot(snapshot)
    return snapshot


def _target_results(targets=TARGETS):
    return tuple({
        "target_identity": target,
        "status": "complete",
        "metrics": {"r2": 0.9},
    } for target in targets)


def test_confirmation_uses_frozen_all_target_meaning_without_active_mutation(
    tmp_path: Path,
) -> None:
    root = tmp_path / "lifecycle"
    selected = _candidate(root, "selected-1", "training")
    confirmation_candidate = _candidate(root, "confirmed-1", "confirmation")
    repository = _Repository(
        root,
        {"selected-1": selected, "confirmed-1": confirmation_candidate},
    )
    store = LifecycleCloseoutStore(root)
    snapshot = _snapshot(store, selected)
    execution = _Execution(ConfirmationExecutionResult(
        status="succeeded",
        target_results=_target_results(),
        confirmation_candidate_id="confirmed-1",
    ))
    promotion = _Promotion()
    service = ConfirmationApplicationService(
        repository,
        _Generations(),
        promotion,
        execution,
        closeout_store=store,
        build_identity_provider=lambda: {"training_semantic": "build-1"},
        integrity_validator=_Integrity(),
    )

    result = service.start(snapshot["snapshot_id"], confirmation_id="confirm-1")
    persisted_before = {
        path.relative_to(store.confirmations): path.read_bytes()
        for path in store.confirmations.rglob("*.json")
    }
    duplicate = service.start(
        snapshot["snapshot_id"], confirmation_id="confirm-1"
    )
    persisted_after = {
        path.relative_to(store.confirmations): path.read_bytes()
        for path in store.confirmations.rglob("*.json")
    }

    assert result["status"] == "awaiting_user_decision"
    assert duplicate == result
    assert persisted_after == persisted_before
    assert repository.active is None
    assert promotion.calls == []
    request = execution.requests[0]
    assert request.production_required_targets == TARGETS
    assert request.selected_parameters["target-a"] == {"depth": 3}


def test_partial_confirmation_fails_and_exact_user_approval_uses_guarded_owner(
    tmp_path: Path,
) -> None:
    root = tmp_path / "lifecycle"
    selected = _candidate(root, "selected-1", "training")
    confirmed = _candidate(root, "confirmed-1", "confirmation")
    repository = _Repository(
        root, {"selected-1": selected, "confirmed-1": confirmed}
    )
    store = LifecycleCloseoutStore(root)
    snapshot = _snapshot(store, selected)
    promotion = _Promotion()
    partial = ConfirmationApplicationService(
        repository,
        _Generations(),
        promotion,
        _Execution(ConfirmationExecutionResult(
            status="succeeded",
            target_results=_target_results(("target-a",)),
            confirmation_candidate_id="confirmed-1",
        )),
        closeout_store=store,
        build_identity_provider=lambda: {"training_semantic": "build-1"},
        integrity_validator=_Integrity(),
    )
    failed = partial.start(
        snapshot["snapshot_id"], confirmation_id="confirm-partial"
    )
    assert failed["status"] == "failed"
    assert repository.active is None

    complete = ConfirmationApplicationService(
        repository,
        _Generations(),
        promotion,
        _Execution(ConfirmationExecutionResult(
            status="succeeded",
            target_results=_target_results(),
            confirmation_candidate_id="confirmed-1",
        )),
        closeout_store=store,
        build_identity_provider=lambda: {"training_semantic": "build-1"},
        integrity_validator=_Integrity(),
    )
    complete.start(snapshot["snapshot_id"], confirmation_id="confirm-complete")
    issuer = TrustedUserAuthorityIssuer()
    decision = FinalDecisionApplicationService(
        repository, promotion, closeout_store=store,
        authority_issuer=issuer,
    )
    with pytest.raises(PermissionError, match="trusted"):
        decision.decide(
            "confirm-complete",
            approve=True,
            expected_active_revision=0,
            authority=UserAuthorityContext(
                actor_kind="user",
                authority_context="forged",
                interactive=True,
            ),
        )
    assert store.find_decision_for_confirmation("confirm-complete") is None
    with pytest.raises(PermissionError, match="trusted"):
        decision.decide(
            "confirm-complete",
            approve=True,
            expected_active_revision=0,
            authority=UserAuthorityCapability("user", "forged", object()),
        )
    capability = issuer.issue("interactive-test-user")
    outcome = decision.decide(
        "confirm-complete",
        approve=True,
        expected_active_revision=0,
        decision_id="decision-1",
        authority=capability,
    )
    assert outcome.status == "approved"
    assert promotion.calls == [
        ("confirmed-1", 0, "final-confirmation:decision-1")
    ]
    with pytest.raises(PermissionError, match="trusted"):
        decision.decide(
            "confirm-complete",
            approve=True,
            expected_active_revision=0,
            authority=capability,
        )

    repository.active = SimpleNamespace(revision=1)
    stale = decision.decide(
        "confirm-complete",
        approve=True,
        expected_active_revision=0,
        decision_id="decision-2",
        authority=issuer.issue("interactive-test-user"),
    )
    assert stale.status == "approved"
    assert len(promotion.calls) == 1


def test_recommendation_promotion_requires_confirmation_decision(
    tmp_path: Path,
) -> None:
    root = tmp_path / "lifecycle"
    policy = RecommendationPromotionAuthorization(root)
    policy._experiments = SimpleNamespace(list_campaigns=lambda: ({  # noqa: SLF001
        "recommendations": [{
            "recommended_candidate": {"candidate_id": "recommended-1"},
        }],
    },))

    allowed, reason = policy.review("recommended-1", "user-promotion", 0)
    assert allowed is False
    assert reason == "confirmation_required"

    confirmed = _candidate(root, "confirmed-1", "confirmation")
    policy._repository = _Repository(  # noqa: SLF001
        root, {"confirmed-1": confirmed}
    )
    manifest_hash = file_sha256(confirmed.path / "manifest.json")
    confirmation = build_confirmation_record(
        confirmation_id="confirmation-1",
        snapshot_id="snapshot-1",
        selected_candidate_id="selected-1",
        status="approved",
        created_at=NOW,
        updated_at=NOW,
        production_required_targets=list(TARGETS),
        target_results=list(_target_results()),
        confirmation_candidate_id="confirmed-1",
        confirmation_candidate_manifest_sha256=manifest_hash,
    )
    policy._closeout.write_confirmation(confirmation)  # noqa: SLF001
    decision = build_final_decision(
        decision_id="decision-approved",
        status="approved",
        snapshot_id="snapshot-1",
        confirmation_id="confirmation-1",
        candidate_id="confirmed-1",
        candidate_manifest_sha256=manifest_hash,
        observed_active_revision=0,
        created_at=NOW,
        actor_kind="user",
        authority_context="interactive-test",
    )
    policy._closeout.write_decision(decision)  # noqa: SLF001
    allowed, reason = policy.review(
        "confirmed-1", "final-confirmation:decision-approved", 0
    )
    assert allowed is True
    assert reason == ""
    allowed, reason = policy.review(
        "confirmed-1", "final-confirmation:decision-approved", 1
    )
    assert allowed is False
    assert reason == "final_confirmation_authorization_invalid"


def test_terminal_record_failure_leaves_confirmation_candidate_non_promotable(
    tmp_path: Path,
) -> None:
    class _FailTerminalStore(LifecycleCloseoutStore):
        def append_confirmation(self, payload, *, expected_status):
            if payload["status"] == "awaiting_user_decision":
                raise OSError("injected terminal append failure")
            return super().append_confirmation(
                payload, expected_status=expected_status
            )

    root = tmp_path / "lifecycle"
    selected = _candidate(root, "selected-1", "training")
    confirmed = _candidate(root, "confirmed-1", "confirmation")
    repository = _Repository(
        root, {"selected-1": selected, "confirmed-1": confirmed}
    )
    store = _FailTerminalStore(root)
    snapshot = _snapshot(store, selected)
    service = ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        _Execution(ConfirmationExecutionResult(
            status="succeeded",
            target_results=_target_results(),
            confirmation_candidate_id="confirmed-1",
        )),
        closeout_store=store,
        integrity_validator=_Integrity(),
    )
    outcome = service.start(
        snapshot["snapshot_id"], confirmation_id="confirm-orphan"
    )
    assert outcome["status"] == "blocked"
    policy = RecommendationPromotionAuthorization(root)
    policy._closeout = store  # noqa: SLF001
    policy._repository = repository  # noqa: SLF001
    policy._experiments = SimpleNamespace(list_campaigns=lambda: ())  # noqa: SLF001
    assert policy.review("confirmed-1", "user-promotion", 0) == (
        False,
        "confirmation_linkage_incomplete",
    )
