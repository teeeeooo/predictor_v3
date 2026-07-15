"""Phase 3 Slice 3A Data Definition inventory-first workflow tests."""

from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path

from apps.train.controllers.data_definition_controller import DataDefinitionController
from apps.train.controllers.data_definition_presentation import (
    project_data_definition_inventory,
)
from apps.train.controllers.data_definition_state_builder import state_from_report
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
    assert all(row.category == "Mapping-backed Input" for row in filtered.rows)
    assert all(row.source_type == "Mapping Lookup" for row in filtered.rows)
    assert tuple(row.identity for row in restored.rows) == state.draft_row_identities
    assert hidden.selected_identity == hidden.rows[0].identity


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
