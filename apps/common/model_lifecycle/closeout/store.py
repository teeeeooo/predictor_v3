"""Symlink-safe immutable storage for Phase 5H lifecycle closeout evidence."""

from __future__ import annotations

import hashlib
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from apps.common.model_lifecycle.filesystem import LifecycleFilesystem
from apps.common.model_lifecycle.locking import lifecycle_lock

from .canonical import (
    canonical_payload,
    content_sha256,
    require_safe_identity,
    require_sha256,
)
from .contracts import (
    CONFIRMATION_EXECUTION_CLAIM_VERSION,
    CONFIRMATION_EXECUTION_START_VERSION,
    MIGRATION_PREVIEW_VERSION,
    RETENTION_PREVIEW_VERSION,
    LOADED_MODEL_LEASE_VERSION,
    validate_confirmation_record,
    validate_final_decision,
    validate_locked_final_test,
    validate_locked_final_test_result,
    validate_snapshot_record,
)
from .materialization import TrainingDataMaterializer
from .start_handshake import (
    build_confirmation_start_permit,
    validate_confirmation_start_handshake,
    validate_confirmation_start_permit,
)
from .start_permit_publication import publish_start_permit_atomic


class LifecycleCloseoutStore:
    """Own closeout records without exposing delete or in-place migration APIs."""

    def __init__(
        self,
        lifecycle_root: str | Path,
        *,
        permit_publication_hook=None,  # noqa: ANN001
    ) -> None:
        self._filesystem = LifecycleFilesystem(lifecycle_root)
        self.root = self._filesystem.root
        self.closeout_root = self.root / "closeout"
        self.blobs = self.closeout_root / "blobs" / "sha256"
        self.snapshots = self.closeout_root / "snapshots"
        self.confirmations = self.closeout_root / "confirmations"
        self.confirmation_executions = (
            self.closeout_root / "confirmation_executions"
        )
        self.decisions = self.closeout_root / "decisions"
        self.locked_tests = self.closeout_root / "locked_final_tests"
        self.locked_test_results = (
            self.closeout_root / "locked_final_test_results"
        )
        self.migration_previews = self.closeout_root / "migration_previews"
        self.retention_previews = self.closeout_root / "retention_previews"
        self.loaded_model_leases = self.closeout_root / "loaded_model_leases"
        self.pins = self.closeout_root / "pins"
        self.holds = self.closeout_root / "holds"
        self._materializer = TrainingDataMaterializer(
            self._filesystem,
            self.blobs,
        )
        self._permit_publication_hook = (
            permit_publication_hook or (lambda _stage: None)
        )

    def materialize_local_source(
        self,
        source: str | Path,
        *,
        filtering_meaning: dict[str, Any],
        materialization_kind: str = "owned_source_bytes",
        expected_content_sha256: str | None = None,
        expected_filtering_meaning: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._materializer.materialize_local_source(
            source,
            filtering_meaning=filtering_meaning,
            materialization_kind=materialization_kind,
            expected_content_sha256=expected_content_sha256,
            expected_filtering_meaning=expected_filtering_meaning,
        )

    def validate_external_reference(
        self,
        reference: dict[str, Any],
    ) -> dict[str, Any]:
        return self._materializer.validate_external_reference(reference)

    def owned_materialization_path(self, identity: str) -> Path:
        return self._materializer.owned_materialization_path(identity)

    def verify_owned_materialization(
        self, descriptor: dict[str, Any]
    ) -> Path:
        return self._materializer.verify_owned_materialization(descriptor)

    def write_snapshot(self, payload: dict[str, Any]) -> Path:
        value = validate_snapshot_record(payload)
        return self._write_identity(
            self.snapshots, value["snapshot_id"], "snapshot.json", value
        )

    def read_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        return validate_snapshot_record(
            self._read_identity(self.snapshots, snapshot_id, "snapshot.json")
        )

    def write_confirmation(self, payload: dict[str, Any]) -> Path:
        value = validate_confirmation_record(payload)
        return self._write_identity(
            self.confirmations,
            value["confirmation_id"],
            "confirmation.json",
            value,
        )

    def append_confirmation(
        self,
        payload: dict[str, Any],
        *,
        expected_status: str,
    ) -> Path:
        value = validate_confirmation_record(payload)
        directory = self.confirmations / value["confirmation_id"]
        self._filesystem.require_directory(directory)
        current = self.read_confirmation(value["confirmation_id"])
        if current["status"] != expected_status:
            raise ValueError("stale confirmation state transition")
        history = directory / "history"
        self._filesystem.ensure_directory(history)
        sequence = len(tuple(history.iterdir())) + 1
        filename = f"{sequence:04d}-{value['status']}.json"
        self._filesystem.write_json_exclusive(history / filename, value)
        return history / filename

    def read_confirmation(self, confirmation_id: str) -> dict[str, Any]:
        initial = self._read_identity(
            self.confirmations, confirmation_id, "confirmation.json"
        )
        directory = self.confirmations / confirmation_id
        history = directory / "history"
        payload = initial
        if self._filesystem.entry_exists(history):
            self._filesystem.require_directory(history)
            entries = sorted(history.iterdir())
            if entries:
                payload = self._filesystem.read_json(entries[-1])
        return validate_confirmation_record(payload)

    def find_confirmation_by_execution_key(
        self, execution_key: str
    ) -> dict[str, Any] | None:
        require_sha256(execution_key, "confirmation execution_key")
        try:
            claim = self._read_confirmation_execution_claim(execution_key)
        except FileNotFoundError:
            return None
        return self._read_claimed_confirmation(claim)

    def claim_confirmation_execution(
        self,
        execution_key: str,
        *,
        requested_confirmation_id: str | None,
        pending: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Durably claim one execution meaning before training can start."""
        require_sha256(execution_key, "confirmation execution_key")
        pending_value = validate_confirmation_record(pending)
        confirmation_id = pending_value["confirmation_id"]
        if pending_value.get("execution_key") != execution_key:
            raise ValueError("confirmation execution claim metadata mismatch")
        if (
            requested_confirmation_id is not None
            and requested_confirmation_id != confirmation_id
        ):
            raise ValueError("requested confirmation identity mismatch")
        with lifecycle_lock(
            self.root / ".lifecycle-write.lock",
            filesystem=self._filesystem,
        ):
            try:
                claim = self._read_confirmation_execution_claim(execution_key)
            except FileNotFoundError:
                try:
                    identity_record = self.read_confirmation(confirmation_id)
                except FileNotFoundError:
                    identity_record = None
                if identity_record is not None:
                    if identity_record.get("execution_key") != execution_key:
                        raise ValueError(
                            "confirmation identity belongs to another execution"
                        )
                    return identity_record, False
                claim = {
                    "schema_version": CONFIRMATION_EXECUTION_CLAIM_VERSION,
                    "execution_key": execution_key,
                    "confirmation_id": confirmation_id,
                    "pending_record_sha256": content_sha256(pending_value),
                    "pending_record": pending_value,
                }
                self._write_identity(
                    self.confirmation_executions,
                    execution_key,
                    "claim.json",
                    canonical_payload(claim),
                )
                try:
                    self.write_confirmation(pending_value)
                except Exception:
                    # The claim remains authoritative and contains the exact
                    # pending record needed by a later fail-closed recovery.
                    raise
                return pending_value, True
            try:
                existing = self._read_claimed_confirmation(claim)
            except FileNotFoundError:
                recovered = claim["pending_record"]
                self._recover_confirmation_from_claim(recovered)
                return recovered, True
            return existing, False

    @contextmanager
    def confirmation_execution_owner(
        self,
        execution_key: str,
        *,
        running: dict[str, Any],
    ):
        """Hold one recoverable owner until Core acknowledges actual start."""
        require_sha256(execution_key, "confirmation execution_key")
        running_value = validate_confirmation_record(running)
        if (
            running_value.get("execution_key") != execution_key
            or running_value["status"] != "confirmation_running"
        ):
            raise ValueError("confirmation execution start metadata mismatch")
        owner_lock = self.root / f".confirmation-{execution_key}.lock"
        with lifecycle_lock(owner_lock, filesystem=self._filesystem):
            with lifecycle_lock(
                self.root / ".lifecycle-write.lock",
                filesystem=self._filesystem,
            ):
                record, owns_execution = self._prepare_confirmation_execution(
                    execution_key,
                    running_value,
                )
            yield record, owns_execution

    def mark_confirmation_execution_started(
        self,
        execution_key: str,
        *,
        handshake: dict[str, Any],
    ) -> None:
        """Publish the exact durable permit a waiting child may consume."""
        require_sha256(execution_key, "confirmation execution_key")
        start = validate_confirmation_start_handshake(handshake)
        with lifecycle_lock(
            self.root / ".lifecycle-write.lock",
            filesystem=self._filesystem,
        ):
            claim = self._read_confirmation_execution_claim(execution_key)
            prepared = self._read_confirmation_execution_start(
                execution_key, claim
            )
            current = self._read_claimed_confirmation(claim)
            if (
                start["execution_key"] != execution_key
                or start["confirmation_id"] != claim["confirmation_id"]
                or current != prepared["running_record"]
                or current["status"] != "confirmation_running"
                or start["permit_path"] != str(
                    self.confirmation_execution_start_permit_path(
                        execution_key
                    )
                )
            ):
                raise ValueError(
                    "confirmation execution acknowledgement mismatch"
                )
            registered = self._read_identity(
                self.confirmation_executions
                / execution_key
                / "start_attempts",
                start["attempt_id"],
                "attempt.json",
            )
            if canonical_payload(registered) != start:
                raise ValueError(
                    "confirmation execution attempt registration mismatch"
                )
            directory = self.confirmation_executions / execution_key
            path = directory / "execution_started.json"
            evidence = build_confirmation_start_permit(start)
            if self._filesystem.entry_exists(path):
                try:
                    validate_confirmation_start_permit(
                        self._filesystem.read_json(path), start
                    )
                except ValueError as exc:
                    raise ValueError(
                        "confirmation execution-start evidence conflict"
                    ) from exc
                return
            publish_start_permit_atomic(
                self._filesystem,
                path,
                evidence,
                failure_hook=self._permit_publication_hook,
            )

    def confirmation_execution_start_permit_path(
        self,
        execution_key: str,
    ) -> Path:
        require_sha256(execution_key, "confirmation execution_key")
        return (
            self.confirmation_executions
            / execution_key
            / "execution_started.json"
        )

    def register_confirmation_execution_start_attempt(
        self,
        execution_key: str,
        *,
        handshake: dict[str, Any],
    ) -> None:
        """Bind one launch attempt before its child may request a permit."""
        require_sha256(execution_key, "confirmation execution_key")
        start = validate_confirmation_start_handshake(handshake)
        with lifecycle_lock(
            self.root / ".lifecycle-write.lock",
            filesystem=self._filesystem,
        ):
            claim = self._read_confirmation_execution_claim(execution_key)
            prepared = self._read_confirmation_execution_start(
                execution_key, claim
            )
            current = self._read_claimed_confirmation(claim)
            permit_path = self.confirmation_execution_start_permit_path(
                execution_key
            )
            if (
                start["execution_key"] != execution_key
                or start["confirmation_id"] != claim["confirmation_id"]
                or start["permit_path"] != str(permit_path)
                or current != prepared["running_record"]
                or current["status"] != "confirmation_running"
            ):
                raise ValueError(
                    "confirmation execution attempt identity mismatch"
                )
            if self._filesystem.entry_exists(permit_path):
                self._validate_confirmation_execution_started(
                    permit_path, prepared
                )
                raise ValueError(
                    "confirmation execution already has a durable start permit"
                )
            self._write_identity(
                self.confirmation_executions
                / execution_key
                / "start_attempts",
                start["attempt_id"],
                "attempt.json",
                start,
            )

    def require_confirmation_execution_started(
        self,
        execution_key: str,
    ) -> None:
        require_sha256(execution_key, "confirmation execution_key")
        with lifecycle_lock(
            self.root / ".lifecycle-write.lock",
            filesystem=self._filesystem,
        ):
            claim = self._read_confirmation_execution_claim(execution_key)
            prepared = self._read_confirmation_execution_start(
                execution_key, claim
            )
            current = self._read_claimed_confirmation(claim)
            if current != prepared["running_record"]:
                raise ValueError(
                    "confirmation running evidence changed before completion"
                )
            self._validate_confirmation_execution_started(
                self.confirmation_executions
                / execution_key
                / "execution_started.json",
                prepared,
            )

    def _prepare_confirmation_execution(
        self,
        execution_key: str,
        proposed_running: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        claim = self._read_confirmation_execution_claim(execution_key)
        current = self._read_claimed_confirmation(claim)
        if current["status"] not in {
            "confirmation_pending",
            "confirmation_running",
        }:
            return current, False
        directory = self.confirmation_executions / execution_key
        prepared_path = directory / "start_prepared.json"
        if self._filesystem.entry_exists(prepared_path):
            prepared = self._read_confirmation_execution_start(
                execution_key, claim
            )
        else:
            self._validate_running_transition(
                claim["pending_record"], proposed_running
            )
            prepared = {
                "schema_version": CONFIRMATION_EXECUTION_START_VERSION,
                "execution_key": execution_key,
                "confirmation_id": claim["confirmation_id"],
                "pending_record_sha256": claim["pending_record_sha256"],
                "running_record_sha256": content_sha256(proposed_running),
                "running_record": proposed_running,
            }
            self._filesystem.write_json_exclusive(prepared_path, prepared)
        running = prepared["running_record"]
        started_path = directory / "execution_started.json"
        if self._filesystem.entry_exists(started_path):
            self._validate_confirmation_execution_started(
                started_path, prepared
            )
            if current != running:
                raise ValueError(
                    "execution-start evidence/running record conflict"
                )
            return current, False
        if current["status"] == "confirmation_pending":
            self.append_confirmation(
                running,
                expected_status="confirmation_pending",
            )
        elif current != running:
            raise ValueError(
                "prepared execution/running record identity conflict"
            )
        return running, True

    def _read_confirmation_execution_start(
        self,
        execution_key: str,
        claim: dict[str, Any],
    ) -> dict[str, Any]:
        path = (
            self.confirmation_executions
            / execution_key
            / "start_prepared.json"
        )
        value = canonical_payload(self._filesystem.read_json(path))
        if (
            value.get("schema_version")
            != CONFIRMATION_EXECUTION_START_VERSION
            or value.get("execution_key") != execution_key
            or value.get("confirmation_id") != claim["confirmation_id"]
            or value.get("pending_record_sha256")
            != claim["pending_record_sha256"]
        ):
            raise ValueError("confirmation execution preparation is corrupt")
        running = validate_confirmation_record(value.get("running_record"))
        if (
            content_sha256(running) != value.get("running_record_sha256")
        ):
            raise ValueError(
                "confirmation execution preparation hash mismatch"
            )
        self._validate_running_transition(claim["pending_record"], running)
        return {**value, "running_record": running}

    @staticmethod
    def _validate_running_transition(
        pending: dict[str, Any],
        running: dict[str, Any],
    ) -> None:
        expected = {
            **pending,
            "status": "confirmation_running",
            "updated_at": running["updated_at"],
        }
        if running != validate_confirmation_record(expected):
            raise ValueError(
                "confirmation running transition identity conflict"
            )

    def _validate_confirmation_execution_started(
        self,
        path: Path,
        prepared: dict[str, Any],
    ) -> None:
        value = canonical_payload(self._filesystem.read_json(path))
        try:
            attempt_id = require_safe_identity(
                value.get("attempt_id"),
                "confirmation start attempt_id",
            )
            handshake = self._read_identity(
                self.confirmation_executions
                / prepared["execution_key"]
                / "start_attempts",
                attempt_id,
                "attempt.json",
            )
            start = validate_confirmation_start_handshake(handshake)
            validate_confirmation_start_permit(value, start)
        except (FileNotFoundError, TypeError, ValueError) as exc:
            raise ValueError(
                "confirmation execution-start evidence is corrupt"
            ) from exc
        if (
            start["execution_key"] != prepared["execution_key"]
            or start["confirmation_id"] != prepared["confirmation_id"]
            or start["permit_path"] != str(path)
        ):
            raise ValueError("confirmation execution-start evidence is corrupt")

    def _recover_confirmation_from_claim(
        self, pending: dict[str, Any]
    ) -> None:
        confirmation_id = pending["confirmation_id"]
        directory = self.confirmations / confirmation_id
        record_path = directory / "confirmation.json"
        if not self._filesystem.entry_exists(directory):
            self.write_confirmation(pending)
            return
        self._filesystem.require_directory(directory)
        if self._filesystem.entry_exists(record_path):
            raise ValueError(
                "partial confirmation record is unreadable or corrupt"
            )
        history = directory / "history"
        if self._filesystem.entry_exists(history):
            self._filesystem.require_directory(history)
            if tuple(history.iterdir()):
                raise ValueError(
                    "partial confirmation has history without an initial record"
                )
        self._filesystem.write_json_exclusive(record_path, pending)

    def _read_confirmation_execution_claim(
        self, execution_key: str
    ) -> dict[str, Any]:
        claim = canonical_payload(self._read_identity(
            self.confirmation_executions,
            execution_key,
            "claim.json",
        ))
        if claim.get("schema_version") != CONFIRMATION_EXECUTION_CLAIM_VERSION:
            raise ValueError("unsupported confirmation execution claim version")
        if claim.get("execution_key") != execution_key:
            raise ValueError("confirmation execution claim identity mismatch")
        require_sha256(claim.get("execution_key"), "confirmation execution_key")
        confirmation_id = require_safe_identity(
            claim.get("confirmation_id"), "confirmation_id"
        )
        pending = validate_confirmation_record(claim.get("pending_record"))
        pending_hash = require_sha256(
            claim.get("pending_record_sha256"),
            "pending confirmation record hash",
        )
        if (
            content_sha256(pending) != pending_hash
            or pending["confirmation_id"] != confirmation_id
            or pending.get("execution_key") != execution_key
            or pending["status"] != "confirmation_pending"
        ):
            raise ValueError(
                "partial confirmation execution claim is inconsistent"
            )
        return {
            **claim,
            "pending_record": pending,
        }

    def _read_claimed_confirmation(
        self, claim: dict[str, Any]
    ) -> dict[str, Any]:
        confirmation_id = claim["confirmation_id"]
        initial = validate_confirmation_record(self._read_identity(
            self.confirmations,
            confirmation_id,
            "confirmation.json",
        ))
        if (
            initial != claim["pending_record"]
            or content_sha256(initial) != claim["pending_record_sha256"]
        ):
            raise ValueError(
                "confirmation execution claim/record identity conflict"
            )
        current = self.read_confirmation(confirmation_id)
        if (
            current["confirmation_id"] != confirmation_id
            or current.get("execution_key") != claim["execution_key"]
            or current["snapshot_id"] != initial["snapshot_id"]
            or current["selected_candidate_id"]
            != initial["selected_candidate_id"]
            or current["created_at"] != initial["created_at"]
            or current["production_required_targets"]
            != initial["production_required_targets"]
        ):
            raise ValueError(
                "confirmation execution claim/record identity conflict"
            )
        return current

    def write_decision(self, payload: dict[str, Any]) -> Path:
        value = validate_final_decision(payload)
        return self._write_identity(
            self.decisions, value["decision_id"], "decision.json", value
        )

    def read_decision(self, decision_id: str) -> dict[str, Any]:
        return validate_final_decision(
            self._read_identity(self.decisions, decision_id, "decision.json")
        )

    def find_decision_for_confirmation(
        self, confirmation_id: str
    ) -> dict[str, Any] | None:
        matches = [
            validate_final_decision(item)
            for item in self.list_records(self.decisions, "decision.json")
            if item.get("confirmation_id") == confirmation_id
            and item.get("status") in {"approved", "rejected"}
        ]
        if len(matches) > 1:
            raise ValueError("confirmation has multiple final decisions")
        return matches[0] if matches else None

    def write_locked_final_test(self, payload: dict[str, Any]) -> Path:
        value = validate_locked_final_test(payload)
        return self._write_identity(
            self.locked_tests, value["seal_id"], "seal.json", value
        )

    def read_locked_final_test(self, seal_id: str) -> dict[str, Any]:
        initial = self._read_identity(self.locked_tests, seal_id, "seal.json")
        consumed_path = self.locked_tests / seal_id / "consumed.json"
        payload = (
            self._filesystem.read_json(consumed_path)
            if self._filesystem.entry_exists(consumed_path)
            else initial
        )
        return validate_locked_final_test(payload)

    def read_initial_locked_final_test(
        self, seal_id: str
    ) -> dict[str, Any]:
        return validate_locked_final_test(
            self._read_identity(self.locked_tests, seal_id, "seal.json")
        )

    def consume_locked_final_test(
        self,
        seal_id: str,
        *,
        confirmation_id: str,
        consumed_at: str,
    ) -> dict[str, Any]:
        sealed = self.read_locked_final_test(seal_id)
        if sealed["status"] != "sealed":
            raise ValueError("locked final-test seal is already consumed")
        consumed = {
            **sealed,
            "status": "consumed",
            "consumed_at": consumed_at,
            "consumed_by_confirmation_id": confirmation_id,
        }
        value = validate_locked_final_test(consumed)
        # A consumed record is a new immutable evidence unit. The original seal
        # remains byte-for-byte intact and prevents same-seal execution reuse.
        self._write_transition(
            self.locked_tests / seal_id,
            "consumed.json",
            value,
        )
        return value

    def write_locked_final_test_result(
        self, payload: dict[str, Any]
    ) -> Path:
        value = validate_locked_final_test_result(payload)
        identity = value["result_id"]
        return self._write_identity(
            self.locked_test_results, identity, "result.json", value
        )

    def read_locked_final_test_result(
        self, result_id: str
    ) -> dict[str, Any]:
        return validate_locked_final_test_result(self._read_identity(
            self.locked_test_results, result_id, "result.json"
        ))

    def write_migration_preview(self, payload: dict[str, Any]) -> Path:
        return self._write_versioned_preview(
            self.migration_previews,
            payload,
            expected_version=MIGRATION_PREVIEW_VERSION,
            identity_field="preview_id",
            filename="preview.json",
        )

    def write_retention_preview(self, payload: dict[str, Any]) -> Path:
        return self._write_versioned_preview(
            self.retention_previews,
            payload,
            expected_version=RETENTION_PREVIEW_VERSION,
            identity_field="preview_id",
            filename="preview.json",
        )

    def write_loaded_model_lease(self, payload: dict[str, Any]) -> Path:
        value = canonical_payload(payload)
        if value.get("schema_version") != LOADED_MODEL_LEASE_VERSION:
            raise ValueError("unsupported loaded model lease version")
        lease_id = require_safe_identity(value.get("lease_id"), "lease_id")
        candidate_id = require_safe_identity(
            value.get("candidate_id"), "loaded model candidate_id"
        )
        observed_at = value.get("observed_at")
        if type(observed_at) is not str or not observed_at:
            raise ValueError("loaded model lease observed_at is invalid")
        observed_digest = hashlib.sha256(
            observed_at.encode("utf-8")
        ).hexdigest()[:16]
        event_id = f"{candidate_id}-{observed_digest}"
        return self._write_identity(
            self.loaded_model_leases / lease_id,
            event_id,
            "lease.json",
            value,
        )

    def list_loaded_model_leases(self) -> tuple[dict[str, Any], ...]:
        if not self._filesystem.entry_exists(self.loaded_model_leases):
            return ()
        values = []
        self._filesystem.require_directory(self.loaded_model_leases)
        for lease_directory in sorted(self.loaded_model_leases.iterdir()):
            self._filesystem.require_directory(lease_directory)
            values.extend(
                self.list_records(lease_directory, "lease.json")
            )
        return tuple(values)

    def list_records(
        self, collection: Path, filename: str
    ) -> tuple[dict[str, Any], ...]:
        if not self._filesystem.entry_exists(collection):
            return ()
        self._filesystem.require_directory(collection)
        records = []
        for child in sorted(collection.iterdir()):
            if child.name.startswith("."):
                continue
            self._filesystem.require_directory(child)
            records.append(self._filesystem.read_json(child / filename))
        return tuple(records)

    def _write_versioned_preview(
        self,
        collection: Path,
        payload: dict[str, Any],
        *,
        expected_version: str,
        identity_field: str,
        filename: str,
    ) -> Path:
        value = canonical_payload(payload)
        if value.get("schema_version") != expected_version:
            raise ValueError("unsupported closeout preview version")
        identity = require_safe_identity(value.get(identity_field), identity_field)
        with lifecycle_lock(
            self.root / ".lifecycle-write.lock",
            filesystem=self._filesystem,
        ):
            return self._write_identity(
                collection, identity, filename, value
            )

    def _write_identity(
        self,
        collection: Path,
        identity: str,
        filename: str,
        payload: dict[str, Any],
    ) -> Path:
        require_safe_identity(identity, "closeout record identity")
        self._filesystem.ensure_directory(collection)
        directory = collection / identity
        if self._filesystem.entry_exists(directory):
            existing = self._read_identity(collection, identity, filename)
            if canonical_payload(existing) == canonical_payload(payload):
                return directory / filename
            raise FileExistsError("immutable closeout record identity conflict")
        self._filesystem.create_child_directory(collection, identity)
        self._filesystem.write_json_exclusive(directory / filename, payload)
        return directory / filename

    def _write_transition(
        self, directory: Path, filename: str, payload: dict[str, Any]
    ) -> Path:
        self._filesystem.require_directory(directory)
        path = directory / filename
        if self._filesystem.entry_exists(path):
            raise ValueError("immutable closeout transition already exists")
        self._filesystem.write_json_exclusive(path, payload)
        return path

    def _read_identity(
        self, collection: Path, identity: str, filename: str
    ) -> dict[str, Any]:
        require_safe_identity(identity, "closeout record identity")
        directory = collection / identity
        self._filesystem.require_directory(directory)
        value = self._filesystem.read_json(directory / filename)
        if not isinstance(value, dict):
            raise ValueError("persisted closeout record must be an object")
        return value
