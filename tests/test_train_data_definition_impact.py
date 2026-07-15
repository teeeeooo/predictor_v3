"""Qt-free Data Definition impact projection tests."""

from __future__ import annotations

import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.controllers.data_definition_state_builder import DataDefinitionBlockerItem
from apps.train.controllers.data_definition_impact_projection import (
    project_data_definition_impact,
)
from apps.train.services.data_definition_service import DataDefinitionService
from core.data_definition import AddDefinitionIntent, EditDefinitionIntent
import core.data_definition.schema_writer as schema_writer_module
from core.ml.artifacts import MODEL_FILE
from core.mapping.paths import MAPPING_JSON_FILE
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH, load_predict_schema_catalog_v2


def test_clean_and_manual_add_impact_classify_authoritative_save_state(tmp_path):
    controller = _controller(tmp_path)
    clean_state = controller.refresh()
    clean = project_data_definition_impact(clean_state)
    added_state = controller.add_definition(
        AddDefinitionIntent("manual_predict", "Fan Diameter", "fan_diameter", "number")
    )
    added = project_data_definition_impact(
        added_state, ("schema_row", "fan_diameter")
    )

    assert clean.status == "clean"
    assert clean.schema_write_status == "no_op"
    assert not clean.save_enabled and clean.save_result_status == "No save attempted."
    assert clean.change_text == "No unsaved definition changes."
    assert added.status == "dirty"
    assert added.schema_write_status == "planned" and added.save_enabled
    assert [(item.action, item.identity, item.label) for item in added.definitions] == [
        ("Add", ("schema_row", "fan_diameter"), "Fan Diameter")
    ]
    assert added.requires_restart and not added.requires_retrain
    assert not added.ml_fingerprint_changed
    assert not added.mapping_impacts
    assert "Predict restart: required" in added.runtime_text
    assert "ML compatibility fingerprint: unchanged" in added.runtime_text


def test_mapping_add_impact_names_requirement_and_data_mapping_ownership(tmp_path):
    controller = _controller(tmp_path)
    controller.refresh()
    state = controller.add_definition(
        AddDefinitionIntent(
            "mapping_predict",
            "Evap Inner Surface Area",
            "evap_inner_surface_area",
            "number",
            mapping_entity="evap_index",
            mapping_attribute="Inner Surface Area",
            trigger_column="evap_index",
        )
    )

    impact = project_data_definition_impact(
        state, ("schema_row", "evap_inner_surface_area")
    )

    assert impact.save_enabled and not impact.ml_fingerprint_changed
    assert impact.mapping_impacts == ((
        "Required",
        "evap_inner_surface_area",
        "",
        "evap_index",
        "Inner Surface Area",
        "evap_index",
        "",
        "optional",
        "Data Mapping owns concrete values",
    ),)
    assert "Inner Surface Area in evap_index" in impact.mapping_text
    assert "Concrete values remain Data Mapping-owned" in impact.mapping_text
    assert "Save schema before opening coverage" in impact.mapping_text


def test_ml_rename_is_complete_blocked_impact_with_selection_relevance(tmp_path):
    controller = _controller(tmp_path)
    controller.refresh()
    identity = ("schema_row", "cooling_capa")
    protected = (tmp_path / "schema.csv", Path("config/ml/features.csv"))
    before = tuple(path.read_bytes() for path in protected)
    state = controller.edit_definition(
        EditDefinitionIntent(
            identity,
            (("label", "Cooling Capacity"), ("ml_name", "Cooling Capacity Renamed")),
        )
    )

    direct = project_data_definition_impact(state, identity)
    other = project_data_definition_impact(state, ("schema_row", "idu"))

    assert direct.status == "blocked"
    assert direct.schema_write_status == "blocked" and not direct.save_enabled
    assert direct.ml_fingerprint_changed and direct.requires_retrain
    assert [field.field_name for field in direct.definitions[0].fields] == [
        "label", "ml_name",
    ]
    assert [
        (item.code, item.related_field, item.relevance)
        for item in direct.blockers
    ] == [
        ("ml_compatibility_projection_write_required", "ml_name", "direct"),
        ("candidate_feature_projection_mismatch", "label", "direct"),
    ]
    assert [item.relevance for item in other.blockers] == [
        "other_definition",
        "other_definition",
    ]
    assert direct.definitions == other.definitions
    assert direct.mapping_impacts == other.mapping_impacts
    assert "ML compatibility fingerprint: changed" in direct.runtime_text
    blocked_save = controller.save_schema()
    assert blocked_save.status == "blocked"
    assert tuple(path.read_bytes() for path in protected) == before


