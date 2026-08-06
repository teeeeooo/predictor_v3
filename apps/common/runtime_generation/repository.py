"""Filesystem adapter for immutable Unified Feature generation bundles."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from typing import Callable, Iterator
from uuid import uuid4

from apps.common.runtime_generation.repository_contract import (
    GenerationPublishResult,
    GenerationSnapshot,
    _issue_generation_snapshot,
)
from core.data_definition.contract import (
    ContractProjections,
    ScopedFingerprints,
    UnifiedFeatureManifest,
    dump_manifest,
    generate_projections,
    load_manifest,
    legacy_bundle_fingerprint_payload,
    ml_csv_text,
    predict_csv_text,
    require_valid_contract,
    scoped_fingerprints,
)

FailureHook = Callable[[str], None]

_REQUIRED_BUNDLE_FILES = frozenset({
    "manifest.json",
    "projections/schema.csv",
    "projections/features.csv",
    "projections/derived.json",
    "projections/one_hot.json",
    "projections/target_registry.json",
    "projections/mapping_requirements.json",
})


class DataDefinitionGenerationRepository:
    """Publish complete same-filesystem bundles, then atomically replace a pointer."""

    def __init__(self, root: str | Path, *, failure_hook: FailureHook | None = None) -> None:
        self.root = Path(root)
        self.generations_path = self.root / "generations"
        self.active_pointer_path = self.root / "active_generation.json"
        self.writer_lock_path = self.root / ".generation-write.lock"
        self._failure_hook = failure_hook or (lambda _stage: None)

    def publish(self, manifest: UnifiedFeatureManifest) -> GenerationPublishResult:
        projections = require_valid_contract(manifest)
        fingerprints = scoped_fingerprints(manifest)
        generation_id = _require_safe_generation_id(manifest.generation.generation_id)
        with self._single_writer():
            previous = self.active_generation_id(optional=True)
            parent = manifest.generation.parent_generation_id
            if parent != previous:
                if parent == "" and previous == generation_id:
                    self.generations_path.mkdir(parents=True, exist_ok=True)
                    final_path = self.generations_path / generation_id
                    try:
                        existing = self.read_generation(generation_id)
                    except FileNotFoundError:
                        existing = self._recover_incomplete_initial_generation(
                            manifest, projections, fingerprints, final_path
                        )
                    if existing.fingerprints.combined == fingerprints.combined:
                        return GenerationPublishResult(
                            generation_id,
                            previous,
                            existing.path,
                        )
                raise ValueError(
                    "stale generation parent: "
                    f"candidate={parent or '<none>'}, active={previous or '<none>'}"
                )
            self.generations_path.mkdir(parents=True, exist_ok=True)
            final_path = self.generations_path / generation_id
            if final_path.exists():
                existing = self.read_generation(generation_id)
                if existing.fingerprints.combined != fingerprints.combined:
                    raise FileExistsError(
                        f"immutable generation already exists: {generation_id}"
                    )
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
        try:
            return _require_safe_generation_id(generation_id)
        except ValueError as exc:
            raise ValueError("active generation pointer is invalid") from exc

    def read_active(self) -> GenerationSnapshot:
        return self.read_generation(self.active_generation_id())

    def read_generation(self, generation_id: str) -> GenerationSnapshot:
        generation_id = _require_safe_generation_id(generation_id)
        path = self.generations_path / generation_id
        metadata = json.loads((path / "bundle.json").read_text(encoding="utf-8"))
        if metadata.get("generation_id") != generation_id:
            raise ValueError("bundle generation metadata mismatch")
        files = _canonical_bundle_files(metadata.get("files"))
        for relative, expected_hash in files.items():
            actual_hash = hashlib.sha256((path / relative).read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                raise ValueError(f"generation bundle hash mismatch: {relative}")
        manifest = load_manifest(path / "manifest.json")
        if manifest.generation.generation_id != generation_id:
            raise ValueError("manifest generation does not match bundle")
        projections = require_valid_contract(manifest)
        fingerprints = scoped_fingerprints(manifest)
        expected_fingerprints = asdict(fingerprints)
        stored_fingerprints = metadata.get("fingerprints")
        candidates = [expected_fingerprints]
        if not manifest.contract_version.endswith(".v4"):
            candidates.append(legacy_bundle_fingerprint_payload(manifest))
        if isinstance(stored_fingerprints, dict) and "target_presentation" not in stored_fingerprints:
            candidates = [
                {key: value for key, value in item.items() if key != "target_presentation"}
                for item in candidates
            ]
        if isinstance(stored_fingerprints, dict) and "derived_semantics" not in stored_fingerprints:
            candidates = [
                {key: value for key, value in item.items() if key != "derived_semantics"}
                for item in candidates
            ]
        if stored_fingerprints not in candidates:
            raise ValueError("bundle fingerprint metadata mismatch")
        self._verify_projection_bytes(path, projections)
        return _issue_generation_snapshot(
            manifest,
            projections,
            fingerprints,
            path,
        )

    def rollback(self, generation_id: str) -> GenerationSnapshot:
        with self._single_writer():
            snapshot = self.read_generation(generation_id)
            self._failure_hook("before_pointer_replace")
            self._replace_active_pointer(generation_id)
            return snapshot

    @contextmanager
    def _single_writer(self) -> Iterator[None]:
        """Serialize parent validation and pointer replacement across processes."""
        with _exclusive_file_lock(self.writer_lock_path):
            yield

    def _stage_and_publish(self, manifest, projections, fingerprints, final_path) -> None:  # noqa: ANN001
        staging = self.generations_path / f".staging-{uuid4().hex}"
        try:
            self._write_bundle_tree(staging, manifest, projections, fingerprints)
            self._fsync_tree(staging)
            self._failure_hook("after_staging")
            os.replace(staging, final_path)
            self._fsync_directory(self.generations_path)
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise

    def _write_bundle_tree(self, root, manifest, projections, fingerprints) -> None:  # noqa: ANN001
        projection_path = root / "projections"
        projection_path.mkdir(parents=True)
        dump_manifest(manifest, root / "manifest.json")
        (projection_path / "schema.csv").write_text(
            predict_csv_text(projections), encoding="utf-8"
        )
        (projection_path / "features.csv").write_text(
            ml_csv_text(projections), encoding="utf-8"
        )
        self._write_projection_json(
            projection_path / "derived.json", projections.generation_id, projections.derived
        )
        self._write_projection_json(
            projection_path / "one_hot.json", projections.generation_id, projections.one_hot
        )
        self._write_projection_json(
            projection_path / "target_registry.json",
            projections.generation_id,
            projections.target_registry,
        )
        self._write_projection_json(
            projection_path / "mapping_requirements.json",
            projections.generation_id,
            projections.mapping_requirements,
        )
        files = {
            _bundle_file_identity(path, root): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*")) if path.is_file()
        }
        bundle = {
            "bundle_version": "unified_feature_generation_bundle.v1",
            "generation_id": manifest.generation.generation_id,
            "contract_version": manifest.contract_version,
            "fingerprints": asdict(fingerprints),
            "files": files,
        }
        (root / "bundle.json").write_text(_json(bundle), encoding="utf-8")

    def _recover_incomplete_initial_generation(
        self, manifest, projections, fingerprints, final_path
    ) -> GenerationSnapshot:  # noqa: ANN001
        if not final_path.exists():
            self._stage_and_publish(manifest, projections, fingerprints, final_path)
            return self.read_generation(manifest.generation.generation_id)
        if not final_path.is_dir() or (final_path / "bundle.json").exists():
            raise ValueError("existing immutable generation is incomplete or corrupt")

        staging = self.generations_path / f".recovery-{uuid4().hex}"
        bundle_tmp = self.generations_path / f".bundle-{uuid4().hex}.tmp"
        try:
            self._write_bundle_tree(staging, manifest, projections, fingerprints)
            expected_files = {
                _bundle_file_identity(item, staging): item
                for item in staging.rglob("*") if item.is_file()
            }
            expected_dirs = {
                _bundle_file_identity(item, staging)
                for item in staging.rglob("*") if item.is_dir()
            }
            for item in final_path.rglob("*"):
                relative = _bundle_file_identity(item, final_path)
                if item.is_symlink():
                    raise ValueError("recoverable generation residue contains a link")
                if item.is_dir():
                    if relative not in expected_dirs:
                        raise ValueError("recoverable generation residue has unknown directories")
                    continue
                if not item.is_file() or relative not in expected_files or relative == "bundle.json":
                    raise ValueError("recoverable generation residue has unknown files")
                if item.read_bytes() != expected_files[relative].read_bytes():
                    raise ValueError(
                        f"recoverable generation residue conflicts with bootstrap: {relative}"
                    )

            for relative, source in expected_files.items():
                if relative == "bundle.json":
                    continue
                destination = final_path / relative
                if destination.exists():
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read_bytes())
                self._fsync_file(destination)
            bundle_tmp.write_bytes(expected_files["bundle.json"].read_bytes())
            self._fsync_file(bundle_tmp)
            os.replace(bundle_tmp, final_path / "bundle.json")
            self._fsync_directory(final_path)
        finally:
            bundle_tmp.unlink(missing_ok=True)
            shutil.rmtree(staging, ignore_errors=True)
        return self.read_generation(manifest.generation.generation_id)

    def _replace_active_pointer(self, generation_id: str) -> None:
        generation_id = _require_safe_generation_id(generation_id)
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
        path.write_text(_projection_json_text(generation_id, rows), encoding="utf-8")

    @staticmethod
    def _verify_projection_bytes(path: Path, projections: ContractProjections) -> None:
        expected = {
            "schema.csv": predict_csv_text(projections),
            "features.csv": ml_csv_text(projections),
            "derived.json": _projection_json_text(
                projections.generation_id,
                projections.derived,
            ),
            "one_hot.json": _projection_json_text(
                projections.generation_id,
                projections.one_hot,
            ),
            "target_registry.json": _projection_json_text(
                projections.generation_id,
                projections.target_registry,
            ),
            "mapping_requirements.json": _projection_json_text(
                projections.generation_id,
                projections.mapping_requirements,
            ),
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
        mode = "r+b" if _platform_name() == "nt" else "rb"
        with path.open(mode) as handle:
            os.fsync(handle.fileno())

    @staticmethod
    def _fsync_directory(path: Path) -> None:
        if _platform_name() == "nt":
            return
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def _require_safe_generation_id(value: object) -> str:
    if not isinstance(value, str) or not value or value.startswith("."):
        raise ValueError("generation_id is not a safe immutable bundle name")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or len(posix.parts) != 1
        or len(windows.parts) != 1
    ):
        raise ValueError("generation_id is not a safe immutable bundle name")
    return value


def _bundle_file_identity(path: PurePath, root: PurePath) -> str:
    """Persist one OS-independent relative bundle identity."""
    return path.relative_to(root).as_posix()


def _canonical_bundle_files(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError("generation bundle file set is incomplete")
    keys = tuple(value)
    if any(not isinstance(key, str) for key in keys):
        raise ValueError("generation bundle file identity is invalid")
    has_backslash = any("\\" in key for key in keys)
    if has_backslash and any("/" in key for key in keys):
        raise ValueError("generation bundle file identity mixes separators")

    canonical: dict[str, str] = {}
    for stored_identity, expected_hash in value.items():
        if not isinstance(expected_hash, str):
            raise ValueError("generation bundle hash metadata is invalid")
        identity = stored_identity.replace("\\", "/")
        if identity in canonical:
            raise ValueError("generation bundle file identity is ambiguous")
        canonical[identity] = expected_hash
    if set(canonical) != _REQUIRED_BUNDLE_FILES:
        raise ValueError("generation bundle file set is incomplete")
    return canonical


def _json(payload: object, *, default=None) -> str:  # noqa: ANN001
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, default=default) + "\n"


def _json_default(value: object) -> object:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def _projection_json_text(generation_id: str, rows: object) -> str:
    return _json(
        {"generation_id": generation_id, "rows": rows},
        default=_json_default,
    )


@contextmanager
def _exclusive_file_lock(path: Path) -> Iterator[None]:
    """Hold one persistent coordination file with the native process lock API."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    locked = False
    try:
        if os.fstat(descriptor).st_size == 0:
            os.write(descriptor, b"\0")
            os.fsync(descriptor)
        os.lseek(descriptor, 0, os.SEEK_SET)
        _lock_descriptor(descriptor)
        locked = True
        yield
    finally:
        if locked:
            os.lseek(descriptor, 0, os.SEEK_SET)
            _unlock_descriptor(descriptor)
        os.close(descriptor)


def _lock_descriptor(descriptor: int) -> None:
    if _platform_name() == "nt":
        import msvcrt

        msvcrt.locking(descriptor, msvcrt.LK_LOCK, 1)
        return
    import fcntl

    fcntl.flock(descriptor, fcntl.LOCK_EX)


def _unlock_descriptor(descriptor: int) -> None:
    if _platform_name() == "nt":
        import msvcrt

        msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
        return
    import fcntl

    fcntl.flock(descriptor, fcntl.LOCK_UN)


def _platform_name() -> str:
    return os.name
