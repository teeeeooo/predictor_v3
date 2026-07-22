"""Phase 4G canonical Target/Result registry ownership regression."""

from __future__ import annotations

import json
from dataclasses import replace

from apps.train.adapters.data_definition_generation_repository import DataDefinitionGenerationRepository
from apps.train.controllers.train_controller import TrainController
from apps.train.controllers.target_authoring_projection import project_target_authoring
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.state.training_run_state import TrainingRequest
from core.data_definition.contract import (
    bootstrap_manifest, candidate_manifest_from_draft, current_target_definitions, load_manifest, migrate_manifest,
    scoped_fingerprints, validate_contract,
)
from core.data_definition.draft import build_data_definition_draft
from core.data_definition.target_registry.commands import apply_target_command
from core.data_definition.target_registry.intents import (
    AddTargetIntent, ChangeTargetModelGroupIntent, ChangeTargetPolicyIntent,
    DuplicateTargetIntent, EditTargetIntent, MoveTargetIntent, RemoveTargetIntent, RenameTargetIntent,
    SetTargetActiveIntent,
)
from core.data_definition.target_registry.runtime import (
    ModelRegistrySnapshot, apply_target_policy, model_registry_snapshot,
    ordered_training_input_pool,
)
from core.data_definition.target_registry.defaults import VALIDATED_MODEL_GROUPS
from core.ml.features import BASE_FEATURES, DERIVED_FEATURES, TARGETS
from core.ml.registry import MODEL_REGISTRY


def _draft():
    manifest = bootstrap_manifest()
    return manifest, build_data_definition_draft(manifest=manifest)


def _add_intent(manifest, *, ml_name="New Target"):
    return AddTargetIntent(
        "새 결과", "new_target", ml_name, manifest.model_groups[0].identity,
        "exclude", (manifest.targets[0].policy_owner_identities[0],),
    )


def test_existing_registry_and_final_training_inputs_match_golden_semantics():
    manifest = bootstrap_manifest()
    snapshot = model_registry_snapshot(manifest)
    assert [item.registry_key for item in snapshot.groups] == ["power_model", "hz_model", "ref_model"]
    assert [[item.ml_name for item in group.targets] for group in snapshot.groups] == [
        ["Cooling Power", "Heating Power"], ["Cooling Hz", "Heating Hz"], ["Ref Qty"],
    ]
    assert [item.use_rfe for item in snapshot.groups] == [True, True, False]
    assert snapshot.active_target_names == tuple(TARGETS)
    assert snapshot.input_ml_names == tuple(
        name for name in BASE_FEATURES + DERIVED_FEATURES if name not in set(TARGETS)
    )
    for group in snapshot.groups:
        for target in group.targets:
            rule = MODEL_REGISTRY[group.registry_key]["target_rules"][target.ml_name]
            expected = tuple(
                name for name in snapshot.input_ml_names
                if name in rule.get("allowed", snapshot.input_ml_names)
                and name not in rule.get("exclude", ())
            )
            assert apply_target_policy(snapshot.input_ml_names, target) == expected


def test_v3_target_policy_migration_is_identity_based_and_model_compatible():
    legacy = load_manifest("config/data_definition/manifest.json")
    migrated = migrate_manifest(legacy)
    assert legacy.contract_version.endswith(".v3")
    assert migrated.contract_version.endswith(".v4")
    assert [item.identity for item in current_target_definitions(legacy)] == [
        item.identity for item in migrated.targets
    ]
    assert [item.feature_identity for item in current_target_definitions(legacy)] == [
        item.feature_identity for item in migrated.targets
    ]
    assert all(item.policy_owner_identities for item in migrated.targets)
    assert scoped_fingerprints(legacy).model_compatibility == scoped_fingerprints(migrated).model_compatibility
    assert validate_contract(legacy) == validate_contract(migrated) == ()


def test_inactive_add_remove_is_exact_clean_and_uses_new_identities():
    manifest, draft = _draft()
    added = apply_target_command(draft, _add_intent(manifest))
    assert added.accepted
    new_target = added.draft.targets[-1]
    new_row = next(item for item in added.draft.rows if item.stable_identity == new_target.feature_identity)
    assert not new_target.active and not new_row.active
    assert new_target.identity not in {item.identity for item in manifest.targets}
    assert new_target.feature_identity not in {item.identity for item in manifest.features}
    removed = apply_target_command(added.draft, RemoveTargetIntent(new_target.identity))
    assert removed.accepted
    assert not removed.draft.is_changed
    assert removed.draft.changes() == ()