def test_independent_ml_and_mapping_parity_blockers_reproject_and_stay_stable(
    tmp_path,
):
    controller = _controller(tmp_path)
    controller.refresh()
    ml_identity = ("schema_row", "cooling_capa")
    parity_identity = ("schema_row", "id_volume")
    protected = tuple(
        path
        for path in (
            tmp_path / "schema.csv",
            Path("config/ml/features.csv"),
            Path(MAPPING_JSON_FILE),
            Path(MODEL_FILE),
        )
        if path.is_file()
    )
    before = tuple(path.read_bytes() for path in protected)
    controller.edit_definition(EditDefinitionIntent(
        ml_identity,
        (("ml_name", "Cooling Capacity Renamed"),),
    ))
    combined_state = controller.edit_definition(EditDefinitionIntent(
        parity_identity,
        (
            ("value_source", "mapping_lookup"),
            ("mapping_entity", "evap_index"),
            ("mapping_attribute", "ID Volume"),
            ("trigger_column", "evap_index"),
            ("rule_id", ""),
        ),
    ))

    ml_selected = project_data_definition_impact(combined_state, ml_identity)
    parity_selected = project_data_definition_impact(combined_state, parity_identity)
    parity_before = next(
        item for item in ml_selected.blockers
        if item.code == "candidate_feature_projection_mismatch"
    )

    assert not combined_state.save_action_enabled
    assert [
        (item.code, item.related_row_identity, item.related_field, item.relevance)
        for item in ml_selected.blockers
    ] == [
        (
            "ml_compatibility_projection_write_required",
            ml_identity,
            "ml_name",
            "direct",
        ),
        (
            "candidate_feature_projection_mismatch",
            parity_identity,
            "trigger_column",
            "other_definition",
        ),
    ]
    assert [
        (item.code, item.related_row_identity, item.related_field, item.relevance)
        for item in parity_selected.blockers
    ] == [
        (
            "candidate_feature_projection_mismatch",
            parity_identity,
            "trigger_column",
            "direct",
        ),
        (
            "ml_compatibility_projection_write_required",
            ml_identity,
            "ml_name",
            "other_definition",
        ),
    ]
    assert controller.save_schema().status == "blocked"
    assert tuple(path.read_bytes() for path in protected) == before

    reverted_state = controller.edit_definition(EditDefinitionIntent(
        ml_identity,
        (("ml_name", "Cooling Capa"),),
    ))
    reverted = project_data_definition_impact(reverted_state, parity_identity)
    parity_after = next(
        item for item in reverted.blockers
        if item.code == "candidate_feature_projection_mismatch"
    )

    assert not any(
        item.code == "ml_compatibility_projection_write_required"
        for item in reverted.blockers
    )
    assert (
        parity_after.code,
        parity_after.related_row_identity,
        parity_after.related_field,
        parity_after.target,
        parity_after.message,
    ) == (
        parity_before.code,
        parity_before.related_row_identity,
        parity_before.related_field,
        parity_before.target,
        parity_before.message,
    )
    assert parity_after.relevance == "direct"
    assert not reverted.save_enabled
    assert tuple(path.read_bytes() for path in protected) == before


def test_added_manual_row_ml_activation_is_attributed_to_add_fields(tmp_path):
    controller = _controller(tmp_path)
    controller.refresh()
    identity = ("schema_row", "fan_diameter")
    protected = tuple(
        path
        for path in (
            tmp_path / "schema.csv",
            Path("config/ml/features.csv"),
            Path(MODEL_FILE),
        )
        if path.is_file()
    )
    before = tuple(path.read_bytes() for path in protected)
    controller.add_definition(
        AddDefinitionIntent("manual_predict", "Fan Diameter", "fan_diameter", "number")
    )
    state = controller.edit_definition(
        EditDefinitionIntent(identity, (
            ("model_input_enabled", True),
            ("ml_name", "Fan Diameter"),
        ))
    )

    direct = project_data_definition_impact(state, identity)
    other = project_data_definition_impact(state, ("schema_row", "idu"))

    assert state.draft_changed and not state.save_action_enabled
    assert [(item.action, item.identity) for item in direct.definitions] == [
        ("Add", identity),
    ]
    assert [field.field_name for field in direct.definitions[0].fields] == [
        "model_input_enabled",
        "ml_name",
    ]
    assert {item.relevance for item in direct.blockers} == {"direct"}
    assert {item.relevance for item in other.blockers} == {"other_definition"}
    assert not any(item.relevance == "global" for item in direct.blockers)
    assert {item.related_row_identity for item in direct.blockers} == {identity}
    assert {item.related_field for item in direct.blockers} == {
        "model_input_enabled",
        "ml_name",
    }
    controller.save_schema()
    assert tuple(path.read_bytes() for path in protected) == before


