"""Effective shared-cell contract behavior at the Data Mapping boundary."""

from __future__ import annotations

import json

from apps.train.application.data_mapping import DataMappingNavigationRequest
from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_mapping_service import (
    DataMappingService,
    RuntimeMappingCatalogProvider,
)
from core.data_definition import MappingRequirement


class MutableRequirementProvider:
    def __init__(self, requirements=()):  # noqa: ANN001
        self.requirements = tuple(requirements)

    def load_mapping_requirements(self):  # noqa: ANN201
        return self.requirements


def test_data_type_conflict_blocks_save_without_first_wins_or_file_mutation(tmp_path):
    mapping_path = _mapping_file(tmp_path)
    before = mapping_path.read_bytes()
    requirements = (
        _requirement("fan_attribute_a", data_type="string", required=False),
        _requirement("fan_attribute_b", data_type="number", required=True),
    )
    provider = MutableRequirementProvider(requirements)
    service = DataMappingService(RuntimeMappingCatalogProvider(str(mapping_path)), provider)
    controller = DataMappingController(service)

    state = controller.refresh("idu")
    issue = next(
        issue
        for issue in state.validation_rows
        if issue.code == "mapping_requirement_contract_conflict"
    )

    assert "Fan Attribute" not in state.value_headers
    assert not any(item.mapping_attribute == "Fan Attribute" for item in state.coverage_items)
    assert issue.entity_key == "idu"
    assert issue.attribute_key == "Fan Attribute"
    assert issue.related_definition_keys == ("fan_attribute_a", "fan_attribute_b")
    assert not _save_enabled(state)
    export_plan = service.plan_exchange_export(tmp_path / "conflicting_bundle.csv")
    assert not export_plan.success
    assert any(
        item.code == "mapping_requirement_contract_conflict"
        for item in export_plan.issues
    )

    normal_service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_path)),
        MutableRequirementProvider(),
    )
    normal_export, _normal_snapshot = normal_service.export_exchange(
        tmp_path / "normal_bundle.csv"
    )
    assert normal_export.success
    preview, _preview_snapshot = service.preview_exchange_import(
        tmp_path / "normal_bundle.csv"
    )
    assert not preview.can_apply
    assert any(
        item.code == "mapping_requirement_contract_conflict"
        for item in preview.blockers
    )

    result, _snapshot = service.save_mapping()
    assert not result.success
    assert mapping_path.read_bytes() == before

    provider.requirements = tuple(reversed(requirements))
    reversed_state = controller.refresh("idu")
    reversed_issue = next(
        item
        for item in reversed_state.validation_rows
        if item.code == "mapping_requirement_contract_conflict"
    )
    assert reversed_issue == issue
    assert "Fan Attribute" not in reversed_state.value_headers
    assert mapping_path.read_bytes() == before


def test_optional_and_required_duplicates_use_one_required_number_contract(tmp_path):
    provider = MutableRequirementProvider(
        (
            _requirement("fan_attribute_b", required=False),
            _requirement("fan_attribute_a", required=True),
        )
    )
    controller = DataMappingController(
        DataMappingService(
            RuntimeMappingCatalogProvider(str(_mapping_file(tmp_path))),
            provider,
        )
    )

    state = controller.refresh("idu")
    coverage = _coverage(state)

    assert state.value_headers.count("Fan Attribute") == 1
    assert coverage.required
    assert coverage.data_type == "number"
    assert coverage.source_definition_column_keys == (
        "fan_attribute_a",
        "fan_attribute_b",
    )
    assert len(state.coverage_items) == 1
    assert (coverage.ready_rows, coverage.missing_rows, coverage.invalid_rows) == (0, 2, 0)
    assert sum(
        issue.code == "required_mapping_value_missing"
        and issue.field == "Fan Attribute"
        for issue in state.validation_rows
    ) == 2
    assert not _save_enabled(state)

    first = controller.edit_cell("idu", 0, "Fan Attribute", "2.5")
    assert (_coverage(first).ready_rows, _coverage(first).missing_rows) == (1, 1)
    ready = controller.edit_cell("idu", 1, "Fan Attribute", "3.5")
    assert _coverage(ready).status == "ready"
    assert _save_enabled(ready)


def test_identical_duplicates_dedupe_coverage_validation_and_both_handoffs(tmp_path):
    provider = MutableRequirementProvider(
        (
            _requirement("fan_attribute_b"),
            _requirement("fan_attribute_a"),
        )
    )
    controller = DataMappingController(
        DataMappingService(
            RuntimeMappingCatalogProvider(str(_mapping_file(tmp_path))),
            provider,
        )
    )
    state = controller.refresh("idu")

    assert state.value_headers.count("Fan Attribute") == 1
    assert len(state.coverage_items) == 1
    assert _coverage(state).source_definition_column_keys == (
        "fan_attribute_a",
        "fan_attribute_b",
    )
    assert sum(
        issue.code == "required_mapping_value_missing"
        and issue.field == "Fan Attribute"
        for issue in state.validation_rows
    ) == 2

    results = tuple(
        controller.open_requirement(_handoff(column_key), "idu")[1]
        for column_key in ("fan_attribute_a", "fan_attribute_b")
    )
    assert all(result.status == "opened_unresolved" for result in results)
    assert results[0].target == results[1].target
    assert results[0].target.row_index == 0


