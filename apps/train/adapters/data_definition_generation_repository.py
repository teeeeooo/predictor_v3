"""Filesystem adapter for immutable Unified Feature generation bundles."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Callable
from uuid import uuid4

from apps.train.application.data_definition import (
    GenerationPublishResult,
    GenerationSnapshot,
)
from core.data_definition.contract import (
    ContractProjections,
    ScopedFingerprints,
    UnifiedFeatureManifest,
    dump_manifest,
    generate_projections,
    load_manifest,
    ml_csv_text,
    predict_csv_text,
    require_valid_contract,
    scoped_fingerprints,
)

FailureHook = Callable[[str], None]


class DataDefinitionGenerationRepository:
    """Publish complete same-filesystem bundles, then atomically replace a pointer."""

    def __init__(self, root: str | Path, *, failure_hook: FailureHook | None = None) -> None:
        self.root = Path(root)
        self.generations_path = self.root / "generations"
        self.active_pointer_path = self.root / "active_generation.json"
        self._failure_hook = failure_hook or (lambda _stage: None)

    def publish(self, manifest: UnifiedFeatureManifest) -> GenerationPublishResult:
        projections = require_valid_contract(manifest)
        fingerprints = scoped_fingerprints(manifest)
        generation_id = manifest.generation.generation_id
        if not generation_id or "/" in generation_id or generation_id.startswith("."):
            raise ValueError("generation_id is not a safe immutable bundle name")
        previous = self.active_generation_id(optional=True)
        self.generations_path.mkdir(parents=True, exist_ok=True)
        final_path = self.generations_path / generation_id
        if final_path.exists():
            existing = self.read_generation(generation_id)
            if existing.fingerprints.combined != fingerprints.combined:
                raise FileExistsError(f"immutable generation already exists: {generation_id}")
        else:
            self._stage_and_publish(manifest, projections, fingerprints, final_path)
        self._failure_hook("before_pointer_replace")
        self._replace_active_pointer(generation_id)
        return GenerationPublishResult(generation_id, previous, final_path)

    def active_generation_id(self, *, optional: bool = False) -> str:
        try:
            payload = json.loads(self.active_pointer_path.read_text(encoding="utf-8"))
            generation_id = payload["generation_id"]
        except FileNotFoundError:
            if optional:
                return ""
            raise
        if not isinstance(generation_id, str) or not generation_id:
            raise ValueError("active generation pointer is invalid")
        return generation_id

    def read_active(self) -> GenerationSnapshot:
        return self.read_generation(self.active_generation_id())

    def read_generation(self, generation_id: str) -> GenerationSnapshot:
        path = self.generations_path / generation_id
        metadata = json.loads((path / "bundle.json").read_text(encoding="utf-8"))
        if metadata.get("generation_id") != generation_id:
            raise ValueError("bundle generation metadata mismatch")
        files = metadata.get("files", {})
        required = {
            "manifest.json",
            "projections/schema.csv",
            "projections/features.csv",
            "projections/derived.json",
            "projections/one_hot.json",
            "projections/target_registry.json",
            "projections/mapping_requirements.json",
        }
        if set(files) != required:
            raise ValueError("generation bundle file set is incomplete")
        for relative, expected_hash in files.items():
            actual_hash = hashlib.sha256((path / relative).read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                raise ValueError(f"generation bundle hash mismatch: {relative}")
        manifest = load_manifest(path / "manifest.json")
        if manifest.generation.generation_id != generation_id:
            raise ValueError("manifest generation does not match bundle")
        projections = require_valid_contract(manifest)
        fingerprints = scoped_fingerprints(manifest)
        if asdict(fingerprints) != metadata.get("fingerprints"):
            raise ValueError("bundle fingerprint metadata mismatch")
        self._verify_projection_bytes(path, projections)
        return GenerationSnapshot(manifest, projections, fingerprints, path)

    def rollback(self, generation_id: str) -> GenerationSnapshot:
        snapshot = self.read_generation(generation_id)
        self._failure_hook("before_pointer_replace")
        self._replace_active_pointer(generation_id)
        return snapshot

    def _stage_and_publish(self, manifest, projections, fingerprints, final_path) -> None:  # noqa: ANN001
        staging = self.generations_path / f".staging-{uuid4().hex}"
        try:
            projection_path = staging / "projections"
            projection_path.mkdir(parents=True)
            dump_manifest(manifest, staging / "manifest.json")
            (projection_path / "schema.csv").write_text(predict_csv_text(projections), encoding="utf-8")
            (projection_path / "features.csv").write_text(ml_csv_text(projections), encoding="utf-8")
            self._write_projection_json(projection_path / "derived.json", projections.generation_id, projections.derived)
            self._write_projection_json(projection_path / "one_hot.json", projections.generation_id, projections.one_hot)
            self._write_projection_json(projection_path / "target_registry.json", projections.generation_id, projections.target_registry)
            self._write_projection_json(projection_path / "mapping_requirements.json", projections.generation_id, projections.mapping_requirements)
            files = {
                str(path.relative_to(staging)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(staging.rglob("*")) if path.is_file()
            }
            bundle = {
                "bundle_version": "unified_feature_generation_bundle.v1",
                "generation_id": manifest.generation.generation_id,
                "contract_version": manifest.contract_version,
                "fingerprints": asdict(fingerprints),
                "files": files,
            }
            (staging / "bundle.json").write_text(_json(bundle), encoding="utf-8")
            self._fsync_tree(staging)
            self._failure_hook("after_staging")
            os.replace(staging, final_path)
            self._fsync_directory(self.generations_path)
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise

    def _replace_active_pointer(self, generation_id: str) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        temporary = self.root / f".active-generation-{uuid4().hex}.tmp"
        try:
            temporary.write_text(_json({"generation_id": generation_id}), encoding="utf-8")
            self._fsync_file(temporary)
            os.replace(temporary, self.active_pointer_path)
            self._fsync_directory(self.root)
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def _write_projection_json(path: Path, generation_id: str, rows: object) -> None:
        path.write_text(
            _json({"generation_id": generation_id, "rows": rows}, default=_json_default),
            encoding="utf-8",
        )

    @staticmethod
    def _verify_projection_bytes(path: Path, projections: ContractProjections) -> None:
        expected = {
            "schema.csv": predict_csv_text(projections),
            "features.csv": ml_csv_text(projections),
        }
        for name, value in expected.items():
            if (path / "projections" / name).read_text(encoding="utf-8") != value:
                raise ValueError(f"generated projection does not match manifest: {name}")

    @staticmethod
    def _fsync_tree(path: Path) -> None:
        for item in sorted(path.rglob("*")):
            if item.is_file():
                DataDefinitionGenerationRepository._fsync_file(item)
        for item in sorted((item for item in path.rglob("*") if item.is_dir()), reverse=True):
            DataDefinitionGenerationRepository._fsync_directory(item)
        DataDefinitionGenerationRepository._fsync_directory(path)

    @staticmethod
    def _fsync_file(path: Path) -> None:
        with path.open("rb") as handle:
            os.fsync(handle.fileno())

    @staticmethod
    def _fsync_directory(path: Path) -> None:
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def _json(payload: object, *, default=None) -> str:  # noqa: ANN001
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, default=default) + "\n"


def _json_default(value: object) -> object:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"not JSON serializable: {type(value).__name__}")