def test_added_row_projection_revert_removes_ml_blocker_and_preserves_add(tmp_path):
    controller = _controller(tmp_path)
    controller.refresh()
    identity = ("schema_row", "fan_diameter")
    controller.add_definition(
        AddDefinitionIntent("manual_predict", "Fan Diameter", "fan_diameter", "number")
    )
    controller.edit_definition(
        EditDefinitionIntent(identity, (
            ("model_input_enabled", True),
            ("ml_name", "Fan Diameter"),
        ))
    )

    reverted_state = controller.edit_definition(
        EditDefinitionIntent(identity, (("model_input_enabled", False),))
    )
    reverted = project_data_definition_impact(reverted_state, identity)

    assert reverted_state.draft_changed and reverted.save_enabled
    assert not reverted.ml_fingerprint_changed
    assert not any(
        item.code == "ml_compatibility_projection_write_required"
        for item in reverted.blockers
    )
    assert [(item.action, item.identity) for item in reverted.definitions] == [
        ("Add", identity),
    ]
    assert [field.field_name for field in reverted.definitions[0].fields] == ["ml_name"]

    saved_state = controller.save_schema()
    assert saved_state.status == "saved" and not saved_state.draft_changed
    assert controller._draft is not None
    assert not controller._draft.controlled_row_additions
    assert not controller._draft.controlled_addition_initial_rows


def test_raw_invalid_role_source_keeps_dirty_draft_and_recovers_save_state(tmp_path):
    controller = _controller(tmp_path)
    controller.refresh()
    identity = ("schema_row", "id_volume")
    schema_path = tmp_path / "schema.csv"
    original = schema_path.read_bytes()
    controller.edit_cell(identity, "notes", "Keep this valid metadata edit")

    blocked_state = controller.edit_cell(identity, "value_source", "manual")
    blocked = project_data_definition_impact(blocked_state, identity)

    assert blocked_state.draft_changed and not blocked.save_enabled
    issue = next(
        item for item in blocked.blockers
        if item.code == "candidate_role_value_source_unsupported"
    )
    assert (issue.related_row_identity, issue.related_field) == (
        identity,
        "value_source",
    )
    assert controller.save_schema().status == "blocked"
    assert schema_path.read_bytes() == original
    assert not (tmp_path / "backups").exists()

    recovered_state = controller.edit_cell(identity, "value_source", "mapping_lookup")
    recovered = project_data_definition_impact(recovered_state, identity)
    assert recovered_state.draft_changed and recovered.save_enabled
    assert not any(
        item.code == "candidate_role_value_source_unsupported"
        for item in recovered.blockers
    )


@pytest.mark.parametrize(
    "intent",
    (
        AddDefinitionIntent(
            "mapping_predict",
            "Evap Inner Surface Area",
            "evap_inner_surface_area",
            "number",
            mapping_entity="evap_index",
            mapping_attribute="Inner Surface Area",
            trigger_column="evap_index",
        ),
        AddDefinitionIntent(
            "mapping_attribute",
            "Cond Inner Area",
            "cond_inner_area",
            "number",
            mapping_entity="cond_specs",
            mapping_attribute="Cond Inner Area",
            trigger_column="odu",
            rule_id="cond_specs_lookup",
        ),
    ),
)
def test_mapping_intent_save_writes_schema_only(tmp_path, intent):
    mapping_path = Path(MAPPING_JSON_FILE)
    mapping_before = mapping_path.read_bytes() if mapping_path.is_file() else None
    features_path = Path("config/ml/features.csv")
    features_before = features_path.read_bytes()
    controller = _controller(tmp_path)
    controller.refresh()
    added = controller.add_definition(intent)

    saved = controller.save_schema()

    assert added.save_action_enabled
    assert saved.status == "saved"
    mapping_after = mapping_path.read_bytes() if mapping_path.is_file() else None
    assert mapping_after == mapping_before
    assert features_path.read_bytes() == features_before


def test_candidate_failure_clears_after_correction_and_writer_error_remains_retryable(
    tmp_path,
    monkeypatch,
):
    controller = _controller(tmp_path)
    state = controller.refresh()
    identity = ("schema_row", "idu")
    controller.edit_cell(identity, "label", "Indoor Unit")
    controller.edit_cell(identity, "data_type", "invalid_type")
    blocked_state = controller.save_schema()
    blocked = project_data_definition_impact(blocked_state, identity)

    assert blocked.status == "blocked"
    assert blocked.save_result_status == "blocked"
    assert not blocked.save_enabled
    assert "candidate_schema_validation_failed" in blocked.result_text
    assert any(item.related_field == "data_type" for item in blocked.blockers)

    corrected_state = controller.edit_cell(identity, "data_type", "string")
    corrected = project_data_definition_impact(corrected_state, identity)
    assert corrected.status == "dirty" and corrected.save_enabled
    assert corrected.save_result_status == "No save attempted."
    assert "candidate_schema_validation_failed" not in corrected.result_text

    real_replace = schema_writer_module.os.replace
    attempts = 0

    def fail_once(source, destination):  # noqa: ANN001, ANN202
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise OSError("temporary replace failure")
        return real_replace(source, destination)

    monkeypatch.setattr(schema_writer_module.os, "replace", fail_once)
    error_state = controller.save_schema()
    error = project_data_definition_impact(error_state, identity)
    assert error.status == "dirty" and error.save_enabled
    assert error.save_result_status == "error"
    assert "retry Save" in error.result_text

    written_state = controller.save_schema()
    written = project_data_definition_impact(written_state, identity)
    assert written.status == "clean" and not written.save_enabled
    assert written.save_result_status == "written"
    assert dict(written.save_result_rows)["Backup"]
    assert "Restart Predict" in written.result_text


