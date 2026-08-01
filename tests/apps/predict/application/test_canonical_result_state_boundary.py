"""Characterization matrix for the canonical Predict result-state boundary."""

from dataclasses import replace

import pytest

from apps.predict.application.result_contract import (
    PredictionExecutionContext,
    PredictionModelIdentity,
    execution_semantics_from_runtime,
)
from apps.predict.application.runtime_snapshot import (
    compatibility_predict_runtime_snapshot,
)
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_state_boundary import PredictSessionProjection
from apps.predict.state.result_row import ResultRow
from tests.helpers.predict_results import accept_result_fixtures


def _session(count=1):  # noqa: ANN202
    session = PredictSession(session_id="canonical-state-boundary")
    session.case_store.append_empty_rows(count)
    return session


def _state(session):  # noqa: ANN001, ANN202
    return (
        session.revision,
        tuple(
            (
                case_id,
                dict(session.case_store.get_case(case_id).input_values),
                dict(session.case_store.get_case(case_id).autofill_values),
                set(session.case_store.get_case(case_id).dirty_fields),
                session.case_store.get_case(case_id).input_revision,
            )
            for case_id in session.case_order
        ),
        dict(session.results_by_case_id),
        tuple(
            (case_id, session.allowed_context_for_case(case_id))
            for case_id in session.case_order
        ),
    )


def _case_rows(session):  # noqa: ANN001, ANN202
    return tuple(
        (
            case_id,
            dict(case.input_values),
            dict(case.autofill_values),
            set(case.dirty_fields),
            case.input_revision,
        )
        for case_id in session.case_order
        for case in (session.case_store.get_case(case_id),)
    )


def test_result_view_cannot_mutate_canonical_storage():
    session = _session()
    case_id = session.case_order[0]

    with pytest.raises(TypeError):
        session.results_by_case_id[case_id] = ResultRow(case_id, "complete")

    assert session.results_by_case_id == {}


@pytest.mark.parametrize("method", ("apply", "restore"))
def test_caller_constructed_projection_cannot_install_malformed_terminal(method):
    session = _session()
    case_id = session.case_order[0]
    snapshot = session.snapshot_runtime_projection()
    malformed = PredictSessionProjection(
        snapshot.case_order,
        snapshot.cases,
        (ResultRow(case_id, "complete"),),
    )
    before = _state(session)

    with pytest.raises(ValueError, match="not issued"):
        if method == "apply":
            session.apply_runtime_projection(
                malformed, expected_revision=session.revision
            )
        else:
            session.restore_runtime_projection(malformed)

    assert _state(session) == before
    assert session.summary_counts()["completed"] == 0


def test_tampered_snapshot_is_rejected_atomically_before_rollback_mutation():
    runtime = compatibility_predict_runtime_snapshot()
    session = _session(2)
    first, second = session.case_order
    accepted = accept_result_fixtures(
        session, ResultRow(first, "complete", {"cooling_power": "12.5"})
    )[0]
    semantics = accepted.execution_context.semantics
    model = accepted.execution_context.model
    allowed = PredictionExecutionContext(
        session.session_id,
        second,
        "still-allowed",
        session.case_store.get_case(second).input_revision,
        semantics,
        model,
    )
    session.allow_result(allowed, runtime.target_descriptors)
    snapshot = session.snapshot_runtime_projection()
    forged = replace(
        snapshot,
        results=(ResultRow(first, "complete"),),
    )
    before = _state(session)

    with pytest.raises(ValueError, match="not issued"):
        session.restore_runtime_projection(forged)

    assert _state(session) == before
    assert session.result_for_case(first) == accepted
    assert session.allowed_context_for_case(second) == allowed


@pytest.mark.parametrize(
    "malformed",
    (
        ResultRow("case-0001", "complete"),
        ResultRow("case-0001", "partial"),
        ResultRow("case-0001", "error", message="legacy error"),
        ResultRow("case-0001", "cancelled", message="legacy cancellation"),
        ResultRow("case-0001", "mystery"),
    ),
)
def test_migration_preparation_rejects_malformed_or_unknown_state(malformed):
    runtime = compatibility_predict_runtime_snapshot()
    session = _session()
    snapshot = session.snapshot_runtime_projection()
    before = _state(session)

    with pytest.raises(ValueError):
        session.prepare_runtime_projection(
            cases=snapshot.cases,
            results=(malformed,),
            runtime_snapshot=runtime,
            model_identity=PredictionModelIdentity(
                "candidate", 1, runtime.generation_id
            ),
        )

    assert _state(session) == before


@pytest.mark.parametrize("status", ("pending", "running", "invalid"))
def test_non_executed_state_migrates_only_through_validated_projection(status):
    runtime = compatibility_predict_runtime_snapshot()
    session = _session()
    case_id = session.case_order[0]
    state = ResultRow(case_id, status, message="non-executed")
    session.set_result(state)
    snapshot = session.snapshot_runtime_projection()
    prepared = session.prepare_runtime_projection(
        cases=snapshot.cases,
        results=(state,),
        runtime_snapshot=runtime,
        model_identity=PredictionModelIdentity(
            "candidate", 1, runtime.generation_id
        ),
    )

    session.apply_runtime_projection(prepared, expected_revision=session.revision)

    assert session.result_for_case(case_id) == state


