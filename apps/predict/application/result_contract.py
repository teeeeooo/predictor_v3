"""Qt-free typed prediction result and immutable execution provenance."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PredictionExecutionSemantics:
    """Existing runtime-owned fingerprints pinned for one execution."""

    runtime_generation_id: str
    ordered_ml_fingerprint: str
    preprocessing_fingerprint: str
    derived_fingerprint: str
    one_hot_fingerprint: str
    target_registry_fingerprint: str

    @property
    def currentness_key(self) -> tuple[str, ...]:
        """Exclude the trace-only generation id from semantic equality."""
        return (
            self.ordered_ml_fingerprint,
            self.preprocessing_fingerprint,
            self.derived_fingerprint,
            self.one_hot_fingerprint,
            self.target_registry_fingerprint,
        )


@dataclass(frozen=True)
class PredictionModelIdentity:
    candidate_id: str
    active_revision: int
    generation_id: str


@dataclass(frozen=True)
class PredictionExecutionContext:
    session_id: str
    case_id: str
    run_id: str
    case_input_revision: int
    semantics: PredictionExecutionSemantics
    model: PredictionModelIdentity


@dataclass(frozen=True)
class ResultAcceptance:
    accepted: bool
    reason_code: str = ""
    case_id: str = ""
    run_id: str = ""


def execution_semantics_from_runtime(runtime) -> PredictionExecutionSemantics:  # noqa: ANN001
    """Reuse runtime-owned fingerprints without inventing a new hash owner."""
    from apps.predict.application.runtime_snapshot import (
        validate_runtime_target_contract,
    )

    validate_runtime_target_contract(runtime)
    return PredictionExecutionSemantics(
        runtime_generation_id=runtime.generation_id,
        ordered_ml_fingerprint=runtime.ordered_ml_fingerprint,
        preprocessing_fingerprint=runtime.preprocessing_fingerprint,
        derived_fingerprint=runtime.derived_fingerprint,
        one_hot_fingerprint=runtime.one_hot_fingerprint,
        target_registry_fingerprint=runtime.target_registry_fingerprint,
    )
