"""Pure shared evaluator for canonical restricted Derived definitions."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.data_definition.contract import (
    UnifiedFeatureManifest,
    current_derived_definitions,
    operand_ml_name,
    require_valid_contract,
)
from core.data_definition.derived_operand_policy import derived_operand_eligibility


@dataclass(frozen=True)
class DerivedEvaluatorInput:
    identity: str
    ml_name: str
    source_kind: str


@dataclass(frozen=True)
class DerivedEvaluationDefinition:
    identity: str
    output_ml_name: str
    operation: str
    numerator_identity: str
    numerator_ml_name: str
    denominator_identity: str
    denominator_ml_name: str
    zero_denominator_policy: str
    zero_value: float


@dataclass(frozen=True)
class DerivedEvaluationSnapshot:
    generation_id: str
    definitions: tuple[DerivedEvaluationDefinition, ...]
    evaluator_inputs: tuple[DerivedEvaluatorInput, ...] = ()


@dataclass(frozen=True)
class DerivedInputDependencyProjection:
    requested_outputs: tuple[str, ...]
    definition_identities: tuple[str, ...]
    base_inputs: tuple[DerivedEvaluatorInput, ...]


def evaluation_snapshot(
    manifest: UnifiedFeatureManifest,
) -> DerivedEvaluationSnapshot:
    """Build an immutable validated execution snapshot without external reads."""
    projections = require_valid_contract(manifest)
    current_by_id = {
        item.identity: item for item in current_derived_definitions(manifest)
    }
    definitions = tuple(
        _evaluation_definition(manifest, current_by_id[item.identity])
        for item in projections.derived
    )
    target_feature_ids = {item.feature_identity for item in manifest.targets}
    feature_by_id = {item.identity: item for item in manifest.features}
    evaluator_inputs = []
    for identity in manifest.ordering.ml:
        feature = feature_by_id.get(identity)
        if feature is None:
            continue
        eligibility = derived_operand_eligibility(
            manifest.features,
            current_by_id.values(),
            identity,
            target_feature_identities=target_feature_ids,
        )
        if eligibility.eligible:
            evaluator_inputs.append(DerivedEvaluatorInput(
                eligibility.identity,
                eligibility.ml_name,
                eligibility.source_kind,
            ))
    return DerivedEvaluationSnapshot(
        manifest.generation.generation_id,
        definitions,
        tuple(evaluator_inputs),
    )


def project_derived_input_dependencies(
    snapshot: DerivedEvaluationSnapshot,
    requested_outputs,
) -> DerivedInputDependencyProjection:  # noqa: ANN001
    """Project the active Derived closure and its transitive base inputs."""
    requested = tuple(dict.fromkeys(str(item) for item in requested_outputs))
    by_identity = {item.identity: item for item in snapshot.definitions}
    by_name = {item.output_ml_name: item for item in snapshot.definitions}
    needed_definitions: set[str] = set()
    needed_inputs: set[str] = set()

    def visit(definition: DerivedEvaluationDefinition) -> None:
        if definition.identity in needed_definitions:
            return
        needed_definitions.add(definition.identity)
        for identity in (
            definition.numerator_identity,
            definition.denominator_identity,
        ):
            dependency = by_identity.get(identity)
            if dependency is None:
                needed_inputs.add(identity)
            else:
                visit(dependency)

    for requested_output in requested:
        definition = by_identity.get(requested_output) or by_name.get(requested_output)
        if definition is not None:
            visit(definition)
    ordered_definitions = tuple(
        item.identity
        for item in snapshot.definitions
        if item.identity in needed_definitions
    )
    inputs_by_id = {item.identity: item for item in snapshot.evaluator_inputs}
    missing = needed_inputs.difference(inputs_by_id)
    if missing:
        raise ValueError(
            "validated Derived snapshot is missing evaluator input identity: "
            + ", ".join(sorted(missing))
        )
    return DerivedInputDependencyProjection(
        requested,
        ordered_definitions,
        tuple(
            item for item in snapshot.evaluator_inputs if item.identity in needed_inputs
        ),
    )


def snapshot_for_dependency_projection(
    snapshot: DerivedEvaluationSnapshot,
    projection: DerivedInputDependencyProjection,
) -> DerivedEvaluationSnapshot:
    """Return an immutable evaluator slice without reinterpreting the DAG."""
    identities = frozenset(projection.definition_identities)
    return DerivedEvaluationSnapshot(
        snapshot.generation_id,
        tuple(item for item in snapshot.definitions if item.identity in identities),
        projection.base_inputs,
    )


def missing_evaluator_input_ml_names(
    available_ml_names,
    projection: DerivedInputDependencyProjection,
) -> tuple[str, ...]:  # noqa: ANN001
    """Classify missing evaluator inputs in canonical projection order."""
    available = frozenset(str(item) for item in available_ml_names)
    return tuple(
        item.ml_name for item in projection.base_inputs if item.ml_name not in available
    )


def evaluate_derived_features(dataframe, snapshot: DerivedEvaluationSnapshot):  # noqa: ANN001, ANN201
    """Return a copy with active Derived outputs in validated DAG order."""
    result = dataframe.copy()
    for definition in snapshot.definitions:
        if definition.operation != "safe_ratio":
            raise ValueError(f"unsupported Derived operation: {definition.operation}")
        if definition.zero_denominator_policy != "constant":
            raise ValueError(
                "unsupported safe_ratio zero-denominator policy: "
                f"{definition.zero_denominator_policy}"
            )
        denominator = result[definition.denominator_ml_name]
        numerator = result[definition.numerator_ml_name]
        result[definition.output_ml_name] = np.where(
            denominator != 0,
            numerator / denominator,
            definition.zero_value,
        )
    return result


def _evaluation_definition(manifest, item):  # noqa: ANN001
    return DerivedEvaluationDefinition(
        identity=item.identity,
        output_ml_name=item.ml_name,
        operation=item.operation,
        numerator_identity=item.numerator_identity,
        numerator_ml_name=operand_ml_name(manifest, item.numerator_identity),
        denominator_identity=item.denominator_identity,
        denominator_ml_name=operand_ml_name(manifest, item.denominator_identity),
        zero_denominator_policy=item.zero_denominator_policy,
        zero_value=float(item.zero_value),
    )
