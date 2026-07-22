"""Controlled One-hot group/category lifecycle tests."""

from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from core.data_definition import AddDefinitionIntent, AddDerivedIntent
from core.data_definition.contract import scoped_fingerprints
from core.data_definition.one_hot.intents import (
    AddOneHotCategoryIntent,
    AddOneHotGroupIntent,
    AssignOneHotSelectorIntent,
    ChangeOneHotSourceModeIntent,
    DuplicateOneHotGroupIntent,
    DuplicateOneHotCategoryIntent,
    EditOneHotCategoryIntent,
    EditOneHotGroupIntent,
    MoveOneHotCategoryIntent,
    RemoveOneHotCategoryIntent,
    RemoveOneHotGroupIntent,
    RenameOneHotEmittedFeatureIntent,
    RenameOneHotGroupIntent,
    SetOneHotCategoryActiveIntent,
    SetOneHotGroupActiveIntent,
)
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.one_hot.model import VocabularyCategory, VocabularySnapshot


def _controller(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path)
    repository.publish(bootstrap_manifest())
    snapshots = (
        VocabularySnapshot("mapping_backed", "ref_type", tuple(
            VocabularyCategory(f"ref:{value}", value)
            for value in ("R410A", "R32", "R290", "R744")
        )),
        VocabularySnapshot("mapping_backed", "exp_type", tuple(
            VocabularyCategory(f"exp:{value}", value)
            for value in ("EEV", "Capi")
        )),
    )
    controller = DataDefinitionController(DataDefinitionService(
        generation_repository=repository,
        vocabulary_snapshots=snapshots,
    ))
    controller.refresh()
    return controller, repository


def _apply(controller, intent):
    prepared = controller.preview_one_hot_command(intent)
    assert prepared.command_accepted, prepared.blockers
    state = controller.apply_prepared_one_hot_command(prepared)
    assert state.last_action_ok
    return prepared


def test_static_inactive_authoring_save_reload_and_active_guard(tmp_path):
    controller, repository = _controller(tmp_path)
    before = repository.read_active().fingerprints
    selector = next(item for item in controller._draft.rows if item.column_key == "idu")
    _apply(controller, AddOneHotGroupIntent(
        "indoor_kind", selector.stable_identity, "static", "",
        "warn_all_zero", "all_zero",
    ))
    group = controller.one_hot_authoring_projection().groups[-1]
    added = _apply(controller, AddOneHotCategoryIntent(
        group.identity, "Wall", "Indoor_Wall"
    ))
    assert not added.model_compatibility_changed
    save = controller.save_schema()
    assert save.last_action_ok
    active = repository.read_active()
    assert active.fingerprints.model_compatibility == before.model_compatibility
    reloaded_selector = next(item for item in controller._draft.rows
                             if item.stable_identity == selector.stable_identity)
    assert reloaded_selector == selector
    group = controller.one_hot_authoring_projection().groups[-1]
    assert not group.active and not group.categories[0].active
    _apply(controller, SetOneHotCategoryActiveIntent(group.categories[0].identity, True))
    preview = controller.preview_one_hot_command(
        SetOneHotGroupActiveIntent(group.identity, True)
    )
    assert not preview.command_accepted
    assert preview.blockers[0].code == "mapping_trigger_reference"


def test_rename_edit_duplicate_preserve_or_create_expected_identities(tmp_path):
    controller, _repository = _controller(tmp_path)
    group = controller.one_hot_authoring_projection().groups[0]
    category = group.categories[0]
    prepared = _apply(controller, RenameOneHotGroupIntent(group.identity, "coolant"))
    assert not prepared.model_compatibility_changed
    renamed = controller.one_hot_authoring_projection().groups[0]
    assert renamed.identity == group.identity
    assert renamed.selector_feature_identity == group.selector_feature_identity
    assert [item.identity for item in renamed.categories] == [
        item.identity for item in group.categories
    ]
    edited = _apply(controller, RenameOneHotEmittedFeatureIntent(
        category.identity, "R410A_Flag"
    ))
    after = next(item for item in controller.one_hot_authoring_projection().groups[0].categories
                 if item.identity == category.identity)
    assert after.emitted_feature_identity == category.emitted_feature_identity
    assert edited.model_compatibility_changed
    source_edited = _apply(controller, EditOneHotCategoryIntent(
        category.identity, source_value="R744"
    ))
    after_source = next(
        item for item in controller.one_hot_authoring_projection().groups[0].categories
        if item.identity == category.identity
    )
    assert after_source.identity == category.identity
    assert after_source.emitted_feature_identity == category.emitted_feature_identity
    assert after_source.source_value == "R744"
    assert source_edited.model_compatibility_changed
    duplicate = _apply(controller, DuplicateOneHotCategoryIntent(
        category.identity, "R410A", "R410A_Copy_Flag"
    ))
    duplicated = next(item for item in controller.one_hot_authoring_projection().groups[0].categories
                      if item.source_value == "R410A")
    assert duplicated.identity != category.identity
    assert duplicated.emitted_feature_identity != category.emitted_feature_identity
    assert not duplicated.active
    assert duplicate.command_accepted


