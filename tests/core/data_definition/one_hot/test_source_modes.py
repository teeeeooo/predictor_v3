"""Static, Mapping-backed, and External ownership boundary tests."""

from dataclasses import replace

from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.adapters.one_hot_vocabulary import (
    load_persisted_mapping_vocabulary_snapshots,
)
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.one_hot.intents import (
    AddOneHotCategoryIntent,
    AddOneHotGroupIntent,
    ChangeOneHotSourceModeIntent,
    EditOneHotCategoryIntent,
    SetOneHotCategoryActiveIntent,
    SetOneHotGroupActiveIntent,
)
from core.data_definition.one_hot.model import VocabularyCategory, VocabularySnapshot


def _repository(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "generations-root")
    repository.publish(bootstrap_manifest())
    return repository


def _controller(repository, snapshots=()):
    controller = DataDefinitionController(DataDefinitionService(
        generation_repository=repository,
        vocabulary_snapshots=snapshots,
    ))
    controller.refresh()
    return controller


def _apply(controller, intent):
    prepared = controller.preview_one_hot_command(intent)
    assert prepared.command_accepted, prepared.blockers
    controller.apply_prepared_one_hot_command(prepared)
    return prepared


def test_mapping_rules_use_persisted_candidates_and_never_write_mapping(tmp_path):
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_bytes(
        b'{"ref_type":{"R410A":{},"R32":{}},"exp_type":{"EEV":{}}}\n'
    )
    before = mapping_path.read_bytes()
    snapshots = load_persisted_mapping_vocabulary_snapshots(mapping_path)
    repository = _repository(tmp_path)
    controller = _controller(repository, snapshots)
    selector = next(item for item in controller._draft.rows if item.column_key == "idu")
    _apply(controller, AddOneHotGroupIntent(
        "mapped_kind", selector.stable_identity, "mapping_backed", "ref_type",
        "warn_all_zero", "all_zero",
    ))
    group = controller.one_hot_authoring_projection().groups[-1]
    blocked = controller.preview_one_hot_command(
        AddOneHotCategoryIntent(group.identity, "R290", "Mapped_R290")
    )
    assert not blocked.command_accepted
    assert blocked.blockers[0].code == "one_hot_source_value_unavailable"
    _apply(controller, AddOneHotCategoryIntent(group.identity, "R32", "Mapped_R32"))
    assert mapping_path.read_bytes() == before
    assert controller.save_schema().last_action_ok
    assert mapping_path.read_bytes() == before


def test_mapping_stale_rule_is_warning_and_unmatched_value_uses_unknown_policy(tmp_path):
    repository = _repository(tmp_path)
    snapshots = (
        VocabularySnapshot("mapping_backed", "ref_type", (
            VocabularyCategory("ref:r32", "R32"),
            VocabularyCategory("ref:r744", "R744"),
        )),
        VocabularySnapshot("mapping_backed", "exp_type", (
            VocabularyCategory("exp:eev", "EEV"),
            VocabularyCategory("exp:capi", "Capi"),
        )),
    )
    controller = _controller(repository, snapshots)
    projection = controller.one_hot_authoring_projection()
    refrigerant = projection.groups[0]
    statuses = {item.source_value: item.drift_status for item in refrigerant.categories}
    assert statuses["R410A"] == "one_hot_mapping_rule_stale"
    assert statuses["R290"] == "one_hot_mapping_rule_stale"
    plan = controller._service.preview_save_plan(controller._draft)
    assert not any(item.severity == "error" and "mapping" in item.code
                   for item in plan.blocked_reasons)
    assert any(item.code == "one_hot_provider_value_unmatched"
               for item in plan.blocked_reasons)


def test_external_provider_identity_value_are_read_only_and_unavailable_blocks(tmp_path):
    repository = _repository(tmp_path)
    external = VocabularySnapshot(
        "external",
        "fake-provider:refrigerant",
        (
            VocabularyCategory("provider-cat-r32", "R32", "R32"),
            VocabularyCategory("provider-cat-r290", "R290", "R290"),
        ),
    )
    controller = _controller(repository, (external,))
    selector = next(item for item in controller._draft.rows if item.column_key == "idu")
    _apply(controller, AddOneHotGroupIntent(
        "external_ref", selector.stable_identity, "external", external.source_binding,
        "warn_all_zero", "all_zero",
    ))
    group = controller.one_hot_authoring_projection().groups[-1]
    _apply(controller, AddOneHotCategoryIntent(
        group.identity, "R32", "External_R32", "provider-cat-r32"
    ))
    category = controller.one_hot_authoring_projection().groups[-1].categories[0]
    blocked = controller.preview_one_hot_command(EditOneHotCategoryIntent(
        category.identity,
        source_value="R744",
        provider_category_identity="provider-cat-r32",
    ))
    assert not blocked.command_accepted
    assert blocked.blockers[0].code == "one_hot_source_value_unavailable"
    _apply(controller, SetOneHotCategoryActiveIntent(category.identity, True))
    active = controller.preview_one_hot_command(
        SetOneHotGroupActiveIntent(group.identity, True)
    )
    assert not active.command_accepted
    assert active.blockers[0].code == "mapping_trigger_reference"
    active_draft = controller._draft
    without_provider = DataDefinitionService(
        generation_repository=repository,
        vocabulary_snapshots=(),
    ).preview_save_plan(active_draft)
    assert any(item.code == "one_hot_provider_unavailable"
               and item.severity == "error" for item in without_provider.blocked_reasons)