def test_valid_rollback_restores_exact_results_revision_and_run_authority():
    runtime = compatibility_predict_runtime_snapshot()
    session = _session(2)
    first, second = session.case_order
    accepted = accept_result_fixtures(
        session, ResultRow(first, "partial", {"cooling_power": "7.25"})
    )[0]
    semantics = accepted.execution_context.semantics
    model = accepted.execution_context.model
    allowed = PredictionExecutionContext(
        session.session_id,
        second,
        "rollback-authority",
        session.case_store.get_case(second).input_revision,
        semantics,
        model,
    )
    session.allow_result(allowed, runtime.target_descriptors)
    snapshot = session.snapshot_runtime_projection()
    expected = _state(session)

    session.case_store.get_case(first).set_input_value("cooling_capa", 999)
    session.revoke_run(allowed.run_id)
    session.clear_result(first)
    session.restore_runtime_projection(snapshot)

    assert _state(session) == expected
    assert session.result_for_case(first) == accepted
    assert session.allowed_context_for_case(second) == allowed


@pytest.mark.parametrize(
    "template",
    (
        ResultRow("case-0001", "complete", {"cooling_power": "10.125"}),
        ResultRow("case-0001", "partial", {"cooling_power": "10.125"}),
        ResultRow("case-0001", "error", {"cooling_power": "target failed"}),
        ResultRow("case-0001", "error", message="infrastructure failed"),
        ResultRow("case-0001", "cancelled", message="cancelled"),
    ),
)
def test_all_valid_terminal_families_migrate_through_sealed_projection(template):
    runtime = compatibility_predict_runtime_snapshot()
    session = _session()
    accepted = accept_result_fixtures(session, template)[0]
    snapshot = session.snapshot_runtime_projection()
    prepared = session.prepare_runtime_projection(
        cases=snapshot.cases,
        results=(accepted,),
        runtime_snapshot=runtime,
        model_identity=accepted.execution_context.model,
    )

    session.apply_runtime_projection(prepared, expected_revision=session.revision)

    assert session.result_for_case(template.case_id) == accepted


def test_projection_cannot_keep_result_current_after_case_revision_change():
    runtime = compatibility_predict_runtime_snapshot()
    session = _session()
    case_id = session.case_order[0]
    accepted = accept_result_fixtures(
        session, ResultRow(case_id, "complete", {"cooling_power": "8.5"})
    )[0]
    snapshot = session.snapshot_runtime_projection()
    changed_cases = tuple(
        (
            item[0],
            item[1],
            item[2],
            item[3],
            item[4] + 1,
        )
        for item in snapshot.cases
    )
    before = _state(session)

    with pytest.raises(ValueError, match="input_revision_changed"):
        session.prepare_runtime_projection(
            cases=changed_cases,
            results=(accepted,),
            runtime_snapshot=runtime,
            model_identity=accepted.execution_context.model,
        )

    assert _state(session) == before


def test_sealed_projection_detects_in_place_payload_tampering_atomically():
    runtime = compatibility_predict_runtime_snapshot()
    session = _session()
    snapshot = session.snapshot_runtime_projection()
    prepared = session.prepare_runtime_projection(
        cases=snapshot.cases,
        results=(),
        runtime_snapshot=runtime,
        model_identity=PredictionModelIdentity(
            "candidate", 1, runtime.generation_id
        ),
    )
    prepared.cases[0][1]["injected"] = "forbidden"
    before = _state(session)

    with pytest.raises(ValueError, match="not issued"):
        session.apply_runtime_projection(
            prepared, expected_revision=session.revision
        )

    assert _state(session) == before


def test_issued_artifact_rejects_wrong_session_and_wrong_lifecycle_kind():
    runtime = compatibility_predict_runtime_snapshot()
    owner = _session()
    other = _session()
    snapshot = owner.snapshot_runtime_projection()
    migration = owner.prepare_runtime_projection(
        cases=_case_rows(owner),
        results=(),
        runtime_snapshot=runtime,
        model_identity=PredictionModelIdentity(
            "candidate", 1, runtime.generation_id
        ),
    )

    with pytest.raises(ValueError, match="not issued"):
        other.restore_runtime_projection(snapshot)
    with pytest.raises(ValueError, match="not issued"):
        owner.apply_runtime_projection(
            snapshot, expected_revision=owner.revision
        )
    with pytest.raises(ValueError, match="not issued"):
        owner.restore_runtime_projection(migration)

    assert owner.issued_projection_count == 2
    assert owner.release_runtime_projection(snapshot, kind="snapshot")
    assert owner.release_runtime_projection(migration, kind="migration")
    assert owner.issued_projection_count == 0


