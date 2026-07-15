"""Latest saved Mapping Requirement reconciliation at the draft-session boundary."""

from __future__ import annotations

import json

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


def test_required_optional_remove_readd_reconciles_draft_baseline_and_undo(tmp_path):
    mapping_path = _mapping_file(tmp_path)
    mapping_before = mapping_path.read_bytes()
    provider = MutableRequirementProvider((_requirement(required=True),))
    service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_path)),
        provider,
    )
    controller = DataMappingController(service)

    required = controller.refresh("idu")
    assert not required.dirty
    assert _coverage(required).required
    assert (_coverage(required).missing_rows, _coverage(required).invalid_rows) == (2, 0)
    assert any(issue.code == "required_mapping_value_missing" for issue in required.validation_rows)
    assert not _save_enabled(required)

    edited = controller.edit_cell("idu", 0, "ID Volume", "9.5")
    assert edited.dirty
    provider.requirements = (_requirement(required=False),)

    optional = controller.refresh("idu")
    repeated = controller.refresh("idu")
    current = service.current_snapshot()

    assert optional.dirty and repeated.dirty and current.dirty
    assert optional.value_headers.count("Fan Attribute") == 1
    assert optional.values[0].values[optional.value_headers.index("ID Volume")] == "9.5"
    assert not _coverage(optional).required
    assert (_coverage(optional).missing_rows, _coverage(optional).invalid_rows) == (2, 0)
    assert "Optional" in _coverage(optional).summary
    assert not any(
        issue.code == "required_mapping_value_missing" and issue.field == "Fan Attribute"
        for issue in optional.validation_rows
    )
    assert _save_enabled(optional)
    assert repeated == optional
    assert mapping_path.read_bytes() == mapping_before

    undone, undo_result = service.undo()
    empty_undo, empty_result = service.undo()
    undone_group = undone.draft.group("idu")
    assert undo_result.applied == 1
    assert empty_result.applied == 0
    assert not undone.dirty and not empty_undo.dirty
    assert undone_group.columns.count("Fan Attribute") == 1
    assert "Fan Attribute" not in undone_group.required_columns
    assert undone_group.rows[0].value_for("ID Volume") == 1.25

    with_value = service.edit_cell("idu", 0, "Fan Attribute", "2.5")
    assert with_value.dirty
    provider.requirements = ()
    removed = service.load_snapshot()
    removed_group = removed.draft.group("idu")

    assert "Fan Attribute" not in removed_group.columns
    assert removed_group.rows[0].value_for("Fan Attribute") == 2.5
    assert removed.mapping_requirements == ()
    assert not any(
        issue.field == "Fan Attribute" for issue in removed.validation_errors
    )
    assert mapping_path.read_bytes() == mapping_before

    save_result, saved = service.save_mapping()
    assert save_result.success and not saved.dirty
    assert json.loads(mapping_path.read_text(encoding="utf-8"))["idu"]["IDU-A"][
        "Fan Attribute"
    ] == 2.5

    provider.requirements = (_requirement(required=False),)
    restored = service.load_snapshot()
    restored_group = restored.draft.group("idu")
    assert restored_group.columns[-1] == "Fan Attribute"
    assert restored_group.rows[0].value_for("Fan Attribute") == 2.5
    assert not restored.dirty


def test_latest_data_type_replaces_stale_type_without_losing_unrelated_edit(tmp_path):
    mapping_path = _mapping_file(tmp_path, fan_value="not-a-number")
    provider = MutableRequirementProvider(
        (_requirement(required=False, data_type="string"),)
    )
    service = DataMappingService(RuntimeMappingCatalogProvider(str(mapping_path)), provider)
    controller = DataMappingController(service)
    controller.refresh("idu")
    controller.edit_cell("idu", 0, "Size", "draft-size")

    provider.requirements = (_requirement(required=False, data_type="number"),)
    changed = controller.refresh("idu")
    group = service.current_snapshot().draft.group("idu")

    assert group.column_data_types["Fan Attribute"] == "number"
    assert group.rows[0].value_for("Size") == "draft-size"
    assert _coverage(changed).invalid_rows == 1
    assert any(
        issue.code == "invalid_number" and issue.field == "Fan Attribute"
        for issue in changed.validation_rows
    )
    assert not _save_enabled(changed)

    provider.requirements = ()
    removed = controller.refresh("idu")
    assert not any(issue.field == "Fan Attribute" for issue in removed.validation_rows)
    assert not any(
        item.definition_column_key == "fan_attribute"
        for item in removed.coverage_items
    )
    assert _save_enabled(removed)

    provider.requirements = (_requirement(required=False, data_type="number"),)
    restored = controller.refresh("idu")
    assert _coverage(restored).invalid_rows == 1
    resolved = controller.edit_cell("idu", 0, "Fan Attribute", "3.5")
    assert _coverage(resolved).invalid_rows == 0
    assert _save_enabled(resolved)


def test_optional_to_required_activates_missing_validation_until_all_values_are_ready(
    tmp_path,
):
    provider = MutableRequirementProvider((_requirement(required=False),))
    controller = DataMappingController(
        DataMappingService(
            RuntimeMappingCatalogProvider(str(_mapping_file(tmp_path))),
            provider,
        )
    )

    optional = controller.refresh("idu")
    assert not _coverage(optional).required
    assert _coverage(optional).missing_rows == 2
    assert _save_enabled(optional)

    provider.requirements = (_requirement(required=True),)
    required = controller.refresh("idu")
    assert _coverage(required).required
    assert _coverage(required).missing_rows == 2
    assert _coverage(required).first_unresolved.row_index == 0
    assert any(
        issue.code == "required_mapping_value_missing"
        and issue.field == "Fan Attribute"
        for issue in required.validation_rows
    )
    assert not _save_enabled(required)

    first = controller.edit_cell("idu", 0, "Fan Attribute", "2.5")
    assert (_coverage(first).ready_rows, _coverage(first).missing_rows) == (1, 1)
    assert _coverage(first).first_unresolved.row_index == 1
    ready = controller.edit_cell("idu", 1, "Fan Attribute", "3.5")
    assert _coverage(ready).status == "ready"
    assert not any(
        issue.code == "required_mapping_value_missing"
        and issue.field == "Fan Attribute"
        for issue in ready.validation_rows
    )
    assert _save_enabled(ready)


def _requirement(*, required, data_type="number"):  # noqa: ANN001, ANN201
    return MappingRequirement(
        column_key="fan_attribute",
        ml_name="",
        mapping_entity="idu",
        mapping_attribute="Fan Attribute",
        trigger_column="idu",
        data_type=data_type,
        required=required,
    )


def _coverage(state):  # noqa: ANN001, ANN201
    return next(
        item for item in state.coverage_items if item.definition_column_key == "fan_attribute"
    )


def _save_enabled(state):  # noqa: ANN001, ANN201
    return next(action.enabled for action in state.actions if action.key == "save_mapping_json")


def _mapping_file(tmp_path, *, fan_value=None):  # noqa: ANN001, ANN201
    idu_a = {"ID Volume": 1.25, "Size": "S1"}
    if fan_value is not None:
        idu_a["Fan Attribute"] = fan_value
    path = tmp_path / "mapping.json"
    path.write_text(
        json.dumps(
            {
                "idu": {
                    "IDU-A": idu_a,
                    "IDU-B": {"ID Volume": 2.5, "Size": "S2"},
                },
                "ref_type": {"R32": {}},
                "exp_type": {"EEV": {}},
            }
        ),
        encoding="utf-8",
    )
    return path
