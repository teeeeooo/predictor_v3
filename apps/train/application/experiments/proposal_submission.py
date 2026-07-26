"""Durable pre-training validation for external Phase 5G proposals."""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any
from uuid import uuid4

from .agent_contracts import (
    apply_delta,
    changed_leaf_paths,
    validate_proposal,
)
from .contracts import ExperimentContractError, resolve_specification
from .records import utc_now

_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")


def submit_proposal(
    experiments,  # noqa: ANN001
    store,  # noqa: ANN001
    record: dict[str, Any],
    proposal: dict[str, Any],
) -> dict[str, Any]:
    try:
        accepted = validate_proposal(proposal, policy=record["policy"])
        expected = _expected_baseline_reference(record)
        if accepted["baseline_reference"] != expected:
            raise ExperimentContractError(
                "proposal_baseline_stale",
                f"Proposal baseline must reference {expected!r}.",
            )
        before = deepcopy(
            record["incumbent_specification"]
            or record["resolved_base_specification"]
        )
        after = resolve_specification(apply_delta(before, accepted["delta"]))
        if after.payload == before:
            raise ExperimentContractError(
                "proposal_delta_noop", "Proposal delta resolves to no change."
            )
        experiments.preflight(after)
    except ExperimentContractError as exc:
        return _reject(store, record, proposal, exc)

    proposal_id = accepted["proposal_id"]
    iteration = record["budget"]["consumed_iterations"] + 1
    evidence = {
        "schema_version": accepted["schema_version"],
        "campaign_id": record["campaign_id"],
        "iteration": iteration,
        "status": "ready_to_execute",
        "recorded_at": utc_now(),
        "proposal": accepted,
        "resolved_specification_before": before,
        "proposed_delta": accepted["delta"],
        "changed_paths": list(changed_leaf_paths(accepted["delta"])),
        "resolved_specification_after": after.payload,
        "policy_validation": {
            "passed": True,
            "allowed_categories": record["policy"]["allowed_categories"],
        },
    }
    reference = store.write_campaign_evidence(
        record["campaign_id"],
        "proposals",
        proposal_id,
        "proposal.json",
        evidence,
    )
    record["proposals"].append({
        "proposal_id": proposal_id,
        "status": "ready_to_execute",
        "evidence_reference": reference,
    })
    record["current_proposal_id"] = proposal_id
    record["status"] = "ready_to_execute"
    record["failure"] = None
    record["updated_at"] = utc_now()
    store.update_campaign(record["campaign_id"], record)
    return record


def _reject(store, record, proposal, error):  # noqa: ANN001, ANN202
    raw_id = proposal.get("proposal_id") if isinstance(proposal, dict) else None
    existing = {item["proposal_id"] for item in record["proposals"]}
    proposal_id = (
        raw_id
        if (
            isinstance(raw_id, str)
            and _SAFE_ID.fullmatch(raw_id) is not None
            and raw_id not in existing
        )
        else f"rejection-{uuid4().hex}"
    )
    evidence = {
        "schema_version": "predictor_v3.proposal_rejection.v1",
        "campaign_id": record["campaign_id"],
        "proposal_id": proposal_id,
        "status": "proposal_rejected",
        "recorded_at": utc_now(),
        "proposal": deepcopy(proposal),
        "rejection": {"code": error.code, "message": str(error)},
        "training_started": False,
        "iteration_consumed": False,
    }
    reference = store.write_campaign_evidence(
        record["campaign_id"],
        "proposals",
        proposal_id,
        "rejection.json",
        evidence,
    )
    record["proposals"].append({
        "proposal_id": proposal_id,
        "status": "proposal_rejected",
        "evidence_reference": reference,
        "reason_code": error.code,
    })
    record["status"] = "proposal_rejected"
    record["failure"] = evidence["rejection"]
    record["updated_at"] = utc_now()
    store.update_campaign(record["campaign_id"], record)
    return record


def _expected_baseline_reference(record: dict[str, Any]) -> str:
    return (
        record["incumbent_candidate_id"]
        or record["baseline"]["active_candidate_id"]
        or "bootstrap"
    )
