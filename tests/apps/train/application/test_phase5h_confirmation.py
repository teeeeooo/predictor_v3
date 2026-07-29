from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest

from apps.common.model_lifecycle.closeout.canonical import (
    content_sha256,
    file_sha256,
)
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
        if request.execution_started is not None:
            request.execution_started()
        return self.result


class _Integrity:
    def validate(self, meaning):
        return None


class _DriftingIntegrity:
    def __init__(self, reason: str) -> None:
        self.reason = reason
        self.calls = 0

    def validate(self, meaning):
        self.calls += 1
        if self.calls == 2:
            raise ValueError(self.reason)


class _GuardedExecution(_Execution):
    def execute(self, request):
        self.requests.append(request)
        if request.execution_started is not None:
            request.execution_started()
        assert request.prepublication_integrity is not None
        request.prepublication_integrity()
        return self.result


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


def _snapshot(
    store: LifecycleCloseoutStore,
    selected,
    *,
    training_semantic_identity: str = HASH,
) -> dict:
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
        "training_semantic_identity": training_semantic_identity,
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


def test_implicit_and_explicit_duplicate_start_share_one_execution(
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
    execution = _Execution(ConfirmationExecutionResult(
        status="succeeded",
        target_results=_target_results(),
        confirmation_candidate_id="confirmed-1",
    ))

    def build_service() -> ConfirmationApplicationService:
        return ConfirmationApplicationService(
            repository,
            _Generations(),
            _Promotion(),
            execution,
            closeout_store=LifecycleCloseoutStore(root),
            integrity_validator=_Integrity(),
        )

    first = build_service().start(snapshot["snapshot_id"])
    implicit_retry = build_service().start(snapshot["snapshot_id"])
    explicit_retry = build_service().start(
        snapshot["snapshot_id"], confirmation_id="caller-selected-rerun"
    )
    identity_conflict = build_service().start(
        snapshot["snapshot_id"],
        confirmation_id=first["confirmation_id"],
        locked_final_test_seal_id="different-seal",
    )

    assert first == implicit_retry == explicit_retry
    assert first["execution_key"]
    assert first["confirmation_id"] == (
        f"confirmation-{first['execution_key']}"
    )
    assert len(execution.requests) == 1
    assert len(tuple(store.confirmations.iterdir())) == 1
    assert not (store.confirmations / "caller-selected-rerun").exists()
    assert identity_conflict["reason_code"] == "confirmation_identity_conflict"


def test_concurrent_duplicate_start_has_one_durable_owner(
    tmp_path: Path,
) -> None:
    class _BlockingExecution(_Execution):
        def __init__(self, result) -> None:  # noqa: ANN001
            super().__init__(result)
            self.started = Event()
            self.release = Event()

        def execute(self, request):  # noqa: ANN001
            self.requests.append(request)
            if request.execution_started is not None:
                request.execution_started()
            self.started.set()
            assert self.release.wait(timeout=5)
            return self.result

    root = tmp_path / "lifecycle"
    selected = _candidate(root, "selected-1", "training")
    confirmed = _candidate(root, "confirmed-1", "confirmation")
    repository = _Repository(
        root, {"selected-1": selected, "confirmed-1": confirmed}
    )
    store = LifecycleCloseoutStore(root)
    snapshot = _snapshot(store, selected)
    execution = _BlockingExecution(ConfirmationExecutionResult(
        status="succeeded",
        target_results=_target_results(),
        confirmation_candidate_id="confirmed-1",
    ))

    def service() -> ConfirmationApplicationService:
        return ConfirmationApplicationService(
            repository,
            _Generations(),
            _Promotion(),
            execution,
            closeout_store=LifecycleCloseoutStore(root),
            integrity_validator=_Integrity(),
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        first_future = pool.submit(service().start, snapshot["snapshot_id"])
        assert execution.started.wait(timeout=5)
        duplicate_future = pool.submit(
            service().start, snapshot["snapshot_id"]
        )
        execution.release.set()
        first = first_future.result(timeout=5)
        duplicate = duplicate_future.result(timeout=5)

    assert duplicate["confirmation_id"] == first["confirmation_id"]
    assert duplicate["status"] in {
        "confirmation_pending", "confirmation_running",
        "awaiting_user_decision",
    }
    assert len(execution.requests) == 1
    reconstructed = service().start(snapshot["snapshot_id"])
    assert reconstructed == first
    assert len(tuple(store.confirmations.iterdir())) == 1


def test_partial_execution_claim_recovers_exact_pending_on_alternate_id_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "lifecycle"
    selected = _candidate(root, "selected-1", "training")
    confirmed = _candidate(root, "confirmed-1", "confirmation")
    repository = _Repository(
        root, {"selected-1": selected, "confirmed-1": confirmed}
    )
    store = LifecycleCloseoutStore(root)
    snapshot = _snapshot(store, selected)
    execution = _Execution(ConfirmationExecutionResult(
        status="succeeded",
        target_results=_target_results(),
        confirmation_candidate_id="confirmed-1",
    ))

    def fail_record_write(_payload):  # noqa: ANN001
        partial = (
            store.confirmations / _payload["confirmation_id"]
        )
        partial.mkdir(parents=True)
        raise OSError("injected confirmation record failure")

    monkeypatch.setattr(store, "write_confirmation", fail_record_write)
    first = ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=store,
        integrity_validator=_Integrity(),
    ).start(snapshot["snapshot_id"])

    assert first["status"] == "blocked"
    assert execution.requests == []
    claim_path = next(
        store.confirmation_executions.glob("*/claim.json")
    )
    claim = json.loads(claim_path.read_text(encoding="utf-8"))
    pending = claim["pending_record"]
    assert claim["pending_record_sha256"] == content_sha256(pending)
    assert not (
        store.confirmations
        / pending["confirmation_id"]
        / "confirmation.json"
    ).exists()

    recovered_store = LifecycleCloseoutStore(root)
    completed = ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=recovered_store,
        integrity_validator=_Integrity(),
    ).start(
        snapshot["snapshot_id"],
        confirmation_id="alternate-caller-id",
    )

    initial_path = (
        recovered_store.confirmations
        / pending["confirmation_id"]
        / "confirmation.json"
    )
    assert json.loads(initial_path.read_text(encoding="utf-8")) == pending
    assert completed["confirmation_id"] == pending["confirmation_id"]
    assert completed["status"] == "awaiting_user_decision"
    assert len(execution.requests) == 1
    assert not (
        recovered_store.confirmations / "alternate-caller-id"
    ).exists()
    assert len(tuple(recovered_store.confirmations.iterdir())) == 1


