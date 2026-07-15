"""Qt-free controlled Data Definition command tests."""

import shutil

import pytest

from apps.train.services.data_definition_service import DataDefinitionService

from core.data_definition import (
    AddDefinitionIntent,
    EditDefinitionIntent,
    apply_add_definition_command,
    apply_edit_definition_command,
    build_data_definition_draft,
    build_data_definition_save_plan,
    extract_mapping_requirements_from_draft,
)
from core.data_definition.projection import (
    project_feature_catalog_from_draft,
    projected_feature_catalog_fingerprint,
)
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH, load_predict_schema_catalog_v2


def test_manual_predict_add_is_complete_projection_neutral_and_writable():
    draft = build_data_definition_draft()
    before = _fingerprint(draft)

    result = apply_add_definition_command(
        draft,
        AddDefinitionIntent(
            kind="manual_predict",
            label="Fan Diameter",
            column_key="Fan Diameter",
            data_type="number",
            visible=True,
            required=False,
        ),
    )

    row = next(item for item in result.draft.rows if item.column_key == "fan_diameter")
    plan = build_data_definition_save_plan(result.draft)
    assert result.accepted
    assert row.identity == ("schema_row", "fan_diameter")
    assert (row.role, row.editor, row.value_source) == ("input", "number", "manual")
    assert row.visible and not row.readonly and not row.model_input_enabled
    assert not row.ml_name and not row.one_hot_group
    assert _fingerprint(result.draft) == before
    assert plan.can_save_schema
    assert plan.requires_restart
    assert not plan.requires_retrain
    assert not any(item.code == "raw_row_add_delete_not_allowed" for item in plan.blocked_reasons)


def test_mapping_predict_and_standalone_attribute_project_requirements_without_ml_change():
    draft = build_data_definition_draft()
    before = _fingerprint(draft)
    mapping_predict = apply_add_definition_command(
        draft,
        AddDefinitionIntent(
            kind="mapping_predict",
            label="Evap Inner Surface Area",
            column_key="evap_inner_surface_area",
            data_type="number",
            mapping_entity="evap_index",
            mapping_attribute="Inner Surface Area",
            trigger_column="evap_index",
        ),
    )
    standalone = apply_add_definition_command(
        mapping_predict.draft,
        AddDefinitionIntent(
            kind="mapping_attribute",
            label="Cond Inner Area",
            column_key="cond_inner_area",
            data_type="number",
            mapping_entity="cond_specs",
            mapping_attribute="Cond Inner Area",
            trigger_column="odu",
            rule_id="cond_specs_lookup",
        ),
    )

    requirements = {
        item.column_key: item for item in extract_mapping_requirements_from_draft(standalone.draft)
    }
    predict_row = next(
        item for item in standalone.draft.rows if item.column_key == "evap_inner_surface_area"
    )
    attribute_row = next(
        item for item in standalone.draft.rows if item.column_key == "cond_inner_area"
    )
    assert mapping_predict.accepted and standalone.accepted
    assert (predict_row.role, predict_row.visible, predict_row.readonly) == ("auto", True, True)
    assert (attribute_row.role, attribute_row.visible, attribute_row.readonly) == (
        "helper", False, True,
    )
    assert requirements["evap_inner_surface_area"].mapping_attribute == "Inner Surface Area"
    assert requirements["cond_inner_area"].rule_id == "cond_specs_lookup"
    assert not requirements["cond_inner_area"].model_input_enabled
    assert _fingerprint(standalone.draft) == before
    assert build_data_definition_save_plan(standalone.draft).can_save_schema


def test_invalid_add_is_atomic_for_duplicate_and_unsupported_mapping_relation():
    draft = build_data_definition_draft()
    before = _snapshot(draft)
    duplicate = apply_add_definition_command(
        draft,
        AddDefinitionIntent("manual_predict", "Duplicate", "cooling_capa", "number"),
    )
    unsupported = apply_add_definition_command(
        draft,
        AddDefinitionIntent(
            "mapping_predict",
            "Unsupported",
            "unsupported_mapping",
            "number",
            mapping_entity="arbitrary",
            mapping_attribute="Value",
            trigger_column="missing",
            rule_id="expression",
        ),
    )

    assert not duplicate.accepted and duplicate.issues[0].code == "column_key_duplicate"
    assert not unsupported.accepted
    assert any(issue.code == "mapping_template_unsupported" for issue in unsupported.issues)
    assert _snapshot(duplicate.draft) == before == _snapshot(unsupported.draft)


@pytest.mark.parametrize(
    "intent, expected_code",
    (
        (AddDefinitionIntent("manual_predict", "   ", "blank_label", "number"), "label_required"),
        (AddDefinitionIntent("manual_predict", "Bad Type", "bad_type", "matrix"), "data_type_unsupported"),
        (
            AddDefinitionIntent(
                "mapping_predict",
                "Incomplete",
                "incomplete_mapping",
                "number",
                mapping_entity="evap_index",
                mapping_attribute="   ",
                trigger_column="evap_index",
            ),
            "mapping_attribute_required",
        ),
    ),
)
def test_add_validation_matrix_is_non_mutating(intent, expected_code):
    draft = build_data_definition_draft()
    before = _snapshot(draft)

    result = apply_add_definition_command(draft, intent)

    assert not result.accepted
    assert expected_code in {issue.code for issue in result.issues}
    assert _snapshot(result.draft) == before