def test_relation_conflict_is_a_defensive_blocker_without_file_mutation(tmp_path):
    mapping_path = _mapping_file(tmp_path)
    before = mapping_path.read_bytes()
    provider = MutableRequirementProvider(
        (
            _requirement("fan_attribute_a", trigger_column="idu"),
            _requirement(
                "fan_attribute_b",
                trigger_column="odu",
                rule_id="alternate_lookup",
            ),
        )
    )
    service = DataMappingService(RuntimeMappingCatalogProvider(str(mapping_path)), provider)

    snapshot = service.load_snapshot()
    conflict = snapshot.mapping_requirement_conflicts[0]

    assert conflict.reasons == ("relation",)
    assert "Fan Attribute" not in snapshot.draft.group("idu").columns
    assert not snapshot.validation_result.save_enabled
    result, _snapshot = service.save_mapping()
    assert not result.success
    assert mapping_path.read_bytes() == before


def test_projection_only_blank_survives_no_refresh_history_or_import_payload(tmp_path):
    mapping_path = _mapping_file(tmp_path)
    provider = MutableRequirementProvider(
        (_requirement("fan_attribute", required=False),)
    )
    service = DataMappingService(RuntimeMappingCatalogProvider(str(mapping_path)), provider)

    projected = service.load_snapshot()
    projected_row = projected.draft.group("idu").rows[0]
    assert projected.dirty is False
    assert projected_row.value_for("Fan Attribute") == ""
    assert not projected_row.has_concrete_value_for("Fan Attribute")

    for requirements in ((), provider.requirements, (), ()):
        provider.requirements = requirements
        refreshed = service.load_snapshot()
        assert refreshed.dirty is False
        assert not refreshed.draft.group("idu").rows[0].has_concrete_value_for(
            "Fan Attribute"
        )

    undone, undo_result = service.undo()
    assert undo_result.applied == 0
    assert undone.dirty is False

    export_result, _snapshot = service.export_exchange(tmp_path / "mapping_bundle.csv")
    assert export_result.success
    preview, _snapshot = service.preview_exchange_import(tmp_path / "mapping_bundle.csv")
    assert preview.can_apply
    assert preview.candidate is not None
    assert not preview.candidate.group("idu").rows[0].has_concrete_value_for(
        "Fan Attribute"
    )

    edited = service.edit_cell("idu", 0, "Size", "S9")
    assert edited.dirty
    save_result, _saved = service.save_mapping()
    payload = json.loads(mapping_path.read_text(encoding="utf-8"))
    assert save_result.success
    assert payload["idu"]["IDU-A"]["Size"] == "S9"
    assert "Fan Attribute" not in payload["idu"]["IDU-A"]


def _requirement(
    column_key: str,
    *,
    data_type: str = "number",
    required: bool = True,
    trigger_column: str = "idu",
    rule_id: str = "",
) -> MappingRequirement:
    return MappingRequirement(
        column_key=column_key,
        ml_name=column_key,
        mapping_entity="idu",
        mapping_attribute="Fan Attribute",
        trigger_column=trigger_column,
        rule_id=rule_id,
        data_type=data_type,
        required=required,
    )


def _handoff(column_key: str) -> DataMappingNavigationRequest:
    return DataMappingNavigationRequest(
        definition_identity=("schema_row", column_key),
        definition_column_key=column_key,
        definition_label=column_key,
        mapping_entity="idu",
        mapping_attribute="Fan Attribute",
        resolved_group_key="idu",
        required=True,
        data_type="number",
    )


def _coverage(state):  # noqa: ANN001, ANN201
    return next(item for item in state.coverage_items if item.mapping_attribute == "Fan Attribute")


def _save_enabled(state):  # noqa: ANN001, ANN201
    return next(action.enabled for action in state.actions if action.key == "save_mapping_json")


def _mapping_file(tmp_path):  # noqa: ANN001, ANN201
    path = tmp_path / "mapping.json"
    path.write_text(
        json.dumps(
            {
                "idu": {
                    "IDU-A": {"ID Volume": 1.25, "Size": "S1"},
                    "IDU-B": {"ID Volume": 2.5, "Size": "S2"},
                },
                "ref_type": {"R32": {}},
                "exp_type": {"EEV": {}},
            }
        ),
        encoding="utf-8",
    )
    return path
