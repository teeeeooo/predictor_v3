"""Experiment/run/campaign nodes for the lifecycle retention graph."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from apps.common.model_lifecycle.closeout.retention import (
    ArtifactNode,
    ArtifactReference,
)
from apps.train.application.experiments.store import ExperimentStore

from .retention_nodes import raw_node


def experiment_inventory(
    experiments: ExperimentStore,
    campaigns: tuple[dict[str, Any], ...],
    now: datetime,
) -> tuple[list[ArtifactNode], list[ArtifactReference], bool]:
    nodes: list[ArtifactNode] = []
    references: list[ArtifactReference] = []
    complete = True
    if experiments.runs.exists():
        for path in sorted(experiments.runs.iterdir()):
            try:
                run = experiments.read_run(path.name)
                nodes.append(raw_node(run["run_id"], "run", run, path, now))
                if run.get("candidate_id"):
                    references.append(ArtifactReference(
                        run["run_id"], run["candidate_id"], "run_candidate"
                    ))
            except (KeyError, OSError, TypeError, ValueError):
                complete = False
    for campaign in campaigns:
        campaign_id = str(campaign.get("campaign_id", ""))
        campaign_path = experiments.campaigns / campaign_id
        nodes.append(raw_node(
            campaign_id, "campaign", campaign, campaign_path, now
        ))
        complete = _campaign_evidence(
            campaign, campaign_path, nodes, references, now
        ) and complete
    return nodes, references, complete


def _campaign_evidence(
    campaign: dict[str, Any],
    campaign_path: Path,
    nodes: list[ArtifactNode],
    references: list[ArtifactReference],
    now: datetime,
) -> bool:
    source = str(campaign.get("campaign_id", "campaign"))
    status = str(campaign.get("status", ""))
    reason = _campaign_reason(status)
    if reason:
        for run in campaign.get("completed_runs", ()):
            candidate_id = (
                run.get("candidate_id") if isinstance(run, dict) else None
            )
            if candidate_id:
                references.append(ArtifactReference(
                    source, candidate_id, reason
                ))
    _proposal_nodes(campaign, campaign_path, source, nodes, references, now)
    _attempt_nodes(campaign, campaign_path, source, nodes, references, now)
    _gate_nodes(campaign, campaign_path, source, nodes, references, now)
    _selection_nodes(campaign, campaign_path, source, nodes, references, now)
    return bool(campaign.get("schema_version"))


def _campaign_reason(status: str) -> str:
    if status in {"created", "running", "ready_to_execute", "awaiting_proposal"}:
        return "campaign_in_progress"
    if status in {
        "paused", "failed_resumable", "cancelled_resumable", "lock_conflict"
    }:
        return "campaign_resumable"
    return ""


def _proposal_nodes(campaign, path, source, nodes, references, now) -> None:  # noqa: ANN001
    for proposal in campaign.get("proposals", ()):
        if not isinstance(proposal, dict) or not proposal.get("proposal_id"):
            continue
        identity = proposal["proposal_id"]
        nodes.append(ArtifactNode(
            identity, "proposal",
            _stable_created_at(proposal, campaign), 0,
            source_artifact_identity=f"{path}/proposals/{identity}",
        ))
        references.append(ArtifactReference(
            source, identity, "campaign_proposal"
        ))


def _attempt_nodes(campaign, path, source, nodes, references, now) -> None:  # noqa: ANN001
    for index, attempt in enumerate(campaign.get("attempt_history", ()), 1):
        if not isinstance(attempt, dict):
            continue
        identity = f"{source}-attempt-{attempt.get('iteration', 0)}-{index}"
        nodes.append(ArtifactNode(
            identity, "attempt", _stable_created_at(attempt, campaign), 0,
            source_artifact_identity=f"{path}/record.json#attempt[{index}]",
        ))
        references.append(ArtifactReference(
            source, identity, "campaign_attempt"
        ))
        if attempt.get("run_id"):
            references.append(ArtifactReference(
                identity, attempt["run_id"], "attempt_run"
            ))


def _gate_nodes(campaign, path, source, nodes, references, now) -> None:  # noqa: ANN001
    for index, gate in enumerate(campaign.get("gates", ()), 1):
        if not isinstance(gate, dict):
            continue
        identity = f"{source}-gate-{index}"
        nodes.append(ArtifactNode(
            identity, "gate", _stable_created_at(gate, campaign), 0,
            source_artifact_identity=f"{path}/record.json#gate[{index}]",
        ))
        references.append(ArtifactReference(source, identity, "campaign_gate"))
        if gate.get("candidate_id"):
            references.append(ArtifactReference(
                identity, gate["candidate_id"], "gate_candidate"
            ))


def _selection_nodes(campaign, path, source, nodes, references, now) -> None:  # noqa: ANN001
    leaderboard = f"{source}-leaderboard"
    nodes.append(ArtifactNode(
        leaderboard, "leaderboard", _stable_created_at(campaign), 0,
        source_artifact_identity=f"{path}/record.json#leaderboard",
    ))
    references.append(ArtifactReference(
        source, leaderboard, "campaign_leaderboard"
    ))
    if campaign.get("incumbent_candidate_id"):
        references.append(ArtifactReference(
            leaderboard,
            campaign["incumbent_candidate_id"],
            "campaign_incumbent",
        ))
    for item in campaign.get("recommendations", ()):
        candidate = (
            item.get("recommended_candidate")
            if isinstance(item, dict) else None
        )
        if not isinstance(candidate, dict) or not candidate.get("candidate_id"):
            continue
        identity = item.get("recommendation_id")
        if identity:
            nodes.append(ArtifactNode(
                identity, "recommendation",
                _stable_created_at(item, campaign), 0,
                source_artifact_identity=(
                    f"{path}/recommendations/{identity}/recommendation.json"
                ),
            ))
            references.append(ArtifactReference(
                source, identity, "campaign_recommendation"
            ))
        references.append(ArtifactReference(
            identity or source,
            candidate["candidate_id"],
            "selected_recommendation",
        ))


def _stable_created_at(*payloads: dict[str, Any]) -> str:
    for payload in payloads:
        for name in ("created_at", "started_at", "completed_at", "updated_at"):
            value = payload.get(name)
            if type(value) is str and value:
                return value
    return "unknown"
