"""Train Data Mapping dynamic requirement integration tests."""

from __future__ import annotations

import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_mapping_service import DataMappingService, RuntimeMappingCatalogProvider
from apps.train.ui.data_mapping_panel import DataMappingPanel
from core.data_definition.model import MappingRequirement


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


def _fan_requirement() -> MappingRequirement:
    return MappingRequirement(
        column_key="fan_diameter",
        ml_name="Fan_Diameter",
        mapping_entity="idu",
        mapping_attribute="Fan Diameter",
        trigger_column="idu",
    )


def _mapping_file(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text(
        json.dumps(
            {
                "idu": {"IDU-A": {"ID Volume": 1.25}},
                "ref_type": {"R32": {}},
                "exp_type": {"EEV": {}},
            }
        ),
        encoding="utf-8",
    )
    return mapping_file
