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


def test_data_mapping_controller_edit_commands_return_dirty_issue_state():
    controller = DataMappingController(DataMappingService(FoundationMappingCatalogProvider()))

    state = controller.edit_cell("idu", 0, "ID Volume", "bad")

    assert state.dirty
    assert state.status == "error"
    assert state.message == "Issues found."
    assert state.validation_rows[0].code == "invalid_number"


def test_data_mapping_controller_add_duplicate_delete_rows():
    controller = DataMappingController(DataMappingService(FoundationMappingCatalogProvider()))

    added = controller.add_row("idu")
    duplicated = controller.duplicate_row("idu", 0)
    deleted = controller.delete_row("idu", 1)

    assert added.dirty
    assert len(added.values) == 2
    assert len(duplicated.values) == 3
    assert len(deleted.values) == 2


def test_data_mapping_controller_save_clears_dirty_for_runtime_provider(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text(
        """
        {
            "idu": {"IDU-A": {"ID Volume": 1.25}},
            "evap_index": {"EVAP-A": {"Evap Area": 8.2, "Evap Volume": 2.1}},
            "odu": {"ODU-A": {"OD Volume": 2.5}},
            "compressor": {"CMP-A": {"Comp EER": 3.2, "Comp cc": 11}},
            "ref_type": {"R32": {}},
            "exp_type": {"EEV": {}},
            "odu_cascade": {
                "ODU-A": {
                    "Available_Fins": ["F&T"],
                    "Available_Pis": ["7"],
                    "Available_Rows": ["1"]
                }
            },
            "cond_specs": {
                "ODU-A F&T 7 1": {"Cond Area": 3.5, "Cond Volume": 4.5}
            }
        }
        """,
        encoding="utf-8",
    )
    controller = DataMappingController(
        DataMappingService(RuntimeMappingCatalogProvider(str(mapping_file)))
    )

    dirty = controller.edit_cell("idu", 0, "ID Volume", "2.5")
    saved = controller.save()

    assert dirty.dirty
    assert not saved.dirty
    assert saved.message == "Saved."


def test_data_mapping_controller_save_failure_surfaces_issue():
    controller = DataMappingController(DataMappingService(FoundationMappingCatalogProvider()))

    state = controller.save()

    assert state.status == "error"
    assert state.message == "Save failed."
    assert state.validation_rows[-1].entity_key == "Save"
    assert state.validation_rows[-1].message == "No writable mapping file is configured."


def test_data_mapping_controller_exports_json_snapshot(tmp_path):
    controller = DataMappingController(DataMappingService(FoundationMappingCatalogProvider()))
    export_file = tmp_path / "snapshot.json"

    state = controller.export_json(export_file)

    assert export_file.exists()
    assert state.message == "Exported."
    assert not state.dirty


def test_data_mapping_controller_export_failure_surfaces_issue(tmp_path):
    controller = DataMappingController(DataMappingService(FoundationMappingCatalogProvider()))
    destination = tmp_path / "already-a-directory"
    destination.mkdir()

    state = controller.export_json(destination)

    assert state.status == "error"
    assert state.message == "Export failed."
    assert state.validation_rows[-1].entity_key == "Export"
    assert "Export failed:" in state.validation_rows[-1].message


def test_data_mapping_controller_export_keeps_dirty_state(tmp_path):
    controller = DataMappingController(DataMappingService(FoundationMappingCatalogProvider()))
    controller.edit_cell("idu", 0, "ID Volume", "2.5")

    state = controller.export_json(tmp_path / "snapshot.json")

    assert state.message == "Exported."
    assert state.dirty


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
