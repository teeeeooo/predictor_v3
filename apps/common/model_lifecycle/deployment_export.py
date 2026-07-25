"""Immutable deployment export derived only from one guarded Active revision."""

from __future__ import annotations

import ctypes
import errno
import hashlib
import json
import os
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from uuid import uuid4

from .promotion import ModelPromotionService
from .repository import ModelLifecycleRepository

EXPORT_SCHEMA_VERSION = "deployment_export_manifest.v1"


@dataclass(frozen=True)
class DeploymentExportResult:
    status: str
    export_id: str = ""
    path: str = ""
    candidate_id: str = ""
    active_revision: int = 0
    message: str = ""
    diagnostic: str = ""


class DeploymentExportService:
    """Validate, stage, verify, and publish one immutable Active export."""

    def __init__(
        self,
        repository: ModelLifecycleRepository,
        promotion: ModelPromotionService,
    ) -> None:
        self._repository = repository
        self._promotion = promotion

    def export_active(
        self,
        destination_parent: str | Path,
        *,
        expected_revision: int,
    ) -> DeploymentExportResult:
        requested_parent = Path(destination_parent)
        parent = requested_parent.resolve()
        stage: Path | None = None
        try:
            if requested_parent.is_symlink() or not parent.is_dir():
                raise ValueError("Export destination must be an existing regular directory")
            active = self._repository.read_active()
            if active.revision != expected_revision:
                raise ValueError("Active revision changed; refresh model management")
            export_id = f"predictor-v3-{active.candidate_id}-r{active.revision}"
            target = parent / export_id
            if target.exists() or target.is_symlink():
                raise FileExistsError(f"immutable export already exists: {export_id}")
            with self._repository.guard_active(active.candidate_id, active.revision):
                candidate = self._repository.read_candidate(active.candidate_id)
                compatibility = self._promotion.inspect_compatibility(
                    active.candidate_id
                )
                if compatibility.status != "compatible":
                    raise ValueError(
                        compatibility.diagnostic_message
                        or "Active Candidate is not currently compatible"
                    )
                stage = parent / f".{export_id}.{uuid4().hex}.staging"
                stage.mkdir(mode=0o700)
                shutil.copyfile(candidate.model_path, stage / "model.pkl")
                model_sha256 = _sha256(stage / "model.pkl")
                if model_sha256 != candidate.manifest.model_sha256:
                    raise ValueError("Exported model checksum differs from Active Candidate")
                manifest = {
                    "schema_version": EXPORT_SCHEMA_VERSION,
                    "export_id": export_id,
                    "source": {
                        "candidate_id": active.candidate_id,
                        "active_revision": active.revision,
                        "active_activated_at": active.activated_at,
                        "candidate_model_sha256": candidate.manifest.model_sha256,
                    },
                    "compatibility": {
                        "generation_id": candidate.manifest.definition_generation_id,
                        "registry_fingerprint": candidate.manifest.registry_fingerprint,
                        "ordered_ml_fingerprint": candidate.manifest.ordered_ml_fingerprint,
                        "derived_semantics_fingerprint": candidate.manifest.derived_semantics_fingerprint,
                        "one_hot_fingerprint": candidate.manifest.one_hot_fingerprint,
                        "preprocessing_version": candidate.manifest.preprocessing_version,
                        "artifact_format_version": candidate.manifest.artifact_format_version,
                    },
                    "production_targets": [
                        asdict(item) for item in candidate.manifest.targets
                    ],
                    "files": {"model.pkl": model_sha256},
                }
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
                    raise FileExistsError(
                        f"immutable export already exists: {export_id}"
                    )
                _rename_directory_no_replace(stage, target)
                stage = None
                try:
                    _fsync_directory(parent)
                except Exception:
                    shutil.rmtree(target)
                    _fsync_directory(parent)
                    raise
            return DeploymentExportResult(
                "exported",
                export_id,
                str(target),
                active.candidate_id,
                active.revision,
                "현재 사용 모델의 immutable deployment export를 생성했습니다.",
            )
        except Exception as exc:
            return DeploymentExportResult(
                "failed",
                message="Deployment export를 생성하지 못했습니다.",
                diagnostic=f"{type(exc).__name__}: {str(exc)}",
            )
        finally:
            if stage is not None and stage.exists():
                if stage.is_symlink():
                    stage.unlink()
                else:
                    shutil.rmtree(stage)


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
            raise ValueError(f"Export verification failed: {name}")
    if manifest["export_id"] != summary["export_id"]:
        raise ValueError("Export identity metadata is inconsistent")


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
    """Atomically publish a directory while refusing every existing target."""
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
        raise OSError(
            "Atomic non-overwriting directory publication is unavailable"
        )
    if result == 0:
        return
    error = ctypes.get_errno()
    if error == errno.EEXIST:
        raise FileExistsError(error, os.strerror(error), str(target))
    raise OSError(error, os.strerror(error), str(target))
