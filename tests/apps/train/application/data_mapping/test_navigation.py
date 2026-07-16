"""Qt-free Data Mapping public navigation integration tests."""

import json
from pathlib import Path

from apps.train.application.data_mapping import DataMappingNavigationRequest
from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_mapping_service import DataMappingService, RuntimeMappingCatalogProvider
from core.data_definition import MappingRequirement


class MutableRequirementProvider:
    def __init__(self, requirements=()):  # noqa: ANN001
        self.requirements = tuple(requirements)

    def load_mapping_requirements(self):  # noqa: ANN201
        return self.requirements


def test_public_navigation_contract_is_qt_free_and_deterministic():
    source = Path(
        "apps/train/application/data_mapping/contracts.py"
    ).read_text(encoding="utf-8")

    assert _request() == _request()
    assert "PySide6" not in source
    assert "QModelIndex" not in source
    assert "QWidget" not in source


def test_navigation_opens_exact_group_attribute_and_first_unresolved(tmp_path):
    requirement = _requirement()
    provider = MutableRequirementProvider((requirement,))
    controller = DataMappingController(
        DataMappingService(
            RuntimeMappingCatalogProvider(str(_mapping_file(tmp_path))),
            provider,
        )
    )

    state, result = controller.open_requirement(_request(), "idu")

    assert result.status == "opened_unresolved"
    assert result.target.group_key == "odu_cond_specs"
    assert result.target.row_key == "ODU-A F&T 7 1"
    assert result.target.attribute_key == "Cond Inner Area"
    assert state.selected_group_key == "odu_cond_specs"
    assert state.value_headers[-1] == "Cond Inner Area"
    item = next(item for item in state.coverage_items if item.definition_column_key == "cond_inner_area")
    assert (item.ready_rows, item.missing_rows, item.invalid_rows) == (0, 1, 0)
    issue_target = next(target for target in state.issue_targets if target is not None)
    assert (issue_target.group_key, issue_target.row_key, issue_target.attribute_key) == (
        item.first_unresolved.group_key,
        item.first_unresolved.row_key,
        item.first_unresolved.attribute_key,
    )


def test_navigation_refresh_projects_requirement_without_discarding_edit_or_undo(tmp_path):
    mapping_file = _mapping_file(tmp_path)
    before = mapping_file.read_bytes()
    provider = MutableRequirementProvider()
    service = DataMappingService(RuntimeMappingCatalogProvider(str(mapping_file)), provider)
    controller = DataMappingController(service)
    controller.refresh("idu")
    edited = controller.edit_cell("idu", 0, "ID Volume", "9.5")
    provider.requirements = (_requirement(),)

    opened, result = controller.open_requirement(_request(), "idu")
    restored = controller.undo("idu")

    assert edited.dirty and opened.dirty
    assert result.status == "opened_unresolved"
    assert next(item for item in opened.entities if item.entity_key == "idu").row_count == 1
    assert service.current_snapshot().draft.group("idu").rows[0].value_for("ID Volume") == 1.25
    assert not restored.dirty
    assert mapping_file.read_bytes() == before


def test_navigation_reports_stale_group_attribute_and_unsaved_request_without_fallback(tmp_path):
    provider = MutableRequirementProvider((_requirement(),))
    controller = DataMappingController(
        DataMappingService(
            RuntimeMappingCatalogProvider(str(_mapping_file(tmp_path))), provider
        )
    )
    initial = controller.refresh("idu")

    group_state, group_result = controller.open_requirement(
        DataMappingNavigationRequest(**{**_request().__dict__, "resolved_group_key": "wrong"}),
        "idu",
    )
    attr_state, attr_result = controller.open_requirement(
        DataMappingNavigationRequest(**{**_request().__dict__, "mapping_attribute": "Stale"}),
        "idu",
    )
    unsaved_state, unsaved_result = controller.open_requirement(
        DataMappingNavigationRequest(**{**_request().__dict__, "saved": False}),
        "idu",
    )

    assert initial.selected_group_key == "idu"
    assert group_state.selected_group_key == attr_state.selected_group_key == "idu"
    assert unsaved_state.selected_group_key == "idu"
    assert group_result.status == "requested_group_unavailable"
    assert attr_result.status == "requested_attribute_unavailable"
    assert unsaved_result.status == "requirement_not_saved"