def test_rename_preserves_both_identities_and_policy_reference_is_rename_safe():
    manifest, draft = _draft()
    target = manifest.targets[0]
    renamed = apply_target_command(draft, RenameTargetIntent(
        target.identity, "냉방 전력 결과", "cooling_power_v2", "Cooling Power v2",
    ))
    assert renamed.accepted
    changed = next(item for item in renamed.draft.targets if item.identity == target.identity)
    assert changed.feature_identity == target.feature_identity
    assert changed.policy_owner_identities == target.policy_owner_identities
    # Stable legacy no-op Result references project the renamed name, not a stale string.
    heating_hz = next(item for item in renamed.draft.targets if item.ml_name == "Heating Hz")
    candidate = model_registry_snapshot(candidate_manifest_from_draft(renamed.draft, manifest))
    runtime = next(item for group in candidate.groups for item in group.targets if item.identity == heating_hz.identity)
    assert "Cooling Power v2" in runtime.legacy_noop_policy_names


def test_duplicate_group_policy_reassign_and_presentation_order_are_independent():
    manifest, draft = _draft()
    source = manifest.targets[0]
    duplicated = apply_target_command(draft, DuplicateTargetIntent(
        source.identity, "복제", "cooling_power_copy", "Cooling Power Copy",
    ))
    assert duplicated.accepted and not duplicated.draft.targets[-1].active
    duplicate = duplicated.draft.targets[-1]
    reassigned = apply_target_command(duplicated.draft, ChangeTargetModelGroupIntent(
        duplicate.identity, manifest.model_groups[1].identity,
    ))
    assert reassigned.accepted
    changed_policy = apply_target_command(reassigned.draft, ChangeTargetPolicyIntent(
        duplicate.identity, "allowed", (manifest.targets[2].policy_owner_identities[0],),
    ))
    assert changed_policy.accepted
    before = scoped_fingerprints(manifest)
    moved = apply_target_command(draft, MoveTargetIntent(source.identity, "down"))
    after_manifest = candidate_manifest_from_draft(moved.draft, manifest)
    after = scoped_fingerprints(after_manifest)
    assert moved.accepted
    assert before.target_presentation != after.target_presentation
    assert before.model_compatibility == after.model_compatibility


def test_policy_validation_blocks_missing_duplicate_result_and_empty_references():
    manifest = bootstrap_manifest()
    target = manifest.targets[0]
    cases = (
        replace(target, policy_owner_identities=("missing",)),
        replace(target, policy_owner_identities=(target.policy_owner_identities[0],) * 2),
        replace(target, policy_owner_identities=(manifest.targets[1].feature_identity,)),
        replace(target, policy_mode="allowed", policy_owner_identities=()),
        replace(target, policy_mode="script"),
    )
    expected = (
        "target_policy_owner_invalid", "target_policy_owner_duplicate",
        "target_policy_owner_invalid", "target_policy_allowed_empty", "target_policy_mode_invalid",
    )
    for changed, code in zip(cases, expected, strict=True):
        raw = replace(manifest, targets=(changed, *manifest.targets[1:]))
        assert code in {item.code for item in validate_contract(raw)}


def test_ordered_training_input_pool_is_the_policy_ui_and_runtime_owner():
    manifest, draft = _draft()
    pool = ordered_training_input_pool(manifest)
    snapshot = model_registry_snapshot(manifest)
    projection = project_target_authoring(draft)
    by_id = {item.identity: item for item in pool.owners}

    assert pool.ml_names == snapshot.input_ml_names
    assert tuple(item.identity for item in projection.policy_owner_options if item.selectable) == pool.identities
    assert any(item.owner_kind == "derived" and item.eligible for item in pool.owners)
    assert any(item.owner_kind == "one_hot_feature" and item.eligible for item in pool.owners)
    assert any(item.owner_kind in {"input", "auto"} and item.eligible for item in pool.owners)
    for target in snapshot.groups[0].targets:
        row = next(item for item in projection.rows if item.identity == target.identity)
        assert row.final_training_inputs == apply_target_policy(pool.ml_names, target)
    assert all(not by_id[item.feature_identity].eligible for item in manifest.targets)


