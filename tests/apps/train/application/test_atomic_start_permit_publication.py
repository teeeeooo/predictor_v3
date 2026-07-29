"""Crash-window regressions for atomic confirmation start permits."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

import pytest

from apps.common.model_lifecycle.closeout.canonical import content_sha256
from apps.common.model_lifecycle.closeout.contracts import (
    build_confirmation_record,
    build_locked_final_test,
)
from apps.common.model_lifecycle.closeout.start_handshake import (
    build_confirmation_start_handshake,
)
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.common.model_lifecycle.durability_errors import (
    PostRenameDurabilityError,
)
from apps.train.adapters.subprocess_training_runner import (
    SubprocessTrainingRunner,
)
from apps.train.ports.training_execution_port import TrainingExecutionCallbacks
from apps.train.state.training_run_state import TrainingRequest
from tools.dev.mock_smoke.generators import write_mock_training_data


HASH = "a" * 64
NOW = "2026-07-29T00:00:00+00:00"
LATER = "2026-07-29T00:00:01+00:00"
PRECOMMIT_STAGES = (
    "after_temporary_create",
    "during_temporary_write",
    "before_temporary_flush_fsync",
    "after_temporary_fsync_before_commit",
)


def _ready_store(
    root: Path,
    *,
    failure_hook=None,  # noqa: ANN001
) -> tuple[LifecycleCloseoutStore, dict]:
    root.mkdir(parents=True)
    store = LifecycleCloseoutStore(
        root,
        permit_publication_hook=failure_hook,
    )
    pending = build_confirmation_record(
        confirmation_id="confirmation-atomic",
        snapshot_id="snapshot-atomic",
        selected_candidate_id="candidate-source",
        status="confirmation_pending",
        created_at=NOW,
        updated_at=NOW,
        production_required_targets=["target-a"],
        execution_key=HASH,
    )
    store.claim_confirmation_execution(
        HASH,
        requested_confirmation_id=None,
        pending=pending,
    )
    running = build_confirmation_record(
        confirmation_id="confirmation-atomic",
        snapshot_id="snapshot-atomic",
        selected_candidate_id="candidate-source",
        status="confirmation_running",
        created_at=NOW,
        updated_at=LATER,
        production_required_targets=["target-a"],
        execution_key=HASH,
    )
    with store.confirmation_execution_owner(
        HASH,
        running=running,
    ) as (record, owns_execution):
        assert record == running
        assert owns_execution
    return store, running


def _handshake(
    store: LifecycleCloseoutStore,
    attempt_id: str,
) -> dict:
    return build_confirmation_start_handshake(
        confirmation_id="confirmation-atomic",
        execution_key=HASH,
        attempt_id=attempt_id,
        training_meaning_sha256="b" * 64,
        permit_path=store.confirmation_execution_start_permit_path(
            HASH, attempt_id
        ),
        liveness_lock_path=store.confirmation_attempt_liveness_path(
            HASH, attempt_id
        ),
    )


def _request(
    tmp_path: Path,
    *,
    run_id: str,
    handshake: dict,
) -> TrainingRequest:
    data_path = write_mock_training_data(
        output_dir=tmp_path / f"{run_id}-data",
        rows=8,
    )
    return TrainingRequest(
        run_id=run_id,
        data_path=str(data_path),
        model_output_path=str(tmp_path / f"{run_id}.pkl"),
        publication_source="confirmation",
        confirmation_fixed_parameters_json='{"target": {"depth": 1}}',
        confirmation_fixed_features_json='{"target": ["feature"]}',
        confirmation_start_handshake_json=json.dumps(
            handshake,
            sort_keys=True,
            separators=(",", ":"),
        ),
    )


def _run_child(
    request: TrainingRequest,
    *,
    marker: Path,
    permit_callback,
) -> tuple[list, list]:
    started: list = []
    finished: list = []
    runner = SubprocessTrainingRunner(
        extra_args=(
            "--dev-fast",
            "--dev-rows",
            "8",
            "--start-permit-timeout-seconds",
            "0.5",
            "--actual-work-marker-path",
            str(marker),
        )
    )
    runner.start(
        request,
        TrainingExecutionCallbacks(
            started=started.append,
            log=lambda _event: None,
            progress=lambda _event: None,
            finished=finished.append,
            failed=lambda _result: None,
            cancelled=lambda _result: None,
            start_requested=permit_callback,
        ),
    )
    return started, finished


def _temporary_permits(store: LifecycleCloseoutStore) -> tuple[Path, ...]:
    directory = store.confirmation_executions / HASH / "start_attempts"
    return tuple(directory.rglob(".permit.json.publishing-*.tmp"))


@pytest.mark.parametrize("failure_stage", PRECOMMIT_STAGES)
def test_precommit_crash_keeps_final_absent_and_retry_executes_once(
    tmp_path: Path,
    failure_stage: str,
) -> None:
    def fail(stage: str) -> None:
        if stage == failure_stage:
            raise RuntimeError(f"injected {stage}")

    root = tmp_path / failure_stage
    store, running = _ready_store(root, failure_hook=fail)
    first_handshake = _handshake(store, "attempt-first")
    store.register_confirmation_execution_start_attempt(
        HASH,
        handshake=first_handshake,
    )
    first = _request(
        tmp_path,
        run_id=f"first-{failure_stage}",
        handshake=first_handshake,
    )
    first_marker = tmp_path / f"{failure_stage}-first-work"

    with pytest.raises(RuntimeError, match=failure_stage):
        _run_child(
            first,
            marker=first_marker,
            permit_callback=lambda start: (
                store.mark_confirmation_execution_started(
                    HASH,
                    handshake=start.handshake,
                )
            ),
        )

    first_path = Path(first_handshake["permit_path"])
    assert not first_path.exists()
    assert not first_marker.exists()
    assert not Path(first.model_output_path).exists()
    assert _temporary_permits(store)

    recovered = LifecycleCloseoutStore(root)
    replacement_handshake = _handshake(
        recovered,
        "attempt-replacement",
    )
    replacement = _request(
        tmp_path,
        run_id=f"replacement-{failure_stage}",
        handshake=replacement_handshake,
    )
    replacement_marker = tmp_path / f"{failure_stage}-replacement-work"
    with recovered.confirmation_execution_owner(
        HASH,
        running=running,
    ) as (_record, owns_execution):
        assert owns_execution
        recovered.register_confirmation_execution_start_attempt(
            HASH,
            handshake=replacement_handshake,
        )
        started, finished = _run_child(
            replacement,
            marker=replacement_marker,
            permit_callback=lambda start: (
                recovered.mark_confirmation_execution_started(
                    HASH,
                    handshake=start.handshake,
                )
            ),
        )

    assert started == [replacement]
    assert len(finished) == 1
    assert replacement_marker.exists()
    replacement_path = Path(replacement_handshake["permit_path"])
    assert replacement_path.exists()
    recovered.require_confirmation_execution_started(
        HASH, attempt_id="attempt-replacement"
    )
    assert _temporary_permits(recovered)


def test_postcommit_pregrant_crash_abandons_attempt_and_allows_restart(
    tmp_path: Path,
) -> None:
    def fail(stage: str) -> None:
        if stage == "after_final_commit":
            raise RuntimeError("injected after_final_commit")

    root = tmp_path / "postcommit"
    store, running = _ready_store(root, failure_hook=fail)
    handshake = _handshake(store, "attempt-committed")
    store.register_confirmation_execution_start_attempt(
        HASH,
        handshake=handshake,
    )
    request = _request(
        tmp_path,
        run_id="postcommit-first",
        handshake=handshake,
    )
    marker = tmp_path / "postcommit-work"

    with pytest.raises(
        PostRenameDurabilityError,
        match="publication committed",
    ):
        _run_child(
            request,
            marker=marker,
            permit_callback=lambda start: (
                store.mark_confirmation_execution_started(
                    HASH,
                    handshake=start.handshake,
                )
            ),
        )

    final_path = Path(handshake["permit_path"])
    assert final_path.exists()
    assert not marker.exists()
    reconstructed = LifecycleCloseoutStore(root)
    reconstructed.require_confirmation_execution_started(
        HASH, attempt_id="attempt-committed"
    )
    with reconstructed.confirmation_execution_owner(
        HASH,
        running=running,
    ) as (record, owns_execution):
        assert record == running
        assert owns_execution
    abandoned = (
        reconstructed.confirmation_executions
        / HASH
        / "start_attempts"
        / "attempt-committed"
        / "abandoned.json"
    )
    assert abandoned.exists()


def test_live_child_fence_blocks_replacement_until_process_termination(
    tmp_path: Path,
) -> None:
    root = tmp_path / "live-child"
    store, running = _ready_store(root)
    first_handshake = _handshake(store, "attempt-live")
    store.register_confirmation_execution_start_attempt(
        HASH,
        handshake=first_handshake,
    )
    first = _request(
        tmp_path,
        run_id="live-child-first",
        handshake=first_handshake,
    )
    requested = Event()
    terminate_parent = Event()

    def parent_waits_before_grant(_start_request):  # noqa: ANN202
        requested.set()
        assert terminate_parent.wait(timeout=5)
        raise RuntimeError("injected parent termination")

    with ThreadPoolExecutor(max_workers=1) as pool:
        first_future = pool.submit(
            _run_child,
            first,
            marker=tmp_path / "live-child-first-work",
            permit_callback=parent_waits_before_grant,
        )
        assert requested.wait(timeout=5)
        reconstructed = LifecycleCloseoutStore(root)
        with reconstructed.confirmation_execution_owner(
            HASH,
            running=running,
        ) as (record, owns_execution):
            assert record == running
            assert not owns_execution
        assert not tuple(
            reconstructed.confirmation_executions.glob(
                "*/start_attempts/*/abandoned.json"
            )
        )
        terminate_parent.set()
        with pytest.raises(RuntimeError, match="parent termination"):
            first_future.result(timeout=5)

    replacement_handshake = _handshake(
        reconstructed,
        "attempt-replacement",
    )
    replacement = _request(
        tmp_path,
        run_id="live-child-replacement",
        handshake=replacement_handshake,
    )
    replacement_marker = tmp_path / "live-child-replacement-work"
    with reconstructed.confirmation_execution_owner(
        HASH,
        running=running,
    ) as (record, owns_execution):
        assert record == running
        assert owns_execution
        reconstructed.register_confirmation_execution_start_attempt(
            HASH,
            handshake=replacement_handshake,
        )
        started, finished = _run_child(
            replacement,
            marker=replacement_marker,
            permit_callback=lambda start: (
                reconstructed.mark_confirmation_execution_started(
                    HASH,
                    handshake=start.handshake,
                )
            ),
        )

    assert started == [replacement]
    assert len(finished) == 1
    assert replacement_marker.exists()
    abandoned = tuple(
        reconstructed.confirmation_executions.glob(
            "*/start_attempts/*/abandoned.json"
        )
    )
    assert len(abandoned) == 1


def test_consumed_locked_seal_terminates_confirmation_after_child_exit(
    tmp_path: Path,
) -> None:
    root = tmp_path / "locked-abandon"
    root.mkdir(parents=True)
    store = LifecycleCloseoutStore(root)
    seal = build_locked_final_test(
        data_sha256="c" * 64,
        ordered_membership_sha256="d" * 64,
        target_identities=["target-a"],
        split_policy="external holdout",
        created_at=NOW,
        creation_identity="preselection",
        evaluation_contract={
            "metric_contract": "e" * 64,
            "schema_contract": "f" * 64,
        },
        required_source_hashes={"snapshot": "1" * 64},
        dataset_reference={
            "path": str(tmp_path / "locked.csv"),
            "sha256": "c" * 64,
        },
        created_before_selection=True,
    )
    store.write_locked_final_test(seal)
    locked_projection = {
        "configured": True,
        "seal_id": seal["seal_id"],
        "schema_version": seal["schema_version"],
        "status": "sealed",
        "independent_final_test_passed": False,
    }
    pending = build_confirmation_record(
        confirmation_id="confirmation-atomic",
        snapshot_id="snapshot-atomic",
        selected_candidate_id="candidate-source",
        status="confirmation_pending",
        created_at=NOW,
        updated_at=NOW,
        production_required_targets=["target-a"],
        execution_key=HASH,
        locked_final_test=locked_projection,
    )
    store.claim_confirmation_execution(
        HASH,
        requested_confirmation_id=None,
        pending=pending,
    )
    running = build_confirmation_record(
        confirmation_id="confirmation-atomic",
        snapshot_id="snapshot-atomic",
        selected_candidate_id="candidate-source",
        status="confirmation_running",
        created_at=NOW,
        updated_at=LATER,
        production_required_targets=["target-a"],
        execution_key=HASH,
        locked_final_test=locked_projection,
    )
    with store.confirmation_execution_owner(
        HASH,
        running=running,
    ) as (_record, owns_execution):
        assert owns_execution
        handshake = _handshake(store, "attempt-locked")
        store.register_confirmation_execution_start_attempt(
            HASH,
            handshake=handshake,
        )
        store.mark_confirmation_execution_started(
            HASH,
            handshake=handshake,
        )
    store.consume_locked_final_test(
        seal["seal_id"],
        confirmation_id="confirmation-atomic",
        consumed_at=LATER,
    )

    reconstructed = LifecycleCloseoutStore(root)
    with reconstructed.confirmation_execution_owner(
        HASH,
        running=running,
    ) as (record, owns_execution):
        assert not owns_execution
        assert record["status"] == "abandoned"
        assert record["confirmation_candidate_id"] is None
    with reconstructed.confirmation_execution_owner(
        HASH,
        running=running,
    ) as (replay, owns_execution):
        assert not owns_execution
        assert replay == record
    assert (
        reconstructed.read_locked_final_test(seal["seal_id"])["status"]
        == "consumed"
    )
    assert not (root / "candidates").exists()


def test_corrupt_attempt_liveness_identity_blocks_recovery(
    tmp_path: Path,
) -> None:
    root = tmp_path / "corrupt-liveness"
    store, running = _ready_store(root)
    handshake = _handshake(store, "attempt-corrupt-liveness")
    store.register_confirmation_execution_start_attempt(
        HASH,
        handshake=handshake,
    )
    attempt_path = (
        store.confirmation_executions
        / HASH
        / "start_attempts"
        / handshake["attempt_id"]
        / "attempt.json"
    )
    corrupt = json.loads(attempt_path.read_text(encoding="utf-8"))
    corrupt["liveness_lock_path"] = str(
        root / ".confirmation-attempt-corrupt.lock"
    )
    meaning = {
        key: value
        for key, value in corrupt.items()
        if key != "handshake_sha256"
    }
    corrupt["handshake_sha256"] = content_sha256(meaning)
    attempt_path.write_text(
        json.dumps(corrupt, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    before = attempt_path.read_bytes()

    with pytest.raises(ValueError, match="liveness identity is corrupt"):
        with LifecycleCloseoutStore(root).confirmation_execution_owner(
            HASH,
            running=running,
        ):
            pass

    assert attempt_path.read_bytes() == before
    assert not tuple(
        store.confirmation_executions.glob(
            "*/start_attempts/*/abandoned.json"
        )
    )


def test_concurrent_exact_publication_commits_once(
    tmp_path: Path,
) -> None:
    commits: list[str] = []
    store, _running = _ready_store(
        tmp_path / "exact",
        failure_hook=lambda stage: (
            commits.append(stage) if stage == "after_final_commit" else None
        ),
    )
    handshake = _handshake(store, "attempt-exact")
    store.register_confirmation_execution_start_attempt(
        HASH,
        handshake=handshake,
    )

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = tuple(
            pool.map(
                lambda _index: store.mark_confirmation_execution_started(
                    HASH,
                    handshake=handshake,
                ),
                range(2),
            )
        )

    assert outcomes[0] == outcomes[1]
    assert outcomes[0]["attempt_id"] == "attempt-exact"
    assert commits == ["after_final_commit"]
    store.require_confirmation_execution_started(
        HASH, attempt_id="attempt-exact"
    )
    assert not _temporary_permits(store)


def test_conflicting_concurrent_publication_fails_closed(
    tmp_path: Path,
) -> None:
    store, _running = _ready_store(tmp_path / "conflict")
    first = _handshake(store, "attempt-first")
    second = _handshake(store, "attempt-second")
    store.register_confirmation_execution_start_attempt(
        HASH, handshake=first
    )
    with pytest.raises(
        ValueError, match="already has one active attempt"
    ):
        store.register_confirmation_execution_start_attempt(
            HASH, handshake=second
        )
    store.mark_confirmation_execution_started(HASH, handshake=first)
    with pytest.raises((FileNotFoundError, ValueError)):
        store.mark_confirmation_execution_started(HASH, handshake=second)
    store.require_confirmation_execution_started(
        HASH, attempt_id="attempt-first"
    )


def test_committed_permit_tamper_is_preserved_and_fails_closed(
    tmp_path: Path,
) -> None:
    store, _running = _ready_store(tmp_path / "tamper")
    handshake = _handshake(store, "attempt-tamper")
    store.register_confirmation_execution_start_attempt(
        HASH,
        handshake=handshake,
    )
    store.mark_confirmation_execution_started(
        HASH,
        handshake=handshake,
    )
    final_path = Path(handshake["permit_path"])
    permit = json.loads(final_path.read_text(encoding="utf-8"))
    permit["attempt_id"] = "attempt-corrupt"
    final_path.write_text(
        json.dumps(permit, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    before = final_path.read_bytes()

    with pytest.raises(ValueError, match="evidence is corrupt"):
        store.require_confirmation_execution_started(
            HASH, attempt_id="attempt-tamper"
        )
    with pytest.raises(
        ValueError,
        match="execution-start evidence is corrupt",
    ):
        store.mark_confirmation_execution_started(
            HASH,
            handshake=handshake,
        )

    assert final_path.read_bytes() == before