def test_navigation_reports_already_ready_without_unrelated_target(tmp_path):
    mapping_file = _mapping_file(tmp_path)
    runtime = json.loads(mapping_file.read_text(encoding="utf-8"))
    runtime["cond_specs"]["ODU-A F&T 7 1"]["Cond Inner Area"] = 2.25
    mapping_file.write_text(json.dumps(runtime), encoding="utf-8")
    controller = DataMappingController(
        DataMappingService(
            RuntimeMappingCatalogProvider(str(mapping_file)),
            MutableRequirementProvider((_requirement(),)),
        )
    )

    state, result = controller.open_requirement(_request(), "idu")

    assert state.selected_group_key == "odu_cond_specs"
    assert result.status == "coverage_ready"
    assert result.target is None


def test_navigation_reports_missing_saved_requirement_and_mapping_source(tmp_path):
    mapping_file = _mapping_file(tmp_path)
    provider = MutableRequirementProvider()
    controller = DataMappingController(
        DataMappingService(RuntimeMappingCatalogProvider(str(mapping_file)), provider)
    )

    missing_requirement_state, missing_requirement = controller.open_requirement(
        _request(), "idu"
    )
    mapping_file.unlink()
    missing_source_state, missing_source = controller.open_requirement(_request(), "idu")

    assert missing_requirement.status == "requirement_not_saved"
    assert missing_requirement_state.selected_group_key == "idu"
    assert missing_source.status == "mapping_source_unavailable"
    assert missing_source_state.selected_group_key == "idu"
    assert missing_source_state.resource_status == "missing"


def test_navigation_load_failure_is_structured_and_non_throwing():
    class FailingProvider:
        source_label = "synthetic broken source"

        def load_draft(self):  # noqa: ANN201
            raise ValueError("synthetic load failure")

    controller = DataMappingController(
        DataMappingService(FailingProvider(), MutableRequirementProvider((_requirement(),)))
    )

    state, result = controller.open_requirement(_request())

    assert result.status == "load_failed"
    assert "synthetic load failure" in result.message
    assert state.resource_status == "load-error"
    assert state.selected_group_key == ""


def _request() -> DataMappingNavigationRequest:
    return DataMappingNavigationRequest(
        definition_identity=("schema_row", "cond_inner_area"),
        definition_column_key="cond_inner_area",
        definition_label="Cond Inner Area",
        mapping_entity="cond_specs",
        mapping_attribute="Cond Inner Area",
        resolved_group_key="odu_cond_specs",
        required=True,
        data_type="number",
    )


def _requirement() -> MappingRequirement:
    return MappingRequirement(
        column_key="cond_inner_area",
        ml_name="",
        mapping_entity="cond_specs",
        mapping_attribute="Cond Inner Area",
        trigger_column="odu",
        rule_id="cond_specs_lookup",
        data_type="number",
        required=True,
    )


def _mapping_file(tmp_path):  # noqa: ANN001, ANN201
    path = tmp_path / "mapping.json"
    path.write_text(
        json.dumps(
            {
                "idu": {"IDU-A": {"ID Volume": 1.25}},
                "odu": {"ODU-A": {"OD Volume": 2.5}},
                "odu_cascade": {
                    "ODU-A": {
                        "Available_Fins": ["F&T"],
                        "Available_Pis": ["7"],
                        "Available_Rows": ["1"],
                    }
                },
                "cond_specs": {
                    "ODU-A F&T 7 1": {"Cond Area": 3.5, "Cond Volume": 4.5}
                },
                "ref_type": {"R32": {}},
                "exp_type": {"EEV": {}},
            }
        ),
        encoding="utf-8",
    )
    return path
