"""Single-use locked final-test seal contract."""

from __future__ import annotations

import math
from typing import Any

from .canonical import (
    canonical_payload,
    content_sha256,
    require_safe_identity,
    require_sha256,
)
from .contract_validation import identity_array, require_object, required_text
from .contracts import (
    LOCKED_FINAL_TEST_RESULT_VERSION,
    LOCKED_FINAL_TEST_VERSION,
    SEAL_STATES,
)


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
    evaluation = require_object(
        value.get("evaluation_contract"), "evaluation_contract"
    )
    require_sha256(evaluation.get("metric_contract"), "metric_contract")
    require_sha256(evaluation.get("schema_contract"), "schema_contract")
    thresholds = evaluation.get("pass_thresholds", {})
    if not isinstance(thresholds, dict):
        raise ValueError("locked final-test thresholds are invalid")
    target_ids = set(value.get("target_identities") or ())
    for target, metrics in thresholds.items():
        if target not in target_ids or not isinstance(metrics, dict):
            raise ValueError("locked final-test threshold Target is invalid")
        for metric, rule in metrics.items():
            if (
                metric not in {"r2", "mae", "rmse"}
                or not isinstance(rule, dict)
                or rule.get("direction") not in {"minimum", "maximum"}
                or not isinstance(rule.get("value"), (int, float))
                or isinstance(rule.get("value"), bool)
                or not math.isfinite(float(rule["value"]))
            ):
                raise ValueError("locked final-test threshold rule is invalid")
    sources = require_object(
        value.get("required_source_hashes"), "required_source_hashes"
    )
    if not sources:
        raise ValueError("locked final-test source hashes are empty")
    for name, digest in sources.items():
        required_text(name, "locked source name")
        require_sha256(digest, "locked source hash")
    dataset = require_object(
        value.get("dataset_reference"), "dataset_reference"
    )
    required_text(dataset.get("path"), "locked dataset path")
    require_sha256(dataset.get("sha256"), "locked dataset reference hash")
    if dataset["sha256"] != value["data_sha256"]:
        raise ValueError("locked dataset reference differs from sealed data")
    computed = locked_final_test_identity(
        data_sha256=value["data_sha256"],
        ordered_membership_sha256=value["ordered_membership_sha256"],
        target_identities=value["target_identities"],
        split_policy=value["split_policy"],
        evaluation_contract=evaluation,
        required_source_hashes=sources,
    )
    if value["seal_id"] != computed:
        raise ValueError("locked final-test seal identity is not canonical")
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
    seal_id: str | None = None,
    data_sha256: str,
    ordered_membership_sha256: str,
    target_identities: list[str],
    split_policy: str,
    created_at: str,
    creation_identity: str,
    evaluation_contract: dict[str, Any],
    required_source_hashes: dict[str, str],
    dataset_reference: dict[str, Any],
    created_before_selection: bool = False,
    genuinely_unseen_external: bool = False,
) -> dict[str, Any]:
    computed = locked_final_test_identity(
        data_sha256=data_sha256,
        ordered_membership_sha256=ordered_membership_sha256,
        target_identities=target_identities,
        split_policy=split_policy,
        evaluation_contract=evaluation_contract,
        required_source_hashes=required_source_hashes,
    )
    if seal_id is not None and seal_id != computed:
        raise ValueError("supplied seal_id differs from canonical evidence")
    return validate_locked_final_test({
        "schema_version": LOCKED_FINAL_TEST_VERSION,
        "seal_id": computed,
        "status": "sealed",
        "data_sha256": data_sha256,
        "ordered_membership_sha256": ordered_membership_sha256,
        "target_identities": target_identities,
        "split_policy": split_policy,
        "evaluation_contract": evaluation_contract,
        "required_source_hashes": required_source_hashes,
        "dataset_reference": dataset_reference,
        "created_at": created_at,
        "creation_identity": creation_identity,
        "created_before_selection": created_before_selection,
        "genuinely_unseen_external": genuinely_unseen_external,
    })


def locked_final_test_identity(
    *,
    data_sha256: str,
    ordered_membership_sha256: str,
    target_identities: list[str],
    split_policy: str,
    evaluation_contract: dict[str, Any],
    required_source_hashes: dict[str, str],
) -> str:
    meaning = {
        "seal_contract_version": LOCKED_FINAL_TEST_VERSION,
        "data_sha256": data_sha256,
        "ordered_membership_sha256": ordered_membership_sha256,
        "target_identities": target_identities,
        "split_policy": split_policy,
        "evaluation_contract": evaluation_contract,
        "required_source_hashes": required_source_hashes,
    }
    return f"locked-final-test-{content_sha256(meaning)}"


def validate_locked_final_test_result(payload: Any) -> dict[str, Any]:
    value = require_object(payload, "locked final-test result")
    if value.get("schema_version") != LOCKED_FINAL_TEST_RESULT_VERSION:
        raise ValueError("unsupported locked final-test result version")
    for name in ("result_id", "seal_id", "confirmation_id", "candidate_id"):
        require_safe_identity(value.get(name), name)
    for name in (
        "candidate_manifest_sha256",
        "data_sha256",
        "ordered_membership_sha256",
    ):
        require_sha256(value.get(name), name)
    if type(value.get("passed")) is not bool:
        raise ValueError("locked final-test result passed flag is invalid")
    results = value.get("target_results")
    if not isinstance(results, list) or not results:
        raise ValueError("locked final-test Target results are incomplete")
    required_text(value.get("created_at"), "locked final-test result created_at")
    meaning = {
        key: value[key]
        for key in (
            "seal_id",
            "confirmation_id",
            "candidate_id",
            "candidate_manifest_sha256",
            "data_sha256",
            "ordered_membership_sha256",
            "target_results",
            "passed",
        )
    }
    if value["result_id"] != f"locked-final-result-{content_sha256(meaning)}":
        raise ValueError("locked final-test result identity is not canonical")
    return canonical_payload(value)
