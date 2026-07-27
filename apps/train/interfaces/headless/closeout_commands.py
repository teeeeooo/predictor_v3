"""Headless adapters for Phase 5H; approval remains interactive user-only."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from apps.common.model_lifecycle.closeout.compatibility import (
    inspect_persisted_contract,
)
from apps.common.model_lifecycle.closeout.retention import RetentionPolicy
from apps.train.composition.confirmation import (
    build_headless_confirmation_services,
)

from .command_contract import EXIT_SUCCESS, emit

_COMMANDS = {
    "snapshot-preflight",
    "snapshot-freeze",
    "snapshot-inspect",
    "confirmation-preflight",
    "confirmation-start",
    "confirmation-inspect",
    "locked-final-test-status",
    "final-decision",
    "final-decision-inspect",
    "compatibility-disposition",
    "retention-preview",
}


def dispatch_closeout(args, lifecycle_root: Path) -> int | None:  # noqa: ANN001
    if args.command not in _COMMANDS:
        return None
    services = build_headless_confirmation_services(
        lifecycle_root=lifecycle_root
    )
    snapshots = services["snapshots"]
    confirmations = services["confirmations"]
    decisions = services["decisions"]
    closeout = services["closeout_store"]
    if args.command in {"snapshot-preflight", "snapshot-freeze"}:
        method = (
            snapshots.preflight
            if args.command == "snapshot-preflight"
            else snapshots.freeze
        )
        kwargs = {"selected_candidate_id": args.candidate_id}
        if args.command == "snapshot-freeze":
            kwargs["actor_kind"] = "user"
        outcome = method(
            args.campaign_id,
            args.recommendation_id,
            **kwargs,
        )
        emit(
            args.command,
            outcome.status,
            outcome.message or "Snapshot command completed.",
            data=outcome.record,
        )
        return EXIT_SUCCESS
    if args.command == "snapshot-inspect":
        outcome = snapshots.inspect(args.snapshot_id)
        emit(args.command, outcome.status, outcome.message or "Snapshot loaded.", data=outcome.record)
        return EXIT_SUCCESS
    if args.command == "confirmation-preflight":
        value = confirmations.preflight(
            args.snapshot_id,
            locked_final_test_seal_id=args.locked_final_test_seal_id,
        )
    elif args.command == "confirmation-start":
        value = confirmations.start(
            args.snapshot_id,
            confirmation_id=args.confirmation_id,
            locked_final_test_seal_id=args.locked_final_test_seal_id,
        )
    elif args.command == "confirmation-inspect":
        value = confirmations.inspect(args.confirmation_id)
    elif args.command == "locked-final-test-status":
        value = closeout.read_locked_final_test(args.seal_id)
    elif args.command == "final-decision-inspect":
        value = decisions.inspect(args.decision_id)
    elif args.command == "final-decision":
        _require_exact_user_authority(args)
        outcome = decisions.decide(
            args.confirmation_id,
            approve=args.decision == "approve",
            authority=services["authority_issuer"].issue(
                args.authority_context
            ),
            expected_active_revision=args.expected_active_revision,
            decision_id=args.decision_id,
            reason=args.reason,
        )
        value = {
            "decision": outcome.decision,
            "promotion": (
                {
                    "status": outcome.promotion.status,
                    "candidate_id": outcome.promotion.candidate_id,
                    "revision": outcome.promotion.revision,
                    "reason_code": outcome.promotion.reason_code,
                }
                if outcome.promotion else None
            ),
        }
    elif args.command == "compatibility-disposition":
        payload = json.loads(Path(args.record).read_text(encoding="utf-8"))
        disposition = inspect_persisted_contract(args.kind, payload)
        value = {
            "status": disposition.status,
            "executable": disposition.executable,
            "reason_code": disposition.reason_code,
            "message": disposition.message,
            "projection": disposition.projection,
        }
    else:
        value = services["retention"].preview(RetentionPolicy(
            minimum_age_days=args.minimum_age_days,
            keep_latest_count=args.keep_latest_count,
            maximum_reclaim_bytes=args.maximum_reclaim_bytes,
        ))
    outcome_name = (
        value.get("status", "success")
        if isinstance(value, dict)
        else "success"
    )
    emit(args.command, outcome_name, "Phase 5H command completed.", data=value)
    return EXIT_SUCCESS


def _require_exact_user_authority(args) -> None:  # noqa: ANN001
    if (
        not sys.stdin.isatty()
        or args.confirm_exact != args.confirmation_id
        or not args.authority_context
    ):
        raise PermissionError(
            "Final decision requires an interactive user and exact confirmation ID."
        )
