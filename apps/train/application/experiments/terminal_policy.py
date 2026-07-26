"""Phase 5F exploratory terminal policy before Candidate publication."""

from __future__ import annotations

from dataclasses import replace


def apply_exploratory_terminal_policy(
    request, terminal: str, result, failure_stage: str, failure_reason: str  # noqa: ANN001
):
    if (
        terminal != "finished"
        or request is None
        or not request.target_scoped_exploratory
    ):
        return terminal, result, failure_stage, failure_reason
    reason = "Target-scoped exploratory training cannot publish a Candidate."
    return (
        "failed",
        replace(
            result,
            status="partial",
            message=reason,
            candidate_id=request.candidate_id,
            publication_outcome="partial",
        ),
        "target_scoped_exploration",
        reason,
    )