def test_group_edit_and_selector_assignment_preserve_group_relations(tmp_path):
    controller, _repository = _controller(tmp_path)
    group = controller.one_hot_authoring_projection().groups[0]
    edited = _apply(controller, EditOneHotGroupIntent(
        group.identity, "warn_all_zero", "all_zero"
    ))
    assert not edited.model_compatibility_changed
    selector = next(item for item in controller._draft.rows if item.column_key == "idu")
    blocked = controller.preview_one_hot_command(AssignOneHotSelectorIntent(
        group.identity, selector.stable_identity, "detach"
    ))
    assert not blocked.command_accepted
    assert blocked.blockers[0].code == "one_hot_selector_restore_missing"
    unchanged = controller.one_hot_authoring_projection().groups[0]
    assert unchanged.identity == group.identity
    assert unchanged.selector_feature_identity == group.selector_feature_identity
    assert [item.identity for item in unchanged.categories] == [
        item.identity for item in group.categories
    ]


def test_reorder_is_group_local_deterministic_and_model_sensitive(tmp_path):
    controller, repository = _controller(tmp_path)
    before = repository.read_active().manifest
    group = controller.one_hot_authoring_projection().groups[0]
    outside_before = tuple(
        identity for identity in before.ordering.ml
        if identity not in {item.emitted_feature_identity for item in group.categories}
    )
    preview = _apply(controller, MoveOneHotCategoryIntent(group.categories[1].identity, "up"))
    assert preview.model_compatibility_changed
    candidate = preview.result.draft
    outside_after = tuple(
        identity[1] for identity in candidate.ml_order
        if identity[1] not in {item.emitted_feature_identity for item in group.categories}
    )
    assert outside_after == outside_before
    reordered = controller.one_hot_authoring_projection().groups[0].categories
    assert [(item.source_value, item.order) for item in reordered] == [
        ("R32", 1), ("R410A", 2), ("R290", 3)
    ]


def test_emitted_feature_remove_is_blocked_by_derived_identity_dependency(tmp_path):
    controller, _repository = _controller(tmp_path)
    group = controller.one_hot_authoring_projection().groups[0]
    emitted = group.categories[0]
    denominator = next(item for item in controller._draft.rows
                       if item.column_key == "cooling_capa")
    derived = controller.preview_derived_command(AddDerivedIntent(
        "OneHot_Ratio", emitted.emitted_feature_identity, denominator.stable_identity
    ))
    assert derived.command_accepted
    controller.apply_prepared_derived_command(derived)
    blocked = controller.preview_one_hot_command(
        RemoveOneHotCategoryIntent(emitted.identity)
    )
    assert not blocked.command_accepted
    assert {item.code for item in blocked.blockers} & {
        "derived_operand_reference",
        "feature_derived_reference",
        "one_hot_emitted_reference",
    }


def test_stale_prepared_result_is_rejected_without_regenerating_identities(tmp_path):
    controller, _repository = _controller(tmp_path)
    group = controller.one_hot_authoring_projection().groups[0]
    first = controller.preview_one_hot_command(
        RenameOneHotGroupIntent(group.identity, "coolant")
    )
    category = group.categories[0]
    _apply(controller, EditOneHotCategoryIntent(category.identity, emitted_ml_name="R410A_Flag"))
    stale = controller.apply_prepared_one_hot_command(first)
    assert not stale.last_action_ok
    assert stale.command_issue_rows[0][0] == "prepared_preview_stale"


