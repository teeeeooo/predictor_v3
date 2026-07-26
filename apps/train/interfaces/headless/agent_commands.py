"""Headless adapter routing for Phase 5G-only commands."""

from __future__ import annotations

from pathlib import Path

from apps.train.application.experiments.agent_campaign import (
    AgentCampaignApplicationService,
)
from apps.train.application.experiments.contracts import load_specification
from apps.train.application.experiments.store import ExperimentStore

from .command_contract import (
    EXIT_SUCCESS,
    campaign_exit,
    emit,
    require_campaign_version,
)


def dispatch_agent_read(args, lifecycle_root: Path) -> int | None:  # noqa: ANN001
    if args.command in {
        "campaign-budget",
        "campaign-leaderboard",
        "campaign-incumbent",
    }:
        record = ExperimentStore(lifecycle_root).read_campaign(args.campaign_id)
        require_campaign_version(record)
        if args.command == "campaign-budget":
            data = {
                "campaign_id": record["campaign_id"],
                "status": record["status"],
                "policy": record.get("policy"),
                "budget": record["budget"],
                "extension_required": (
                    record["budget"].get("remaining_iterations", 1) == 0
                ),
            }
        elif args.command == "campaign-leaderboard":
            data = record.get("leaderboard")
        else:
            data = {
                "campaign_id": record["campaign_id"],
                "incumbent_candidate_id": record.get("incumbent_candidate_id"),
                "active_candidate_id": record.get("baseline", {}).get(
                    "active_candidate_id"
                ),
            }
        emit(args.command, record["status"], "Campaign record loaded.", data=data)
        return EXIT_SUCCESS
    if args.command == "campaign-recommendation":
        store = ExperimentStore(lifecycle_root)
        record = store.read_campaign(args.campaign_id)
        require_campaign_version(record)
        data = store.read_campaign_evidence(
            args.campaign_id,
            "recommendations",
            args.recommendation_id,
            "recommendation.json",
        )
        emit(args.command, "recommendation_ready", "Recommendation loaded.", data=data)
        return EXIT_SUCCESS
    return None


def dispatch_agent_mutation(args, service) -> int | None:  # noqa: ANN001
    campaigns = AgentCampaignApplicationService(service)
    if args.command == "campaign-create":
        definition = load_specification(args.definition)
        record = campaigns.create(definition, campaign_id=args.campaign_id)
        emit(args.command, record["status"], "Agent campaign created.", data=record)
        return campaign_exit(record["status"])
    if args.command == "campaign-proposal-submit":
        proposal = load_specification(args.proposal)
        record = campaigns.submit_proposal(args.campaign_id, proposal)
        emit(args.command, record["status"], "Proposal preflight returned.", data=record)
        return campaign_exit(record["status"])
    if args.command == "campaign-execute":
        record = campaigns.execute(args.campaign_id, args.proposal_id)
        emit(args.command, record["status"], "Campaign iteration returned.", data=record)
        return campaign_exit(record["status"])
    if args.command == "campaign-budget-extend":
        record = campaigns.extend_budget_operator(
            args.campaign_id,
            new_total=args.new_total,
            operator_reference=args.operator_reference,
        )
        emit(
            args.command,
            record["status"],
            "Operator budget extension recorded.",
            data=record,
        )
        return EXIT_SUCCESS
    if args.command == "campaign-recommendation-create":
        artifact = campaigns.recommend(
            args.campaign_id, recommendation_id=args.recommendation_id
        )
        emit(
            args.command,
            "recommendation_ready",
            "Immutable recommendation created.",
            data=artifact,
        )
        return EXIT_SUCCESS
    if args.command == "campaign-complete":
        if not args.without_recommendation:
            artifact = campaigns.recommend(args.campaign_id)
            emit(
                args.command,
                "recommendation_ready",
                "Campaign completed with an immutable recommendation.",
                data=artifact,
            )
            return EXIT_SUCCESS
        record = campaigns.complete_without_recommendation(args.campaign_id)
        emit(
            args.command,
            record["status"],
            "Campaign completed without a recommendation.",
            data=record,
        )
        return EXIT_SUCCESS
    return None
