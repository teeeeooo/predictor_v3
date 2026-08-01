"""Qt-free Predict Layout B workspace policy tests."""

import pytest

from apps.predict.application.prediction_usecase import PredictionRunSummary
from apps.predict.application.workspace_state import (
    PredictWorkspaceState,
    WorkspaceSurface,
)


def _summary(
    *,
    complete: int = 0,
    partial: int = 0,
    error: int = 0,
    invalid: int = 0,
    cancelled: int = 0,
) -> PredictionRunSummary:
    return PredictionRunSummary(
        total=complete + partial + error + invalid + cancelled,
        complete=complete,
        partial=partial,
        error=error,
        invalid=invalid,
        cancelled=cancelled,
    )


def test_initial_surface_and_stable_case_reconciliation_are_canonical_ordered():
    state = PredictWorkspaceState()

    assert state.current_surface is WorkspaceSurface.INPUT
    assert state.reconcile_case_ids(("case-b", "case-a")) == "case-b"
    state.select_case("case-a", ("case-b", "case-a"))
    assert state.reconcile_case_ids(("case-a",)) == "case-a"
    assert state.reconcile_case_ids(("case-b",)) == "case-b"
    assert state.reconcile_case_ids(()) is None

    with pytest.raises(ValueError, match="belong"):
        state.select_case("deleted", ("case-b",))


@pytest.mark.parametrize(
    "summary",
    (_summary(complete=1), _summary(partial=1)),
)
def test_terminal_success_reveals_result_once(summary: PredictionRunSummary):
    state = PredictWorkspaceState()
    state.begin_run()

    assert state.run_start_surface is WorkspaceSurface.INPUT
    assert state.finish_run(summary)
    assert state.current_surface is WorkspaceSurface.RESULT
    assert not state.finish_run(summary)


@pytest.mark.parametrize(
    "summary",
    (
        _summary(error=1),
        _summary(cancelled=1),
        _summary(error=1, invalid=1),
    ),
)
def test_terminal_without_complete_or_partial_does_not_force_result(
    summary: PredictionRunSummary,
):
    state = PredictWorkspaceState()
    state.begin_run()

    assert not state.finish_run(summary)
    assert state.current_surface is WorkspaceSurface.INPUT


def test_validation_only_run_returns_to_input_but_run_start_never_forces_it():
    state = PredictWorkspaceState()
    state.choose_surface(WorkspaceSurface.RESULT)
    state.begin_run()

    assert state.current_surface is WorkspaceSurface.RESULT
    assert state.run_start_surface is WorkspaceSurface.RESULT
    assert state.finish_run(_summary(invalid=2))
    assert state.current_surface is WorkspaceSurface.INPUT


def test_explicit_input_during_run_suppresses_reveal_and_next_run_resets_choice():
    state = PredictWorkspaceState()
    state.begin_run()
    state.choose_surface(WorkspaceSurface.RESULT)
    state.choose_surface(WorkspaceSurface.INPUT)

    assert state.run_user_surface_choice is WorkspaceSurface.INPUT
    assert not state.finish_run(_summary(complete=1))
    assert state.current_surface is WorkspaceSurface.INPUT

    state.begin_run()
    assert state.run_user_surface_choice is None
    assert state.finish_run(_summary(complete=1))
    assert state.current_surface is WorkspaceSurface.RESULT


def test_progressive_phase_and_abort_do_not_change_surface():
    state = PredictWorkspaceState()
    state.begin_run()

    assert state.current_surface is WorkspaceSurface.INPUT
    assert state.run_active
    state.abort_run()
    assert state.current_surface is WorkspaceSurface.INPUT
    assert not state.run_active
