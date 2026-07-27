"""Symlink-safe immutable storage for Phase 5H lifecycle closeout evidence."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from apps.common.model_lifecycle.filesystem import LifecycleFilesystem

from .canonical import (
    canonical_payload,
    require_safe_identity,
)
from .contracts import (
    MIGRATION_PREVIEW_VERSION,
    RETENTION_PREVIEW_VERSION,
    LOADED_MODEL_LEASE_VERSION,
    validate_confirmation_record,
    validate_final_decision,
    validate_locked_final_test,
    validate_snapshot_record,
)
from .materialization import TrainingDataMaterializer


class LifecycleCloseoutStore:
    """Own closeout records without exposing delete or in-place migration APIs."""

    def __init__(self, lifecycle_root: str | Path) -> None:
        self._filesystem = LifecycleFilesystem(lifecycle_root)
        self.root = self._filesystem.root
        self.closeout_root = self.root / "closeout"
        self.blobs = self.closeout_root / "blobs" / "sha256"
        self.snapshots = self.closeout_root / "snapshots"
        self.confirmations = self.closeout_root / "confirmations"
        self.decisions = self.closeout_root / "decisions"
        self.locked_tests = self.closeout_root / "locked_final_tests"
        self.migration_previews = self.closeout_root / "migration_previews"
        self.retention_previews = self.closeout_root / "retention_previews"
        self.loaded_model_leases = self.closeout_root / "loaded_model_leases"
        self._materializer = TrainingDataMaterializer(
            self._filesystem,
            self.blobs,
        )

    def materialize_local_source(
        self,
        source: str | Path,
        *,
        filtering_meaning: dict[str, Any],
        materialization_kind: str = "owned_source_bytes",
    ) -> dict[str, Any]:
        return self._materializer.materialize_local_source(
            source,
            filtering_meaning=filtering_meaning,
            materialization_kind=materialization_kind,
        )

    def validate_external_reference(
        self,
        reference: dict[str, Any],
    ) -> dict[str, Any]:
        return self._materializer.validate_external_reference(reference)

    def owned_materialization_path(self, identity: str) -> Path:
        return self._materializer.owned_materialization_path(identity)

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

    def write_decision(self, payload: dict[str, Any]) -> Path:
        value = validate_final_decision(payload)
        return self._write_identity(
            self.decisions, value["decision_id"], "decision.json", value
        )

    def read_decision(self, decision_id: str) -> dict[str, Any]:
        return validate_final_decision(
            self._read_identity(self.decisions, decision_id, "decision.json")
        )

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
        return self._write_identity(collection, identity, filename, value)

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
