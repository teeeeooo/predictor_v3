"""Port contracts for fixed-meaning confirmation execution."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class FrozenConfirmationRequest:
    confirmation_id: str
    snapshot_id: str
    selected_candidate_id: str
    resolved_specification: dict[str, Any]
    production_required_targets: tuple[str, ...]
    selected_parameters: dict[str, dict[str, Any]]
    training_data: dict[str, Any]
    definition_runtime: dict[str, Any]
    evaluation_contract: dict[str, Any]
    execution_key: str = ""
    start_attempt_id: str = ""
    start_permit_path: str = ""
    locked_final_test: dict[str, Any] | None = None
    prepublication_integrity: Callable[[], None] | None = None
    execution_start_prepare: (
        Callable[[str], dict[str, Any]] | None
    ) = None
    execution_start_permit: (
        Callable[[dict[str, Any]], dict[str, Any]] | None
    ) = None


@dataclass(frozen=True)
class ConfirmationExecutionResult:
    status: str
    target_results: tuple[dict[str, Any], ...] = ()
    confirmation_candidate_id: str = ""
    message: str = ""
    reason_code: str = ""
    independent_final_test_passed: bool = False
    locked_final_test_result: dict[str, Any] | None = None


class ConfirmationExecutionPort(Protocol):
    """Must publish through TrainingLifecycle/CandidatePublisher with no search."""

    def execute(
        self, request: FrozenConfirmationRequest
    ) -> ConfirmationExecutionResult: ...
