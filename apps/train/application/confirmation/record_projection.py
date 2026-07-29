"""Persisted confirmation transition projections."""

from __future__ import annotations

from typing import Any

from apps.common.model_lifecycle.closeout.contracts import (
    LOCKED_FINAL_TEST_VERSION,
)
from apps.common.model_lifecycle.closeout.canonical import content_sha256


def record_arguments(record: dict[str, Any]) -> dict[str, Any]:
    values = {
        key: record[key]
        for key in (
            "confirmation_id",
            "snapshot_id",
            "selected_candidate_id",
            "created_at",
            "production_required_targets",
            "target_results",
            "confirmation_candidate_id",
            "confirmation_candidate_manifest_sha256",
            "locked_final_test",
            "blocking_reasons",
        )
    }
    values["execution_key"] = record.get("execution_key")
    return values


def locked_projection(
    value: dict[str, Any] | None,
    *,
    consumed: bool,
    independent_passed: bool = False,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if value is None:
        return {
            "configured": False,
            "status": "not_configured",
            "independent_final_test_passed": False,
        }
    projection = {
        "configured": True,
        "seal_id": value["seal_id"],
        "schema_version": LOCKED_FINAL_TEST_VERSION,
        "status": "consumed" if consumed else "sealed",
        "independent_final_test_passed": bool(independent_passed),
    }
    if result is not None:
        projection["result_id"] = result["result_id"]
        projection["result_evidence_sha256"] = content_sha256(result)
    return projection


def blocked_outcome(code: str, message: str) -> dict[str, Any]:
    return {
        "status": "blocked",
        "reason_code": code,
        "message": message,
    }
