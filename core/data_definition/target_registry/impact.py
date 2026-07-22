"""Target-specific prepared command impact evidence."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.target_registry.runtime import apply_target_policy, model_registry_snapshot


@dataclass(frozen=True)
class TargetImpactEvidence:
    target_identity: str
    result_feature_identity: str
    before: tuple[str, str, str, bool, int] | None
    after: tuple[str, str, str, bool, int] | None
    model_group_before: str
    model_group_after: str
    policy_before: tuple[str, tuple[str, ...]] | None
    policy_after: tuple[str, tuple[str, ...]] | None
    training_inputs_before: tuple[str, ...]
    training_inputs_after: tuple[str, ...]
    active_targets_before: tuple[str, ...]
    active_targets_after: tuple[str, ...]
    presentation_fingerprint_changed: bool
    registry_fingerprint_changed: bool


def build_target_impact_evidence(base, candidate, result, before_fp, after_fp):  # noqa: ANN001
    feature_identity = (
        result.identity[1]
        if result.identity and result.identity[0] == "schema_row" else ""
    )
    before_by_feature = {item.feature_identity: item for item in base.targets}
    after_by_feature = {item.feature_identity: item for item in candidate.targets}
    before_target = before_by_feature.get(feature_identity)
    after_target = after_by_feature.get(feature_identity)
    if result.identity and result.identity[0] == "target":
        before_target = next((item for item in base.targets if item.identity == result.identity[1]), None)
        after_target = next((item for item in candidate.targets if item.identity == result.identity[1]), None)
    if before_target is None and after_target is None:
        return None
    target_identity = (after_target or before_target).identity
    before_target = next((item for item in base.targets if item.identity == target_identity), before_target)
    after_target = next((item for item in candidate.targets if item.identity == target_identity), after_target)
    before_snapshot = model_registry_snapshot(base)
    after_snapshot = model_registry_snapshot(candidate)

    def shape(target, manifest):  # noqa: ANN001
        if target is None:
            return None
        row = next(item for item in manifest.features if item.identity == target.feature_identity)
        return (row.label, row.column_key, target.ml_name, target.active, target.presentation_order)

    def policy(target, manifest, snapshot):  # noqa: ANN001
        if target is None:
            return None, ()
        owners = {item.identity: item.ml_name for item in (*manifest.features, *manifest.derived)}
        names = tuple(owners[identity] for identity in target.policy_owner_identities if identity in owners)
        runtime = next((item for group in snapshot.groups for item in group.targets if item.identity == target.identity), None)
        if runtime is not None:
            inputs = apply_target_policy(snapshot.input_ml_names, runtime)
        elif target.policy_mode == "allowed":
            inputs = tuple(name for name in snapshot.input_ml_names if name in set(names))
        else:
            inputs = tuple(name for name in snapshot.input_ml_names if name not in set(names))
        return (target.policy_mode, names), inputs

    before_policy, before_inputs = policy(before_target, base, before_snapshot)
    after_policy, after_inputs = policy(after_target, candidate, after_snapshot)
    return TargetImpactEvidence(
        target_identity,
        feature_identity or (after_target or before_target).feature_identity,
        shape(before_target, base), shape(after_target, candidate),
        before_target.model_group_identity if before_target else "",
        after_target.model_group_identity if after_target else "",
        before_policy, after_policy, before_inputs, after_inputs,
        before_snapshot.active_target_names, after_snapshot.active_target_names,
        before_fp.target_presentation != after_fp.target_presentation,
        before_fp.target_registry != after_fp.target_registry,
    )
