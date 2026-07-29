"""Training-input materialization owned by the lifecycle root."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Any

from apps.common.model_lifecycle.filesystem import LifecycleFilesystem

from .canonical import canonical_payload, file_sha256, require_safe_identity
from .canonical import require_sha256


class TrainingDataMaterializer:
    def __init__(
        self,
        filesystem: LifecycleFilesystem,
        blobs: Path,
    ) -> None:
        self._filesystem = filesystem
        self.blobs = blobs

    def materialize_local_source(
        self,
        source: str | Path,
        *,
        filtering_meaning: dict[str, Any],
        materialization_kind: str = "owned_source_bytes",
        expected_content_sha256: str | None = None,
        expected_filtering_meaning: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if materialization_kind not in {
            "owned_source_bytes",
            "lossless_training_projection",
        }:
            raise ValueError("unsupported owned materialization kind")
        path = Path(source)
        before = _require_stable_regular_source(path)
        digest, size = _hash_source(path)
        header, rows, ordered_rows = _csv_shape(path)
        if expected_content_sha256 is not None:
            require_sha256(expected_content_sha256, "selected run data hash")
            if digest != expected_content_sha256:
                raise ValueError(
                    "materialized training bytes differ from selected run"
                )
        filtering = canonical_payload(filtering_meaning)
        if (
            expected_filtering_meaning is not None
            and filtering != canonical_payload(expected_filtering_meaning)
        ):
            raise ValueError(
                "materialized training selection differs from selected run"
            )
        after = path.stat()
        if _stat_identity(before) != _stat_identity(after):
            raise ValueError("training source changed during materialization")
        blob_path = self.blobs / digest
        self._filesystem.ensure_directory(self.blobs)
        if self._filesystem.entry_exists(blob_path):
            self._filesystem.require_regular_file(blob_path)
            if file_sha256(blob_path) != digest or blob_path.stat().st_size != size:
                raise ValueError("content-addressed training blob is corrupt")
        else:
            self._copy_and_verify(path, blob_path, digest)
        return {
            "materialization_kind": materialization_kind,
            "materialized_identity": f"sha256:{digest}",
            "content_sha256": digest,
            "size_bytes": size,
            "schema_columns": header,
            "row_count": rows,
            "column_count": len(header),
            "ordered_row_set_sha256": ordered_rows,
            "filtering_meaning": filtering,
            "source_reference": {
                "kind": "historical_local_path",
                "path": str(path),
            },
        }

    def verify_owned_materialization(
        self, descriptor: dict[str, Any]
    ) -> Path:
        path = self.owned_materialization_path(
            str(descriptor.get("materialized_identity", ""))
        )
        digest, size = _hash_source(path)
        header, rows, ordered_rows = _csv_shape(path)
        expected = {
            "content_sha256": digest,
            "size_bytes": size,
            "schema_columns": header,
            "row_count": rows,
            "column_count": len(header),
            "ordered_row_set_sha256": ordered_rows,
        }
        for name, value in expected.items():
            if descriptor.get(name) != value:
                raise ValueError(
                    f"materialized training evidence mismatch: {name}"
                )
        return path

    def validate_external_reference(
        self,
        reference: dict[str, Any],
    ) -> dict[str, Any]:
        required = {
            "object_version_id",
            "content_sha256",
            "size_bytes",
            "schema_columns",
            "row_count",
            "column_count",
            "ordered_row_set_sha256",
            "filtering_meaning",
            "retrievability_verified_until",
            "retrievability_verified",
            "independent_row_meaning_preserved",
        }
        if not isinstance(reference, dict) or required.difference(reference):
            raise ValueError("verified external training reference is incomplete")
        if (
            reference.get("retrievability_verified") is not True
            or reference.get("independent_row_meaning_preserved") is not True
        ):
            raise ValueError("external training reference cannot prove preservation")
        require_safe_identity(
            reference.get("object_version_id"), "external object version"
        )
        require_sha256(reference.get("content_sha256"), "external content hash")
        require_sha256(
            reference.get("ordered_row_set_sha256"),
            "external ordered row-set hash",
        )
        if not _valid_shape(reference):
            raise ValueError("external training reference shape is invalid")
        return {
            "materialization_kind": "verified_external_reference",
            "materialized_identity": reference["object_version_id"],
            **canonical_payload(reference),
        }

    def owned_materialization_path(self, identity: str) -> Path:
        prefix = "sha256:"
        if not identity.startswith(prefix):
            raise ValueError("materialization is not a lifecycle-owned blob")
        digest = require_sha256(
            identity[len(prefix):], "materialized training blob identity"
        )
        path = self.blobs / digest
        self._filesystem.require_regular_file(path)
        if file_sha256(path) != digest:
            raise ValueError("materialized training blob integrity failed")
        return path

    def _copy_and_verify(self, source: Path, target: Path, digest: str) -> None:
        try:
            with source.open("rb") as source_file, (
                self._filesystem.open_exclusive(target)
            ) as output:
                for block in iter(lambda: source_file.read(1024 * 1024), b""):
                    output.write(block)
            if file_sha256(target) != digest:
                raise ValueError("materialized training blob hash mismatch")
        except Exception:
            if self._filesystem.entry_exists(target):
                self._filesystem.remove_file(target, missing_ok=True)
            raise


def _valid_shape(reference: dict[str, Any]) -> bool:
    return (
        type(reference.get("size_bytes")) is int
        and reference["size_bytes"] >= 0
        and type(reference.get("row_count")) is int
        and reference["row_count"] >= 0
        and type(reference.get("column_count")) is int
        and reference["column_count"] >= 1
    )


def _stat_identity(value: os.stat_result) -> tuple[int, int, int, int]:
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns


def _require_stable_regular_source(path: Path) -> os.stat_result:
    entry = path.lstat()
    if stat.S_ISLNK(entry.st_mode) or not stat.S_ISREG(entry.st_mode):
        raise ValueError("training source must be a regular non-symlink file")
    return entry


def _hash_source(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    return digest.hexdigest(), size


def _csv_shape(path: Path) -> tuple[list[str], int, str]:
    digest = hashlib.sha256()
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError("training source has no schema row") from exc
        if not header or len(header) != len(set(header)):
            raise ValueError("training source schema is empty or ambiguous")
        rows = 0
        for row in reader:
            if len(row) != len(header):
                raise ValueError("training source row shape is inconsistent")
            digest.update(
                json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode(
                    "utf-8"
                )
            )
            digest.update(b"\n")
            rows += 1
    return header, rows, digest.hexdigest()
