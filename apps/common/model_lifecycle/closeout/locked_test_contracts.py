"""Single-use locked final-test seal contract."""

from __future__ import annotations

from typing import Any

from .canonical import canonical_payload, require_safe_identity, require_sha256
from .contract_validation import identity_array, require_object, required_text
from .contracts import LOCKED_FINAL_TEST_VERSION, SEAL_STATES


def validate_locked_final_test(payload: Any) -> dict[str, Any]:
    value = require_object(payload, "locked final test")
    if value.get("schema_version") != LOCKED_FINAL_TEST_VERSION:
        raise ValueError("unsupported locked final-test version")
    require_safe_identity(value.get("seal_id"), "seal_id")
    if value.get("status") not in SEAL_STATES:
        raise ValueError("unsupported locked final-test state")
    for name in ("data_sha256", "ordered_membership_sha256"):
        require_sha256(value.get(name), name)
    identity_array(value.get("target_identities"), "target_identities")
    required_text(value.get("split_policy"), "split_policy")
    required_text(value.get("creation_identity"), "creation_identity")
    required_text(value.get("created_at"), "locked final-test created_at")
    if value.get("created_before_selection") is not True and (
        value.get("genuinely_unseen_external") is not True
    ):
        raise ValueError("locked final-test leakage boundary is unproven")
    if value["status"] == "consumed":
        required_text(value.get("consumed_at"), "locked final-test consumed_at")
        require_safe_identity(
            value.get("consumed_by_confirmation_id"),
            "consumed_by_confirmation_id",
        )
    return canonical_payload(value)


def build_locked_final_test(
    *,
    seal_id: str,
    data_sha256: str,
    ordered_membership_sha256: str,
    target_identities: list[str],
    split_policy: str,
    created_at: str,
    creation_identity: str,
    created_before_selection: bool = False,
    genuinely_unseen_external: bool = False,
) -> dict[str, Any]:
    return validate_locked_final_test({
        "schema_version": LOCKED_FINAL_TEST_VERSION,
        "seal_id": seal_id,
        "status": "sealed",
        "data_sha256": data_sha256,
        "ordered_membership_sha256": ordered_membership_sha256,
        "target_identities": target_identities,
        "split_policy": split_policy,
        "created_at": created_at,
        "creation_identity": creation_identity,
        "created_before_selection": created_before_selection,
        "genuinely_unseen_external": genuinely_unseen_external,
    })