def test_claim_and_initial_record_mismatch_blocks_without_rewrite(
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
    execution = _Execution(ConfirmationExecutionResult(
        status="succeeded",
        target_results=_target_results(),
        confirmation_candidate_id="confirmed-1",
    ))
    service = ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=store,
        integrity_validator=_Integrity(),
    )
    completed = service.start(snapshot["snapshot_id"])
    initial_path = (
        store.confirmations
        / completed["confirmation_id"]
        / "confirmation.json"
    )
    initial = json.loads(initial_path.read_text(encoding="utf-8"))
    initial["updated_at"] = "2026-07-27T00:00:01+00:00"
    initial_path.write_text(
        json.dumps(initial, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    before = initial_path.read_bytes()

    outcome = service.start(
        snapshot["snapshot_id"],
        confirmation_id=completed["confirmation_id"],
    )

    assert outcome["status"] == "blocked"
    assert len(execution.requests) == 1
    assert initial_path.read_bytes() == before
    assert len(tuple(store.confirmations.iterdir())) == 1


def test_retry_claims_start_when_pending_write_succeeded_before_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "lifecycle"
    selected = _candidate(root, "selected-1", "training")
    confirmed = _candidate(root, "confirmed-1", "confirmation")
    repository = _Repository(
        root, {"selected-1": selected, "confirmed-1": confirmed}
    )
    store = LifecycleCloseoutStore(root)
    snapshot = _snapshot(store, selected)
    execution = _Execution(ConfirmationExecutionResult(
        status="succeeded",
        target_results=_target_results(),
        confirmation_candidate_id="confirmed-1",
    ))
    write_confirmation = store.write_confirmation

    def write_then_fail(payload):  # noqa: ANN001
        write_confirmation(payload)
        raise OSError("injected ambiguous publication failure")

    monkeypatch.setattr(store, "write_confirmation", write_then_fail)
    first = ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=store,
        integrity_validator=_Integrity(),
    ).start(snapshot["snapshot_id"])
    assert first["status"] == "blocked"
    assert execution.requests == []

    recovered = ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=LifecycleCloseoutStore(root),
        integrity_validator=_Integrity(),
    ).start(snapshot["snapshot_id"], confirmation_id="alternate-id")

    assert recovered["status"] == "awaiting_user_decision"
    assert len(execution.requests) == 1
    assert len(tuple(store.confirmations.iterdir())) == 1


