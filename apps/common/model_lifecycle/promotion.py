"""Qt-free promotion and rollback compatibility boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
from typing import Callable

import joblib

from core.data_definition.target_registry.runtime import (
    ModelRegistrySnapshot,
    apply_target_policy,
)

from .repository_contracts import CandidateSnapshot
from .repository import ModelLifecycleRepository
from .durability_errors import (
    ActiveCommittedCleanupError,
    LifecycleRecoveryRequiredError,
)


@dataclass(frozen=True)
class PromotionResult:
    status: str
    candidate_id: str
    revision: int = 0
    message: str = ""


class ModelPromotionService:
    def __init__(
        self,
        repository: ModelLifecycleRepository,
        registry_provider: Callable[[], ModelRegistrySnapshot],
        *,
        prediction_smoke: Callable[[CandidateSnapshot], None] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._repository = repository
        self._registry_provider = registry_provider
        self._prediction_smoke = prediction_smoke or _bounded_structural_smoke
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def promote(
        self,
        candidate_id: str,
        *,
        expected_revision: int,
        source: str = "user-promotion",
    ) -> PromotionResult:
        try:
            snapshot = self._repository.read_candidate(candidate_id)
            self._validate_compatibility(snapshot, self._registry_provider())
            self._prediction_smoke(snapshot)
            reference = self._repository.replace_active(
                candidate_id,
                activated_at=self._clock().isoformat(),
                source=source,
                expected_revision=expected_revision,
            )
        except ActiveCommittedCleanupError as exc:
            return PromotionResult(
                "recovery-required",
                candidate_id,
                revision=exc.revision,
                message=str(exc).splitlines()[0],
            )
        except LifecycleRecoveryRequiredError as exc:
            return PromotionResult(
                "recovery-required",
                candidate_id,
                message=str(exc).splitlines()[0],
            )
        except Exception as exc:
            return PromotionResult("blocked", candidate_id, message=str(exc).splitlines()[0])
        return PromotionResult("active", candidate_id, reference.revision, "Candidate promoted.")

    def rollback(
        self, candidate_id: str, *, expected_revision: int
    ) -> PromotionResult:
        return self.promote(
            candidate_id,
            expected_revision=expected_revision,
            source="rollback-repromotion",
        )

    @staticmethod
    def _validate_compatibility(
        candidate: CandidateSnapshot,
        current: ModelRegistrySnapshot,
    ) -> None:
        manifest = candidate.manifest
        if not manifest.promotion_eligible or manifest.blocking_reasons:
            raise ValueError("Candidate is not promotion eligible")
        if manifest.contains_unpublished_features:
            raise ValueError("Candidate contains unpublished experimental features")
        checks = {
            "Definition generation": (manifest.definition_generation_id, current.generation_id),
            "registry fingerprint": (manifest.registry_fingerprint, current.registry_fingerprint),
            "ordered ML fingerprint": (manifest.ordered_ml_fingerprint, current.ordered_ml_fingerprint),
            "derived semantics fingerprint": (
                manifest.derived_semantics_fingerprint,
                current.derived_semantics_fingerprint,
            ),
            "one-hot fingerprint": (manifest.one_hot_fingerprint, current.one_hot_fingerprint),
            "preprocessing version": (manifest.preprocessing_version, current.preprocessing_version),
        }
        mismatched = [name for name, values in checks.items() if values[0] != values[1]]
        if mismatched:
            raise ValueError("Candidate compatibility mismatch: " + ", ".join(mismatched))
        by_identity = {
            target.identity: target
            for group in current.groups for target in group.targets
        }
        targets = tuple(
            by_identity[identity]
            for identity in current.target_presentation_order
            if identity in by_identity
        )
        if tuple(
            (item.identity, item.ml_name) for item in manifest.targets
        ) != tuple((item.identity, item.ml_name) for item in targets):
            raise ValueError("Candidate production target identity/order mismatch")
        expected_inputs = current.input_ml_names
        for artifact, target in zip(manifest.targets, targets):
            allowed = apply_target_policy(expected_inputs, target)
            positions = [allowed.index(name) for name in artifact.feature_names if name in allowed]
            if (
                len(positions) != len(artifact.feature_names)
                or len(set(artifact.feature_names)) != len(artifact.feature_names)
                or positions != sorted(positions)
            ):
                raise ValueError(f"Candidate feature order is incompatible: {artifact.ml_name}")


def _bounded_structural_smoke(candidate: CandidateSnapshot) -> None:
    import pandas as pd

    payload = joblib.load(candidate.model_path)
    for target in candidate.manifest.targets:
        model = payload["models"][target.ml_name]
        if not callable(getattr(model, "predict", None)):
            raise ValueError(f"Candidate model cannot predict: {target.ml_name}")
        values = model.predict(pd.DataFrame(
            [{name: 0.0 for name in target.feature_names}],
            columns=target.feature_names,
        ))
        if len(values) != 1 or not math.isfinite(float(values[0])):
            raise ValueError(f"Candidate prediction smoke failed: {target.ml_name}")
