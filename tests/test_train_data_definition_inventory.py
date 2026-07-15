"""Phase 3 Slice 3A Data Definition inventory-first workflow tests."""

from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path

from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.controllers.data_definition_detail_projection import project_blockers
from apps.train.controllers.data_definition_presentation import (
    project_data_definition_inventory,
)
from apps.train.controllers.data_definition_state_builder import (
    DataDefinitionBlockerItem,
    state_from_report,
)
from apps.train.services.data_definition_service import DataDefinitionService
from core.mapping.paths import MAPPING_JSON_FILE


def test_inventory_projection_preserves_identity_order_and_projects_detail():
    state = DataDefinitionController().refresh()

    projection = project_data_definition_inventory(state)

    assert tuple(row.identity for row in projection.rows) == state.draft_row_identities
    assert projection.selected_identity == state.draft_row_identities[0]
    assert projection.detail.identity == projection.selected_identity
    assert dict(projection.detail.rows)["Internal key"] == projection.rows[0].internal_key
    assert dict(projection.detail.rows)["Direct edit"] == "Allowed"
    assert dict(projection.detail.rows)["Save blockers"] == "None"
    assert projection.status_key == "clean"
    assert not projection.save_enabled
    derived = next(row for row in projection.rows if row.identity[0] == "derived_policy")
    derived_detail = project_data_definition_inventory(
        state,
        selected_identity=derived.identity,
    ).detail
    assert derived.category == "Derived Policy"
    assert derived.lifecycle_state == "Blocked"
    assert dict(derived_detail.rows)["Direct edit"] == "Blocked"
    assert "Derived policy persistence" in dict(derived_detail.rows)["Direct edit policy"]


def test_inventory_search_filter_and_selection_are_deterministic():
    state = DataDefinitionController().refresh()
    base = project_data_definition_inventory(state)
    target = next(row for row in base.rows if row.internal_key == "evap_area")

    searched = project_data_definition_inventory(
        state,
        search="  EVAP_AREA  ",
        selected_identity=target.identity,
    )
    filtered = project_data_definition_inventory(
        state,
        category="Mapping-backed Input",
        source_type="Mapping Lookup",
        lifecycle_state="Active",
        selected_identity=target.identity,
    )
    hidden = project_data_definition_inventory(
        state,
        search="cooling_capa",
        selected_identity=target.identity,
    )
    restored = project_data_definition_inventory(state, selected_identity=hidden.selected_identity)

    assert [row.internal_key for row in searched.rows] == ["evap_area"]
    assert filtered.selected_identity == target.identity
    assert filtered.resolved_category == "Mapping-backed Input"
    assert filtered.resolved_source_type == "Mapping Lookup"
    assert filtered.resolved_lifecycle_state == "Active"
    assert all(row.category == "Mapping-backed Input" for row in filtered.rows)
    assert all(row.source_type == "Mapping Lookup" for row in filtered.rows)
    assert tuple(row.identity for row in restored.rows) == state.draft_row_identities
    assert hidden.selected_identity == hidden.rows[0].identity


def test_inventory_filter_falls_back_when_selected_option_disappears():
    controller = DataDefinitionController()
    state = controller.refresh()
    rule_option_identities = (
        ("schema_row", "fin_type"),
        ("schema_row", "pi"),
        ("schema_row", "row"),
    )
    for identity in rule_option_identities:
        state = controller.edit_cell(identity, "value_source", "manual")

    before = state
    projection = project_data_definition_inventory(
        state,
        source_type="Rule Options",
        selected_identity=rule_option_identities[-1],
    )

    assert "Rule Options" not in projection.source_types
    assert projection.resolved_source_type == ""
    assert tuple(row.identity for row in projection.rows) == state.draft_row_identities
    assert projection.selected_identity == rule_option_identities[-1]
    assert projection.detail.identity == projection.selected_identity
    assert projection.view_state == "populated"
    assert state == before


