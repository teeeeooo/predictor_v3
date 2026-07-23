"""Idempotent import boundary for one pre-lifecycle model.pkl."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import joblib

from core.data_definition.target_registry.runtime import (
    ModelRegistrySnapshot,
    apply_target_policy,
)

from .candidate_contracts import (
    CandidateManifest,
    CandidateResult,
    TargetArtifactContract,
)
from .errors import (
    ActiveReferenceCorruptionError,
    CandidateCorruptionError,
    LegacyArtifactError,
    ModelLifecycleError,
)
from .promotion import ModelPromotionService
from .repository import ModelLifecycleRepository


@dataclass(frozen=True)
class LegacyMigrationResult:
    status: str
    candidate_id: str = ""
    message: str = ""
    reason_code: str = ""


class LegacyModelMigrationService:
    def __init__(
        self,
        repository: ModelLifecycleRepository,
        registry_provider,
    ) -> None:  # noqa: ANN001
        self._repository = repository
        self._registry_provider = registry_provider

    def migrate_if_needed(self, legacy_model: str | Path) -> LegacyMigrationResult:
        try:
            active = self._repository.read_active(optional=True)
        except ActiveReferenceCorruptionError as exc:
            return LegacyMigrationResult(
                "invalid-active",
                message=f"Existing lifecycle Active is invalid: {str(exc).splitlines()[0]}",
                reason_code="active_reference_corrupt",
            )
        if active is not None:
            return LegacyMigrationResult("not-needed", message="Lifecycle Active already exists.")
        source = Path(legacy_model)
        try:
            source_available = source.is_file()
        except OSError as exc:
            return LegacyMigrationResult(
                "bootstrap",
                message=f"Legacy model is unreadable: {str(exc).splitlines()[0]}",
                reason_code="legacy_source_unreadable",
            )
        if not source_available:
            return LegacyMigrationResult("bootstrap", message="No legacy model is available.")
        try:
            original_hash = _sha256(source)
        except OSError as exc:
            return LegacyMigrationResult(
                "bootstrap",
                message=f"Legacy model is unreadable: {str(exc).splitlines()[0]}",
                reason_code="legacy_source_unreadable",
            )
        candidate_id = f"legacy-{original_hash[:24]}"
        try:
            existing = self._repository.read_candidate(candidate_id)
        except FileNotFoundError:
            try:
                existing = self._import(source, original_hash, candidate_id)
            except _LEGACY_ARTIFACT_FAILURES as exc:
                return LegacyMigrationResult(
                    "bootstrap", candidate_id,
                    f"Legacy model was preserved but could not be imported: {str(exc).splitlines()[0]}",
                    "legacy_import_failed",
                )
        except CandidateCorruptionError as exc:
            return LegacyMigrationResult(
                "retraining-required",
                candidate_id,
                f"Imported legacy Candidate is corrupt: {str(exc).splitlines()[0]}",
                "legacy_candidate_corrupt",
            )
        if not existing.manifest.promotion_eligible:
            return LegacyMigrationResult(
                "retraining-required", candidate_id,
                "Legacy model metadata cannot prove current compatibility.",
                "legacy_compatibility_unproven",
            )
        promotion = ModelPromotionService(
            self._repository, self._registry_provider
        ).promote(candidate_id, expected_revision=0, source="legacy-migration")
        if promotion.status != "active":
            return LegacyMigrationResult(
                "bootstrap",
                candidate_id,
                promotion.message,
                "legacy_activation_blocked",
            )
        return LegacyMigrationResult(
            "active", candidate_id, "Compatible legacy model imported as lifecycle Active."
        )

    def _import(
        self, source: Path, original_hash: str, candidate_id: str
    ):  # noqa: ANN202
        try:
            payload = joblib.load(source)
        except Exception as exc:
            # This catch is limited to the untrusted deserialize operation.
            raise LegacyArtifactError(
                f"legacy model cannot be deserialized: {str(exc).splitlines()[0]}"
            ) from exc
        if not isinstance(payload, dict):
            raise LegacyArtifactError("legacy model bundle is invalid")
        models, features = payload.get("models"), payload.get("features")
        if not isinstance(models, dict) or not isinstance(features, dict):
            raise LegacyArtifactError("legacy model bundle is incomplete")
        snapshot: ModelRegistrySnapshot = self._registry_provider()
        targets = _ordered_targets(snapshot)
        try:
            blockers = _legacy_blockers(payload, snapshot, targets)
        except (KeyError, TypeError, ValueError) as exc:
            raise LegacyArtifactError(
                f"legacy compatibility metadata is invalid: {str(exc).splitlines()[0]}"
            ) from exc
        staging = self._repository.create_staging(candidate_id)
        try:
            imported_hash = self._repository.copy_model_to_staging(staging, source)
            if imported_hash != original_hash:
                raise LegacyArtifactError("legacy copy hash mismatch")
            manifest = CandidateManifest(
                candidate_id=candidate_id,
                run_id=candidate_id,
                created_at=datetime.now(timezone.utc).isoformat(),
                source="legacy-model-import",
                model_sha256=imported_hash,
                original_model_sha256=original_hash,
                definition_generation_id=snapshot.generation_id,
                registry_fingerprint=snapshot.registry_fingerprint,
                ordered_ml_fingerprint=snapshot.ordered_ml_fingerprint,
                derived_semantics_fingerprint=snapshot.derived_semantics_fingerprint,
                one_hot_fingerprint=snapshot.one_hot_fingerprint,
                preprocessing_version=str(payload.get("preprocess_version", "")),
                targets=tuple(TargetArtifactContract(
                    target.identity,
                    target.ml_name,
                    tuple(features.get(target.ml_name, ())),
                ) for target in targets),
                promotion_eligible=not blockers,
                blocking_reasons=blockers,
            )
            result = CandidateResult(
                candidate_id, candidate_id, "complete", "imported",
                not blockers, blockers,
            )
            return self._repository.publish(staging, manifest, result)
        except _LEGACY_ARTIFACT_FAILURES:
            self._repository.discard_staging(staging)
            raise


def _legacy_blockers(payload, snapshot, targets) -> tuple[str, ...]:  # noqa: ANN001
    blockers = []
    contract = payload.get("training_contract")
    expected = {
        "generation_id": snapshot.generation_id,
        "registry_fingerprint": snapshot.registry_fingerprint,
        "ordered_ml_fingerprint": snapshot.ordered_ml_fingerprint,
        "derived_semantics_fingerprint": snapshot.derived_semantics_fingerprint,
        "one_hot_fingerprint": snapshot.one_hot_fingerprint,
    }
    if payload.get("preprocess_version") != snapshot.preprocessing_version:
        blockers.append("preprocessing_version_unproven")
    if not isinstance(contract, dict) or any(contract.get(key) != value for key, value in expected.items()):
        blockers.append("definition_compatibility_unproven")
    expected_names = tuple(target.ml_name for target in targets)
    if set(payload["models"]) != set(expected_names) or set(payload["features"]) != set(expected_names):
        blockers.append("production_targets_incomplete")
    for target in targets:
        feature_names = tuple(payload["features"].get(target.ml_name, ()))
        allowed = apply_target_policy(snapshot.input_ml_names, target)
        positions = [allowed.index(name) for name in feature_names if name in allowed]
        if (
            len(positions) != len(feature_names)
            or len(set(feature_names)) != len(feature_names)
            or positions != sorted(positions)
        ):
            blockers.append(f"feature_order_unproven:{target.ml_name}")
    return tuple(blockers)


def _ordered_targets(snapshot: ModelRegistrySnapshot):  # noqa: ANN202
    by_identity = {
        target.identity: target
        for group in snapshot.groups for target in group.targets
    }
    return tuple(
        by_identity[identity]
        for identity in snapshot.target_presentation_order
        if identity in by_identity
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


_LEGACY_ARTIFACT_FAILURES = (
    LegacyArtifactError,
    ModelLifecycleError,
    OSError,
)