@pytest.mark.parametrize("corruption", ("hash", "identity"))
def test_corrupt_partial_execution_claim_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    corruption: str,
) -> None:
    root = tmp_path / corruption
    selected = _candidate(root, "selected-1", "training")
    confirmed = _candidate(root, "confirmed-1", "confirmation")
    repository = _Repository(
        root, {"selected-1": selected, "confirmed-1": confirmed}
    )
    store = LifecycleCloseoutStore(root)
    snapshot = _snapshot(store, selected)
    execution = _Execution(ConfirmationExecutionResult(
        status="succeeded",
        target_results=_target_results(),
        confirmation_candidate_id="confirmed-1",
    ))
    monkeypatch.setattr(
        store,
        "write_confirmation",
        lambda _payload: (_ for _ in ()).throw(OSError("injected")),
    )
    ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=store,
        integrity_validator=_Integrity(),
    ).start(snapshot["snapshot_id"])
    claim_path = next(store.confirmation_executions.glob("*/claim.json"))
    claim = json.loads(claim_path.read_text(encoding="utf-8"))
    if corruption == "hash":
        claim["pending_record_sha256"] = "b" * 64
    else:
        claim["pending_record"]["confirmation_id"] = "corrupt-identity"
    claim_path.write_text(
        json.dumps(claim, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    outcome = ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=LifecycleCloseoutStore(root),
        integrity_validator=_Integrity(),
    ).start(snapshot["snapshot_id"], confirmation_id="alternate-id")

    assert outcome["status"] == "blocked"
    assert execution.requests == []
    assert not tuple(store.confirmations.glob("*/confirmation.json"))
    assert set(repository.candidates) == {"selected-1", "confirmed-1"}
    assert repository.active is None


def test_concurrent_partial_execution_claim_recovery_has_one_owner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _CountingExecution(_Execution):
        def __init__(self, result) -> None:  # noqa: ANN001
            super().__init__(result)
            self.started = Event()
            self.release = Event()

        def execute(self, request):  # noqa: ANN001
            self.requests.append(request)
            if request.execution_started is not None:
                request.execution_started()
            self.started.set()
            assert self.release.wait(timeout=5)
            return self.result

    root = tmp_path / "lifecycle"
    selected = _candidate(root, "selected-1", "training")
    confirmed = _candidate(root, "confirmed-1", "confirmation")
    repository = _Repository(
        root, {"selected-1": selected, "confirmed-1": confirmed}
    )
    store = LifecycleCloseoutStore(root)
    snapshot = _snapshot(store, selected)
    execution = _CountingExecution(ConfirmationExecutionResult(
        status="succeeded",
        target_results=_target_results(),
        confirmation_candidate_id="confirmed-1",
    ))
    monkeypatch.setattr(
        store,
        "write_confirmation",
        lambda _payload: (_ for _ in ()).throw(OSError("injected")),
    )
    ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=store,
        integrity_validator=_Integrity(),
    ).start(snapshot["snapshot_id"])

    def retry(identity: str) -> dict:
        return ConfirmationApplicationService(
            repository,
            _Generations(),
            _Promotion(),
            execution,
            closeout_store=LifecycleCloseoutStore(root),
            integrity_validator=_Integrity(),
        ).start(snapshot["snapshot_id"], confirmation_id=identity)

    with ThreadPoolExecutor(max_workers=2) as pool:
        first_future = pool.submit(retry, "alternate-a")
        assert execution.started.wait(timeout=5)
        duplicate_future = pool.submit(retry, "alternate-b")
        execution.release.set()
        first = first_future.result(timeout=5)
        duplicate = duplicate_future.result(timeout=5)

    assert first["confirmation_id"] == duplicate["confirmation_id"]
    assert len(execution.requests) == 1
    assert len(tuple(store.confirmations.iterdir())) == 1


