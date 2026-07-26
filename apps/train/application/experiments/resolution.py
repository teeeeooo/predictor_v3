"""Registry, target, Feature, and Derived resolution for experiments."""

from __future__ import annotations

from dataclasses import replace
import math
from typing import Any

from apps.train.application.experiments.contracts import ExperimentContractError
from core.data_definition.derived.evaluator import (
    DerivedEvaluationDefinition,
    DerivedEvaluationSnapshot,
    DerivedEvaluatorInput,
)
from core.data_definition.target_registry.runtime import (
    ModelRegistrySnapshot,
    RuntimeModelGroup,
    apply_target_policy,
)
from core.ml.derived_adapter import current_derived_evaluation_snapshot


def resolve_registry(
    snapshot: ModelRegistrySnapshot, payload: dict[str, Any]
) -> ModelRegistrySnapshot:
    requested = [*payload["targets"]["primary"], *payload["targets"]["guardrail"]]
    selected_ids = set(resolve_target_ids(snapshot, requested, default_all=True))
    included = tuple(payload["features"]["included"])
    excluded = set(payload["features"]["excluded"])
    experimental_names = {
        item.get("output")
        for item in payload["features"]["experimental_derived"]
        if isinstance(item, dict)
    }
    unknown = (set(included) | excluded).difference(snapshot.input_ml_names)
    unknown.difference_update(experimental_names)
    if unknown:
        raise ExperimentContractError(
            "feature_unknown", "Unknown training Feature(s): " + ", ".join(sorted(unknown))
        )
    input_names = tuple(dict.fromkeys(
        (*snapshot.input_ml_names, *(name for name in experimental_names if name))
    ))
    groups = []
    for group in snapshot.groups:
        targets = []
        for target in group.targets:
            if target.identity not in selected_ids:
                continue
            effective = tuple(dict.fromkeys((
                *apply_target_policy(input_names, target),
                *(name for name in experimental_names if name),
            )))
            if included:
                effective = tuple(name for name in effective if name in included)
            effective = tuple(name for name in effective if name not in excluded)
            targets.append(replace(
                target,
                policy_mode="allowed",
                policy_owner_identities=(),
                policy_ml_names=effective,
                legacy_noop_policy_names=(),
            ))
        groups.append(RuntimeModelGroup(
            group.identity, group.registry_key, group.name, group.use_rfe, tuple(targets)
        ))
    return replace(
        snapshot,
        input_ml_names=input_names,
        target_presentation_order=tuple(
            identity
            for identity in snapshot.target_presentation_order
            if identity in selected_ids
        ),
        groups=tuple(groups),
    )


def resolve_target_ids(
    snapshot: ModelRegistrySnapshot, values: list[Any], *, default_all: bool
) -> tuple[str, ...]:
    by_reference = {
        reference: target.identity
        for group in snapshot.groups
        for target in group.targets
        for reference in (target.identity, target.ml_name)
    }
    if not values and default_all:
        return tuple(snapshot.target_presentation_order)
    if any(type(item) is not str or item not in by_reference for item in values):
        raise ExperimentContractError(
            "target_unknown", "Target roles contain an unknown identity or ML name."
        )
    return tuple(dict.fromkeys(by_reference[item] for item in values))


def resolve_derived(
    snapshot: ModelRegistrySnapshot,
    payload: dict[str, Any],
    *,
    canonical: DerivedEvaluationSnapshot | None = None,
) -> DerivedEvaluationSnapshot:
    canonical = canonical or current_derived_evaluation_snapshot()
    definitions = list(canonical.definitions)
    inputs = list(canonical.evaluator_inputs)
    names = {item.output_ml_name for item in definitions} | {
        item.ml_name for item in inputs
    } | set(snapshot.known_ml_names)
    name_to_identity = {
        **{item.output_ml_name: item.identity for item in definitions},
        **{item.ml_name: item.identity for item in inputs},
    }
    for index, item in enumerate(payload["features"]["experimental_derived"]):
        _validate_derived_item(item, names, name_to_identity)
        output = item["output"]
        operands = (item["numerator"], item["denominator"])
        identity = f"experiment-derived-{index}-{_safe_fragment(output)}"
        definitions.append(DerivedEvaluationDefinition(
            identity,
            output,
            "safe_ratio",
            name_to_identity[operands[0]],
            operands[0],
            name_to_identity[operands[1]],
            operands[1],
            "constant",
            float(item["zero_value"]),
        ))
        names.add(output)
        name_to_identity[output] = identity
    required_inputs = [
        DerivedEvaluatorInput(f"experiment-input-{_safe_fragment(name)}", name, "feature")
        for name in snapshot.input_ml_names
        if name not in names
    ]
    return DerivedEvaluationSnapshot(
        snapshot.generation_id, tuple(definitions), tuple((*inputs, *required_inputs))
    )


def _validate_derived_item(item: Any, names: set[str], identities: dict[str, str]) -> None:
    fields = {
        "output", "operation", "numerator", "denominator",
        "zero_denominator_policy", "zero_value",
    }
    if not isinstance(item, dict) or set(item) != fields:
        raise ExperimentContractError(
            "experimental_derived_invalid",
            "Experimental Derived entries must use the closed v1 field set.",
        )
    output = item["output"]
    if (
        type(output) is not str
        or not output
        or output in names
        or item["operation"] != "safe_ratio"
        or item["zero_denominator_policy"] != "constant"
        or type(item["zero_value"]) not in {int, float}
        or not math.isfinite(float(item["zero_value"]))
    ):
        raise ExperimentContractError(
            "experimental_derived_invalid",
            "Experimental Derived definition is unsupported or conflicts with an owner.",
        )
    if any(
        type(value) is not str or value not in identities
        for value in (item["numerator"], item["denominator"])
    ):
        raise ExperimentContractError(
            "experimental_derived_operand_invalid",
            "Experimental Derived operands must reference known prior Features.",
        )


def _safe_fragment(value: str) -> str:
    return "".join(character if character.isalnum() else "-" for character in value)[:48]
