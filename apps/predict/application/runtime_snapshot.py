"""Immutable generation-bound Predict execution semantics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from weakref import ref

from apps.common.runtime_generation import GenerationSnapshot
from apps.common.runtime_generation.repository_contract import (
    _issue_generation_snapshot,
    require_issued_generation_snapshot,
)
from apps.predict.application.runtime_columns import (
    PredictRuntimeColumnDescriptor,
    build_runtime_column_descriptors,
)
from apps.predict.application.target_outcome import (
    MODEL_PREDICTION_VALUE_SOURCE,
    PredictionTargetDescriptor,
)
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
from core.data_definition.target_registry.runtime import (
    RuntimeTarget,
    model_registry_snapshot,
)
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
    target_registry_targets: tuple[RuntimeTarget, ...]
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


_ISSUED_PREDICT_RUNTIMES: dict[
    int,
    tuple[ref[PredictRuntimeSnapshot], tuple[object, ...]],
] = {}


def build_predict_runtime_snapshot(
    generation: GenerationSnapshot,
) -> PredictRuntimeSnapshot:
    """Project one already validated repository snapshot without external reads."""
    require_issued_generation_snapshot(generation)
    manifest = generation.manifest
    column_descriptors = build_runtime_column_descriptors(
        manifest.features,
        manifest.ordering.predict,
        generation.projections.predict,
    )
    registry = model_registry_snapshot(manifest)
    feature_by_id = {item.identity: item for item in manifest.features}
    runtime_target_by_id = {
        target.identity: target
        for group in registry.groups
        for target in group.targets
    }
    ordered_targets = tuple(
        runtime_target_by_id[identity]
        for identity in registry.target_presentation_order
        if identity in runtime_target_by_id
    )
    target_result_keys = tuple(
        (
            target.ml_name,
            feature_by_id[target.result_feature_identity].column_key,
        )
        for target in ordered_targets
    )
    target_descriptors = tuple(
        PredictionTargetDescriptor(
            target_identity=target.identity,
            result_feature_identity=target.result_feature_identity,
            ml_name=target.ml_name,
            result_key=feature_by_id[target.result_feature_identity].column_key,
            canonical_unit=_canonical_target_unit(target.identity),
        )
        for target in ordered_targets
    )
    if len(ordered_targets) != len(registry.target_presentation_order):
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
    runtime = PredictRuntimeSnapshot(
        generation_id=manifest.generation.generation_id,
        preprocessing_version=manifest.preprocessing_version,
        predict_projection=generation.projections.predict,
        column_descriptors=column_descriptors,
        ordered_input_ml_names=registry.input_ml_names,
        derived=evaluation_snapshot(manifest),
        one_hot=generation.projections.one_hot_runtime,
        active_targets=registry.active_target_names,
        target_registry_targets=ordered_targets,
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
    _validate_runtime_target_projection(runtime)
    _issue_predict_runtime(runtime)
    return runtime


def compatibility_predict_runtime_snapshot() -> PredictRuntimeSnapshot:
    """Build the legacy/default facade once; production passes repository state."""
    manifest = bootstrap_manifest()
    generation = _issue_generation_snapshot(
        manifest,
        generate_projections(manifest),
        scoped_fingerprints(manifest),
        Path("."),
    )
    return build_predict_runtime_snapshot(generation)


def validate_runtime_target_contract(runtime: PredictRuntimeSnapshot) -> None:
    """Require issued runtime provenance before validating its Target projection."""
    issued = _ISSUED_PREDICT_RUNTIMES.get(id(runtime))
    if (
        issued is None
        or issued[0]() is not runtime
        or issued[1] != _runtime_payload(runtime)
    ):
        raise ValueError(
            "Predict runtime Target authority provenance is missing or invalid"
        )
    _validate_runtime_target_projection(runtime)


def _validate_runtime_target_projection(runtime: PredictRuntimeSnapshot) -> None:
    """Check builder-owned convenience fields against its canonical projection."""
    descriptors = tuple(runtime.target_descriptors)
    authoritative = tuple(runtime.target_registry_targets)
    if not descriptors or not authoritative:
        raise ValueError("Predict runtime Target contract is empty")
    required_fields = tuple(
        (
            item.target_identity,
            item.result_feature_identity,
            item.ml_name,
            item.result_key,
            item.canonical_unit,
            item.value_source,
        )
        for item in descriptors
    )
    if any(not all(fields) for fields in required_fields):
        raise ValueError("Predict runtime Target descriptor is incomplete")
    for index, label in (
        (0, "Target identity"),
        (1, "result Feature identity"),
        (2, "Target ML name"),
        (3, "result key"),
    ):
        values = tuple(fields[index] for fields in required_fields)
        if len(values) != len(set(values)):
            raise ValueError(f"Predict runtime {label} is duplicated")
    authority_ids = tuple(item.identity for item in authoritative)
    if len(authority_ids) != len(set(authority_ids)):
        raise ValueError("Predict authoritative Target identity is duplicated")
    columns = {item.feature_identity: item for item in runtime.column_descriptors}
    expected = []
    for target in authoritative:
        column = columns.get(target.result_feature_identity)
        if column is None or column.role != "result" or not column.active:
            raise ValueError(
                "Predict authoritative Target/result Feature projection is invalid"
            )
        expected.append(PredictionTargetDescriptor(
            target_identity=target.identity,
            result_feature_identity=target.result_feature_identity,
            ml_name=target.ml_name,
            result_key=column.key,
            canonical_unit=_canonical_target_unit(target.identity),
            value_source=MODEL_PREDICTION_VALUE_SOURCE,
        ))
    expected_descriptors = tuple(expected)
    expected_targets = tuple(item.ml_name for item in expected_descriptors)
    expected_keys = tuple(
        (item.ml_name, item.result_key) for item in expected_descriptors
    )
    if tuple(runtime.active_targets) != expected_targets:
        raise ValueError("Predict active Target projection is not authoritative")
    if tuple(runtime.target_result_keys) != expected_keys:
        raise ValueError("Predict Target/result-key projection is not authoritative")
    if descriptors != expected_descriptors:
        raise ValueError(
            "Predict Target descriptors do not match authoritative metadata"
        )


def _issue_predict_runtime(runtime: PredictRuntimeSnapshot) -> None:
    identity = id(runtime)

    def release(reference: ref[PredictRuntimeSnapshot]) -> None:
        current = _ISSUED_PREDICT_RUNTIMES.get(identity)
        if current is not None and current[0] is reference:
            _ISSUED_PREDICT_RUNTIMES.pop(identity, None)

    reference = ref(runtime, release)
    _ISSUED_PREDICT_RUNTIMES[identity] = (reference, _runtime_payload(runtime))


def _runtime_payload(runtime: PredictRuntimeSnapshot) -> tuple[object, ...]:
    return tuple(
        getattr(runtime, name)
        for name in PredictRuntimeSnapshot.__dataclass_fields__
    )


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