def test_detail_blockers_attribute_plan_blocker_to_its_definition():
    service = DataDefinitionService()
    controller = DataDefinitionController(service)
    state = controller.refresh()
    valid_identity = ("schema_row", "idu")
    blocked_identity = ("schema_row", "cooling_capa")
    before = _hash(service.schema_path)
    controller.edit_cell(valid_identity, "label", "Indoor Unit Label")
    blocked = controller.edit_cell(
        blocked_identity,
        "ml_name",
        "Cooling Capacity Renamed",
    )

    valid_summary = dict(
        project_data_definition_inventory(
            blocked,
            selected_identity=valid_identity,
        ).detail.rows
    )["Save blockers"]
    blocked_summary = dict(
        project_data_definition_inventory(
            blocked,
            selected_identity=blocked_identity,
        ).detail.rows
    )["Save blockers"]
    valid_items = project_blockers(blocked, valid_identity)
    blocked_items = project_blockers(blocked, blocked_identity)

    assert valid_summary.startswith("No direct blocker for this definition.")
    assert "Draft blockers from other definitions" in valid_summary
    assert "cooling_capa" in valid_summary
    assert "ml_compatibility_projection_write_required" in valid_summary
    assert blocked_summary.startswith("Direct blockers")
    assert "ml_name" in blocked_summary
    assert [item.relevance for item in valid_items] == ["other_definition"]
    assert [item.relevance for item in blocked_items] == ["direct"]
    assert not blocked.save_action_enabled
    assert _hash(service.schema_path) == before


def test_detail_blockers_attribute_compound_ml_activation_to_definition():
    service = DataDefinitionService()
    controller = DataDefinitionController(service)
    controller.refresh()
    identity = ("schema_row", "idu")
    other_identity = ("schema_row", "cooling_capa")
    protected_paths = (
        service.schema_path,
        Path("config/ml/features.csv"),
        Path(MAPPING_JSON_FILE),
    )
    before = tuple(_hash(path) for path in protected_paths)
    controller.edit_cell(identity, "model_input_enabled", True)
    blocked = controller.edit_cell(identity, "ml_name", "IDU")

    direct = project_blockers(blocked, identity)
    other = project_blockers(blocked, other_identity)

    assert [item.relevance for item in direct] == ["direct", "direct"]
    assert [item.related_field for item in direct] == ["model_input_enabled", "ml_name"]
    assert all(item.related_row_identity == identity for item in direct)
    assert [item.relevance for item in other] == [
        "other_definition",
        "other_definition",
    ]
    assert not any(item.relevance == "global" for item in (*direct, *other))
    assert not blocked.save_action_enabled
    assert tuple(_hash(path) for path in protected_paths) == before


def test_detail_blockers_attribute_compound_ml_activation_for_multiple_definitions():
    controller = DataDefinitionController()
    controller.refresh()
    first_identity = ("schema_row", "idu")
    second_identity = ("schema_row", "evap_index")
    for identity, ml_name in (
        (first_identity, "IDU"),
        (second_identity, "Evap Index"),
    ):
        controller.edit_cell(identity, "model_input_enabled", True)
        blocked = controller.edit_cell(identity, "ml_name", ml_name)

    first = project_blockers(blocked, first_identity)
    second = project_blockers(blocked, second_identity)

    assert [(item.relevance, item.related_row_identity, item.related_field) for item in first] == [
        ("direct", first_identity, "model_input_enabled"),
        ("direct", first_identity, "ml_name"),
        ("other_definition", second_identity, "model_input_enabled"),
        ("other_definition", second_identity, "ml_name"),
    ]
    assert [(item.relevance, item.related_row_identity, item.related_field) for item in second] == [
        ("direct", second_identity, "model_input_enabled"),
        ("direct", second_identity, "ml_name"),
        ("other_definition", first_identity, "model_input_enabled"),
        ("other_definition", first_identity, "ml_name"),
    ]
    assert not any(item.relevance == "global" for item in (*first, *second))


def test_detail_blockers_remove_compound_ml_attribution_after_partial_revert():
    controller = DataDefinitionController()
    controller.refresh()
    identity = ("schema_row", "idu")
    controller.edit_cell(identity, "model_input_enabled", True)
    blocked = controller.edit_cell(identity, "ml_name", "IDU")

    recovered = controller.edit_cell(identity, "ml_name", "")

    assert project_blockers(blocked, identity)
    assert not any(
        item.code == "ml_compatibility_projection_write_required"
        for item in recovered.blocker_items
    )
    assert project_blockers(recovered, identity) == ()
    assert recovered.can_save_schema
    assert recovered.save_action_enabled


