"""Immutable generation-bound Predict execution semantics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from apps.common.runtime_generation import GenerationSnapshot
from apps.predict.application.runtime_columns import (
    PredictRuntimeColumnDescriptor,
    build_runtime_column_descriptors,
)
from apps.predict.application.target_outcome import PredictionTargetDescriptor
from core.data_definition.contract import (
    bootstrap_manifest,
    generate_projections,
    scoped_fingerprints,
)
from core.data_definition.derived.evaluator import (
    DerivedEvaluationSnapshot,
    evaluation_snapshot,
)
from core.data_definition.one_hot import OneHotRuntimeSnapshot
from core.data_definition.target_registry.runtime import model_registry_snapshot
from core.predictor_schema.catalog_v2 import PredictSchemaV2Row


@dataclass(frozen=True)
class PredictRuntimeSnapshot:
    """Every contract that can change Predict preparation or result semantics."""

    generation_id: str
    preprocessing_version: str
    predict_projection: tuple[PredictSchemaV2Row, ...]
    column_descriptors: tuple[PredictRuntimeColumnDescriptor, ...]
    ordered_input_ml_names: tuple[str, ...]
    derived: DerivedEvaluationSnapshot
    one_hot: OneHotRuntimeSnapshot
    active_targets: tuple[str, ...]
    target_result_keys: tuple[tuple[str, str], ...]
    target_descriptors: tuple[PredictionTargetDescriptor, ...]
    zero_fill_policies: tuple[tuple[str, str], ...]
    predict_fingerprint: str
    ordered_ml_fingerprint: str
    derived_fingerprint: str
    one_hot_fingerprint: str
    target_registry_fingerprint: str
    preprocessing_fingerprint: str

    @property
    def zero_fill_policy_by_ml_name(self) -> dict[str, str]:
        return dict(self.zero_fill_policies)

    @property
    def expected_model_contract(self) -> dict[str, str]:
        return {
            "registry_fingerprint": self.target_registry_fingerprint,
            "ordered_ml_fingerprint": self.ordered_ml_fingerprint,
            "derived_semantics_fingerprint": self.derived_fingerprint,
            "one_hot_fingerprint": self.one_hot_fingerprint,
        }


def build_predict_runtime_snapshot(
    generation: GenerationSnapshot,
) -> PredictRuntimeSnapshot:
    """Project one already validated repository snapshot without external reads."""
    manifest = generation.manifest
    column_descriptors = build_runtime_column_descriptors(
        manifest.features,
        manifest.ordering.predict,
        generation.projections.predict,
    )
    registry = model_registry_snapshot(manifest)
    target_by_id = {item.identity: item for item in manifest.targets if item.active}
    feature_by_id = {item.identity: item for item in manifest.features}
    ordered_targets = tuple(
        target_by_id[identity]
        for identity in manifest.ordering.targets
        if identity in target_by_id
    )
    target_result_keys = tuple(
        (target.ml_name, feature_by_id[target.feature_identity].column_key)
        for target in ordered_targets
    )
    runtime_target_by_id = {
        target.identity: target
        for group in registry.groups
        for target in group.targets
    }
    target_descriptors = tuple(
        PredictionTargetDescriptor(
            target_identity=target.identity,
            result_feature_identity=target.feature_identity,
            ml_name=target.ml_name,
            result_key=feature_by_id[target.feature_identity].column_key,
            canonical_unit=_canonical_target_unit(target.identity),
        )
        for target in ordered_targets
        if target.identity in runtime_target_by_id
    )
    if len(target_descriptors) != len(ordered_targets):
        raise ValueError("Predict target descriptor projection is incomplete")
    target_identities = tuple(item.target_identity for item in target_descriptors)
    if len(target_identities) != len(set(target_identities)):
        raise ValueError("Predict target descriptor identity is duplicated")
    zero_fill = tuple(
        (item.ml_name, item.zero_fill_policy)
        for item in generation.projections.ml
        if item.active and item.ml_name
    )
    fingerprints = generation.fingerprints
    return PredictRuntimeSnapshot(
        generation_id=manifest.generation.generation_id,
        preprocessing_version=manifest.preprocessing_version,
        predict_projection=generation.projections.predict,
        column_descriptors=column_descriptors,
        ordered_input_ml_names=registry.input_ml_names,
        derived=evaluation_snapshot(manifest),
        one_hot=generation.projections.one_hot_runtime,
        active_targets=registry.active_target_names,
        target_result_keys=target_result_keys,
        target_descriptors=target_descriptors,
        zero_fill_policies=zero_fill,
        predict_fingerprint=fingerprints.predict,
        ordered_ml_fingerprint=fingerprints.ordered_ml,
        derived_fingerprint=fingerprints.derived_semantics,
        one_hot_fingerprint=fingerprints.one_hot,
        target_registry_fingerprint=fingerprints.target_registry,
        preprocessing_fingerprint=fingerprints.preprocessing,
    )


def compatibility_predict_runtime_snapshot() -> PredictRuntimeSnapshot:
    """Build the legacy/default facade once; production passes repository state."""
    manifest = bootstrap_manifest()
    return build_predict_runtime_snapshot(GenerationSnapshot(
        manifest,
        generate_projections(manifest),
        scoped_fingerprints(manifest),
        Path("."),
    ))


_TARGET_UNIT_BY_ID = {
    "ufm_target_df11df5180785a149e85f5f228aaa7e1": "W",
    "ufm_target_78b4bbb97725586a97e41ae0ad04c561": "W",
    "ufm_target_330e4539dc7e5bb583132943914a5df5": "kg",
    "ufm_target_4e8d07df9558577a94701a10cdeabf71": "Hz",
    "ufm_target_e73ce9f258985ccf8ce1d3774cc108ce": "Hz",
}


def _canonical_target_unit(target_identity: str) -> str:
    try:
        return _TARGET_UNIT_BY_ID[target_identity]
    except KeyError as exc:
        raise ValueError(
            "Predict canonical unit is missing for active Target identity "
            f"{target_identity}"
        ) from exc
