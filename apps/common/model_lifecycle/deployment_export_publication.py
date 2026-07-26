"""Verified staging and atomic no-replace deployment-export publication."""

from __future__ import annotations

import ctypes
import errno
import hashlib
import json
import os
import shutil
import sys
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from .active_contracts import ActiveModelReference
from .repository_contracts import CandidateSnapshot

EXPORT_SCHEMA_VERSION = "deployment_export_manifest.v1"


def publish_deployment_export(
    parent: Path,
    target: Path,
    export_id: str,
    *,
    active: ActiveModelReference,
    candidate: CandidateSnapshot,
) -> None:
    stage = parent / f".{export_id}.{uuid4().hex}.staging"
    try:
        stage.mkdir(mode=0o700)
        shutil.copyfile(candidate.model_path, stage / "model.pkl")
        model_sha256 = _sha256(stage / "model.pkl")
        if model_sha256 != candidate.manifest.model_sha256:
            raise OSError("Exported model checksum differs from Active Candidate")
        manifest = _export_manifest(export_id, active, candidate, model_sha256)
        summary = {
            "export_id": export_id,
            "source_candidate_id": active.candidate_id,
            "source_active_revision": active.revision,
            "generation_id": candidate.manifest.definition_generation_id,
            "production_target_count": len(candidate.manifest.targets),
            "message": "Immutable Predict-compatible Active model export.",
        }
        _write_json(stage / "manifest.json", manifest)
        _write_json(stage / "export_summary.json", summary)
        checksums = {
            name: _sha256(stage / name)
            for name in ("model.pkl", "manifest.json", "export_summary.json")
        }
        (stage / "checksums.sha256").write_text(
            "".join(f"{digest}  {name}\n" for name, digest in checksums.items()),
            encoding="utf-8",
        )
        _verify_export(stage, checksums, manifest, summary)
        _fsync_tree(stage)
        if target.exists() or target.is_symlink():
            raise FileExistsError(f"immutable export already exists: {export_id}")
        _rename_directory_no_replace(stage, target)
        stage = None
        try:
            _fsync_directory(parent)
        except Exception:
            shutil.rmtree(target)
            _fsync_directory(parent)
            raise
    finally:
        if stage is not None and stage.exists():
            if stage.is_symlink():
                stage.unlink()
            else:
                shutil.rmtree(stage)


def _export_manifest(
    export_id: str,
    active: ActiveModelReference,
    candidate: CandidateSnapshot,
    model_sha256: str,
) -> dict[str, object]:
    manifest = candidate.manifest
    return {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "export_id": export_id,
        "source": {
            "candidate_id": active.candidate_id,
            "active_revision": active.revision,
            "active_activated_at": active.activated_at,
            "candidate_model_sha256": manifest.model_sha256,
        },
        "compatibility": {
            "generation_id": manifest.definition_generation_id,
            "registry_fingerprint": manifest.registry_fingerprint,
            "ordered_ml_fingerprint": manifest.ordered_ml_fingerprint,
            "derived_semantics_fingerprint": manifest.derived_semantics_fingerprint,
            "one_hot_fingerprint": manifest.one_hot_fingerprint,
            "preprocessing_version": manifest.preprocessing_version,
            "artifact_format_version": manifest.artifact_format_version,
        },
        "production_targets": [asdict(item) for item in manifest.targets],
        "files": {"model.pkl": model_sha256},
    }


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_export(
    stage: Path,
    checksums: dict[str, str],
    manifest: dict[str, object],
    summary: dict[str, object],
) -> None:
    for name, expected in checksums.items():
        if not (stage / name).is_file() or _sha256(stage / name) != expected:
            raise OSError(f"Export verification failed: {name}")
    if manifest["export_id"] != summary["export_id"]:
        raise OSError("Export identity metadata is inconsistent")


def _fsync_tree(path: Path) -> None:
    for item in path.iterdir():
        if item.is_file():
            with item.open("rb") as source:
                os.fsync(source.fileno())
    _fsync_directory(path)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _rename_directory_no_replace(source: Path, target: Path) -> None:
    if sys.platform == "win32":
        os.rename(source, target)
        return
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin":
        rename = libc.renamex_np
        rename.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint)
        rename.restype = ctypes.c_int
        result = rename(os.fsencode(source), os.fsencode(target), 0x00000004)
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        rename = libc.renameat2
        rename.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        )
        rename.restype = ctypes.c_int
        result = rename(
            -100,
            os.fsencode(source),
            -100,
            os.fsencode(target),
            0x00000001,
        )
    else:
        raise OSError("Atomic non-overwriting directory publication is unavailable")
    if result == 0:
        return
    error = ctypes.get_errno()
    if error == errno.EEXIST:
        raise FileExistsError(error, os.strerror(error), str(target))
    raise OSError(error, os.strerror(error), str(target))
