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
from apps.train.application.experiments.campaign_execution import execute_campaign
from apps.train.application.experiments.records import (
    build_identity_is_identified,
    utc_now,
)
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
        for resolved in resolved_runs:
            self._experiments.preflight(resolved)
        self._experiments.ensure_runtime_initialized()
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
        current = record.get("current") or {}
        run_id = current.get("run_id")
        if run_id and not current.get("training_started"):
            try:
                run = self._experiments.inspect_run(run_id)
            except FileNotFoundError:
                pass
            else:
                if run.get("training_started"):
                    record = deepcopy(record)
                    record["current"]["training_started"] = True
                    record["current"]["training_started_at"] = run.get(
                        "training_started_at", ""
                    )
                    record["budget"]["consumed_iterations"] = max(
                        record["budget"]["consumed_iterations"],
                        int(record["current"]["iteration"]),
                    )
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
        if not self._experiments.has_current_runtime():
            blocked = deepcopy(record)
            blocked["status"] = "blocked"
            blocked["failure"] = {
                "code": "resume_definition_generation_unavailable",
                "message": (
                    "The saved campaign cannot resume without its current "
                    "Definition generation."
                ),
                "next_action": "Create a new campaign from an initialized workspace.",
            }
            blocked["updated_at"] = utc_now()
            return blocked
        resolved = tuple(
            self._experiments.validate(item)
            for item in record["configured_experiments"]
        )
        current_identity = [
            self._experiments.execution_identity(item) for item in resolved
        ]
        if not _build_identities_identified(record["contract_identity"]) or not (
            _build_identities_identified(current_identity)
        ):
            blocked = deepcopy(record)
            blocked["status"] = "blocked"
            blocked["failure"] = {
                "code": "resume_build_identity_unavailable",
                "message": (
                    "The saved and current repository build identities must both "
                    "be identifiable before this campaign can resume."
                ),
                "next_action": (
                    "Create a new campaign in an identifiable repository build."
                ),
            }
            blocked["updated_at"] = utc_now()
            return blocked
        if current_identity != record["contract_identity"]:
            blocked = deepcopy(record)
            blocked["status"] = "blocked"
            blocked["failure"] = {
                "code": "resume_contract_changed",
                "message": "Current training meaning differs from the saved campaign.",
                "saved": record["contract_identity"],
                "current": current_identity,
                "next_action": "Create a new campaign for the current training build.",
            }
            blocked["updated_at"] = utc_now()
            return blocked
        exhausted = _retry_exhausted_outcome(record)
        if exhausted is not None:
            return exhausted
        self._store.clear_control(campaign_id)
        record["pause_requested"] = False
        record["cancel_requested"] = False
        self._store.update_campaign(campaign_id, record)
        return self._execute(campaign_id, resolved)

    def _execute(
        self, campaign_id: str, resolved_runs: tuple[ResolvedExperiment, ...]
    ) -> dict[str, Any]:
        return execute_campaign(self._experiments, campaign_id, resolved_runs)

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


def _build_identities_identified(identities: Any) -> bool:
    return (
        isinstance(identities, list)
        and bool(identities)
        and all(
            isinstance(identity, dict)
            and build_identity_is_identified(identity.get("build_revision"))
            for identity in identities
        )
    )


def _retry_exhausted_outcome(
    record: dict[str, Any],
) -> dict[str, Any] | None:
    iteration = int(record["budget"]["consumed_iterations"]) + 1
    configured = record["configured_experiments"]
    if iteration > len(configured):
        return None
    maximum = int(configured[iteration - 1]["retry"]["max_attempts"])
    attempts = sum(
        item.get("iteration") == iteration for item in record["attempt_history"]
    )
    if attempts < maximum:
        return None
    exhausted = deepcopy(record)
    exhausted["status"] = "retry_exhausted"
    exhausted["failure"] = {
        "code": "campaign_retry_exhausted",
        "message": (
            f"Iteration {iteration} exhausted its configured {maximum} attempts."
        ),
        "iteration": iteration,
        "attempts_used": attempts,
        "max_attempts": maximum,
        "next_action": (
            "Create a new campaign; resume cannot increase the saved retry allowance."
        ),
    }
    return exhausted
