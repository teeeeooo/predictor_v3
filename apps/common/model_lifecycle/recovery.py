"""Recovery markers for post-rename Candidate and Active durability failures."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from .durability_errors import (
    ActiveCommittedCleanupError,
    LifecycleDurabilityError,
    LifecycleRecoveryRequiredError,
)
from .errors import LifecycleFilesystemError
from .filesystem import LifecycleFilesystem


class LifecycleRecovery:
    """Keep indeterminate mutations hidden and restore their previous state."""

    def __init__(
        self,
        filesystem: LifecycleFilesystem,
        *,
        candidates_path: Path,
        staging_path: Path,
        active_reference_path: Path,
    ) -> None:
        self._filesystem = filesystem
        self.root = filesystem.root
        self.candidates_path = candidates_path
        self.staging_path = staging_path
        self.active_reference_path = active_reference_path
        self.active_marker = self.root / ".active-recovery.json"

    def candidate_marker(self, candidate_id: str) -> Path:
        return self.root / f".candidate-recovery-{candidate_id}.json"

    def require_candidate_clear(self, candidate_id: str) -> None:
        if self._filesystem.entry_exists(self.candidate_marker(candidate_id)):
            raise LifecycleRecoveryRequiredError(
                f"Candidate {candidate_id} requires publication recovery"
            )

    def begin_candidate(self, candidate_id: str, staging: Path) -> Path:
        marker = self.candidate_marker(candidate_id)
        self._filesystem.write_json_exclusive(
            marker,
            {
                "candidate_id": candidate_id,
                "staging_name": staging.name,
                "status": "publishing",
            },
        )
        return marker

    def rollback_candidate(
        self,
        final: Path,
        staging: Path,
        *,
        before_rollback,
        cause: Exception,
    ) -> None:  # noqa: ANN001
        marker = self.candidate_marker(final.name)
        try:
            before_rollback()
            self._filesystem.rollback_directory(final, staging)
            self._cleanup_marker(marker)
        except Exception as rollback_exc:
            raise LifecycleRecoveryRequiredError(
                "Candidate publication recovery required after rollback failure"
            ) from rollback_exc
        raise LifecycleDurabilityError(
            "Candidate publication durability failed; publication rolled back"
        ) from cause

    def finish_candidate(self, candidate_id: str) -> None:
        try:
            self._cleanup_marker(self.candidate_marker(candidate_id))
        except Exception as exc:
            raise LifecycleRecoveryRequiredError(
                "Candidate publication committed but recovery marker cleanup failed"
            ) from exc

    def recover_candidate(self, candidate_id: str) -> None:
        marker = self.candidate_marker(candidate_id)
        if not self._filesystem.entry_exists(marker):
            return
        payload = self._filesystem.read_json(marker)
        staging_name = str(payload.get("staging_name", ""))
        if (
            payload.get("candidate_id") != candidate_id
            or not staging_name
            or "/" in staging_name
            or "\\" in staging_name
        ):
            raise LifecycleRecoveryRequiredError(
                "Candidate recovery marker is invalid"
            )
        final = self.candidates_path / candidate_id
        staging = self.staging_path / staging_name
        final_exists = self._filesystem.entry_exists(final)
        staging_exists = self._filesystem.entry_exists(staging)
        if final_exists and not staging_exists:
            self._filesystem.rollback_directory(final, staging)
        elif final_exists == staging_exists:
            raise LifecycleRecoveryRequiredError(
                "Candidate recovery state is ambiguous"
            )
        self._cleanup_marker(marker)

    def require_active_clear(self) -> None:
        if self._filesystem.entry_exists(self.active_marker):
            raise LifecycleRecoveryRequiredError(
                "Active reference recovery is required before it can be resolved"
            )

    def begin_active(
        self,
        backup: Path,
        *,
        previous_exists: bool,
        expected_revision: int,
        intended_revision: int,
    ) -> None:
        if previous_exists:
            self._filesystem.copy_regular_exclusive(
                self.active_reference_path, backup
            )
        self._filesystem.write_json_exclusive(
            self.active_marker,
            {
                "backup_name": backup.name if previous_exists else "",
                "expected_revision": expected_revision,
                "intended_revision": intended_revision,
                "status": "replacing",
            },
        )

    def rollback_active(
        self,
        backup: Path,
        *,
        previous_exists: bool,
        before_rollback,
        cause: Exception,
    ) -> None:  # noqa: ANN001
        try:
            before_rollback()
            if previous_exists:
                self._filesystem.replace_file(
                    backup, self.active_reference_path
                )
            else:
                self._filesystem.remove_file(self.active_reference_path)
            self._cleanup_marker(self.active_marker)
        except Exception as rollback_exc:
            raise LifecycleRecoveryRequiredError(
                "Active reference recovery required after rollback failure"
            ) from rollback_exc
        raise LifecycleDurabilityError(
            "Active reference durability failed; activation rolled back"
        ) from cause

    def abort_active_before_rename(self, backup: Path) -> None:
        self._filesystem.remove_file(backup, missing_ok=True)
        self._cleanup_marker(self.active_marker)

    def finish_active(
        self,
        backup: Path,
        *,
        previous_exists: bool,
        before_backup_cleanup,
        before_marker_cleanup,
    ) -> None:  # noqa: ANN001
        payload = self._filesystem.read_json(self.active_marker)
        intended_revision = payload.get("intended_revision")
        if type(intended_revision) is not int or intended_revision < 1:
            raise LifecycleRecoveryRequiredError(
                "Active recovery marker is invalid"
            )
        committed = dict(payload)
        committed["status"] = "committed"
        try:
            self._replace_active_marker(committed)
        except Exception as exc:
            self.rollback_active(
                backup,
                previous_exists=previous_exists,
                before_rollback=lambda: None,
                cause=exc,
            )
        try:
            before_backup_cleanup()
            self._filesystem.remove_file(backup, missing_ok=True)
            before_marker_cleanup()
            self._cleanup_marker(self.active_marker)
        except Exception as exc:
            raise ActiveCommittedCleanupError(
                "Active reference committed but forward cleanup is required",
                revision=intended_revision,
            ) from exc

    def recover_active(self) -> None:
        if not self._filesystem.entry_exists(self.active_marker):
            return
        payload = self._filesystem.read_json(self.active_marker)
        backup_name = str(payload.get("backup_name", ""))
        expected_revision = payload.get("expected_revision")
        intended_revision = payload.get("intended_revision")
        status = payload.get("status")
        if (
            type(expected_revision) is not int
            or expected_revision < 0
            or type(intended_revision) is not int
            or intended_revision != expected_revision + 1
            or status not in {"replacing", "committed"}
        ):
            raise LifecycleRecoveryRequiredError(
                "Active recovery marker is invalid"
            )
        if status == "committed":
            self._reconcile_committed_active(backup_name, intended_revision)
            return
        if backup_name:
            self._restore_active_backup(backup_name, expected_revision)
        elif self._filesystem.entry_exists(self.active_reference_path):
            self._filesystem.remove_file(self.active_reference_path)
        self._cleanup_marker(self.active_marker)

    def cleanup_temporary(self, temporary: Path, backup: Path) -> None:
        self._remove_owned_file_best_effort(temporary)
        if not self._filesystem.entry_exists(self.active_marker):
            self._remove_owned_file_best_effort(backup)

    def _restore_active_backup(
        self, backup_name: str, expected_revision: int
    ) -> None:
        self._require_backup_name(backup_name)
        backup = self.root / backup_name
        if self._filesystem.entry_exists(backup):
            self._filesystem.replace_file(backup, self.active_reference_path)
            return
        if not self._filesystem.entry_exists(self.active_reference_path):
            raise LifecycleRecoveryRequiredError(
                "Active recovery backup is missing"
            )
        current = self._filesystem.read_json(self.active_reference_path)
        if current.get("revision") != expected_revision:
            raise LifecycleRecoveryRequiredError(
                "Active recovery backup is missing"
            )

    def _reconcile_committed_active(
        self, backup_name: str, intended_revision: int
    ) -> None:
        if not self._filesystem.entry_exists(self.active_reference_path):
            raise LifecycleRecoveryRequiredError(
                "Committed Active reference is missing"
            )
        current = self._filesystem.read_json(self.active_reference_path)
        history = current.get("history")
        if (
            current.get("revision") != intended_revision
            or not isinstance(history, list)
            or not history
            or not isinstance(history[-1], dict)
            or history[-1].get("revision") != intended_revision
        ):
            raise LifecycleRecoveryRequiredError(
                "Committed Active reference does not match recovery marker"
            )
        if backup_name:
            self._require_backup_name(backup_name)
            self._filesystem.remove_file(
                self.root / backup_name, missing_ok=True
            )
        self._cleanup_marker(self.active_marker)

    def _replace_active_marker(self, payload: dict[str, object]) -> None:
        temporary = self.root / f".active-recovery-{uuid4().hex}.tmp"
        try:
            self._filesystem.write_json_exclusive(temporary, payload)
            self._filesystem.replace_file(temporary, self.active_marker)
        finally:
            self._remove_owned_file_best_effort(temporary)

    @staticmethod
    def _require_backup_name(backup_name: str) -> None:
        if (
            not backup_name.startswith(".active-model-")
            or not backup_name.endswith(".backup")
            or "/" in backup_name
            or "\\" in backup_name
        ):
            raise LifecycleRecoveryRequiredError(
                "Active recovery backup identity is invalid"
            )

    def _cleanup_marker(self, path: Path) -> None:
        try:
            self._filesystem.remove_file(path)
        except Exception:
            if self._filesystem.entry_exists(path):
                raise

    def _remove_owned_file_best_effort(self, path: Path) -> None:
        try:
            self._filesystem.remove_file(path, missing_ok=True)
        except (FileNotFoundError, LifecycleFilesystemError):
            pass
