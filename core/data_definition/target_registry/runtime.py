"""Pure immutable projection consumed by Train and Target impact previews."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from core.data_definition.target_registry.defaults import VALIDATED_MODEL_GROUPS


@dataclass(frozen=True)
class TrainingInputOwner:
    identity: str
    ml_name: str
    owner_kind: str
    eligible: bool
    blocker_code: str = ""
    reason: str = ""


@dataclass(frozen=True)
class OrderedTrainingInputPool:
    owners: tuple[TrainingInputOwner, ...]

    @property
    def eligible_owners(self) -> tuple[TrainingInputOwner, ...]:
        return tuple(item for item in self.owners if item.eligible)

    @property
    def identities(self) -> tuple[str, ...]:
        return tuple(item.identity for item in self.eligible_owners)

    @property
    def ml_names(self) -> tuple[str, ...]:
        return tuple(item.ml_name for item in self.eligible_owners)


@dataclass(frozen=True)
class RuntimeTarget:
    identity: str
    result_feature_identity: str
    ml_name: str
    policy_mode: str
    policy_owner_identities: tuple[str, ...]
    policy_ml_names: tuple[str, ...]
    legacy_noop_policy_names: tuple[str, ...] = ()


@dataclass(frozen=True)
class RuntimeModelGroup:
    identity: str
    registry_key: str
    name: str
    use_rfe: bool
    targets: tuple[RuntimeTarget, ...]


@dataclass(frozen=True)
class ModelRegistrySnapshot:
    generation_id: str
    registry_fingerprint: str
    ordered_ml_fingerprint: str
    derived_semantics_fingerprint: str
    one_hot_fingerprint: str
    preprocessing_version: str
    input_ml_names: tuple[str, ...]
    training_headers: tuple[str, ...]
    known_ml_names: tuple[str, ...]
    target_presentation_order: tuple[str, ...]
    groups: tuple[RuntimeModelGroup, ...]

    @property
    def active_target_names(self) -> tuple[str, ...]:
        by_id = {target.identity: target for group in self.groups for target in group.targets}
        return tuple(by_id[identity].ml_name for identity in self.target_presentation_order if identity in by_id)

    def compatibility_registry(self) -> dict[str, dict[str, object]]:
        return {
            group.registry_key: {
                "name": group.name,
                "targets": [item.ml_name for item in group.targets],
                "use_rfe": group.use_rfe,
                "target_rules": {
                    item.ml_name: {
                        item.policy_mode: [*item.policy_ml_names, *item.legacy_noop_policy_names]
                    }
                    for item in group.targets
                },
            }
            for group in self.groups
        }

    def to_payload(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> "ModelRegistrySnapshot":
        return cls(
            generation_id=str(payload["generation_id"]),
            registry_fingerprint=str(payload["registry_fingerprint"]),
            ordered_ml_fingerprint=str(payload["ordered_ml_fingerprint"]),
            derived_semantics_fingerprint=str(payload["derived_semantics_fingerprint"]),
            one_hot_fingerprint=str(payload["one_hot_fingerprint"]),
            preprocessing_version=str(payload["preprocessing_version"]),
            input_ml_names=tuple(payload["input_ml_names"]),
            training_headers=tuple(payload["training_headers"]),
            known_ml_names=tuple(payload["known_ml_names"]),
            target_presentation_order=tuple(payload["target_presentation_order"]),
            groups=tuple(RuntimeModelGroup(
                identity=str(group["identity"]),
                registry_key=str(group["registry_key"]),
                name=str(group["name"]),
                use_rfe=bool(group["use_rfe"]),
                targets=tuple(RuntimeTarget(
                    **{key: value for key, value in target.items()
                       if key not in {"policy_owner_identities", "policy_ml_names", "legacy_noop_policy_names"}},
                    policy_owner_identities=tuple(target["policy_owner_identities"]),
                    policy_ml_names=tuple(target["policy_ml_names"]),
                    legacy_noop_policy_names=tuple(target.get("legacy_noop_policy_names", ())),
                ) for target in group["targets"]),
            ) for group in payload["groups"]),
        )


def model_registry_snapshot(manifest) -> ModelRegistrySnapshot:  # noqa: ANN001
    """Project one validated manifest without filesystem or mutable state reads."""
    from core.data_definition.contract.compatibility import current_target_definitions
    from core.data_definition.contract.fingerprints import scoped_fingerprints

    targets = current_target_definitions(manifest)
    owners = {
        item.identity: item.ml_name
        for item in (*manifest.features, *manifest.derived)
        if item.ml_name
    }
    owner_objects = {item.identity: item for item in (*manifest.features, *manifest.derived)}
    input_pool = ordered_training_input_pool(manifest)
    input_ml_names = input_pool.ml_names
    training_headers = tuple(
        item.ml_name for item in manifest.features
        if item.active and item.ml_name and item.role in {"input", "auto", "one_hot_feature", "result"}
    )
    known_ml_names = tuple(
        owner_objects[identity].ml_name for identity in manifest.ordering.ml
        if owner_objects[identity].ml_name
    )
    groups_by_id = {item.identity: item for item in manifest.model_groups}
    groups_by_key = {item.registry_key: item for item in manifest.model_groups}
    runtime_groups = []
    for supported in VALIDATED_MODEL_GROUPS:
        group = groups_by_key[supported.registry_key]
        runtime_targets = tuple(
            RuntimeTarget(
                identity=item.identity,
                result_feature_identity=item.feature_identity,
                ml_name=item.ml_name,
                policy_mode=item.policy_mode,
                policy_owner_identities=item.policy_owner_identities,
                policy_ml_names=tuple(owners[identity] for identity in item.policy_owner_identities),
                legacy_noop_policy_names=tuple(
                    owners[identity] for identity in item.legacy_noop_result_identities
                ),
            )
            for item in sorted(
                (target for target in targets if target.active and target.model_group_identity == group.identity),
                key=lambda item: (item.registry_order, item.identity),
            )
        )
        runtime_groups.append(RuntimeModelGroup(
            identity=group.identity,
            registry_key=group.registry_key,
            name=group.name,
            use_rfe=group.use_rfe,
            targets=runtime_targets,
        ))
    fingerprints = scoped_fingerprints(manifest)
    return ModelRegistrySnapshot(
        generation_id=manifest.generation.generation_id,
        registry_fingerprint=fingerprints.target_registry,
        ordered_ml_fingerprint=fingerprints.ordered_ml,
        derived_semantics_fingerprint=fingerprints.derived_semantics,
        one_hot_fingerprint=fingerprints.one_hot,
        preprocessing_version=manifest.preprocessing_version,
        input_ml_names=input_ml_names,
        training_headers=training_headers,
        known_ml_names=known_ml_names,
        target_presentation_order=tuple(
            identity for identity in manifest.ordering.targets
            if next(item for item in targets if item.identity == identity).active
        ),
        groups=tuple(runtime_groups),
    )


def apply_target_policy(columns, target: RuntimeTarget) -> tuple[str, ...]:  # noqa: ANN001
    """Apply the closed policy catalog deterministically to an ordered input pool."""
    return apply_ordered_target_policy(
        columns, target.policy_mode, target.policy_ml_names,
    )


def apply_ordered_target_policy(ordered_values, mode: str, selected_values) -> tuple[str, ...]:  # noqa: ANN001
    """Apply one policy to ordered identity or ML-name values without reordering."""
    ordered = tuple(ordered_values)
    selected = set(selected_values)
    if mode == "allowed":
        return tuple(value for value in ordered if value in selected)
    if mode == "exclude":
        return tuple(value for value in ordered if value not in selected)
    raise ValueError(f"unsupported Target policy mode: {mode}")


def ordered_training_input_pool(manifest) -> OrderedTrainingInputPool:  # noqa: ANN001
    """Project the one ordered identity pool shared by policy and Train runtime."""
    from core.data_definition.contract.model import DerivedDefinition, LegacyDerivedDefinition

    all_owners = tuple((*manifest.features, *manifest.derived))
    owner_by_id = {item.identity: item for item in all_owners}
    ordered_ids = tuple(manifest.ordering.ml)
    ordered_set = set(ordered_ids)
    storage_ids = tuple(item.identity for item in all_owners if item.ml_name)
    candidate_ids = (*ordered_ids, *(identity for identity in storage_ids if identity not in ordered_set))
    ml_name_counts: dict[str, int] = {}
    for owner in all_owners:
        if owner.ml_name:
            ml_name_counts[owner.ml_name] = ml_name_counts.get(owner.ml_name, 0) + 1

    projected = []
    for identity in candidate_ids:
        owner = owner_by_id.get(identity)
        if owner is None:
            projected.append(TrainingInputOwner(
                identity, "", "missing", False, "training_input_owner_missing",
                "Canonical ML order references a missing owner.",
            ))
            continue
        is_derived = isinstance(owner, (DerivedDefinition, LegacyDerivedDefinition))
        role = "derived" if is_derived else owner.role
        reason = ""
        code = ""
        if not getattr(owner, "active", True):
            code, reason = "training_input_owner_inactive", "Owner is inactive."
        elif not owner.ml_name:
            code, reason = "training_input_ml_name_missing", "Owner has no ML name."
        elif identity not in ordered_set:
            code, reason = "training_input_owner_unordered", "Owner is not in canonical ML order."
        elif role == "result":
            code, reason = "training_input_result_leakage", "Result Features cannot be training inputs."
        elif ml_name_counts.get(owner.ml_name, 0) != 1:
            code, reason = "training_input_ml_name_duplicate", "ML name projection is not unique."
        elif not is_derived and role not in {"input", "auto", "one_hot_feature"}:
            code, reason = "training_input_shape_unsupported", "Feature runtime role is not supported by Train."
        elif not is_derived and not owner.model_input_enabled:
            code, reason = "training_input_intent_disabled", "Feature is not enabled as a model input."
        projected.append(TrainingInputOwner(
            identity=identity,
            ml_name=owner.ml_name,
            owner_kind=role,
            eligible=not code,
            blocker_code=code,
            reason=reason,
        ))
    return OrderedTrainingInputPool(tuple(projected))