@pytest.mark.parametrize("retry_id", (None, "alternate-retry-id"))
def test_prepared_start_recovers_after_running_transition_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    retry_id: str | None,
) -> None:
    root = tmp_path / str(retry_id or "implicit")
    selected = _candidate(root, "selected-1", "training")
    confirmed = _candidate(root, "confirmed-1", "confirmation")
    repository = _Repository(
        root, {"selected-1": selected, "confirmed-1": confirmed}
    )
    store = LifecycleCloseoutStore(root)
    snapshot = _snapshot(store, selected)
    execution = _Execution(ConfirmationExecutionResult(
        status="succeeded",
        target_results=_target_results(),
        confirmation_candidate_id="confirmed-1",
    ))
    append_confirmation = store.append_confirmation

    def fail_running(payload, *, expected_status):  # noqa: ANN001
        if payload["status"] == "confirmation_running":
            assert tuple(
                store.confirmation_executions.glob(
                    "*/start_prepared.json"
                )
            )
            raise OSError("injected running transition failure")
        return append_confirmation(
            payload, expected_status=expected_status
        )

    monkeypatch.setattr(store, "append_confirmation", fail_running)
    first = ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=store,
        integrity_validator=_Integrity(),
    ).start(snapshot["snapshot_id"])

    assert first["status"] == "blocked"
    assert execution.requests == []
    pending = next(store.confirmations.glob("*/confirmation.json"))
    confirmation_id = pending.parent.name

    recovered_service = ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=LifecycleCloseoutStore(root),
        integrity_validator=_Integrity(),
    )
    kwargs = {"confirmation_id": retry_id} if retry_id else {}
    recovered = recovered_service.start(snapshot["snapshot_id"], **kwargs)
    replay = recovered_service.start(
        snapshot["snapshot_id"],
        confirmation_id="later-alternate-id",
    )

    assert recovered["confirmation_id"] == confirmation_id
    assert replay == recovered
    assert len(execution.requests) == 1
    assert execution.requests[0].confirmation_id == confirmation_id
    history = tuple(
        (store.confirmations / confirmation_id / "history").glob("*.json")
    )
    assert sum("confirmation_running" in path.name for path in history) == 1
    assert tuple(
        store.confirmation_executions.glob("*/execution_started.json")
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("confirmation_id", "corrupt-confirmation"),
        ("execution_key", "b" * 64),
        ("running_record_sha256", "b" * 64),
    ),
)
def test_corrupt_prepared_start_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: str,
) -> None:
    root = tmp_path / field
    selected = _candidate(root, "selected-1", "training")
    confirmed = _candidate(root, "confirmed-1", "confirmation")
    repository = _Repository(
        root, {"selected-1": selected, "confirmed-1": confirmed}
    )
    store = LifecycleCloseoutStore(root)
    snapshot = _snapshot(store, selected)
    execution = _Execution(ConfirmationExecutionResult(
        status="succeeded",
        target_results=_target_results(),
        confirmation_candidate_id="confirmed-1",
    ))
    monkeypatch.setattr(
        store,
        "append_confirmation",
        lambda *_args, **_kwargs: (
            (_ for _ in ()).throw(OSError("injected"))
        ),
    )
    ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=store,
        integrity_validator=_Integrity(),
    ).start(snapshot["snapshot_id"])
    prepared_path = next(
        store.confirmation_executions.glob("*/start_prepared.json")
    )
    prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
    prepared[field] = value
    prepared_path.write_text(
        json.dumps(prepared, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    before = prepared_path.read_bytes()

    outcome = ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=LifecycleCloseoutStore(root),
        integrity_validator=_Integrity(),
    ).start(
        snapshot["snapshot_id"],
        confirmation_id="alternate-id",
    )

    assert outcome["status"] == "blocked"
    assert execution.requests == []
    assert prepared_path.read_bytes() == before
    assert len(tuple(store.confirmations.iterdir())) == 1
    assert repository.active is None


def test_concurrent_prepared_start_recovery_has_one_execution_owner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _RecoveringExecution(_Execution):
        def __init__(self, result) -> None:  # noqa: ANN001
            super().__init__(result)
            self.started = Event()
            self.release = Event()

        def execute(self, request):  # noqa: ANN001
            self.requests.append(request)
            if request.execution_started is not None:
                request.execution_started()
            self.started.set()
            assert self.release.wait(timeout=5)
            return self.result

    root = tmp_path / "lifecycle"
    selected = _candidate(root, "selected-1", "training")
    confirmed = _candidate(root, "confirmed-1", "confirmation")
    repository = _Repository(
        root, {"selected-1": selected, "confirmed-1": confirmed}
    )
    store = LifecycleCloseoutStore(root)
    snapshot = _snapshot(store, selected)
    execution = _RecoveringExecution(ConfirmationExecutionResult(
        status="succeeded",
        target_results=_target_results(),
        confirmation_candidate_id="confirmed-1",
    ))
    monkeypatch.setattr(
        store,
        "append_confirmation",
        lambda *_args, **_kwargs: (
            (_ for _ in ()).throw(OSError("injected"))
        ),
    )
    ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=store,
        integrity_validator=_Integrity(),
    ).start(snapshot["snapshot_id"])

    def retry(identity: str) -> dict:
        return ConfirmationApplicationService(
            repository,
            _Generations(),
            _Promotion(),
            execution,
            closeout_store=LifecycleCloseoutStore(root),
            integrity_validator=_Integrity(),
        ).start(snapshot["snapshot_id"], confirmation_id=identity)

    with ThreadPoolExecutor(max_workers=2) as pool:
        first_future = pool.submit(retry, "alternate-a")
        assert execution.started.wait(timeout=5)
        second_future = pool.submit(retry, "alternate-b")
        execution.release.set()
        first = first_future.result(timeout=5)
        second = second_future.result(timeout=5)

    assert first == second
    assert len(execution.requests) == 1
    confirmation_id = first["confirmation_id"]
    history = tuple(
        (store.confirmations / confirmation_id / "history").glob("*.json")
    )
    assert sum("confirmation_running" in path.name for path in history) == 1


