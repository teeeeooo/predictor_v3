"""Train Data Mapping dynamic requirement integration tests."""

from __future__ import annotations

import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_mapping_service import DataMappingService, RuntimeMappingCatalogProvider
from apps.train.ui.data_mapping_panel import DataMappingPanel
from core.data_definition.model import DataDefinitionRow, MappingRequirement
from core.data_definition.projection import extract_mapping_requirements


class RequirementProvider:
    def __init__(self, requirements):
        self._requirements = tuple(requirements)

    def load_mapping_requirements(self):
        return self._requirements


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_data_mapping_service_injects_requirement_and_blocks_missing_value(tmp_path):
    mapping_file = _mapping_file(tmp_path)
    requirement = _fan_requirement()
    service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_file)),
        RequirementProvider((requirement,)),
    )

    snapshot = service.load_snapshot()
    result, after_save = service.save_mapping()

    idu = snapshot.draft.group("idu")
    assert idu is not None
    assert "Fan Diameter" in idu.columns
    assert not snapshot.is_valid
    assert [issue.code for issue in snapshot.validation_errors] == [
        "required_mapping_value_missing"
    ]
    assert not {action.key: action for action in snapshot.actions}["save_mapping_json"].enabled
    assert not result.success
    assert result.message == "Resolve Issues before saving."
    assert not after_save.is_valid
    assert json.loads(mapping_file.read_text(encoding="utf-8"))["idu"] == {
        "IDU-A": {"ID Volume": 1.25}
    }


def test_data_mapping_controller_marks_dynamic_attribute_required(tmp_path):
    mapping_file = _mapping_file(tmp_path)
    controller = DataMappingController(
        DataMappingService(
            RuntimeMappingCatalogProvider(str(mapping_file)),
            RequirementProvider((_fan_requirement(),)),
        )
    )

    state = controller.refresh("idu")
    attribute = next(row for row in state.attributes if row.attribute_key == "Fan Diameter")

    assert attribute.required
    assert attribute.notes == "Required by Data Definition."
    assert state.value_headers[-1] == "Fan Diameter"
    assert state.values[0].values[-1] == ""
    assert state.validation_rows[0].code == "required_mapping_value_missing"


def test_data_mapping_panel_displays_dynamic_requirement(tmp_path):
    app = _app()
    mapping_file = _mapping_file(tmp_path)
    controller = DataMappingController(
        DataMappingService(
            RuntimeMappingCatalogProvider(str(mapping_file)),
            RequirementProvider((_fan_requirement(),)),
        )
    )
    panel = DataMappingPanel(controller=controller)
    try:
        app.processEvents()
        attribute_model = panel.attribute_table.model()
        value_model = panel.row_table.model()
        validation_model = panel.validation_table.model()

        assert attribute_model.cell_value(attribute_model.rowCount() - 1, 0) == "Fan Diameter"
        assert attribute_model.cell_value(attribute_model.rowCount() - 1, 3) == "true"
        assert value_model.headerData(
            value_model.columnCount() - 1,
            Qt.Horizontal,
            Qt.DisplayRole,
        ) == "Fan Diameter"
        assert validation_model.cell_value(0, 0) == "error"
        assert validation_model.cell_value(0, 4) == "Fan Diameter is required by Data Definition."
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()


def test_cond_inner_area_round_trips_through_validation_save_reload_and_export(tmp_path):
    mapping_file = _mapping_file(tmp_path)
    requirement = _cond_inner_area_requirement()
    provider = RequirementProvider((requirement,))
    service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_file)),
        provider,
    )

    initial = service.load_snapshot()
    group = initial.draft.group("odu_cond_specs")
    assert group.columns == (
        "ODU", "Fin Type", "Pi", "Row", "Cond Area", "Cond Volume", "Cond Inner Area"
    )
    assert [issue.code for issue in initial.validation_errors] == [
        "required_mapping_value_missing"
    ]
    controller = DataMappingController(service)
    state = controller.refresh("odu_cond_specs")
    attribute = next(
        item for item in state.attributes if item.attribute_key == "Cond Inner Area"
    )
    assert attribute.data_type == "number"
    assert attribute.required

    edited = service.edit_cell("odu_cond_specs", 0, "Cond Inner Area", "2.25")
    assert edited.is_valid
    result, saved_snapshot = service.save_mapping()
    assert result.success
    assert saved_snapshot.is_valid

    runtime = json.loads(mapping_file.read_text(encoding="utf-8"))
    assert runtime["cond_specs"]["ODU-A F&T 7 1"] == {
        "Cond Area": 3.5,
        "Cond Volume": 4.5,
        "Cond Inner Area": 2.25,
    }

    reloaded_service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_file)),
        provider,
    )
    reloaded = reloaded_service.load_snapshot()
    reloaded_group = reloaded.draft.group("odu_cond_specs")
    assert reloaded_group.columns[-1] == "Cond Inner Area"
    assert reloaded_group.rows[0].value_for("Cond Inner Area") == 2.25

    export_file = tmp_path / "mapping-review.json"
    export_result, _ = reloaded_service.export_snapshot(export_file)
    export_payload = json.loads(export_file.read_text(encoding="utf-8"))
    cond_group = next(
        item for item in export_payload["groups"] if item["key"] == "odu_cond_specs"
    )
    assert export_result.success
    assert cond_group["columns"][-1] == "Cond Inner Area"
    assert cond_group["rows"][0]["values"]["Cond Inner Area"] == 2.25


def test_dynamic_numeric_attribute_rejects_invalid_value(tmp_path):
    service = DataMappingService(
        RuntimeMappingCatalogProvider(str(_mapping_file(tmp_path))),
        RequirementProvider((_cond_inner_area_requirement(),)),
    )

    snapshot = service.edit_cell(
        "odu_cond_specs", 0, "Cond Inner Area", "not-a-number"
    )

    assert [issue.code for issue in snapshot.validation_errors] == ["invalid_number"]
    assert snapshot.validation_errors[0].field == "Cond Inner Area"


def _fan_requirement() -> MappingRequirement:
    return MappingRequirement(
        column_key="fan_diameter",
        ml_name="Fan_Diameter",
        mapping_entity="idu",
        mapping_attribute="Fan Diameter",
        trigger_column="idu",
    )


def _cond_inner_area_requirement() -> MappingRequirement:
    return extract_mapping_requirements(
        (
            DataDefinitionRow(
                column_key="cond_inner_area",
                label="Cond Inner Area",
                role="auto",
                value_source="mapping_lookup",
                mapping_entity="cond_specs",
                mapping_attribute="Cond Inner Area",
                trigger_column="odu",
                ml_name="Cond Inner Area",
                data_type="number",
                required=True,
            ),
        )
    )[0]


def _mapping_file(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text(
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
    return mapping_file
