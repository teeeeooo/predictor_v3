"""Filesystem adapter for immutable Candidates and atomic Active references."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from uuid import uuid4

from .active_contracts import (
    ACTIVE_REFERENCE_SCHEMA_VERSION,
    ActivationRecord,
    ActiveModelReference,
)
from .candidate_validation import load_candidate_model, validate_candidate_files
from .candidate_contracts import (
    CandidateManifest,
    CandidateResult,
)
from .errors import (
    ActiveReferenceCorruptionError,
    CandidateCorruptionError,
    LifecycleFilesystemError,
)
from .durability_errors import PostRenameDurabilityError
from .filesystem import LifecycleFilesystem
from .locking import lifecycle_lock
from .recovery import LifecycleRecovery
from .repository_contracts import CandidateSnapshot


class ModelLifecycleRepository:
    """Own same-filesystem Candidate publication and Active state."""

    def __init__(self, root: str | Path, *, failure_hook=None) -> None:  # noqa: ANN001
        self._filesystem = LifecycleFilesystem(root)
        self.root = self._filesystem.root
        self.candidates_path = self.root / "candidates"
        self.staging_path = self.root / ".staging"
        self.active_reference_path = self.root / "active_model.json"
        self.writer_lock_path = self.root / ".lifecycle-write.lock"
        self._failure_hook = failure_hook or (lambda _stage: None)
        self._recovery = LifecycleRecovery(
            self._filesystem,
            candidates_path=self.candidates_path,
            staging_path=self.staging_path,
            active_reference_path=self.active_reference_path,
        )
        self.active_recovery_path = self._recovery.active_marker

    def create_staging(self, candidate_id: str) -> Path:
        _require_safe_identity(candidate_id)
        self._filesystem.ensure_directory(self.staging_path)
        return self._filesystem.create_child_directory(
            self.staging_path, f"{candidate_id}-{uuid4().hex}"
        )

    def publish(
        self,
        staging: str | Path,
        manifest: CandidateManifest,
        result: CandidateResult,
    ) -> CandidateSnapshot:
        _require_safe_identity(manifest.candidate_id)
        if (
            result.candidate_id != manifest.candidate_id
            or result.run_id != manifest.run_id
        ):
            raise ValueError("Candidate publication identity metadata mismatch")
        stage = self._owned_staging(staging)
        self._filesystem.ensure_directory(self.root)
        self._failure_hook("before_lifecycle_lock")
        with lifecycle_lock(self.writer_lock_path, filesystem=self._filesystem):
            validate_candidate_files(self._filesystem, stage, manifest)
            self._filesystem.ensure_directory(self.candidates_path)
            final = self.candidates_path / manifest.candidate_id
            self._recovery.require_candidate_clear(manifest.candidate_id)
            if self._filesystem.entry_exists(final):
                existing = self.read_candidate(manifest.candidate_id)
                if existing.manifest == manifest and existing.result == result:
                    self._remove_owned_staging(stage)
                    return existing
                raise FileExistsError(
                    f"immutable Candidate identity conflict: {manifest.candidate_id}"
                )
            self._filesystem.write_json_exclusive(
                stage / "manifest.json", manifest.to_payload()
            )
            self._filesystem.write_json_exclusive(
                stage / "result.json", result.to_payload()
            )
            self._filesystem.fsync_tree(stage)
            self._failure_hook("before_candidate_replace")
            recovery = self._recovery.begin_candidate(
                manifest.candidate_id, stage
            )
            try:
                self._filesystem.publish_directory(
                    stage,
                    final,
                    after_replace=lambda: self._failure_hook(
                        "after_candidate_replace"
                    ),
                )
            except PostRenameDurabilityError as exc:
                self._recovery.rollback_candidate(
                    final,
                    stage,
                    before_rollback=lambda: self._failure_hook(
                        "before_candidate_rollback"
                    ),
                    cause=exc,
                )
            except Exception:
                self._filesystem.remove_file(recovery, missing_ok=True)
                raise
            self._recovery.finish_candidate(manifest.candidate_id)
            return self.read_candidate(manifest.candidate_id)

    def read_candidate(self, candidate_id: str) -> CandidateSnapshot:
        _require_safe_identity(candidate_id)
        self._recovery.require_candidate_clear(candidate_id)
        path = self.candidates_path / candidate_id
        if not self._filesystem.entry_exists(path):
            raise FileNotFoundError(f"Candidate does not exist: {candidate_id}")
        try:
            self._filesystem.require_directory(path)
            manifest = CandidateManifest.from_payload(
                self._filesystem.read_json(path / "manifest.json")
            )
            result_payload = self._filesystem.read_json(path / "result.json")
            result = CandidateResult.from_payload(result_payload)
            if (
                manifest.candidate_id != candidate_id
                or result.candidate_id != candidate_id
            ):
                raise ValueError("Candidate identity metadata mismatch")
            validate_candidate_files(
                self._filesystem, path, manifest, require_metadata=True
            )
        except CandidateCorruptionError:
            raise
        except _ARTIFACT_FAILURES as exc:
            raise CandidateCorruptionError(
                f"Candidate {candidate_id} is corrupt: {str(exc).splitlines()[0]}"
            ) from exc
        return CandidateSnapshot(manifest, result, path)

    def discard_staging(self, staging: str | Path) -> None:
        stage = self._owned_staging(staging)
        if self._filesystem.is_owned_directory(stage):
            shutil.rmtree(stage)

    def inspect_staged_model(self, staging: str | Path) -> tuple[str, object]:
        stage = self._owned_staging(staging)
        self._filesystem.require_directory(stage)
        return load_candidate_model(self._filesystem, stage / "model.pkl")

    def copy_model_to_staging(
        self, staging: str | Path, source: str | Path
    ) -> str:
        stage = self._owned_staging(staging)
        self._filesystem.require_directory(stage)
        with Path(source).open("rb") as source_file, (
            self._filesystem.open_exclusive(stage / "model.pkl")
        ) as target:
            shutil.copyfileobj(source_file, target, length=1024 * 1024)
        model_sha256, _payload = load_candidate_model(
            self._filesystem, stage / "model.pkl"
        )
        return model_sha256

    def list_candidates(self) -> tuple[CandidateSnapshot, ...]:
        if not self._filesystem.entry_exists(self.candidates_path):
            return ()
        self._filesystem.require_directory(self.candidates_path)
        snapshots = []
        for path in sorted(self.candidates_path.iterdir()):
            if (
                not path.name.startswith(".")
                and not self._filesystem.entry_exists(
                    self._recovery.candidate_marker(path.name)
                )
                and self._filesystem.is_owned_directory(path)
            ):
                snapshots.append(self.read_candidate(path.name))
        return tuple(snapshots)

    def read_active(self, *, optional: bool = False) -> ActiveModelReference | None:
        self._recovery.require_active_clear()
        if not self._filesystem.entry_exists(self.active_reference_path):
            if optional:
                return None
            raise FileNotFoundError("No Active model has been selected.")
        try:
            payload = self._filesystem.read_json(self.active_reference_path)
            if payload.get("schema_version") != ACTIVE_REFERENCE_SCHEMA_VERSION:
                raise ValueError("unsupported Active reference schema version")
            history = tuple(ActivationRecord(**item) for item in payload["history"])
            reference = ActiveModelReference(
                candidate_id=str(payload["candidate_id"]),
                revision=int(payload["revision"]),
                activated_at=str(payload["activated_at"]),
                history=history,
            )
            if not history or history[-1].revision != reference.revision:
                raise ValueError("Active reference history is inconsistent")
            return reference
        except ActiveReferenceCorruptionError:
            raise
        except _ARTIFACT_FAILURES as exc:
            raise ActiveReferenceCorruptionError(
                f"Active reference is corrupt: {str(exc).splitlines()[0]}"
            ) from exc

    def replace_active(
        self,
        candidate_id: str,
        *,
        activated_at: str,
        source: str,
        expected_revision: int,
    ) -> ActiveModelReference:
        _require_safe_identity(candidate_id)
        if type(expected_revision) is not int or expected_revision < 0:
            raise ValueError("expected Active revision must be a non-negative integer")
        self._filesystem.ensure_directory(self.root)
        self._failure_hook("before_lifecycle_lock")
        with lifecycle_lock(self.writer_lock_path, filesystem=self._filesystem):
            previous = self.read_active(optional=True)
            current_revision = previous.revision if previous else 0
            if expected_revision != current_revision:
                raise ValueError("stale Active reference revision")
            revision = current_revision + 1
            record = ActivationRecord(revision, candidate_id, activated_at, source)
            reference = ActiveModelReference(
                candidate_id,
                revision,
                activated_at,
                (*previous.history, record) if previous else (record,),
            )
            temporary = self.root / f".active-model-{uuid4().hex}.tmp"
            backup = self.root / f".active-model-{uuid4().hex}.backup"
            try:
                self._failure_hook("before_active_temporary_write")
                self._filesystem.write_json_exclusive(
                    temporary, reference.to_payload()
                )
                self._failure_hook("after_active_temporary_fsync")
                self._failure_hook("before_active_replace")
                self._recovery.begin_active(
                    backup,
                    previous_exists=previous is not None,
                    expected_revision=current_revision,
                    intended_revision=revision,
                )
                try:
                    self._filesystem.replace_file(
                        temporary,
                        self.active_reference_path,
                        after_replace=lambda: self._failure_hook(
                            "after_active_replace"
                        ),
                    )
                except PostRenameDurabilityError as exc:
                    self._recovery.rollback_active(
                        backup,
                        previous_exists=previous is not None,
                        before_rollback=lambda: self._failure_hook(
                            "before_active_rollback"
                        ),
                        cause=exc,
                    )
                except Exception:
                    self._recovery.abort_active_before_rename(backup)
                    raise
                self._recovery.finish_active(backup)
            finally:
                self._recovery.cleanup_temporary(temporary, backup)
            return reference

    def recover_candidate_publication(self, candidate_id: str) -> None:
        """Restore a failed publication to staging before removing its marker."""
        _require_safe_identity(candidate_id)
        self._filesystem.ensure_directory(self.root)
        with lifecycle_lock(self.writer_lock_path, filesystem=self._filesystem):
            self._recovery.recover_candidate(candidate_id)

    def recover_active_reference(self) -> ActiveModelReference | None:
        """Restore the pre-mutation Active pointer recorded by the marker."""
        self._filesystem.ensure_directory(self.root)
        with lifecycle_lock(self.writer_lock_path, filesystem=self._filesystem):
            if not self._filesystem.entry_exists(
                self.active_recovery_path
            ):
                return self.read_active(optional=True)
            self._recovery.recover_active()
            return self.read_active(optional=True)

    def _remove_owned_staging(self, stage: Path) -> None:
        self.discard_staging(stage)

    def _owned_staging(self, staging: str | Path) -> Path:
        stage = Path(os.path.abspath(staging))
        if stage.parent != self.staging_path:
            raise LifecycleFilesystemError(
                "Candidate staging must belong to this repository"
            )
        return stage

def _require_safe_identity(value: str) -> None:
    if not value or value.startswith(".") or "/" in value or "\\" in value:
        raise ValueError("unsafe lifecycle identity")


_ARTIFACT_FAILURES = (
    LifecycleFilesystemError,
    json.JSONDecodeError,
    UnicodeError,
    OSError,
    EOFError,
    ImportError,
    AttributeError,
    KeyError,
    TypeError,
    ValueError,
)
