"""Explicit, bounded, non-agent campaign lifecycle foundation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import uuid4

from apps.train.application.experiments.contracts import (
    CAMPAIGN_RECORD_VERSION,
    ExperimentContractError,
    ResolvedExperiment,
    resolve_specification,
)
from apps.train.application.experiments.records import utc_now
from apps.train.application.experiments.service import ExperimentApplicationService


class CampaignApplicationService:
    def __init__(self, experiments: ExperimentApplicationService) -> None:
        self._experiments = experiments
        self._store = experiments.store

    def start(
        self, specification: dict[str, Any], *, campaign_id: str | None = None
    ) -> dict[str, Any]:
        base = self._experiments.validate(specification)
        configured = base.payload["campaign"]["experiments"]
        if not configured:
            raise ExperimentContractError(
                "campaign_experiments_missing",
                "A Phase 5F campaign requires explicit configured experiments.",
            )
        resolved_runs = tuple(
            resolve_specification(item, campaign=_campaign_defaults(base.payload))
            for item in configured
        )
        identity = campaign_id or f"campaign-{uuid4().hex}"
        record = {
            "schema_version": CAMPAIGN_RECORD_VERSION,
            "campaign_id": identity,
            "status": "created",
            "created_at": utc_now(),
            "updated_at": utc_now(),
            "resolved_campaign_configuration": base.payload,
            "configured_experiments": [item.payload for item in resolved_runs],
            "contract_identity": [
                self._experiments.execution_identity(item) for item in resolved_runs
            ],
            "current": None,
            "completed_runs": [],
            "attempt_history": [],
            "budget": {
                "configured_iterations": base.payload["campaign"]["max_iterations"],
                "consumed_iterations": 0,
                "configured_experiments": len(resolved_runs),
            },
            "pause_requested": False,
            "cancel_requested": False,
            "failure": None,
            "diagnostics_reference": None,
        }
        self._store.create_campaign(identity, record)
        return self._execute(identity, resolved_runs)

    def status(self, campaign_id: str) -> dict[str, Any]:
        record = self._store.read_campaign(campaign_id)
        self._require_supported(record)
        return record

    def pause(self, campaign_id: str) -> dict[str, Any]:
        record = self.status(campaign_id)
        if record["status"] in {"completed", "blocked"}:
            return record
        self._store.request_control(campaign_id, "pause")
        record["pause_requested"] = True
        record["updated_at"] = utc_now()
        self._store.update_campaign(campaign_id, record)
        return record

    def cancel(self, campaign_id: str) -> dict[str, Any]:
        record = self.status(campaign_id)
        if record["status"] in {"completed", "blocked"}:
            return record
        self._store.request_control(campaign_id, "cancel")
        record["cancel_requested"] = True
        record["updated_at"] = utc_now()
        self._store.update_campaign(campaign_id, record)
        return record

    def resume(self, campaign_id: str) -> dict[str, Any]:
        record = self.status(campaign_id)
        if record["status"] not in {
            "paused", "lock_conflict", "failed_resumable", "cancelled_resumable"
        }:
            raise ExperimentContractError(
                "campaign_not_resumable", "Campaign is not in a resumable state."
            )
        resolved = tuple(
            self._experiments.validate(item)
            for item in record["configured_experiments"]
        )
        current_identity = [
            self._experiments.execution_identity(item) for item in resolved
        ]
        if current_identity != record["contract_identity"]:
            record["status"] = "blocked"
            record["failure"] = {
                "code": "resume_contract_changed",
                "message": "Current training meaning differs from the saved campaign.",
                "saved": record["contract_identity"],
                "current": current_identity,
            }
            record["updated_at"] = utc_now()
            self._store.update_campaign(campaign_id, record)
            return record
        self._store.clear_control(campaign_id)
        record["pause_requested"] = False
        record["cancel_requested"] = False
        self._store.update_campaign(campaign_id, record)
        return self._execute(campaign_id, resolved)

    def _execute(
        self, campaign_id: str, resolved_runs: tuple[ResolvedExperiment, ...]
    ) -> dict[str, Any]:
        record = self.status(campaign_id)
        budget = record["budget"]["configured_iterations"]
        index = record["budget"]["consumed_iterations"]
        while index < min(len(resolved_runs), budget):
            if self._store.read_control(campaign_id) in {"pause", "cancel"}:
                record["status"] = "paused"
                record["pause_requested"] = True
                break
            experiment = resolved_runs[index]
            max_attempts = experiment.payload["retry"]["max_attempts"]
            terminal_status = ""
            for attempt in range(1, max_attempts + 1):
                run_id = f"{campaign_id}-iteration-{index + 1}-attempt-{attempt}"
                record["status"] = "running"
                record["current"] = {
                    "iteration": index + 1, "attempt": attempt, "run_id": run_id
                }
                record["updated_at"] = utc_now()
                self._store.update_campaign(campaign_id, record)
                accepted = []
                result = self._experiments.run(
                    experiment,
                    run_id=run_id,
                    execution_owner="campaign",
                    campaign_id=campaign_id,
                    attempt=attempt,
                    callbacks={"accepted_callback": accepted.append},
                )
                if result is not None and result.status == "lock_conflict":
                    record["status"] = "lock_conflict"
                    record["failure"] = {
                        "code": "execution_lock_conflict",
                        "message": result.message,
                        "diagnostics": result.summary,
                    }
                    record["current"] = None
                    self._store.update_campaign(campaign_id, record)
                    return record
                if result is not None and not accepted:
                    record["status"] = "failed_resumable"
                    record["failure"] = {
                        "code": "training_preflight_failed",
                        "message": result.message,
                    }
                    record["current"] = None
                    self._store.update_campaign(campaign_id, record)
                    return record
                run = self._experiments.inspect_run(run_id)
                terminal_status = run["status"]
                record["attempt_history"].append({
                    "iteration": index + 1,
                    "attempt": attempt,
                    "run_id": run_id,
                    "status": terminal_status,
                })
                if accepted and not any(
                    item["iteration"] == index + 1
                    for item in record["completed_runs"]
                ):
                    record["budget"]["consumed_iterations"] = index + 1
                if terminal_status in {"success", "partial", "cancelled"}:
                    break
                if (
                    attempt >= max_attempts
                    or terminal_status
                    not in experiment.payload["retry"]["retryable_statuses"]
                ):
                    break
            record["completed_runs"].append({
                "iteration": index + 1,
                "run_id": run_id,
                "status": terminal_status,
            })
            record["current"] = None
            record["updated_at"] = utc_now()
            control = self._store.read_control(campaign_id)
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
                "completed"
                if index >= len(resolved_runs)
                else "paused_budget_exhausted"
            )
        record["updated_at"] = utc_now()
        self._store.update_campaign(campaign_id, record)
        return record

    @staticmethod
    def _require_supported(record: dict[str, Any]) -> None:
        if record.get("schema_version") != CAMPAIGN_RECORD_VERSION:
            raise ExperimentContractError(
                "unsupported_campaign_version",
                "Unsupported campaign record version.",
            )


def _campaign_defaults(payload: dict[str, Any]) -> dict[str, Any]:
    defaults = deepcopy(payload)
    defaults["campaign"]["experiments"] = []
    return defaults
