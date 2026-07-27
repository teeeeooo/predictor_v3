"""Persisted confirmation transition projections."""

from __future__ import annotations

from typing import Any

from apps.common.model_lifecycle.closeout.contracts import (
    LOCKED_FINAL_TEST_VERSION,
)


def record_arguments(record: dict[str, Any]) -> dict[str, Any]:
    return {
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


def locked_projection(
    value: dict[str, Any] | None,
    *,
    consumed: bool,
    independent_passed: bool = False,
) -> dict[str, Any]:
    if value is None:
        return {
            "configured": False,
            "status": "not_configured",
            "independent_final_test_passed": False,
        }
    return {
        "configured": True,
        "seal_id": value["seal_id"],
        "schema_version": LOCKED_FINAL_TEST_VERSION,
        "status": "consumed" if consumed else "sealed",
        "independent_final_test_passed": bool(independent_passed),
    }


def blocked_outcome(code: str, message: str) -> dict[str, Any]:
    return {
        "status": "blocked",
        "reason_code": code,
        "message": message,
    }
