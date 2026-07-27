"""Public Phase 5H closeout contract surface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SNAPSHOT_VERSION = "predictor_v3.confirmation_snapshot.v1"
CONFIRMATION_VERSION = "predictor_v3.confirmation.v1"
FINAL_DECISION_VERSION = "predictor_v3.final_decision.v1"
LOCKED_FINAL_TEST_VERSION = "predictor_v3.locked_final_test.v1"
MIGRATION_PREVIEW_VERSION = "predictor_v3.migration_preview.v1"
MIGRATION_RECEIPT_VERSION = "predictor_v3.migration_receipt.v1"
RETENTION_PREVIEW_VERSION = "predictor_v3.retention_preview.v1"
LOADED_MODEL_LEASE_VERSION = "predictor_v3.loaded_model_lease.v1"

SNAPSHOT_STATES = {"creating", "frozen", "failed", "blocked_incomplete"}
CONFIRMATION_STATES = {
    "confirmation_pending",
    "confirmation_running",
    "succeeded",
    "failed",
    "blocked",
    "cancelled",
    "awaiting_user_decision",
}
DECISION_STATES = {"approved", "rejected", "stale"}
SEAL_STATES = {"sealed", "consumed"}


@dataclass(frozen=True)
class ContractDisposition:
    status: str
    executable: bool
    reason_code: str = ""
    message: str = ""
    projection: dict[str, Any] | None = None


# Keep the package's original public import path stable while implementation
# owners stay small and independently reviewable.
from .confirmation_contracts import (  # noqa: E402
    build_confirmation_record,
    build_final_decision,
    validate_confirmation_record,
    validate_final_decision,
)
from .locked_test_contracts import (  # noqa: E402
    build_locked_final_test,
    validate_locked_final_test,
)
from .snapshot_contracts import (  # noqa: E402
    build_snapshot_record,
    validate_snapshot_record,
)

__all__ = [
    "CONFIRMATION_VERSION",
    "FINAL_DECISION_VERSION",
    "LOADED_MODEL_LEASE_VERSION",
    "LOCKED_FINAL_TEST_VERSION",
    "MIGRATION_PREVIEW_VERSION",
    "MIGRATION_RECEIPT_VERSION",
    "RETENTION_PREVIEW_VERSION",
    "SNAPSHOT_VERSION",
    "ContractDisposition",
    "build_confirmation_record",
    "build_final_decision",
    "build_locked_final_test",
    "build_snapshot_record",
    "validate_confirmation_record",
    "validate_final_decision",
    "validate_locked_final_test",
    "validate_snapshot_record",
]