def test_policy_rejects_owners_outside_actual_ordered_runtime_pool():
    manifest = bootstrap_manifest()
    target = manifest.targets[0]
    owner = next(
        item for item in manifest.features
        if item.identity in manifest.ordering.ml and item.role == "input"
    )

    def issues_for(changed_owner, *, keep_order):  # noqa: ANN001
        features = tuple(
            changed_owner if item.identity == owner.identity else item
            for item in manifest.features
        )
        ml_order = manifest.ordering.ml if keep_order else tuple(
            identity for identity in manifest.ordering.ml if identity != owner.identity
        )
        raw = replace(
            manifest,
            features=features,
            ordering=replace(manifest.ordering, ml=ml_order),
            targets=(replace(
                target, policy_mode="allowed", policy_owner_identities=(owner.identity,),
            ), *manifest.targets[1:]),
        )
        return {item.code for item in validate_contract(raw)}

    assert "target_policy_owner_invalid" in issues_for(
        replace(owner, model_input_enabled=False), keep_order=False,
    )
    assert "target_policy_owner_invalid" in issues_for(owner, keep_order=False)
    assert "target_policy_owner_invalid" in issues_for(
        replace(owner, active=False), keep_order=False,
    )
    assert "target_policy_owner_invalid" in issues_for(
        replace(owner, role="helper"), keep_order=True,
    )

    all_inputs = ordered_training_input_pool(manifest).identities
    exclude_all = replace(
        target, policy_mode="exclude", policy_owner_identities=all_inputs,
    )
    assert "target_policy_result_empty" in {
        item.code for item in validate_contract(replace(
            manifest, targets=(exclude_all, *manifest.targets[1:]),
        ))
    }
    command = apply_target_command(
        build_data_definition_draft(manifest=manifest),
        ChangeTargetPolicyIntent(target.identity, "allowed", (manifest.targets[1].feature_identity,)),
    )
    assert not command.accepted
    assert command.draft == build_data_definition_draft(manifest=manifest)
    assert "target_policy_owner_invalid" in {item.code for item in command.issues}


def test_validated_model_group_identities_are_immutable_catalog_facts():
    manifest = bootstrap_manifest()
    expected = tuple(item.identity for item in VALIDATED_MODEL_GROUPS)
    assert tuple(item.identity for item in manifest.model_groups) == expected

    replacement = "ufm_model_group_replacement"
    replaced_groups = (
        replace(manifest.model_groups[0], identity=replacement),
        *manifest.model_groups[1:],
    )
    replaced_targets = tuple(
        replace(item, model_group_identity=replacement)
        if item.model_group_identity == expected[0] else item
        for item in manifest.targets
    )
    assert "model_group_identity_mutation" in {
        item.code for item in validate_contract(replace(
            manifest, model_groups=replaced_groups, targets=replaced_targets,
        ))
    }

    swapped_groups = (
        replace(manifest.model_groups[0], identity=expected[1]),
        replace(manifest.model_groups[1], identity=expected[0]),
        manifest.model_groups[2],
    )
    swapped_targets = tuple(replace(
        item,
        model_group_identity=(
            expected[1] if item.model_group_identity == expected[0]
            else expected[0] if item.model_group_identity == expected[1]
            else item.model_group_identity
        ),
    ) for item in manifest.targets)
    assert "model_group_identity_mutation" in {
        item.code for item in validate_contract(replace(
            manifest, model_groups=swapped_groups, targets=swapped_targets,
        ))
    }
    assert "stable_identity_duplicate" in {
        item.code for item in validate_contract(replace(
            manifest,
            model_groups=(manifest.model_groups[0], replace(
                manifest.model_groups[1], identity=expected[0],
            ), manifest.model_groups[2]),
        ))
    }
    assert "model_group_catalog_invalid" in {
        item.code for item in validate_contract(replace(
            manifest,
            model_groups=(*manifest.model_groups, replace(
                manifest.model_groups[0],
                identity="ufm_model_group_fourth", registry_key="fourth_model",
            )),
        ))
    }


def test_visibility_preview_is_complete_and_presentation_only(tmp_path):
    manifest, draft = _draft()
    target = manifest.targets[0]
    row = next(item for item in draft.rows if item.stable_identity == target.feature_identity)
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    repository.publish(manifest)
    service = DataDefinitionService(generation_repository=repository)
    prepared = service.prepare_feature_command(
        draft, EditTargetIntent(target.identity, row.label, not row.visible), source_revision=1,
    )
    evidence = prepared.preview.target_evidence
    assert prepared.command_accepted and evidence is not None
    assert evidence.before[3] is row.visible
    assert evidence.after[3] is (not row.visible)
    assert evidence.presentation_fingerprint_changed
    assert not evidence.registry_fingerprint_changed
    assert not prepared.model_compatibility_changed
    assert evidence.training_inputs_before == evidence.training_inputs_after
    assert evidence.active_targets_before == evidence.active_targets_after


