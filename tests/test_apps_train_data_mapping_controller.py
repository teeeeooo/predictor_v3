"""Train Data Mapping controller foundation tests."""

from core.mapping.entity_model import (
    MappingAttributeDefinition,
    MappingEntityCatalog,
    MappingEntityDefinition,
    MappingEntityRow,
)
from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_mapping_service import (
    DataMappingService,
    FoundationMappingCatalogProvider,
    RuntimeMappingCatalogProvider,
)


class InvalidProvider:
    source_label = "invalid test provider"

    def load_catalog(self) -> MappingEntityCatalog:
        return MappingEntityCatalog(
            entities=(
                MappingEntityDefinition(
                    "fan_motor",
                    "Fan Motor",
                    "motor_code",
                    (
                        MappingAttributeDefinition("motor_code", "Motor Code"),
                        MappingAttributeDefinition(
                            "motor_efficiency",
                            "Motor Efficiency",
                            data_type="number",
                        ),
                    ),
                ),
            ),
            rows=(MappingEntityRow("fan_motor", "FM-A", {"motor_efficiency": "bad"}),),
        )


def test_data_mapping_controller_returns_entity_list_and_selected_details():
    controller = DataMappingController(DataMappingService(FoundationMappingCatalogProvider()))

    state = controller.refresh()

    assert state.status == "ready"
    assert state.selected_entity_key == "fan_motor"
    assert [entity.entity_key for entity in state.entities] == ["fan_motor", "evap_index"]
    assert state.entities[0].row_count == 2
    assert [attribute.attribute_key for attribute in state.attributes] == [
        "motor_code",
        "motor_efficiency",
        "enabled",
    ]
    assert state.value_headers == ("motor_efficiency", "enabled")
    assert state.values[0].row_key == "FM-A"
    assert state.values[0].values == ("0.82", "true")


def test_data_mapping_controller_selects_requested_entity():
    controller = DataMappingController(DataMappingService(FoundationMappingCatalogProvider()))

    state = controller.refresh("evap_index")

    assert state.selected_entity_key == "evap_index"
    assert [attribute.attribute_key for attribute in state.attributes] == [
        "evap_index",
        "Size",
        "Inner Surface Area",
    ]
    assert state.value_headers == ("Size", "Inner Surface Area")
    assert state.values[0].values == ("1", "8.2")


def test_data_mapping_controller_returns_validation_status_and_rows():
    controller = DataMappingController(DataMappingService(InvalidProvider()))

    state = controller.refresh()

    assert state.status == "error"
    assert state.validation_rows[0].code == "invalid_value_type"
    assert state.validation_rows[0].entity_key == "fan_motor"
    assert all(not action.enabled for action in state.actions)


def test_data_mapping_controller_preserves_runtime_source_on_load_failure(tmp_path):
    missing_mapping = tmp_path / "missing.json"
    controller = DataMappingController(
        DataMappingService(RuntimeMappingCatalogProvider(str(missing_mapping)))
    )

    state = controller.refresh()

    assert state.status == "error"
    assert state.source_label == f"File: {missing_mapping}"
    assert state.message == "Unable to load data."
    assert state.validation_rows[0].code == "load_failed"
    assert state.validation_rows[0].field == "source"
    assert str(missing_mapping) in state.validation_rows[0].message
