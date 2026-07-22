"""Pure immutable projection consumed by Train and Target impact previews."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from core.data_definition.target_registry.defaults import VALIDATED_MODEL_GROUPS


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
    input_ml_names = tuple(
        owner_objects[identity].ml_name
        for identity in manifest.ordering.ml
        if getattr(owner_objects[identity], "active", True)
        and getattr(owner_objects[identity], "role", "derived") != "result"
        and owner_objects[identity].ml_name
    )
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
    ordered = tuple(columns)
    selected = set(target.policy_ml_names)
    if target.policy_mode == "allowed":
        return tuple(name for name in ordered if name in selected)
    if target.policy_mode == "exclude":
        return tuple(name for name in ordered if name not in selected)
    raise ValueError(f"unsupported Target policy mode: {target.policy_mode}")
