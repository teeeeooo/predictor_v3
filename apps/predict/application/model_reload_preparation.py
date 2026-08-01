"""Detached Candidate validation and Predict replacement preparation."""

from __future__ import annotations

import traceback
from typing import Callable

from apps.common.model_lifecycle.durability_errors import (
    LifecycleRecoveryRequiredError,
)
from apps.common.model_lifecycle.errors import (
    CandidateCorruptionError,
    ModelLifecycleError,
)
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.predict.application.runtime_snapshot import (
    PredictRuntimeSnapshot,
    validate_runtime_target_contract,
)
from apps.predict.ports.prediction_workflow_ports import PredictionServicePort


class ReloadPreparationFailure(RuntimeError):
    def __init__(
        self,
        reason_code: str,
        diagnostic: str,
        diagnostic_traceback: str,
    ) -> None:
        super().__init__(diagnostic)
        self.reason_code = reason_code
        self.diagnostic = diagnostic
        self.diagnostic_traceback = diagnostic_traceback


def prepare_model_replacement(
    repository: ModelLifecycleRepository,
    *,
    candidate_id: str,
    runtime: PredictRuntimeSnapshot,
    service_factory: Callable[[str, PredictRuntimeSnapshot], PredictionServicePort],
) -> PredictionServicePort:
    validate_runtime_target_contract(runtime)
    try:
        candidate = repository.read_candidate(candidate_id)
    except LifecycleRecoveryRequiredError as exc:
        raise _failure("recovery_required", exc) from exc
    except (
        CandidateCorruptionError,
        FileNotFoundError,
        OSError,
        ModelLifecycleError,
    ) as exc:
        raise _failure("corrupt_active", exc) from exc
    try:
        _validate_compatibility(candidate.manifest, runtime)
    except ValueError as exc:
        raise _failure("incompatible_active", exc) from exc
    try:
        prepared = service_factory(str(candidate.model_path), runtime)
        prepared.prepare_model()
        return prepared
    except Exception as exc:
        raise _failure("replacement_preparation_failed", exc) from exc


def _failure(reason_code: str, exc: Exception) -> ReloadPreparationFailure:
    return ReloadPreparationFailure(
        reason_code,
        f"{type(exc).__name__}: {str(exc)}",
        traceback.format_exc(),
    )


def _validate_compatibility(manifest, runtime: PredictRuntimeSnapshot) -> None:  # noqa: ANN001
    checks = {
        "generation": (manifest.definition_generation_id, runtime.generation_id),
        "registry": (
            manifest.registry_fingerprint,
            runtime.target_registry_fingerprint,
        ),
        "feature order": (
            manifest.ordered_ml_fingerprint,
            runtime.ordered_ml_fingerprint,
        ),
        "derived semantics": (
            manifest.derived_semantics_fingerprint,
            runtime.derived_fingerprint,
        ),
        "one-hot": (manifest.one_hot_fingerprint, runtime.one_hot_fingerprint),
        "preprocessing": (
            manifest.preprocessing_version,
            runtime.preprocessing_version,
        ),
    }
    mismatched = tuple(
        name for name, values in checks.items() if values[0] != values[1]
    )
    if mismatched:
        raise ValueError(
            "Active Candidate compatibility differs: " + ", ".join(mismatched)
        )
    if tuple(item.ml_name for item in manifest.targets) != runtime.active_targets:
        raise ValueError("Active Candidate production targets are incomplete")
    ordered = runtime.ordered_input_ml_names
    for target in manifest.targets:
        positions = [
            ordered.index(name) for name in target.feature_names if name in ordered
        ]
        if len(positions) != len(target.feature_names) or positions != sorted(positions):
            raise ValueError(
                f"Active Candidate feature order is incompatible: {target.ml_name}"
            )
