"""Application-owned Target inventory and structured policy choices."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.contract.candidate import candidate_manifest_from_draft
from core.data_definition.target_registry.runtime import (
    apply_target_policy,
    model_registry_snapshot,
    ordered_training_input_pool,
)


@dataclass(frozen=True)
class TargetPolicyOwnerOption:
    identity: str
    ml_name: str
    owner_kind: str
    selectable: bool
    reason: str = ""


@dataclass(frozen=True)
class TargetAuthoringRow:
    identity: str
    result_feature_identity: str
    label: str
    column_key: str
    ml_name: str
    visible: bool
    active: bool
    presentation_order: int
    model_group_identity: str
    registry_key: str
    model_group_name: str
    use_rfe: bool
    policy_mode: str
    policy_owner_identities: tuple[str, ...]
    policy_ml_names: tuple[str, ...]
    final_training_inputs: tuple[str, ...]


@dataclass(frozen=True)
class TargetAuthoringProjection:
    rows: tuple[TargetAuthoringRow, ...]
    policy_owner_options: tuple[TargetPolicyOwnerOption, ...]
    active_target_names: tuple[str, ...]
    model_groups: tuple[tuple[str, str, str, bool], ...]


def project_target_authoring(draft) -> TargetAuthoringProjection:  # noqa: ANN001
    manifest = candidate_manifest_from_draft(draft, draft.base_manifest)
    snapshot = model_registry_snapshot(manifest)
    row_by_feature = {
        item.stable_identity: item for item in draft.rows if item.source_kind == "schema_row"
    }
    group_by_id = {item.identity: item for item in snapshot.groups}
    runtime_target_by_id = {
        item.identity: item for group in snapshot.groups for item in group.targets
    }
    input_pool = ordered_training_input_pool(manifest)
    ordered_pool = input_pool.ml_names
    owners = {item.identity: item for item in (*manifest.features, *manifest.derived)}
    owner_options = tuple(TargetPolicyOwnerOption(
        identity=item.identity,
        ml_name=item.ml_name,
        owner_kind=item.owner_kind,
        selectable=item.eligible,
        reason=item.reason,
    ) for item in input_pool.owners)
    rows = []
    for target in draft.targets:
        result = row_by_feature[target.feature_identity]
        group = group_by_id[target.model_group_identity]
        runtime_target = runtime_target_by_id.get(target.identity)
        policy_names = tuple(
            owners[identity].ml_name for identity in target.policy_owner_identities
            if identity in owners
        )
        if runtime_target is not None:
            final_inputs = apply_target_policy(ordered_pool, runtime_target)
        elif target.policy_mode == "allowed":
            final_inputs = tuple(name for name in ordered_pool if name in set(policy_names))
        else:
            final_inputs = tuple(name for name in ordered_pool if name not in set(policy_names))
        rows.append(TargetAuthoringRow(
            identity=target.identity,
            result_feature_identity=target.feature_identity,
            label=result.label,
            column_key=result.column_key,
            ml_name=target.ml_name,
            visible=result.visible,
            active=target.active,
            presentation_order=target.presentation_order,
            model_group_identity=group.identity,
            registry_key=group.registry_key,
            model_group_name=group.name,
            use_rfe=group.use_rfe,
            policy_mode=target.policy_mode,
            policy_owner_identities=target.policy_owner_identities,
            policy_ml_names=policy_names,
            final_training_inputs=final_inputs,
        ))
    return TargetAuthoringProjection(
        tuple(rows), owner_options, snapshot.active_target_names,
        tuple((group.identity, group.registry_key, group.name, group.use_rfe) for group in snapshot.groups),
    )