def test_multiple_commands_are_deterministic_and_projection_is_non_mutating(tmp_path):
    controller = _controller(tmp_path)
    controller.refresh()
    controller.add_definition(
        AddDefinitionIntent("manual_predict", "Fan Diameter", "fan_diameter", "number")
    )
    state = controller.edit_definition(
        EditDefinitionIntent(("schema_row", "idu"), (("notes", "Updated"),))
    )
    before = state

    first = project_data_definition_impact(state, ("schema_row", "idu"))
    second = project_data_definition_impact(state, ("schema_row", "fan_diameter"))

    assert [item.identity[1] for item in first.definitions] == ["idu", "fan_diameter"]
    assert [item.action for item in first.definitions] == ["Edit", "Add"]
    assert first.definitions == second.definitions
    assert state == before

    saved_state = controller.save_schema()
    saved = project_data_definition_impact(saved_state, ("schema_row", "fan_diameter"))
    assert saved.save_result_status == "written"
    assert not saved_state.draft_changed and not saved.save_enabled
    loaded = load_predict_schema_catalog_v2(tmp_path / "schema.csv")
    assert dict(saved.save_result_rows)["Rows written"] == str(len(loaded.rows))
    assert any(row.column_key == "fan_diameter" for row in loaded.rows)


def test_impact_renders_direct_other_and_global_blocker_groups(tmp_path):
    state = _controller(tmp_path).refresh()
    selected = ("schema_row", "cooling_capa")
    fixture = replace(state, blocker_items=(
        DataDefinitionBlockerItem(
            "error", "direct_issue", "schema_csv", "Direct issue.", selected,
            "label", "save_plan",
        ),
        DataDefinitionBlockerItem(
            "error", "other_issue", "schema_csv", "Other issue.",
            ("schema_row", "heating_capa"), "editor", "save_plan",
        ),
        DataDefinitionBlockerItem(
            "error", "global_issue", "schema_csv", "Global issue.", None, "", "save_plan",
        ),
    ))

    impact = project_data_definition_impact(fixture, selected)

    assert [item.relevance for item in impact.blockers] == [
        "direct", "other_definition", "global",
    ]
    assert "Direct" in impact.save_text and "(direct_issue)" in impact.save_text
    assert "Other Definition" in impact.save_text and "(other_issue)" in impact.save_text
    assert "Global" in impact.save_text and "(global_issue)" in impact.save_text

    no_selection = project_data_definition_impact(fixture, None)
    assert [item.relevance for item in no_selection.blockers] == [
        "selection_unavailable",
        "selection_unavailable",
        "global",
    ]
    assert [item.code for item in no_selection.blockers] == [
        "direct_issue",
        "other_issue",
        "global_issue",
    ]
    assert "Selection Unavailable" in no_selection.save_text
    assert "(direct_issue)" in no_selection.save_text
    assert "(other_issue)" in no_selection.save_text
    assert "Global" in no_selection.save_text and "(global_issue)" in no_selection.save_text
    direct_line = next(
        line for line in no_selection.save_text.splitlines() if "direct_issue" in line
    )
    other_line = next(
        line for line in no_selection.save_text.splitlines() if "other_issue" in line
    )
    global_line = next(
        line for line in no_selection.save_text.splitlines() if "global_issue" in line
    )
    assert "definition: cooling_capa" in direct_line
    assert "field: label" in direct_line and "target: schema_csv" in direct_line
    assert "definition: heating_capa" in other_line
    assert "field: editor" in other_line and "target: schema_csv" in other_line
    assert "definition:" not in global_line

    restored = project_data_definition_impact(fixture, selected)
    assert "selection_unavailable" not in restored.save_text
    assert "definition: cooling_capa" not in restored.save_text
    assert "definition: heating_capa" in restored.save_text


def _controller(tmp_path) -> DataDefinitionController:
    schema_path = tmp_path / "schema.csv"
    shutil.copyfile(DEFAULT_SCHEMA_PATH, schema_path)
    return DataDefinitionController(DataDefinitionService(schema_path=schema_path))
