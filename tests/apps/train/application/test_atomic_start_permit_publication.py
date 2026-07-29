"""Crash-window regressions for atomic confirmation start permits."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from apps.common.model_lifecycle.closeout.contracts import (
    build_confirmation_record,
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
        permit_path=store.confirmation_execution_start_permit_path(HASH),
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
    directory = store.confirmation_execution_start_permit_path(HASH).parent
    return tuple(directory.glob(".execution_started.json.publishing-*.tmp"))


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

    final_path = store.confirmation_execution_start_permit_path(HASH)
    assert not final_path.exists()
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
    assert final_path.exists()
    recovered.require_confirmation_execution_started(HASH)
    assert _temporary_permits(recovered)


def test_postcommit_crash_leaves_complete_permit_and_blocks_retry(
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

    final_path = store.confirmation_execution_start_permit_path(HASH)
    assert final_path.exists()
    assert not marker.exists()
    reconstructed = LifecycleCloseoutStore(root)
    reconstructed.require_confirmation_execution_started(HASH)
    with reconstructed.confirmation_execution_owner(
        HASH,
        running=running,
    ) as (record, owns_execution):
        assert record == running
        assert not owns_execution


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

    assert outcomes == (None, None)
    assert commits == ["after_final_commit"]
    store.require_confirmation_execution_started(HASH)
    assert not _temporary_permits(store)


def test_conflicting_concurrent_publication_fails_closed(
    tmp_path: Path,
) -> None:
    store, _running = _ready_store(tmp_path / "conflict")
    first = _handshake(store, "attempt-first")
    second = _handshake(store, "attempt-second")
    for handshake in (first, second):
        store.register_confirmation_execution_start_attempt(
            HASH,
            handshake=handshake,
        )

    def publish(handshake: dict):  # noqa: ANN202
        try:
            store.mark_confirmation_execution_started(
                HASH,
                handshake=handshake,
            )
            return "published"
        except ValueError:
            return "blocked"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = tuple(pool.map(publish, (first, second)))

    assert sorted(outcomes) == ["blocked", "published"]
    store.require_confirmation_execution_started(HASH)


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
    final_path = store.confirmation_execution_start_permit_path(HASH)
    permit = json.loads(final_path.read_text(encoding="utf-8"))
    permit["attempt_id"] = "attempt-corrupt"
    final_path.write_text(
        json.dumps(permit, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    before = final_path.read_bytes()

    with pytest.raises(ValueError, match="evidence is corrupt"):
        store.require_confirmation_execution_started(HASH)
    with pytest.raises(
        ValueError,
        match="execution-start evidence conflict",
    ):
        store.mark_confirmation_execution_started(
            HASH,
            handshake=handshake,
        )

    assert final_path.read_bytes() == before
