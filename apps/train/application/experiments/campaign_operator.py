"""Operator-only budget mutation and immutable recommendation commands."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from .agent_contracts import BUDGET_EXTENSION_VERSION
from .contracts import ExperimentContractError
from .recommendation import build_recommendation
from .records import utc_now


def extend_budget_operator(
    store, record: dict[str, Any], *, new_total: int, operator_reference: str
) -> dict[str, Any]:  # noqa: ANN001
    old = record["budget"]["max_iterations"]
    consumed = record["budget"]["consumed_iterations"]
    if (
        type(new_total) is not int
        or new_total <= old
        or new_total < consumed
        or new_total > 100
        or type(operator_reference) is not str
        or not operator_reference.strip()
    ):
        raise ExperimentContractError(
            "budget_extension_invalid",
            "Operator extension must increase the total bounded allowance.",
        )
    campaign_id = record["campaign_id"]
    extension_id = f"extension-{uuid4().hex}"
    evidence = {
        "schema_version": BUDGET_EXTENSION_VERSION,
        "campaign_id": campaign_id,
        "extension_id": extension_id,
        "operator_reference": operator_reference,
        "approval_required_before": True,
        "approval_recorded": True,
        "old_total_maximum": old,
        "new_total_maximum": new_total,
        "consumed_iterations": consumed,
        "remaining_before": old - consumed,
        "remaining_after": new_total - consumed,
        "recorded_at": utc_now(),
    }
    reference = store.write_campaign_evidence(
        campaign_id,
        "budget_extensions",
        extension_id,
        "extension.json",
        evidence,
    )
    record["budget"]["max_iterations"] = new_total
    record["budget"]["remaining_iterations"] = new_total - consumed
    record["policy"]["max_iterations"] = new_total
    record.setdefault("budget_extensions", []).append(reference)
    record["status"] = "awaiting_proposal"
    record["updated_at"] = utc_now()
    store.update_campaign(campaign_id, record)
    return record


def create_recommendation(
    store,
    record: dict[str, Any],
    *,
    recommendation_id: str | None,
    status_after: str = "recommendation_ready",
) -> dict[str, Any]:  # noqa: ANN001
    identity = recommendation_id or f"recommendation-{uuid4().hex}"
    artifact = build_recommendation(
        record, recommendation_id=identity, created_at=utc_now()
    )
    reference = store.write_campaign_evidence(
        record["campaign_id"],
        "recommendations",
        identity,
        "recommendation.json",
        artifact,
    )
    record["recommendations"].append({
        "recommendation_id": identity,
        "evidence_reference": reference,
        "recommended_candidate": artifact["recommended_candidate"],
        "approval_required": True,
    })
    record["recommendation_status"] = "recommendation_ready"
    record["status"] = status_after
    record["updated_at"] = utc_now()
    store.update_campaign(record["campaign_id"], record)
    return artifact


def complete_without_recommendation(
    store, record: dict[str, Any]
) -> dict[str, Any]:  # noqa: ANN001
    if record["current_proposal_id"] is not None:
        raise ExperimentContractError(
            "campaign_completion_blocked",
            "A ready proposal must execute or be cancelled before completion.",
        )
    record["status"] = "completed_without_recommendation"
    record["recommendation_status"] = "not_requested"
    record["updated_at"] = utc_now()
    store.update_campaign(record["campaign_id"], record)
    return record
