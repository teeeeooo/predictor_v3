"""Prepared Preview/Apply and generation Save tests for Derived authoring."""

from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.services.data_definition_service import DataDefinitionService
from core.data_definition import AddDerivedIntent, EditDerivedIntent
from core.data_definition.contract import bootstrap_manifest


def _controller(tmp_path):
    repository = DataDefinitionGenerationRepository(tmp_path / "definitions")
    manifest = bootstrap_manifest()
    repository.publish(manifest)
    return DataDefinitionController(
        DataDefinitionService(generation_repository=repository)
    ), repository, manifest


def test_inactive_add_prepared_candidate_applies_and_publishes_same_generation(tmp_path):
    controller, repository, manifest = _controller(tmp_path)
    controller.refresh()
    prepared = controller.preview_derived_command(AddDerivedIntent(
        "Inactive_authored_ratio",
        manifest.features[0].identity,
        manifest.derived[0].denominator_identity,
        zero_value=4,
    ))
    assert prepared.command_accepted
    assert prepared.derived_semantics_changed
    assert not prepared.model_compatibility_changed
    assert prepared.save_allowed
    applied = controller.apply_prepared_derived_command(prepared)
    assert applied.last_action_ok and applied.draft_changed and applied.save_action_enabled
    saved = controller.save_schema()
    assert saved.status == "saved"
    active = repository.read_active()
    authored = next(item for item in active.manifest.derived if item.ml_name == "Inactive_authored_ratio")
    assert not authored.active and authored.zero_value == 4.0
    assert active.manifest.generation.generation_id == prepared.candidate_generation_id


def test_active_semantics_edit_previews_with_retraining_required(tmp_path):
    controller, _repository, manifest = _controller(tmp_path)
    state = controller.refresh()
    first = manifest.derived[0]
    identity = next(
        item for item in state.draft_row_identities
        if item == ("derived_policy", first.identity)
    )
    prepared = controller.preview_derived_command(EditDerivedIntent(
        identity,
        first.numerator_identity,
        first.denominator_identity,
        zero_value=1,
    ))
    assert prepared.command_accepted
    assert prepared.derived_semantics_changed
    assert prepared.model_compatibility_changed
    assert prepared.requires_retraining
    assert prepared.save_allowed
    applied = controller.apply_prepared_derived_command(prepared)
    assert applied.last_action_ok and applied.draft_changed
    assert applied.save_action_enabled
    assert "model_compatibility_migration_required" in {
        item[1] for item in applied.save_blocker_rows
    }


def test_prepared_derived_candidate_becomes_stale_after_another_command(tmp_path):
    controller, _repository, manifest = _controller(tmp_path)
    controller.refresh()
    first = controller.preview_derived_command(AddDerivedIntent(
        "First_inactive", manifest.features[0].identity, manifest.derived[0].denominator_identity
    ))
    second = controller.preview_derived_command(AddDerivedIntent(
        "Second_inactive", manifest.features[0].identity, manifest.derived[0].denominator_identity
    ))
    assert controller.apply_prepared_derived_command(second).last_action_ok
    stale = controller.apply_prepared_derived_command(first)
    assert not stale.last_action_ok
    assert stale.command_issue_rows[0][0] == "prepared_preview_stale"
