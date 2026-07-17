"""Phase 4C atomic basic Feature mutation command tests."""

from core.data_definition import (
    AddDefinitionIntent,
    DuplicateDefinitionIntent,
    MoveDefinitionIntent,
    RemoveDefinitionIntent,
    RenameDefinitionIntent,
    SetDefinitionActiveIntent,
    apply_add_definition_command,
    apply_duplicate_definition_command,
    apply_move_definition_command,
    apply_remove_definition_command,
    apply_rename_definition_command,
    apply_set_definition_active_command,
    build_data_definition_draft,
)
from core.data_definition.contract import (
    bootstrap_manifest,
    candidate_manifest_from_draft,
    require_valid_contract,
)
from apps.train.adapters.data_definition_generation_repository import (
    DataDefinitionGenerationRepository,
)
from apps.train.services.data_definition_service import DataDefinitionService
from apps.train.controllers.data_definition_controller import DataDefinitionController


def _canonical_draft():  # noqa: ANN202
    manifest = bootstrap_manifest()
    return build_data_definition_draft(manifest=manifest)


def _service(tmp_path):  # noqa: ANN001
    repository = DataDefinitionGenerationRepository(tmp_path / "definition-store")
    repository.publish(bootstrap_manifest())
    return DataDefinitionService(generation_repository=repository), repository


def test_add_rename_remove_round_trip_is_clean_and_identity_is_stable():
    baseline = _canonical_draft()
    added = apply_add_definition_command(
        baseline,
        AddDefinitionIntent(
            "predict_only",
            "Fan Diameter",
            "fan_diameter",
            "number",
        ),
    )
    added_row = next(row for row in added.draft.rows if row.column_key == "fan_diameter")

    renamed = apply_rename_definition_command(
        added.draft,
        RenameDefinitionIntent(
            added_row.identity,
            label="Indoor Fan Diameter",
            column_key="indoor_fan_diameter",
        ),
    )
    renamed_row = next(row for row in renamed.draft.rows if row.identity == added_row.identity)
    removed = apply_remove_definition_command(
        renamed.draft,
        RemoveDefinitionIntent(renamed_row.identity),
    )

    assert added.accepted and renamed.accepted and removed.accepted
    assert renamed_row.stable_identity == added_row.stable_identity
    assert renamed_row.column_key == "indoor_fan_diameter"
    assert not removed.draft.is_changed
    assert removed.draft.rows == baseline.rows


def test_duplicate_requires_new_names_and_allocates_new_identity():
    draft = _canonical_draft()
    original = next(row for row in draft.rows if row.column_key == "cooling_capa")
    duplicated = apply_duplicate_definition_command(
        draft,
        DuplicateDefinitionIntent(
            original.identity,
            "Alternate Cooling Capacity",
            "alternate_cooling_capa",
            "Alternate Cooling Capa",
        ),
    )
    duplicate = next(
        row for row in duplicated.draft.rows
        if row.column_key == "alternate_cooling_capa"
    )

    assert duplicated.accepted
    assert duplicate.identity != original.identity
    assert duplicate.model_input_enabled
    assert not duplicate.required
    assert duplicate.active


def test_rename_requires_identifier_and_rejects_collisions_atomically():
    draft = _canonical_draft()
    row = next(item for item in draft.rows if item.column_key == "idu")
    snapshot = draft.rows
    label_only = apply_rename_definition_command(
        draft,
        RenameDefinitionIntent(row.identity, label="Indoor Unit"),
    )
    collision = apply_rename_definition_command(
        draft,
        RenameDefinitionIntent(row.identity, column_key="odu"),
    )

    assert not label_only.accepted
    assert label_only.issues[0].code == "rename_identifier_required"
    assert label_only.issues[0].resolution == "Use Edit for a label-only change."
    assert not collision.accepted
    assert "column_key_duplicate" in {item.code for item in collision.issues}
    assert label_only.draft.rows == collision.draft.rows == snapshot


def test_protected_predict_and_ml_dependencies_block_rename_remove_disable():
    draft = _canonical_draft()
    cooling = next(row for row in draft.rows if row.column_key == "cooling_capa")

    rename = apply_rename_definition_command(
        draft,
        RenameDefinitionIntent(cooling.identity, ml_name="Cooling Capacity"),
    )
    remove = apply_remove_definition_command(draft, RemoveDefinitionIntent(cooling.identity))
    disable = apply_set_definition_active_command(
        draft,
        SetDefinitionActiveIntent(cooling.identity, False),
    )

    assert not rename.accepted and not remove.accepted and not disable.accepted
    assert "derived_expression_reference" in {item.code for item in rename.issues}
    assert "protected_predict_consumer" in {item.code for item in remove.issues}
    assert "derived_expression_reference" in {item.code for item in disable.issues}
    assert rename.draft is remove.draft is disable.draft is draft


def test_enable_disable_is_distinct_from_remove_for_unreferenced_unsaved_feature():
    draft = _canonical_draft()
    added = apply_add_definition_command(
        draft,
        AddDefinitionIntent("predict_only", "Optional Note", "optional_note", "string"),
    )
    identity = added.identity
    disabled = apply_set_definition_active_command(
        added.draft,
        SetDefinitionActiveIntent(identity, False),
    )
    enabled = apply_set_definition_active_command(
        disabled.draft,
        SetDefinitionActiveIntent(identity, True),
    )

    assert disabled.accepted and enabled.accepted
    assert len(disabled.draft.rows) == len(added.draft.rows)
    assert not next(row for row in disabled.draft.rows if row.identity == identity).active
    assert next(row for row in enabled.draft.rows if row.identity == identity).active