def test_clear_and_remove_delete_state_without_creating_terminal_results():
    session = _session(2)
    first, second = session.case_order
    accept_result_fixtures(
        session,
        ResultRow(first, "complete"),
        ResultRow(second, "cancelled", message="cancelled"),
    )

    session.clear_result(first)
    session.remove_results_for_cases([second])
    session.case_store.remove_rows([second])

    assert session.results_by_case_id == {}
    assert session.summary_counts()["completed"] == 0
    assert session.summary_counts()["cancelled"] == 0


@pytest.mark.parametrize(
    "runtime_mutation",
    (
        lambda runtime: replace(runtime, target_descriptors=()),
        lambda runtime: replace(
            runtime,
            target_descriptors=(
                runtime.target_descriptors[0],
                replace(
                    runtime.target_descriptors[1],
                    target_identity=runtime.target_descriptors[0].target_identity,
                ),
                *runtime.target_descriptors[2:],
            ),
        ),
        lambda runtime: replace(
            runtime,
            target_descriptors=(
                replace(runtime.target_descriptors[0], canonical_unit=""),
                *runtime.target_descriptors[1:],
            ),
        ),
        lambda runtime: replace(runtime, active_targets=("incomplete",)),
        lambda runtime: replace(
            runtime, target_result_keys=((runtime.active_targets[0], "wrong"),)
        ),
    ),
)
def test_zero_result_migration_rejects_invalid_destination_contract_before_issue(
    runtime_mutation,
):
    runtime = compatibility_predict_runtime_snapshot()
    session = _session()
    case_id = session.case_order[0]
    semantics = execution_semantics_from_runtime(runtime)
    model = PredictionModelIdentity("candidate", 1, runtime.generation_id)
    context = PredictionExecutionContext(
        session.session_id,
        case_id,
        "before-invalid-migration",
        0,
        semantics,
        model,
    )
    session.allow_result(context, runtime.target_descriptors)
    session.revoke_run(context.run_id)
    before = _state(session)

    with pytest.raises(ValueError, match="Predict .*Target|Predict Target"):
        session.prepare_runtime_projection(
            cases=_case_rows(session),
            results=(),
            runtime_snapshot=runtime_mutation(runtime),
            model_identity=model,
        )

    assert _state(session) == before
    assert session.issued_projection_count == 0
    next_context = replace(context, run_id="valid-next-run")
    session.allow_result(next_context, runtime.target_descriptors)
    assert session.allowed_context_for_case(case_id) == next_context


def test_zero_result_migration_accepts_one_complete_runtime_contract():
    runtime = compatibility_predict_runtime_snapshot()
    session = _session()
    model = PredictionModelIdentity("candidate", 1, runtime.generation_id)

    projection = session.prepare_runtime_projection(
        cases=_case_rows(session),
        results=(),
        runtime_snapshot=runtime,
        model_identity=model,
    )

    assert session.issued_projection_count == 1
    session.apply_runtime_projection(projection, expected_revision=session.revision)
    assert session.issued_projection_count == 0
    assert session.results_by_case_id == {}


def test_direct_case_removal_atomically_cleans_result_and_run_authority():
    runtime = compatibility_predict_runtime_snapshot()
    session = _session(3)
    completed, running, unrelated = session.case_order
    accepted, preserved = accept_result_fixtures(
        session,
        ResultRow(completed, "complete", {"cooling_power": "12.5"}),
        ResultRow(unrelated, "cancelled", message="preserve unrelated"),
    )
    context = PredictionExecutionContext(
        session.session_id,
        running,
        "remove-running",
        session.case_store.get_case(running).input_revision,
        accepted.execution_context.semantics,
        accepted.execution_context.model,
    )
    session.allow_result(context, runtime.target_descriptors)
    session.set_result(ResultRow(running, "running"))
    unrelated_revision = session.case_store.get_case(unrelated).input_revision
    before_revision = session.revision

    removed = session.case_store.remove_rows((completed, running))

    assert removed == [completed, running]
    assert set(session.results_by_case_id) == {unrelated}
    assert session.result_for_case(unrelated) == preserved
    assert session.allowed_context_for_case(running) is None
    assert session.case_store.get_case(unrelated).input_revision == unrelated_revision
    assert session.revision == before_revision + 1
    counts = session.summary_counts()
    assert counts["total"] == 1
    assert sum(counts[key] for key in ("completed", "errors", "cancelled")) <= 1


def test_case_removal_callback_failure_leaves_canonical_state_unchanged(monkeypatch):
    session = _session(2)
    case_id = session.case_order[0]
    accept_result_fixtures(session, ResultRow(case_id, "complete"))
    before = _state(session)

    def fail_before_cleanup(_case_ids):  # noqa: ANN001
        raise RuntimeError("injected removal failure")

    monkeypatch.setattr(session, "_remove_case_dependencies", fail_before_cleanup)
    with pytest.raises(RuntimeError, match="injected removal failure"):
        session.case_store.remove_rows((case_id,))

    assert _state(session) == before