def test_sequential_add_allocates_stable_identity_and_order_and_reset_source_is_unchanged():
    draft = build_data_definition_draft()
    first = apply_add_definition_command(
        draft,
        AddDefinitionIntent("manual_predict", "First", "first_added", "string"),
    )
    second = apply_add_definition_command(
        first.draft,
        AddDefinitionIntent("manual_predict", "Second", "second_added", "number"),
    )
    added = [row for row in second.draft.rows if row.column_key in {"first_added", "second_added"}]

    assert [row.display_order for row in added] == [420, 430]
    assert len({row.display_order for row in second.draft.rows if row.source_kind == "schema_row"}) == (
        len([row for row in second.draft.rows if row.source_kind == "schema_row"])
    )
    assert not draft.is_changed
    assert not any(row.column_key in {"first_added", "second_added"} for row in draft.rows)


def test_controlled_edit_is_atomic_and_restricted_fields_are_rejected():
    draft = build_data_definition_draft()
    identity = ("schema_row", "idu")
    accepted = apply_edit_definition_command(
        draft,
        EditDefinitionIntent(identity, (("label", "Indoor Unit"), ("notes", "Updated note"))),
    )
    before_restricted = _snapshot(accepted.draft)
    rejected = apply_edit_definition_command(
        accepted.draft,
        EditDefinitionIntent(identity, (("label", "Partial"), ("display_order", 999))),
    )

    row = next(item for item in accepted.draft.rows if item.identity == identity)
    assert accepted.accepted
    assert row.label == "Indoor Unit" and row.notes == "Updated note"
    assert not rejected.accepted
    assert rejected.issues[0].code == "restricted_edit"
    assert _snapshot(rejected.draft) == before_restricted


@pytest.mark.parametrize("field_name, value", (
    ("column_key", "cooling_capacity"),
    ("display_order", 999),
    ("role", "auto"),
))
def test_controlled_edit_rejects_identity_order_and_role_without_mutation(
    field_name,
    value,
):
    draft = build_data_definition_draft()
    before = _snapshot(draft)

    result = apply_edit_definition_command(
        draft,
        EditDefinitionIntent(("schema_row", "cooling_capa"), ((field_name, value),)),
    )

    assert not result.accepted
    assert result.issues[0].code == "restricted_edit"
    assert _snapshot(result.draft) == before


def test_controlled_edit_rejects_derived_policy_without_mutation():
    draft = build_data_definition_draft()
    derived = next(item for item in draft.rows if item.source_kind == "derived_policy")
    before = _snapshot(draft)

    result = apply_edit_definition_command(
        draft,
        EditDefinitionIntent(derived.identity, (("notes", "Not persistable"),)),
    )

    assert not result.accepted
    assert result.issues[0].code == "restricted_edit"
    assert _snapshot(result.draft) == before


def test_projection_changing_controlled_edit_is_complete_but_save_blocked():
    draft = build_data_definition_draft()
    identity = ("schema_row", "cooling_capa")
    result = apply_edit_definition_command(
        draft,
        EditDefinitionIntent(
            identity,
            (("label", "Cooling Capacity"), ("ml_name", "Cooling Capacity Renamed")),
        ),
    )
    plan = build_data_definition_save_plan(result.draft)
    row = next(item for item in result.draft.rows if item.identity == identity)

    assert result.accepted
    assert row.label == "Cooling Capacity"
    assert row.ml_name == "Cooling Capacity Renamed"
    assert not plan.can_save_schema
    blocker = next(
        item for item in plan.blocked_reasons
        if item.code == "ml_compatibility_projection_write_required"
    )
    assert blocker.row_identity == identity and blocker.field_name == "ml_name"


def test_controlled_add_uses_existing_writer_and_reload_keeps_identity_and_order(tmp_path):
    schema_path = tmp_path / "schema.csv"
    shutil.copyfile(DEFAULT_SCHEMA_PATH, schema_path)
    service = DataDefinitionService(schema_path=schema_path)
    command = service.add_definition(
        service.load_draft(),
        AddDefinitionIntent("manual_predict", "Fan Diameter", "fan_diameter", "number"),
    )

    result = service.save_schema_draft(command.draft)

    loaded = load_predict_schema_catalog_v2(schema_path)
    row = next(item for item in loaded.rows if item.column_key == "fan_diameter")
    assert result.status == "written"
    assert result.backup_path is not None and result.backup_path.exists()
    assert row.display_order == 420
    assert row.label == "Fan Diameter"
    assert not service.load_draft().is_changed


def _fingerprint(draft):
    return projected_feature_catalog_fingerprint(project_feature_catalog_from_draft(draft))


def _snapshot(draft):
    return (
        draft.rows,
        draft.baseline_rows,
        draft.issues,
        draft.controlled_row_additions,
        draft.changes(),
    )
