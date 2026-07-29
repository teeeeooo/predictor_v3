"""Parser, output envelope, and exit contract for the headless adapter."""

from __future__ import annotations

import argparse
import json
from uuid import uuid4

from apps.train.application.experiments.contracts import (
    EXPERIMENT_OUTPUT_VERSION,
    ExperimentContractError,
)

EXIT_SUCCESS = 0
EXIT_VALIDATION = 2
EXIT_LOCK_CONFLICT = 3
EXIT_CANCELLED = 4
EXIT_PARTIAL = 5
EXIT_TRAINING_FAILURE = 6
EXIT_INTERNAL = 70


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Versioned machine-readable headless Experiment interface."
    )
    subcommands = root.add_subparsers(dest="command", required=True)
    for name in ("validate", "resolve"):
        command = subcommands.add_parser(name)
        command.add_argument("specification")
    run = subcommands.add_parser("run")
    run.add_argument("specification")
    run.add_argument("--run-id")
    for name in ("run-status", "run-result", "run-logs", "run-artifacts"):
        command = subcommands.add_parser(name)
        command.add_argument("run_id")
    start = subcommands.add_parser("campaign-start")
    start.add_argument("specification")
    start.add_argument("--campaign-id", default=f"campaign-{uuid4().hex}")
    create = subcommands.add_parser("campaign-create")
    create.add_argument("definition")
    create.add_argument("--campaign-id", default=f"campaign-{uuid4().hex}")
    submit = subcommands.add_parser("campaign-proposal-submit")
    submit.add_argument("campaign_id")
    submit.add_argument("proposal")
    execute = subcommands.add_parser("campaign-execute")
    execute.add_argument("campaign_id")
    execute.add_argument("proposal_id")
    extend = subcommands.add_parser("campaign-budget-extend")
    extend.add_argument("campaign_id")
    extend.add_argument("new_total", type=int)
    extend.add_argument("--operator-reference", required=True)
    recommend = subcommands.add_parser("campaign-recommendation-create")
    recommend.add_argument("campaign_id")
    recommend.add_argument("--recommendation-id")
    recommendation = subcommands.add_parser("campaign-recommendation")
    recommendation.add_argument("campaign_id")
    recommendation.add_argument("recommendation_id")
    complete = subcommands.add_parser("campaign-complete")
    complete.add_argument("campaign_id")
    complete.add_argument("--without-recommendation", action="store_true")
    for name in (
        "campaign-status",
        "campaign-pause",
        "campaign-cancel",
        "campaign-resume",
        "campaign-budget",
        "campaign-leaderboard",
        "campaign-incumbent",
    ):
        command = subcommands.add_parser(name)
        command.add_argument("campaign_id")
    subcommands.add_parser("lock-status")
    subcommands.add_parser("models")
    for name in ("snapshot-preflight", "snapshot-freeze"):
        command = subcommands.add_parser(name)
        command.add_argument("campaign_id")
        command.add_argument("recommendation_id")
        command.add_argument("candidate_id")
    snapshot = subcommands.add_parser("snapshot-inspect")
    snapshot.add_argument("snapshot_id")
    for name in ("confirmation-preflight", "confirmation-start"):
        command = subcommands.add_parser(name)
        command.add_argument("snapshot_id")
        command.add_argument("--confirmation-id")
        command.add_argument("--locked-final-test-seal-id")
    confirmation = subcommands.add_parser("confirmation-inspect")
    confirmation.add_argument("confirmation_id")
    locked = subcommands.add_parser("locked-final-test-status")
    locked.add_argument("seal_id")
    decision = subcommands.add_parser("final-decision")
    decision.add_argument("confirmation_id")
    decision.add_argument("decision", choices=("approve", "reject"))
    decision.add_argument("--expected-active-revision", type=int, required=True)
    decision.add_argument("--decision-id")
    decision.add_argument("--authority-context", required=True)
    decision.add_argument("--confirm-exact", required=True)
    decision.add_argument("--reason", default="")
    decision_read = subcommands.add_parser("final-decision-inspect")
    decision_read.add_argument("decision_id")
    compatibility = subcommands.add_parser("compatibility-disposition")
    compatibility.add_argument("kind")
    compatibility.add_argument("record")
    retention = subcommands.add_parser("retention-preview")
    retention.add_argument("--minimum-age-days", type=int, default=30)
    retention.add_argument("--keep-latest-count", type=int, default=5)
    retention.add_argument("--maximum-reclaim-bytes", type=int, default=0)
    return root


def emit(
    command: str,
    outcome: str,
    message: str,
    diagnostics=None,  # noqa: ANN001
    data=None,  # noqa: ANN001
) -> None:
    print(json.dumps(
        {
            "schema_version": EXPERIMENT_OUTPUT_VERSION,
            "command": command,
            "outcome": outcome,
            "message": message,
            "diagnostics": diagnostics or {},
            "data": data,
        },
        ensure_ascii=False,
        sort_keys=True,
    ))


def require_run_version(record: dict) -> None:
    if record.get("schema_version") != "predictor_v3.experiment_run.v1":
        raise ExperimentContractError(
            "unsupported_run_version", "Unsupported experiment run record version."
        )


def require_campaign_version(record: dict) -> None:
    if record.get("schema_version") not in {
        "predictor_v3.campaign.v1",
        "predictor_v3.agent_campaign.v1",
    }:
        raise ExperimentContractError(
            "unsupported_campaign_version",
            "Unsupported campaign record version.",
        )


def json_diagnostics(value: str) -> dict:
    try:
        payload = json.loads(value)
        return payload if isinstance(payload, dict) else {"raw": value}
    except json.JSONDecodeError:
        return {"raw": value}


def run_exit(status: str) -> int:
    return {
        "success": EXIT_SUCCESS,
        "cancelled": EXIT_CANCELLED,
        "partial": EXIT_PARTIAL,
        "training_failure": EXIT_TRAINING_FAILURE,
    }.get(status, EXIT_INTERNAL)


def campaign_exit(status: str) -> int:
    if status == "lock_conflict":
        return EXIT_LOCK_CONFLICT
    if status == "cancelled_resumable":
        return EXIT_CANCELLED
    if status in {"failed_resumable", "blocked", "retry_exhausted"}:
        return EXIT_TRAINING_FAILURE
    if status == "proposal_rejected":
        return EXIT_VALIDATION
    return EXIT_SUCCESS