def test_predict_and_ml_move_orders_are_independent_and_candidate_is_valid():
    draft = _canonical_draft()
    manifest = draft.base_manifest
    idu = next(row for row in draft.rows if row.column_key == "idu")
    cooling = next(row for row in draft.rows if row.column_key == "cooling_capa")
    predict_before = draft.predict_order
    ml_before = draft.ml_order

    predict_move = apply_move_definition_command(
        draft,
        MoveDefinitionIntent(idu.identity, "predict", "down"),
    )
    ml_move = apply_move_definition_command(
        draft,
        MoveDefinitionIntent(cooling.identity, "ml", "down"),
    )

    assert predict_move.accepted and ml_move.accepted
    assert predict_move.draft.ml_order == ml_before
    assert predict_move.draft.predict_order != predict_before
    assert ml_move.draft.predict_order == predict_before
    assert ml_move.draft.ml_order != ml_before
    require_valid_contract(candidate_manifest_from_draft(predict_move.draft, manifest))
    require_valid_contract(candidate_manifest_from_draft(ml_move.draft, manifest))


def test_move_boundary_rejects_without_mutation_and_predict_order_keeps_inactive():
    draft = _canonical_draft()
    first = draft.predict_order[0]
    boundary = apply_move_definition_command(
        draft,
        MoveDefinitionIntent(first, "predict", "up"),
    )
    added = apply_add_definition_command(
        draft,
        AddDefinitionIntent("predict_only", "Inactive", "inactive_feature", "number"),
    )
    disabled = apply_set_definition_active_command(
        added.draft,
        SetDefinitionActiveIntent(added.identity, False),
    )
    moved = apply_move_definition_command(
        disabled.draft,
        MoveDefinitionIntent(added.identity, "predict", "up"),
    )

    assert not boundary.accepted and boundary.issues[0].code == "move_boundary"
    assert boundary.draft is draft
    assert moved.accepted
    assert added.identity in moved.draft.predict_order
    assert not next(row for row in moved.draft.rows if row.identity == added.identity).active


def test_command_preview_matches_published_predict_only_candidate(tmp_path):
    service, repository = _service(tmp_path)
    draft = service.load_draft()
    intent = AddDefinitionIntent(
        "predict_only",
        "Optional Ambient Note",
        "optional_ambient_note",
        "string",
    )

    preview = service.preview_feature_command(draft, intent)
    result = service.apply_feature_command(draft, intent)
    saved = service.save_schema_draft(result.draft)
    active = repository.read_active()

    assert preview.command_accepted and preview.predict_projection_changed
    assert not preview.ordered_ml_projection_changed
    assert not preview.model_compatibility_changed
    assert preview.save_allowed and saved.status == "written"
    assert any(row.column_key == "optional_ambient_note" for row in active.projections.predict)


def test_ml_order_preview_reports_compatibility_and_existing_save_guard(tmp_path):
    service, repository = _service(tmp_path)
    draft = service.load_draft()
    cooling = next(row for row in draft.rows if row.column_key == "cooling_capa")
    intent = MoveDefinitionIntent(cooling.identity, "ml", "down")

    preview = service.preview_feature_command(draft, intent)
    result = service.apply_feature_command(draft, intent)
    saved = service.save_schema_draft(result.draft)

    assert preview.command_accepted
    assert preview.ordered_ml_projection_changed
    assert preview.model_compatibility_changed and preview.requires_retraining
    assert not preview.save_allowed
    assert saved.status == "blocked"
    assert repository.read_active().manifest == draft.base_manifest


def test_controller_selection_dirty_and_remove_neighbor_workflow(tmp_path):
    service, _repository = _service(tmp_path)
    controller = DataDefinitionController(service)
    clean = controller.refresh()
    first = controller.add_definition(
        AddDefinitionIntent("predict_only", "First New", "first_new", "string")
    )
    first_identity = first.focus_identity
    second = controller.add_definition(
        AddDefinitionIntent("predict_only", "Second New", "second_new", "string")
    )
    second_identity = second.focus_identity
    removed = controller.remove_definition(RemoveDefinitionIntent(first_identity))

    assert not clean.draft_changed
    assert first.draft_changed and second.draft_changed and removed.draft_changed
    assert first_identity != second_identity
    assert removed.focus_identity == second_identity
    assert first_identity not in removed.draft_row_identities


def test_controller_rejected_command_and_preview_preserve_unsaved_draft(tmp_path):
    service, _repository = _service(tmp_path)
    controller = DataDefinitionController(service)
    initial = controller.refresh()
    cooling = next(
        identity
        for identity, cells in zip(initial.draft_row_identities, initial.draft_rows, strict=True)
        if dict((cell.field_name, cell.value) for cell in cells)["column_key"] == "cooling_capa"
    )
    added = controller.add_definition(
        AddDefinitionIntent("predict_only", "Unsaved", "unsaved_feature", "number")
    )
    before = added.draft_row_identities
    preview = controller.preview_feature_command(
        RenameDefinitionIntent(cooling, ml_name="Cooling Capacity")
    )
    rejected = controller.rename_definition(
        RenameDefinitionIntent(cooling, ml_name="Cooling Capacity")
    )

    assert not preview.command_accepted and not rejected.last_action_ok
    assert rejected.draft_row_identities == before
    assert rejected.draft_changed
    assert any("Next:" in row[2] for row in rejected.command_issue_rows)
