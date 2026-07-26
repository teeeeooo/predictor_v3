"""One-step externally proposed Phase 5G campaign orchestration."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .agent_contracts import AGENT_CAMPAIGN_VERSION
from .agent_campaign_creation import comparison_analysis, create_agent_campaign
from .campaign_evidence import CampaignEvidenceReader
from .campaign_execution import execute_one_iteration
from .candidate_gate import evaluate_candidate
from .contracts import ExperimentContractError
from .leaderboard import rebuild_leaderboard
from .campaign_operator import (
    complete_without_recommendation, create_recommendation, extend_budget_operator
)
from .proposal_submission import submit_proposal
from .records import utc_now
from .service import ExperimentApplicationService


class AgentCampaignApplicationService:
    def __init__(self, experiments: ExperimentApplicationService) -> None:
        self._experiments = experiments
        self._store = experiments.store
        self._evidence = CampaignEvidenceReader(self._store.root.parent)

    def create(
        self, definition: dict[str, Any], *, campaign_id: str | None = None
    ) -> dict[str, Any]:
        return create_agent_campaign(
            self._experiments,
            self._evidence,
            definition,
            campaign_id=campaign_id,
        )

    def status(self, campaign_id: str) -> dict[str, Any]:
        record = self._store.read_campaign(campaign_id)
        self._require_supported(record)
        return record

    def submit_proposal(
        self, campaign_id: str, proposal: dict[str, Any]
    ) -> dict[str, Any]:
        record = self.status(campaign_id)
        if record["budget"]["remaining_iterations"] <= 0:
            return self._detached_budget_exhausted(record)
        if record["current_proposal_id"] is not None:
            raise ExperimentContractError(
                "proposal_already_pending",
                "The current proposal must execute or be cleared before another submission.",
            )
        return submit_proposal(
            self._experiments, self._store, record, proposal
        )

    def execute(self, campaign_id: str, proposal_id: str) -> dict[str, Any]:
        record = self.status(campaign_id)
        if record["current_proposal_id"] != proposal_id:
            raise ExperimentContractError(
                "proposal_not_ready", "The requested proposal is not ready to execute."
            )
        control = self._store.read_control(campaign_id)
        if control in {"pause", "cancel"}:
            record["status"] = "paused"
            record["pause_requested"] = True
            record["cancel_requested"] = control == "cancel"
            record["updated_at"] = utc_now()
            self._store.update_campaign(campaign_id, record)
            return record
        proposal_evidence = self._store.read_campaign_evidence(
            campaign_id, "proposals", proposal_id, "proposal.json"
        )
        resolved = self._experiments.validate(
            proposal_evidence["resolved_specification_after"]
        )
        iteration = int(proposal_evidence["iteration"])
        terminal, started, run_id, record = execute_one_iteration(
            self._experiments,
            campaign_id,
            resolved,
            iteration - 1,
            record,
            attempt_scope=proposal_id,
        )
        if not started:
            if record["status"] != "lock_conflict":
                record["current_proposal_id"] = None
                record["updated_at"] = utc_now()
                self._store.update_campaign(campaign_id, record)
            return record
        run = self._experiments.inspect_run(run_id)
        analysis, integrity = self._evidence.run_analysis(run)
        baseline_analysis = comparison_analysis(self._evidence, record)
        gate = evaluate_candidate(
            analysis,
            run_record=run,
            policy=record["policy"],
            baseline_analysis=baseline_analysis,
            artifact_integrity=integrity,
        )
        completed = {
            "iteration": iteration,
            "proposal_id": proposal_id,
            "run_id": run_id,
            "candidate_id": gate["candidate_id"],
            "status": terminal,
            "resolved_specification_before": proposal_evidence[
                "resolved_specification_before"
            ],
            "proposed_delta": proposal_evidence["proposed_delta"],
            "resolved_specification_after": resolved.payload,
            "execution_result_reference": f"experiments/runs/{run_id}/record.json",
            "gate": gate,
            "interpretation": {
                "gate_pass": gate["gate_pass"],
                "blocking_reason_codes": [
                    item["code"] for item in gate["blocking_reasons"]
                ],
            },
            "next_action_rationale": (
                "Await an explicit external proposal or recommendation request."
            ),
        }
        result_reference = self._store.write_campaign_evidence(
            campaign_id, "iterations", proposal_id, "result.json", completed
        )
        completed["evidence_reference"] = result_reference
        record["iterations"].append(completed)
        record["completed_runs"].append({
            "iteration": iteration,
            "run_id": run_id,
            "status": terminal,
        })
        record["gates"].append(gate)
        record["current"] = None
        record["current_proposal_id"] = None
        record["budget"]["remaining_iterations"] = (
            record["budget"]["max_iterations"]
            - record["budget"]["consumed_iterations"]
        )
        record["leaderboard"] = rebuild_leaderboard(
            record["gates"], policy=record["policy"], baseline=record["baseline"]
        )
        record["incumbent_candidate_id"] = record["leaderboard"][
            "incumbent_candidate_id"
        ]
        record["incumbent_specification"] = self._incumbent_specification(record)
        if terminal == "cancelled":
            record["status"] = "paused"
            record["cancel_requested"] = True
            record["candidate_state"] = (
                "candidate_available"
                if record["incumbent_candidate_id"] else "no_valid_candidate"
            )
        elif record["budget"]["remaining_iterations"] <= 0:
            record["status"] = "budget_exhausted"
            record["candidate_state"] = (
                "recommendation_ready"
                if record["incumbent_candidate_id"] else "no_valid_candidate"
            )
        else:
            record["status"] = "awaiting_proposal"
            record["candidate_state"] = (
                "candidate_available"
                if record["incumbent_candidate_id"] else "no_valid_candidate"
            )
        record["updated_at"] = utc_now()
        self._store.update_campaign(campaign_id, record)
        if record["budget"]["remaining_iterations"] <= 0:
            create_recommendation(
                self._store,
                record,
                recommendation_id=None,
                status_after="budget_exhausted",
            )
        return record

    def resume(self, campaign_id: str) -> dict[str, Any]:
        record = self.status(campaign_id)
        if record["status"] not in {"paused", "lock_conflict", "proposal_rejected"}:
            raise ExperimentContractError(
                "campaign_not_resumable", "Agent campaign is not paused or resumable."
            )
        self._store.clear_control(campaign_id)
        record["pause_requested"] = False
        record["cancel_requested"] = False
        record["status"] = (
            "ready_to_execute"
            if record["current_proposal_id"] else "awaiting_proposal"
        )
        record["updated_at"] = utc_now()
        self._store.update_campaign(campaign_id, record)
        return record

    def extend_budget_operator(
        self,
        campaign_id: str,
        *,
        new_total: int,
        operator_reference: str,
    ) -> dict[str, Any]:
        return extend_budget_operator(
            self._store,
            self.status(campaign_id),
            new_total=new_total,
            operator_reference=operator_reference,
        )

    def recommend(
        self, campaign_id: str, *, recommendation_id: str | None = None
    ) -> dict[str, Any]:
        return create_recommendation(
            self._store,
            self.status(campaign_id),
            recommendation_id=recommendation_id,
        )

    def complete_without_recommendation(self, campaign_id: str) -> dict[str, Any]:
        return complete_without_recommendation(
            self._store, self.status(campaign_id)
        )

    @staticmethod
    def _incumbent_specification(record: dict[str, Any]) -> dict[str, Any] | None:
        incumbent = record["incumbent_candidate_id"]
        for item in record["iterations"]:
            if item["candidate_id"] == incumbent:
                return deepcopy(item["resolved_specification_after"])
        return None

    @staticmethod
    def _detached_budget_exhausted(record: dict[str, Any]) -> dict[str, Any]:
        outcome = deepcopy(record)
        outcome["status"] = "budget_exhausted"
        outcome["failure"] = {
            "code": "campaign_budget_exhausted",
            "message": "No proposal or training may start without operator extension.",
        }
        return outcome

    @staticmethod
    def _require_supported(record: dict[str, Any]) -> None:
        if record.get("schema_version") != AGENT_CAMPAIGN_VERSION:
            raise ExperimentContractError(
                "unsupported_agent_campaign_version",
                "Unsupported agent campaign record version.",
            )
