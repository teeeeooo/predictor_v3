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
    return DerivedEvaluationSnapshot(manifest.generation.generation_id, definitions)


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