def test_inactive_save_is_allowed_active_enable_keeps_model_guard(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    repository.publish(bootstrap_manifest())
    service = DataDefinitionService(generation_repository=repository)
    draft = service.load_draft()
    prepared = service.prepare_feature_command(draft, _add_intent(draft.base_manifest), source_revision=1)
    assert prepared.command_accepted and prepared.save_allowed
    saved = service.save_schema_draft(prepared.result.draft)
    assert saved.success
    reloaded = service.load_draft()
    new_target = reloaded.targets[-1]
    enable = service.prepare_feature_command(
        reloaded, SetTargetActiveIntent(new_target.identity, True), source_revision=2,
    )
    assert enable.command_accepted
    assert enable.model_compatibility_changed
    assert not enable.save_allowed
    assert "model_compatibility_migration_required" in {item.code for item in enable.blockers}


class _CaptureExecution:
    def __init__(self):
        self.request = None

    def start(self, request, callbacks=None):  # noqa: ANN001
        self.request = request

    def cancel(self):
        return True


def test_training_start_freezes_generation_registry_payload(tmp_path):
    manifest = bootstrap_manifest()
    first = model_registry_snapshot(manifest)
    changed = replace(manifest, generation=replace(manifest.generation, generation_id="later"))
    snapshots = [first]
    execution = _CaptureExecution()
    controller = TrainController(
        execution=execution,
        registry_provider=lambda: snapshots[-1],
    )
    data = tmp_path / "train.csv"; data.write_text("x\n", encoding="utf-8")
    controller.start(TrainingRequest("frozen", str(data)))
    frozen = execution.request
    snapshots.append(model_registry_snapshot(changed))
    decoded = ModelRegistrySnapshot.from_payload(json.loads(frozen.registry_payload_json))
    assert frozen.generation_id == first.generation_id
    assert frozen.registry_fingerprint == first.registry_fingerprint
    assert decoded == first
    assert controller.registry_snapshot().generation_id == "later"
    assert frozen.generation_id != controller.registry_snapshot().generation_id


def test_training_production_path_has_no_static_registry_or_target_owner():
    training_source = open("core/ml/training.py", encoding="utf-8").read()
    preprocessing_source = open("core/ml/preprocessing.py", encoding="utf-8").read()
    assert "for model_key in MODEL_REGISTRY" not in training_source
    assert "get_model_config(" not in training_source
    assert "config[\"targets\"] + TARGETS" not in preprocessing_source


def test_target_publication_does_not_touch_mapping_or_model_artifact(tmp_path):
    mapping = tmp_path / "mapping.json"; mapping.write_bytes(b'{"sentinel":true}\n')
    model = tmp_path / "model.pkl"; model.write_bytes(b"model-sentinel")
    before = mapping.read_bytes(), model.read_bytes()
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    repository.publish(bootstrap_manifest())
    service = DataDefinitionService(generation_repository=repository)
    draft = service.load_draft()
    result = apply_target_command(draft, _add_intent(draft.base_manifest))
    assert result.accepted and service.save_schema_draft(result.draft).success
    assert (mapping.read_bytes(), model.read_bytes()) == before
    assert not tuple((tmp_path / "definitions").glob("*.staging-*"))


def test_raw_invalid_target_candidate_is_blocked_before_staging(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    manifest = bootstrap_manifest()
    repository.publish(manifest)
    invalid = replace(
        manifest,
        generation=replace(manifest.generation, generation_id="invalid-target"),
        targets=(replace(manifest.targets[0], model_group_identity="unknown"), *manifest.targets[1:]),
    )
    try:
        repository.publish(invalid)
    except ValueError as exc:
        assert "target_model_group_invalid" in str(exc)
    else:
        raise AssertionError("invalid Target candidate was published")
    assert repository.active_generation_id() == manifest.generation.generation_id
    assert not (tmp_path / "definitions" / "generations" / "invalid-target").exists()
    assert not tuple((tmp_path / "definitions").glob("*.staging-*"))
