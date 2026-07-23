"""Filesystem adapter for immutable Candidates and atomic Active references."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

import joblib

from .active_contracts import (
    ACTIVE_REFERENCE_SCHEMA_VERSION,
    ActiveModelReference,
    ActivationRecord,
)
from .candidate_contracts import (
    RESULT_SCHEMA_VERSION,
    CandidateManifest,
    CandidateResult,
)
from .repository_contracts import CandidateSnapshot
from .locking import lifecycle_lock


class ModelLifecycleRepository:
    """Own same-filesystem Candidate publication and Active state."""

    def __init__(self, root: str | Path, *, failure_hook=None) -> None:  # noqa: ANN001
        self.root = Path(root)
        self.candidates_path = self.root / "candidates"
        self.staging_path = self.root / ".staging"
        self.active_reference_path = self.root / "active_model.json"
        self.writer_lock_path = self.root / ".lifecycle-write.lock"
        self._failure_hook = failure_hook or (lambda _stage: None)

    def create_staging(self, candidate_id: str) -> Path:
        _require_safe_identity(candidate_id)
        self.staging_path.mkdir(parents=True, exist_ok=True)
        path = self.staging_path / f"{candidate_id}-{uuid4().hex}"
        path.mkdir()
        return path

    def publish(
        self,
        staging: str | Path,
        manifest: CandidateManifest,
        result: CandidateResult,
    ) -> CandidateSnapshot:
        _require_safe_identity(manifest.candidate_id)
        stage = Path(staging)
        if stage.parent != self.staging_path:
            raise ValueError("Candidate staging must belong to this repository")
        with lifecycle_lock(self.writer_lock_path):
            self._validate_staging(stage, manifest, result)
            self.candidates_path.mkdir(parents=True, exist_ok=True)
            final = self.candidates_path / manifest.candidate_id
            if final.exists():
                existing = self.read_candidate(manifest.candidate_id)
                if existing.manifest == manifest and existing.result == result:
                    shutil.rmtree(stage, ignore_errors=True)
                    return existing
                raise FileExistsError(
                    f"immutable Candidate identity conflict: {manifest.candidate_id}"
                )
            _write_json(stage / "manifest.json", manifest.to_payload())
            _write_json(stage / "result.json", result.to_payload())
            self._fsync_tree(stage)
            self._failure_hook("before_candidate_replace")
            os.replace(stage, final)
            self._fsync_directory(self.candidates_path)
            return self.read_candidate(manifest.candidate_id)

    def read_candidate(self, candidate_id: str) -> CandidateSnapshot:
        _require_safe_identity(candidate_id)
        path = self.candidates_path / candidate_id
        manifest = CandidateManifest.from_payload(_read_json(path / "manifest.json"))
        result_payload = _read_json(path / "result.json")
        if result_payload.get("schema_version") != RESULT_SCHEMA_VERSION:
            raise ValueError("unsupported Candidate result schema version")
        result = CandidateResult(
            run_id=str(result_payload["run_id"]),
            candidate_id=str(result_payload["candidate_id"]),
            status=str(result_payload["status"]),
            publication_outcome=str(result_payload["publication_outcome"]),
            promotion_eligible=bool(result_payload["promotion_eligible"]),
            blocking_reasons=tuple(result_payload.get("blocking_reasons", ())),
        )
        if manifest.candidate_id != candidate_id or result.candidate_id != candidate_id:
            raise ValueError("Candidate identity metadata mismatch")
        self._validate_staging(path, manifest, result, require_metadata=True)
        return CandidateSnapshot(manifest, result, path)

    def list_candidates(self) -> tuple[CandidateSnapshot, ...]:
        if not self.candidates_path.exists():
            return ()
        return tuple(
            self.read_candidate(path.name)
            for path in sorted(self.candidates_path.iterdir())
            if path.is_dir() and not path.name.startswith(".")
        )

    def read_active(self, *, optional: bool = False) -> ActiveModelReference | None:
        if not self.active_reference_path.is_file():
            if optional:
                return None
            raise FileNotFoundError("No Active model has been selected.")
        payload = _read_json(self.active_reference_path)
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

    def replace_active(
        self,
        candidate_id: str,
        *,
        activated_at: str,
        source: str,
        expected_revision: int | None = None,
    ) -> ActiveModelReference:
        with lifecycle_lock(self.writer_lock_path):
            previous = self.read_active(optional=True)
            revision = 1 if previous is None else previous.revision + 1
            if expected_revision is not None and expected_revision != (
                previous.revision if previous else 0
            ):
                raise ValueError("stale Active reference revision")
            record = ActivationRecord(revision, candidate_id, activated_at, source)
            reference = ActiveModelReference(
                candidate_id, revision, activated_at,
                (*previous.history, record) if previous else (record,),
            )
            self.root.mkdir(parents=True, exist_ok=True)
            temporary = self.root / f".active-model-{uuid4().hex}.tmp"
            try:
                _write_json(temporary, reference.to_payload())
                self._fsync_file(temporary)
                self._failure_hook("before_active_replace")
                os.replace(temporary, self.active_reference_path)
                self._fsync_directory(self.root)
            finally:
                temporary.unlink(missing_ok=True)
            return reference

    def _validate_staging(
        self, path: Path, manifest: CandidateManifest, result: CandidateResult,
        *, require_metadata: bool = False,
    ) -> None:
        required = {"model.pkl"}
        if require_metadata:
            required |= {"manifest.json", "result.json"}
        if not path.is_dir() or not required.issubset(
            item.name for item in path.iterdir() if item.is_file()
        ):
            raise ValueError("Candidate artifact set is incomplete")
        model_path = path / "model.pkl"
        if _sha256(model_path) != manifest.model_sha256:
            raise ValueError("Candidate model hash mismatch")
        payload = joblib.load(model_path)
        if not isinstance(payload, dict):
            raise ValueError("Candidate model bundle is invalid")
        models, features = payload.get("models"), payload.get("features")
        if not isinstance(models, dict) or not isinstance(features, dict):
            raise ValueError("Candidate model bundle is incomplete")
        expected = tuple(item.ml_name for item in manifest.targets)
        if set(models) != set(expected) or set(features) != set(expected):
            raise ValueError("Candidate production target order is incomplete")
        for target in manifest.targets:
            if tuple(features[target.ml_name]) != target.feature_names:
                raise ValueError(f"Candidate feature order mismatch: {target.ml_name}")
        if (
            manifest.promotion_eligible
            and payload.get("preprocess_version") != manifest.preprocessing_version
        ):
            raise ValueError("Candidate preprocessing version mismatch")
        contract = payload.get("training_contract")
        expected_contract = {
            "generation_id": manifest.definition_generation_id,
            "registry_fingerprint": manifest.registry_fingerprint,
            "ordered_ml_fingerprint": manifest.ordered_ml_fingerprint,
            "derived_semantics_fingerprint": manifest.derived_semantics_fingerprint,
            "one_hot_fingerprint": manifest.one_hot_fingerprint,
        }
        if manifest.promotion_eligible and (
            not isinstance(contract, dict) or any(
                contract.get(key) != value for key, value in expected_contract.items()
            )
        ):
            raise ValueError("Candidate runtime fingerprint metadata mismatch")

    @staticmethod
    def _fsync_tree(path: Path) -> None:
        for item in sorted(path.rglob("*")):
            if item.is_file():
                ModelLifecycleRepository._fsync_file(item)
        ModelLifecycleRepository._fsync_directory(path)

    @staticmethod
    def _fsync_file(path: Path) -> None:
        with path.open("rb") as source:
            os.fsync(source.fileno())

    @staticmethod
    def _fsync_directory(path: Path) -> None:
        if os.name == "nt":
            return
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def _require_safe_identity(value: str) -> None:
    if not value or value.startswith(".") or "/" in value or "\\" in value:
        raise ValueError("unsafe lifecycle identity")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
