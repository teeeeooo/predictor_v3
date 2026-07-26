"""Training-start-accounted execution for one explicit campaign."""

from __future__ import annotations

from typing import Any

from apps.train.application.experiments.contracts import ResolvedExperiment
from apps.train.application.experiments.records import utc_now
from apps.train.application.experiments.service import ExperimentApplicationService


def execute_campaign(
    experiments: ExperimentApplicationService,
    campaign_id: str,
    resolved_runs: tuple[ResolvedExperiment, ...],
) -> dict[str, Any]:
    store = experiments.store
    record = store.read_campaign(campaign_id)
    budget = record["budget"]["configured_iterations"]
    index = record["budget"]["consumed_iterations"]
    while index < min(len(resolved_runs), budget):
        if store.read_control(campaign_id) in {"pause", "cancel"}:
            record["status"] = "paused"
            record["pause_requested"] = True
            break
        experiment = resolved_runs[index]
        terminal_status, iteration_started, run_id, record = _run_iteration(
            experiments, campaign_id, experiment, index, record
        )
        if not iteration_started:
            return record
        record["completed_runs"].append({
            "iteration": index + 1,
            "run_id": run_id,
            "status": terminal_status,
        })
        record["current"] = None
        record["updated_at"] = utc_now()
        control = store.read_control(campaign_id)
        if terminal_status == "cancelled" or control == "cancel":
            record["status"] = "cancelled_resumable"
            record["cancel_requested"] = True
            break
        if control == "pause":
            record["status"] = "paused"
            record["pause_requested"] = True
            break
        if terminal_status == "training_failure":
            record["status"] = "failed_resumable"
            break
        index += 1
    else:
        record["status"] = (
            "completed" if index >= len(resolved_runs) else "paused_budget_exhausted"
        )
    record["updated_at"] = utc_now()
    store.update_campaign(campaign_id, record)
    return record


def _run_iteration(
    experiments: ExperimentApplicationService,
    campaign_id: str,
    experiment: ResolvedExperiment,
    index: int,
    record: dict[str, Any],
) -> tuple[str, bool, str, dict[str, Any]]:
    store = experiments.store
    previous_attempts = sum(
        item.get("iteration") == index + 1 for item in record["attempt_history"]
    )
    maximum = experiment.payload["retry"]["max_attempts"]
    terminal_status = ""
    run_id = ""
    if previous_attempts >= maximum:
        return terminal_status, False, run_id, record
    for attempt in range(previous_attempts + 1, maximum + 1):
        run_id = f"{campaign_id}-iteration-{index + 1}-attempt-{attempt}"
        record["status"] = "running"
        record["current"] = {
            "iteration": index + 1,
            "attempt": attempt,
            "run_id": run_id,
            "training_started": False,
            "training_started_at": "",
        }
        record["updated_at"] = utc_now()
        store.update_campaign(campaign_id, record)

        def mark_training_started(_request) -> None:  # noqa: ANN001
            latest = store.read_campaign(campaign_id)
            current = latest.get("current") or {}
            if current.get("run_id") != run_id:
                raise RuntimeError("Campaign training-start acknowledgement is stale.")
            if current.get("training_started"):
                return
            current["training_started"] = True
            current["training_started_at"] = utc_now()
            latest["budget"]["consumed_iterations"] = max(
                latest["budget"]["consumed_iterations"], index + 1
            )
            latest["updated_at"] = utc_now()
            store.update_campaign(campaign_id, latest)

        result = experiments.run(
            experiment,
            run_id=run_id,
            execution_owner="campaign",
            campaign_id=campaign_id,
            attempt=attempt,
            callbacks={"started_callback": mark_training_started},
        )
        if result is not None and result.status == "lock_conflict":
            return "", False, run_id, _lock_conflict(store, campaign_id, record, result)
        try:
            run = experiments.inspect_run(run_id)
        except FileNotFoundError:
            return "", False, run_id, _preflight_failure(
                store, campaign_id, record, result
            )
        record = store.read_campaign(campaign_id)
        terminal_status = run["status"]
        started = bool(run.get("training_started"))
        record["attempt_history"].append({
            "iteration": index + 1,
            "attempt": attempt,
            "run_id": run_id,
            "status": terminal_status,
            "training_started": started,
            "consumed_iteration": started,
        })
        if not started:
            return terminal_status, False, run_id, _start_failure(
                store, campaign_id, record, result, run_id
            )
        record["budget"]["consumed_iterations"] = max(
            record["budget"]["consumed_iterations"], index + 1
        )
        if terminal_status in {"success", "partial", "cancelled"}:
            break
        if (
            attempt >= maximum
            or terminal_status not in experiment.payload["retry"]["retryable_statuses"]
        ):
            break
    return terminal_status, True, run_id, record


def _lock_conflict(store, campaign_id, record, result):  # noqa: ANN001, ANN202
    record["status"] = "lock_conflict"
    record["failure"] = {
        "code": "execution_lock_conflict",
        "message": result.message,
        "diagnostics": result.summary,
    }
    record["current"] = None
    store.update_campaign(campaign_id, record)
    return record


def _preflight_failure(store, campaign_id, record, result):  # noqa: ANN001, ANN202
    record["status"] = "failed_resumable"
    record["failure"] = {
        "code": "training_preflight_failed",
        "message": (
            result.message
            if result is not None
            else "Training preflight ended without a durable run."
        ),
        "diagnostics": result.summary if result is not None else "",
    }
    record["current"] = None
    store.update_campaign(campaign_id, record)
    return record


def _start_failure(
    store, campaign_id, record, result, run_id  # noqa: ANN001
):  # noqa: ANN202
    record["status"] = "failed_resumable"
    record["failure"] = {
        "code": "training_start_failed",
        "message": (
            (result.message if result is not None else "")
            or "Execution ended before Core ML training started."
        ),
        "diagnostics_reference": f"experiments/runs/{run_id}/record.json",
    }
    record["current"] = None
    record["updated_at"] = utc_now()
    store.update_campaign(campaign_id, record)
    return record
