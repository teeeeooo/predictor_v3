"""Idempotent import boundary for one pre-lifecycle model.pkl."""

from __future__ import annotations

import hashlib
import shutil
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
from .promotion import ModelPromotionService
from .repository import ModelLifecycleRepository


@dataclass(frozen=True)
class LegacyMigrationResult:
    status: str
    candidate_id: str = ""
    message: str = ""


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
        except Exception as exc:
            return LegacyMigrationResult(
                "invalid-active",
                message=f"Existing lifecycle Active is invalid: {str(exc).splitlines()[0]}",
            )
        if active is not None:
            return LegacyMigrationResult("not-needed", message="Lifecycle Active already exists.")
        source = Path(legacy_model)
        if not source.is_file():
            return LegacyMigrationResult("bootstrap", message="No legacy model is available.")
        original_hash = _sha256(source)
        candidate_id = f"legacy-{original_hash[:24]}"
        try:
            existing = self._repository.read_candidate(candidate_id)
        except FileNotFoundError:
            try:
                existing = self._import(source, original_hash, candidate_id)
            except Exception as exc:
                return LegacyMigrationResult(
                    "bootstrap", candidate_id,
                    f"Legacy model was preserved but could not be imported: {str(exc).splitlines()[0]}",
                )
        if not existing.manifest.promotion_eligible:
            return LegacyMigrationResult(
                "retraining-required", candidate_id,
                "Legacy model metadata cannot prove current compatibility.",
            )
        promotion = ModelPromotionService(
            self._repository, self._registry_provider
        ).promote(candidate_id, expected_revision=0, source="legacy-migration")
        if promotion.status != "active":
            return LegacyMigrationResult("bootstrap", candidate_id, promotion.message)
        return LegacyMigrationResult(
            "active", candidate_id, "Compatible legacy model imported as lifecycle Active."
        )

    def _import(
        self, source: Path, original_hash: str, candidate_id: str
    ):  # noqa: ANN202
        payload = joblib.load(source)
        if not isinstance(payload, dict):
            raise ValueError("legacy model bundle is invalid")
        models, features = payload.get("models"), payload.get("features")
        if not isinstance(models, dict) or not isinstance(features, dict):
            raise ValueError("legacy model bundle is incomplete")
        snapshot: ModelRegistrySnapshot = self._registry_provider()
        targets = _ordered_targets(snapshot)
        blockers = _legacy_blockers(payload, snapshot, targets)
        staging = self._repository.create_staging(candidate_id)
        try:
            shutil.copy2(source, staging / "model.pkl")
            imported_hash = _sha256(staging / "model.pkl")
            if imported_hash != original_hash:
                raise ValueError("legacy copy hash mismatch")
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
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
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