def test_group_duplicate_disable_enable_and_remove_are_atomic(tmp_path):
    controller, _repository = _controller(tmp_path)
    original = controller.one_hot_authoring_projection().groups[0]
    selector = next(item for item in controller._draft.rows if item.column_key == "idu")
    _apply(controller, DuplicateOneHotGroupIntent(
        original.identity, "refrigerant_copy", selector.stable_identity, "_copy"
    ))
    duplicate = controller.one_hot_authoring_projection().groups[-1]
    assert not duplicate.active
    assert duplicate.identity != original.identity
    assert all(item.identity not in {source.identity for source in original.categories}
               for item in duplicate.categories)
    assert all(not item.active for item in duplicate.categories)
    _apply(controller, RemoveOneHotGroupIntent(duplicate.identity, "detach"))
    assert all(item.identity != duplicate.identity
               for item in controller.one_hot_authoring_projection().groups)
    detached = next(item for item in controller._draft.rows
                    if item.stable_identity == selector.stable_identity)
    assert detached == next(
        item for item in controller._draft.baseline_rows
        if item.stable_identity == selector.stable_identity
    )

    disabled = controller.preview_one_hot_command(
        SetOneHotGroupActiveIntent(original.identity, False)
    )
    assert not disabled.command_accepted
    assert "target_policy_owner_invalid" in {item.code for item in disabled.blockers}
    assert controller.one_hot_authoring_projection().groups[0].active


def test_inactive_reservation_remove_detach_restores_exact_clean_baseline(tmp_path):
    controller, _repository = _controller(tmp_path)
    baseline = controller._draft
    selector = next(item for item in baseline.rows if item.column_key == "idu")

    _apply(controller, AddOneHotGroupIntent(
        "reserved_idu", selector.stable_identity, "static", "",
        "warn_all_zero", "all_zero",
    ))
    reserved = next(
        item for item in controller._draft.rows
        if item.stable_identity == selector.stable_identity
    )
    assert reserved == selector
    group = controller.one_hot_authoring_projection().groups[-1]
    _apply(controller, RemoveOneHotGroupIntent(group.identity, "detach"))

    assert controller._draft.rows == baseline.rows
    assert controller._draft.predict_order == baseline.predict_order
    assert controller._draft.ml_order == baseline.ml_order
    assert controller._draft.one_hot_groups == baseline.one_hot_groups
    assert not controller._draft.is_changed


def test_takeover_activation_disable_and_detach_restore_exact_shape(tmp_path):
    controller, _repository = _controller(tmp_path)
    added = controller.preview_feature_command(AddDefinitionIntent(
        "manual_predict", "Selector", "safe_selector", "string"
    ))
    assert added.command_accepted
    controller.apply_prepared_feature_command(added)
    selector = next(item for item in controller._draft.rows
                    if item.column_key == "safe_selector")
    _apply(controller, AddOneHotGroupIntent(
        "safe_group", selector.stable_identity, "static", "",
        "warn_all_zero", "all_zero",
    ))
    group = controller.one_hot_authoring_projection().groups[-1]
    _apply(controller, AddOneHotCategoryIntent(group.identity, "A", "Safe_A"))
    category = controller.one_hot_authoring_projection().groups[-1].categories[0]
    _apply(controller, SetOneHotCategoryActiveIntent(category.identity, True))
    enabled = _apply(controller, SetOneHotGroupActiveIntent(group.identity, True))
    taken_over = next(item for item in enabled.result.draft.rows
                      if item.stable_identity == selector.stable_identity)
    assert taken_over.value_source == "one_hot"
    assert taken_over.active

    _apply(controller, SetOneHotGroupActiveIntent(group.identity, False))
    restored = next(item for item in controller._draft.rows
                    if item.stable_identity == selector.stable_identity)
    assert restored == selector
    _apply(controller, RemoveOneHotGroupIntent(group.identity, "detach"))
    assert next(item for item in controller._draft.rows
                if item.stable_identity == selector.stable_identity) == selector


def test_source_mode_change_preserves_identities_and_is_model_sensitive(tmp_path):
    controller, _repository = _controller(tmp_path)
    group = controller.one_hot_authoring_projection().groups[0]
    preview = controller.preview_one_hot_command(ChangeOneHotSourceModeIntent(
        group.identity, "static", ""
    ))
    assert preview.command_accepted
    assert preview.model_compatibility_changed
    assert preview.requires_retraining
    assert preview.save_allowed
    controller.apply_prepared_one_hot_command(preview)
    changed = controller.one_hot_authoring_projection().groups[0]
    assert changed.identity == group.identity
    assert changed.selector_feature_identity == group.selector_feature_identity
    assert [item.identity for item in changed.categories] == [
        item.identity for item in group.categories
    ]
