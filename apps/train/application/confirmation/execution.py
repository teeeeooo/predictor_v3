"""Confirmation orchestration over one frozen snapshot and an execution port."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from apps.common.model_lifecycle.closeout.canonical import file_sha256
from apps.common.model_lifecycle.closeout.contracts import (
    build_confirmation_record,
)
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.common.model_lifecycle.promotion import ModelPromotionService
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.common.runtime_generation.repository import (
    DataDefinitionGenerationRepository,
)

from .execution_contracts import (
    ConfirmationExecutionPort,
    ConfirmationExecutionResult,
    FrozenConfirmationRequest,
)
from .record_projection import (
    blocked_outcome,
    locked_projection,
    record_arguments,
)


class ConfirmationApplicationService:
    def __init__(
        self,
        repository: ModelLifecycleRepository,
        generations: DataDefinitionGenerationRepository,
        promotion: ModelPromotionService,
        execution: ConfirmationExecutionPort,
        *,
        closeout_store: LifecycleCloseoutStore | None = None,
        build_identity_provider=None,  # noqa: ANN001
        clock=None,  # noqa: ANN001
    ) -> None:
        self._repository = repository
        self._generations = generations
        self._promotion = promotion
        self._execution = execution
        self._store = closeout_store or LifecycleCloseoutStore(repository.root)
        self._build_identity = build_identity_provider
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def preflight(
        self,
        snapshot_id: str,
        *,
        locked_final_test_seal_id: str | None = None,
    ) -> dict[str, Any]:
        snapshot = self._store.read_snapshot(snapshot_id)
        if snapshot["status"] != "frozen":
            return blocked_outcome("snapshot_not_frozen", "Snapshot is not frozen.")
        meaning = snapshot["meaning"]
        try:
            self._validate_current_meaning(meaning)
            request = self._request(
                snapshot,
                confirmation_id="confirmation-preflight",
                locked_final_test_seal_id=locked_final_test_seal_id,
            )
        except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
            return blocked_outcome(
                "confirmation_preflight_blocked", str(exc).splitlines()[0]
            )
        return {
            "status": "confirmation_pending",
            "snapshot_id": snapshot_id,
            "production_required_targets": list(
                request.production_required_targets
            ),
            "locked_final_test": (
                "sealed" if request.locked_final_test else "not_configured"
            ),
            "search_disabled": True,
        }

    def start(
        self,
        snapshot_id: str,
        *,
        confirmation_id: str | None = None,
        locked_final_test_seal_id: str | None = None,
    ) -> dict[str, Any]:
        identity = confirmation_id or f"confirmation-{uuid4().hex}"
        now = self._clock().isoformat()
        try:
            snapshot = self._store.read_snapshot(snapshot_id)
            if snapshot["status"] != "frozen":
                raise ValueError("confirmation requires one frozen snapshot")
            self._validate_current_meaning(snapshot["meaning"])
            request = self._request(
                snapshot,
                confirmation_id=identity,
                locked_final_test_seal_id=locked_final_test_seal_id,
            )
            pending = build_confirmation_record(
                confirmation_id=identity,
                snapshot_id=snapshot_id,
                selected_candidate_id=request.selected_candidate_id,
                status="confirmation_pending",
                created_at=now,
                updated_at=now,
                production_required_targets=list(
                    request.production_required_targets
                ),
                locked_final_test=locked_projection(
                    request.locked_final_test, consumed=False
                ),
            )
            self._store.write_confirmation(pending)
            running = build_confirmation_record(
                **{
                    **record_arguments(pending),
                    "status": "confirmation_running",
                    "updated_at": self._clock().isoformat(),
                }
            )
            self._store.append_confirmation(
                running, expected_status="confirmation_pending"
            )
            if locked_final_test_seal_id:
                self._store.consume_locked_final_test(
                    locked_final_test_seal_id,
                    confirmation_id=identity,
                    consumed_at=self._clock().isoformat(),
                )
            result = self._execution.execute(request)
            return self._finish(running, request, result)
        except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
            try:
                current = self._store.read_confirmation(identity)
            except (FileNotFoundError, OSError, TypeError, ValueError):
                return blocked_outcome(
                    "confirmation_start_blocked", str(exc).splitlines()[0]
                )
            blocked = build_confirmation_record(
                **{
                    **record_arguments(current),
                    "status": "blocked",
                    "updated_at": self._clock().isoformat(),
                    "blocking_reasons": [{
                        "code": "confirmation_start_blocked",
                        "reason": str(exc).splitlines()[0],
                    }],
                }
            )
            self._store.append_confirmation(
                blocked, expected_status=current["status"]
            )
            return blocked

    def inspect(self, confirmation_id: str) -> dict[str, Any]:
        return self._store.read_confirmation(confirmation_id)

    def _finish(
        self,
        running: dict[str, Any],
        request: FrozenConfirmationRequest,
        result: ConfirmationExecutionResult,
    ) -> dict[str, Any]:
        if result.status == "cancelled":
            status = "cancelled"
            blockers = [{"code": "confirmation_cancelled", "reason": result.message}]
            candidate_id = None
            candidate_hash = None
        elif result.status != "succeeded":
            status = "failed"
            blockers = [{
                "code": result.reason_code or "confirmation_execution_failed",
                "reason": result.message or "Confirmation execution failed.",
            }]
            candidate_id = None
            candidate_hash = None
        else:
            try:
                candidate_id, candidate_hash = self._validate_success(
                    request, result
                )
            except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
                status = "failed"
                blockers = [{
                    "code": "confirmation_evidence_invalid",
                    "reason": str(exc).splitlines()[0],
                }]
                candidate_id = None
                candidate_hash = None
            else:
                if (
                    request.locked_final_test
                    and not result.independent_final_test_passed
                ):
                    status = "failed"
                    blockers = [{
                        "code": "locked_final_test_failed",
                        "reason": (
                            "Configured locked final-test did not produce "
                            "passing independent evidence."
                        ),
                    }]
                else:
                    status = "awaiting_user_decision"
                    blockers = []
        locked = locked_projection(
            request.locked_final_test,
            consumed=bool(request.locked_final_test),
            independent_passed=(
                result.independent_final_test_passed
                if request.locked_final_test
                else False
            ),
        )
        completed = build_confirmation_record(
            **{
                **record_arguments(running),
                "status": status,
                "updated_at": self._clock().isoformat(),
                "target_results": list(result.target_results),
                "confirmation_candidate_id": candidate_id,
                "confirmation_candidate_manifest_sha256": candidate_hash,
                "locked_final_test": locked,
                "blocking_reasons": blockers,
            }
        )
        self._store.append_confirmation(
            completed, expected_status="confirmation_running"
        )
        return completed

    def _validate_success(
        self,
        request: FrozenConfirmationRequest,
        result: ConfirmationExecutionResult,
    ) -> tuple[str, str]:
        required = set(request.production_required_targets)
        complete = {
            item.get("target_identity")
            for item in result.target_results
            if item.get("status") == "complete"
        }
        if complete != required:
            raise ValueError(
                "confirmation did not complete every production-required Target"
            )
        candidate = self._repository.read_candidate(
            result.confirmation_candidate_id
        )
        if candidate.manifest.source != "confirmation":
            raise ValueError("confirmation Candidate source is not confirmation")
        if set(item.identity for item in candidate.manifest.targets) != required:
            raise ValueError("confirmation Candidate Target set is incomplete")
        compatibility = self._promotion.inspect_compatibility(
            candidate.manifest.candidate_id
        )
        if compatibility.status != "compatible":
            raise ValueError(
                compatibility.reason_code
                or "confirmation Candidate lifecycle compatibility failed"
            )
        self._validate_current_meaning(
            self._store.read_snapshot(request.snapshot_id)["meaning"]
        )
        return (
            candidate.manifest.candidate_id,
            file_sha256(candidate.path / "manifest.json"),
        )

    def _validate_current_meaning(self, meaning: dict[str, Any]) -> None:
        selected = meaning["selected_candidate"]
        candidate = self._repository.read_candidate(selected["candidate_id"])
        if file_sha256(candidate.path / "manifest.json") != selected[
            "manifest_sha256"
        ]:
            raise ValueError("selected Candidate manifest changed")
        generation = meaning["definition_runtime"]["generation_id"]
        if self._generations.active_generation_id() != generation:
            raise ValueError("Definition/runtime generation changed")
        self._generations.read_generation(generation)
        compatibility = self._promotion.inspect_compatibility(
            selected["candidate_id"]
        )
        if compatibility.status != "compatible":
            raise ValueError(
                compatibility.reason_code
                or "selected Candidate lifecycle compatibility changed"
            )
        if self._build_identity is not None:
            current = self._build_identity()
            if current != meaning["build_identity"]:
                raise ValueError("training-semantic build identity changed")

    def _request(
        self,
        snapshot: dict[str, Any],
        *,
        confirmation_id: str,
        locked_final_test_seal_id: str | None,
    ) -> FrozenConfirmationRequest:
        meaning = snapshot["meaning"]
        roles = meaning["target_roles"]
        required = tuple(roles["production_required"])
        if not required:
            raise ValueError("snapshot has no production-required Targets")
        parameters = meaning["training_configuration"]["selected_parameters"]
        if set(parameters) != set(required):
            raise ValueError(
                "frozen selected parameters do not cover production Targets"
            )
        if (
            meaning["training_configuration"].get(
                "search_disabled_for_confirmation"
            )
            is not True
        ):
            raise ValueError("confirmation search boundary is not frozen")
        if meaning["resolved_specification"]["features"]["experimental_derived"]:
            raise ValueError("experimental Candidate cannot enter confirmation")
        locked = None
        if locked_final_test_seal_id:
            locked = self._store.read_locked_final_test(
                locked_final_test_seal_id
            )
            if locked["status"] != "sealed":
                raise ValueError("locked final-test seal is already consumed")
            if set(locked["target_identities"]) != set(required):
                raise ValueError("locked final-test Target set differs")
        return FrozenConfirmationRequest(
            confirmation_id,
            snapshot["snapshot_id"],
            meaning["selected_candidate"]["candidate_id"],
            meaning["resolved_specification"],
            required,
            parameters,
            meaning["training_data"],
            meaning["definition_runtime"],
            meaning["evaluation_contract"],
            locked,
        )