def test_detail_blockers_deduplicate_only_cross_source_logical_duplicates():
    state = DataDefinitionController().refresh()
    selected_identity = ("schema_row", "cooling_capa")
    duplicate = DataDefinitionBlockerItem(
        "error",
        "duplicate_code",
        "schema_csv",
        "Same logical issue.",
        selected_identity,
        "data_type",
        "save_plan",
    )
    distinct = DataDefinitionBlockerItem(
        "error",
        "duplicate_code",
        "schema_csv",
        "Different candidate issue.",
        ("schema_row", "heating_capa"),
        "editor",
        "last_save_result",
    )
    fixture = replace(
        state,
        blocker_items=(
            duplicate,
            replace(duplicate, source="last_save_result", message=" Same logical  issue. "),
            distinct,
        ),
    )
    before = fixture

    blockers = project_blockers(fixture, selected_identity)
    summary = dict(
        project_data_definition_inventory(
            fixture,
            selected_identity=selected_identity,
        ).detail.rows
    )["Save blockers"]

    assert len(blockers) == 2
    assert [item.relevance for item in blockers] == ["direct", "other_definition"]
    assert summary.count("Same logical") == 1
    assert "Different candidate issue" in summary
    assert fixture == before


def test_detail_blockers_keep_global_attribution_for_every_selection():
    state = DataDefinitionController().refresh()
    first_identity = ("schema_row", "cooling_capa")
    second_identity = ("schema_row", "heating_capa")
    first_item = DataDefinitionBlockerItem(
        "error",
        "first_definition_blocked",
        "schema_csv",
        "Cooling definition is blocked.",
        first_identity,
        "data_type",
        "save_plan",
    )
    second_item = DataDefinitionBlockerItem(
        "error",
        "second_definition_blocked",
        "schema_csv",
        "Heating definition is blocked.",
        second_identity,
        "editor",
        "save_plan",
    )
    global_item = DataDefinitionBlockerItem(
        "error",
        "schema_write_target_unavailable",
        "schema_csv",
        "The schema write target is unavailable.",
        None,
        "",
        "save_plan",
    )
    fixture = replace(
        state,
        blocker_items=(global_item, second_item, first_item),
    )

    first = project_blockers(fixture, first_identity)
    second = project_blockers(fixture, second_identity)
    first_summary = dict(
        project_data_definition_inventory(
            fixture,
            selected_identity=first_identity,
        ).detail.rows
    )["Save blockers"]

    assert [item.relevance for item in first] == [
        "direct",
        "other_definition",
        "global",
    ]
    assert [item.code for item in first] == [
        "first_definition_blocked",
        "second_definition_blocked",
        "schema_write_target_unavailable",
    ]
    assert [item.relevance for item in second] == [
        "direct",
        "other_definition",
        "global",
    ]
    assert [item.code for item in second] == [
        "second_definition_blocked",
        "first_definition_blocked",
        "schema_write_target_unavailable",
    ]
    assert first[-1].related_row_identity is None
    assert "Direct blockers" in first_summary
    assert "Global draft blockers" in first_summary


def test_inventory_no_match_empty_and_load_error_states_are_explicit():
    state = DataDefinitionController().refresh()
    no_match = project_data_definition_inventory(state, search="definitely-not-present")
    empty = project_data_definition_inventory(
        replace(state, draft_rows=(), draft_row_identities=()),
    )
    error = project_data_definition_inventory(_FailingController().refresh())

    assert no_match.view_state == "no_match"
    assert no_match.selected_identity is None
    assert no_match.detail.state == "no_selection"
    assert empty.view_state == "empty"
    assert error.view_state == "load_error"
    assert error.status_key == "load_error"
    assert "failed" in error.view_message.lower()


def test_inventory_projection_does_not_mutate_definition_or_mapping_sources():
    service = DataDefinitionService()
    draft = service.load_draft()
    report = service.load_report()
    plan = service.preview_save_plan(draft, current_report=report)
    state = state_from_report(report, draft, plan)
    fixture = Path("tests/fixtures/mapping/mapping_runtime_equivalent.json")
    before = (
        draft.rows,
        draft.baseline_rows,
        draft.changes(),
        plan,
        _hash(service.schema_path),
        _hash(Path(MAPPING_JSON_FILE)),
        _hash(fixture),
    )

    first = project_data_definition_inventory(state, search="area")
    if first.rows:
        project_data_definition_inventory(
            state,
            category=first.rows[0].category,
            source_type=first.rows[0].source_type,
            lifecycle_state=first.rows[0].lifecycle_state,
            selected_identity=first.rows[0].identity,
        )

    assert before == (
        draft.rows,
        draft.baseline_rows,
        draft.changes(),
        plan,
        _hash(service.schema_path),
        _hash(Path(MAPPING_JSON_FILE)),
        _hash(fixture),
    )


class _FailingService(DataDefinitionService):
    def refresh_report(self, *, training_data_path=None):  # noqa: ANN001
        raise RuntimeError("fixture load failed")


class _FailingController(DataDefinitionController):
    def __init__(self) -> None:
        super().__init__(_FailingService())


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "missing"