def test_production_projection_disables_external_creation_without_registration(tmp_path):
    controller = _controller(_repository(tmp_path))
    projection = controller.one_hot_authoring_projection()
    assert not projection.external_creation_enabled
    assert "No production external" in projection.external_disabled_reason
    assert not projection.mapping_values_editable


def test_mapping_value_rename_does_not_replace_canonical_category_identity(tmp_path):
    repository = _repository(tmp_path)
    original = _controller(repository, (
        VocabularySnapshot("mapping_backed", "ref_type", (
            VocabularyCategory("mapping:r32", "R32"),
        )),
    ))
    identity = original.one_hot_authoring_projection().groups[0].categories[1].identity
    renamed = _controller(repository, (
        VocabularySnapshot("mapping_backed", "ref_type", (
            VocabularyCategory("mapping:r32-new", "R32-new"),
        )),
    ))
    category = renamed.one_hot_authoring_projection().groups[0].categories[1]
    assert category.identity == identity
    assert category.source_value == "R32"
    assert category.drift_status == "one_hot_mapping_rule_stale"


def test_external_unknown_duplicate_and_incomplete_relations_reject_atomically(tmp_path):
    repository = _repository(tmp_path)
    external = VocabularySnapshot(
        "external",
        "provider:ref",
        (
            VocabularyCategory("provider:r410a", "R410A"),
            VocabularyCategory("provider:r32", "R32"),
            VocabularyCategory("provider:r290", "R290"),
        ),
        source_revision="provider-rev-1",
    )
    controller = _controller(repository, (external,))
    group = controller.one_hot_authoring_projection().groups[0]
    original = controller._draft
    category_ids = tuple(item.identity for item in group.categories)

    invalid_cases = (
        (
            tuple(zip(category_ids, ("provider:r410a", "provider:r32", "missing"), strict=True)),
            "one_hot_provider_category_missing",
        ),
        (
            tuple(zip(category_ids, ("provider:r410a", "provider:r410a", "provider:r290"), strict=True)),
            "one_hot_provider_category_duplicate",
        ),
        (
            ((category_ids[0], "provider:r410a"),),
            "one_hot_external_overlay_incomplete",
        ),
        (
            (("unknown-category", "provider:r410a"), *tuple(
                zip(category_ids[1:], ("provider:r32", "provider:r290"), strict=True)
            )),
            "one_hot_provider_category_missing",
        ),
    )
    for assignments, code in invalid_cases:
        prepared = controller.preview_one_hot_command(ChangeOneHotSourceModeIntent(
            group.identity, "external", external.source_binding, assignments
        ))
        assert not prepared.command_accepted
        assert prepared.blockers[0].code == code
        assert prepared.result.draft is original
        assert controller._draft is original

    valid = controller.preview_one_hot_command(ChangeOneHotSourceModeIntent(
        group.identity,
        "external",
        external.source_binding,
        tuple(zip(
            category_ids,
            ("provider:r410a", "provider:r32", "provider:r290"),
            strict=True,
        )),
    ))
    assert valid.command_accepted


def test_provider_revision_change_rejects_prepared_candidate(tmp_path):
    repository = _repository(tmp_path)
    first = VocabularySnapshot(
        "mapping_backed",
        "ref_type",
        (VocabularyCategory("ref:r410a", "R410A"),),
        source_revision="mapping-rev-1",
    )
    controller = _controller(repository, (first,))
    group = controller.one_hot_authoring_projection().groups[0]
    prepared = controller.preview_one_hot_command(
        ChangeOneHotSourceModeIntent(group.identity, "static", "")
    )
    assert prepared.command_accepted
    controller._service._one_hot.snapshots = (replace(
        first, source_revision="mapping-rev-2"
    ),)

    state = controller.apply_prepared_one_hot_command(prepared)

    assert not state.last_action_ok
    assert state.command_issue_rows[0][0] == "one_hot_provider_snapshot_stale"
    assert controller._draft is prepared.source_draft
