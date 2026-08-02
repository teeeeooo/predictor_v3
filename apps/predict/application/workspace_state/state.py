"""Qt-independent Layout B workspace state and terminal reveal policy."""

from __future__ import annotations

from enum import Enum
from typing import Iterable

from apps.predict.application.prediction_usecase import PredictionRunSummary


class WorkspaceSurface(str, Enum):
    """The two full-area surfaces owned by Predict."""

    INPUT = "input"
    RESULT = "result"


class PredictWorkspaceState:
    """Own shared surface/case state without retaining case or result rows."""

    def __init__(self) -> None:
        self._current_surface = WorkspaceSurface.INPUT
        self._selected_case_id: str | None = None
        self._run_active = False
        self._run_start_surface: WorkspaceSurface | None = None
        self._run_user_surface_choice: WorkspaceSurface | None = None

    @property
    def current_surface(self) -> WorkspaceSurface:
        return self._current_surface

    @property
    def selected_case_id(self) -> str | None:
        return self._selected_case_id

    @property
    def run_active(self) -> bool:
        return self._run_active

    @property
    def run_start_surface(self) -> WorkspaceSurface | None:
        return self._run_start_surface

    @property
    def run_user_surface_choice(self) -> WorkspaceSurface | None:
        return self._run_user_surface_choice

    def choose_surface(
        self,
        surface: WorkspaceSurface,
        *,
        user_initiated: bool = True,
    ) -> None:
        """Select a surface and remember an explicit choice for the active run."""
        resolved = WorkspaceSurface(surface)
        self._current_surface = resolved
        if self._run_active and user_initiated:
            self._run_user_surface_choice = resolved

    def select_case(self, case_id: str | None, case_ids: Iterable[str]) -> None:
        """Set the shared stable identity only when it belongs to this session."""
        available = tuple(case_ids)
        if case_id is not None and case_id not in available:
            raise ValueError("selected case_id must belong to the Predict session")
        self._selected_case_id = case_id

    def reconcile_case_ids(self, case_ids: Iterable[str]) -> str | None:
        """Remove dangling selection, preferring the first canonical case."""
        available = tuple(case_ids)
        if self._selected_case_id not in available:
            self._selected_case_id = available[0] if available else None
        return self._selected_case_id

    def begin_run(self) -> None:
        """Capture the visible surface and reset prior run-local choices."""
        self._run_active = True
        self._run_start_surface = self._current_surface
        self._run_user_surface_choice = None

    def abort_run(self) -> None:
        """Discard run-local state when execution cannot start."""
        self._clear_run_state()

    def finish_run(self, summary: PredictionRunSummary) -> bool:
        """Apply the one terminal auto-reveal decision and return whether it moved."""
        if not self._run_active:
            return False
        previous = self._current_surface
        successful = summary.complete + summary.partial
        validation_only = (
            summary.invalid > 0
            and summary.invalid == summary.total
            and not successful
            and summary.error == 0
            and summary.cancelled == 0
        )
        if validation_only:
            self._current_surface = WorkspaceSurface.INPUT
        elif (
            successful > 0
            and self._run_user_surface_choice is not WorkspaceSurface.INPUT
        ):
            self._current_surface = WorkspaceSurface.RESULT
        self._clear_run_state()
        return previous is not self._current_surface

    def _clear_run_state(self) -> None:
        self._run_active = False
        self._run_start_surface = None
        self._run_user_surface_choice = None