@pytest.mark.parametrize("reason", (
    "captured Candidate artifacts changed",
    "captured Definition generation artifacts changed",
    "captured campaign evidence changed",
    "owned materialized training data hash mismatch",
))
def test_prepublication_snapshot_drift_blocks_without_candidate_link(
    tmp_path: Path,
    reason: str,
) -> None:
    root = tmp_path / reason.split()[1]
    selected = _candidate(root, "selected-1", "training")
    confirmed = _candidate(root, "confirmed-1", "confirmation")
    repository = _Repository(
        root, {"selected-1": selected, "confirmed-1": confirmed}
    )
    store = LifecycleCloseoutStore(root)
    snapshot = _snapshot(store, selected)
    integrity = _DriftingIntegrity(reason)
    execution = _GuardedExecution(ConfirmationExecutionResult(
        status="succeeded",
        target_results=_target_results(),
        confirmation_candidate_id="confirmed-1",
    ))
    before = tuple(repository.candidates)

    outcome = ConfirmationApplicationService(
        repository,
        _Generations(),
        _Promotion(),
        execution,
        closeout_store=store,
        integrity_validator=integrity,
    ).start(snapshot["snapshot_id"])

    assert outcome["status"] == "blocked"
    assert outcome["confirmation_candidate_id"] is None
    assert outcome["blocking_reasons"] == [{
        "code": "confirmation_start_blocked",
        "reason": reason,
    }]
    assert tuple(repository.candidates) == before
    assert integrity.calls == 2


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

    retry_snapshot = _snapshot(
        store, selected, training_semantic_identity="b" * 64
    )
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
    complete.start(
        retry_snapshot["snapshot_id"], confirmation_id="confirm-complete"
    )
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
