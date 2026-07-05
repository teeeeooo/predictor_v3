"""Train Data Mapping controller foundation tests."""

from apps.train.controllers.data_mapping_controller import (
    DataMappingController,
    _display_source_label,
)
from apps.train.services.data_mapping_service import (
    DataMappingService,
    FoundationMappingCatalogProvider,
    RuntimeMappingCatalogProvider,
)


def test_data_mapping_controller_returns_entity_list_and_selected_details():
    controller = DataMappingController(DataMappingService(FoundationMappingCatalogProvider()))

    state = controller.refresh()

    assert state.status == "ready"
    assert state.selected_group_key == "idu"
    assert [entity.label for entity in state.entities] == [
        "IDU",
        "Evap Index",
        "ODU",
        "Compressor",
        "Refrigerant",
        "Expansion",
        "ODU Cond Specs",
    ]
    assert state.entities[0].row_count == 1
    assert [attribute.attribute_key for attribute in state.attributes] == [
        "IDU",
        "ID Volume",
        "Size",
    ]
    assert state.value_headers == ("IDU", "ID Volume", "Size")
    assert state.values[0].row_key == "IDU-A"
    assert state.values[0].values == ("IDU-A", "1.25", "S1")


def test_data_mapping_controller_selects_requested_entity():
    controller = DataMappingController(DataMappingService(FoundationMappingCatalogProvider()))

    state = controller.refresh("evap_index")

    assert state.selected_group_key == "evap_index"
    assert [attribute.attribute_key for attribute in state.attributes] == [
        "Evap Index",
        "Size",
        "Evap Area",
        "Evap Volume",
    ]
    assert state.value_headers == ("Evap Index", "Size", "Evap Area", "Evap Volume")
    assert state.values[0].values == ("EVAP-A", "S1", "8.2", "2.1")


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


def test_source_display_only_removes_known_runtime_prefix():
    assert (
        _display_source_label("Runtime mapping repository: /tmp/mapping.json")
        == "File: /tmp/mapping.json"
    )
    assert _display_source_label(r"C:\data\mapping.json") == r"File: C:\data\mapping.json"
    assert (
        _display_source_label("Vendor source: C:/data/mapping.json")
        == "File: Vendor source: C:/data/mapping.json"
    )
