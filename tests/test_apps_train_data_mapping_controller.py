"""Train Data Mapping controller foundation tests."""

from pathlib import Path

from apps.train.controllers.data_mapping_controller import (
    DataMappingController,
    _exception_summary,
    _display_source_label,
)
from apps.train.services.data_mapping_service import (
    DataMappingService,
    FoundationMappingCatalogProvider,
    RuntimeMappingCatalogProvider,
)
from core.mapping.editor_projection import project_runtime_mapping_to_editor_draft


RUNTIME_FIXTURE = Path("tests/fixtures/mapping/mapping_runtime_equivalent.json")


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
    assert saved.message.startswith(f"Saved mapping JSON to {mapping_file}.")
    assert "Backup:" in saved.message


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


def test_data_mapping_controller_exports_xlsx_snapshot(tmp_path):
    controller = DataMappingController(DataMappingService(FoundationMappingCatalogProvider()))
    export_file = tmp_path / "snapshot.xlsx"

    state = controller.export_xlsx(export_file)

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

    state = controller.export_snapshot(tmp_path / "snapshot.xlsx", "xlsx")

    assert state.message == "Exported."
    assert state.dirty


def test_data_mapping_controller_distinguishes_missing_runtime_source(tmp_path):
    missing_mapping = tmp_path / "missing.json"
    controller = DataMappingController(
        DataMappingService(RuntimeMappingCatalogProvider(str(missing_mapping)))
    )

    state = controller.refresh()

    assert state.status == "missing"
    assert state.resource_status == "missing"
    assert state.source_label == f"File: {missing_mapping}"
    assert state.message == "Mapping resource not found."
    assert state.validation_rows[0].code == "resource_missing"
    assert state.validation_rows[0].field == "source"
    assert [action.key for action in state.actions] == ["reload_runtime"]


def test_data_mapping_controller_distinguishes_existing_source_load_error(tmp_path):
    malformed_mapping = tmp_path / "mapping.json"
    malformed_mapping.write_text("{not-json", encoding="utf-8")
    controller = DataMappingController(
        DataMappingService(RuntimeMappingCatalogProvider(str(malformed_mapping)))
    )

    state = controller.refresh()

    assert state.status == "error"
    assert state.resource_status == "load-error"
    assert state.source_label == f"File: {malformed_mapping}"
    assert state.message == "Unable to load mapping data."
    assert state.validation_rows[0].code == "load_failed"
    assert [action.key for action in state.actions] == ["reload_runtime"]


def test_data_mapping_controller_preserves_selection_across_non_destructive_updates(tmp_path):
    controller = DataMappingController(DataMappingService(FoundationMappingCatalogProvider()))
    controller.edit_cell("odu_cond_specs", 0, "Cond Area", "4.25")

    refreshed = controller.refresh("odu_cond_specs")
    exported = controller.export_snapshot(
        tmp_path / "snapshot.json",
        "json",
        "odu_cond_specs",
    )

    assert refreshed.selected_group_key == "odu_cond_specs"
    assert refreshed.dirty
    assert refreshed.values[0].values[-2:] == ("4.25", "4.5")
    assert exported.selected_group_key == "odu_cond_specs"
    assert exported.dirty


def test_failed_reload_keeps_service_owned_draft_available():
    class FlakyProvider:
        source_label = "Flaky fixture"

        def __init__(self):
            self.fail = False

        def load_draft(self):
            if self.fail:
                raise ValueError("fixture became unreadable")
            return project_runtime_mapping_to_editor_draft(
                {
                    "idu": {"IDU-A": {"ID Volume": 1.25}},
                    "ref_type": {"R32": {}},
                    "exp_type": {"EEV": {}},
                },
                source_label=self.source_label,
            )

    provider = FlakyProvider()
    controller = DataMappingController(DataMappingService(provider))
    controller.edit_cell("idu", 0, "ID Volume", "2.5")
    provider.fail = True

    failed = controller.reload("idu")
    recovered = controller.refresh("idu")

    assert failed.resource_status == "available"
    assert failed.message == "Reload failed. Current draft preserved."
    assert recovered.selected_group_key == "idu"
    assert recovered.values[0].values[1] == "2.5"
    assert recovered.dirty


def test_dirty_runtime_draft_survives_source_delete_refresh_and_failed_reload(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    original = RUNTIME_FIXTURE.read_bytes()
    mapping_file.write_bytes(original)
    controller = DataMappingController(
        DataMappingService(RuntimeMappingCatalogProvider(str(mapping_file)))
    )
    controller.refresh("idu")
    controller.edit_cell("idu", 0, "ID Volume", "99.5")
    mapping_file.unlink()

    refreshed = controller.refresh("idu")
    failed_reload = controller.reload("idu")

    assert refreshed.selected_group_key == "idu"
    assert refreshed.values[0].values[1] == "99.5"
    assert refreshed.dirty
    assert refreshed.resource_status == "missing"
    assert refreshed.status == "warning"
    assert refreshed.message == "Unsaved changes. Source missing."
    assert refreshed.validation_rows[-1].severity == "warning"
    actions = {action.key: action for action in refreshed.actions}
    assert actions["save_mapping_json"].enabled
    assert actions["reload_runtime"].enabled

    assert failed_reload.selected_group_key == "idu"
    assert failed_reload.values[0].values[1] == "99.5"
    assert failed_reload.dirty
    assert failed_reload.resource_status == "missing"
    assert failed_reload.message == "Reload failed. Current draft preserved."
    assert failed_reload.validation_rows[-1].code == "reload_failed"

    mapping_file.write_bytes(original)
    restored = controller.reload("idu")
    assert restored.resource_status == "exists"
    assert not restored.dirty
    assert restored.values[0].values[1] != "99.5"


def test_refresh_uses_cached_draft_while_reload_reads_provider_again():
    class CountingProvider:
        source_label = "Counting fixture"

        def __init__(self):
            self.load_calls = 0

        def load_draft(self):
            self.load_calls += 1
            return project_runtime_mapping_to_editor_draft(
                {
                    "idu": {"IDU-A": {"ID Volume": self.load_calls}},
                    "ref_type": {"R32": {}},
                    "exp_type": {"EEV": {}},
                },
                source_label=self.source_label,
            )

    provider = CountingProvider()
    controller = DataMappingController(DataMappingService(provider))

    initial = controller.refresh("idu")
    refreshed = controller.refresh("idu")
    reloaded = controller.reload("idu")

    assert initial.values[0].values[1] == "1"
    assert refreshed.values[0].values[1] == "1"
    assert reloaded.values[0].values[1] == "2"
    assert provider.load_calls == 2


def test_initial_empty_message_exception_becomes_stable_load_error():
    class EmptyErrorProvider:
        source_label = "Empty error fixture"

        def load_draft(self):
            raise ValueError()

    state = DataMappingController(DataMappingService(EmptyErrorProvider())).refresh()

    assert state.resource_status == "load-error"
    assert state.message == "Unable to load mapping data."
    assert state.validation_rows[0].message == "ValueError"


def test_reload_empty_message_exception_preserves_cached_draft():
    class EmptyReloadErrorProvider:
        source_label = "Empty reload error fixture"

        def __init__(self):
            self.fail = False

        def load_draft(self):
            if self.fail:
                raise OSError()
            return project_runtime_mapping_to_editor_draft(
                {
                    "idu": {"IDU-A": {"ID Volume": 1.25}},
                    "ref_type": {"R32": {}},
                    "exp_type": {"EEV": {}},
                },
                source_label=self.source_label,
            )

    provider = EmptyReloadErrorProvider()
    controller = DataMappingController(DataMappingService(provider))
    controller.refresh("idu")
    provider.fail = True

    state = controller.reload("idu")

    assert state.values[0].values[1] == "1.25"
    assert state.message == "Reload failed. Current draft preserved."
    assert state.validation_rows[-1].message == "Reload failed: OSError"


def test_exception_summary_uses_first_non_empty_line_and_class_fallback():
    assert _exception_summary(ValueError("\n useful detail\nsecond")) == "useful detail"
    assert _exception_summary(ValueError()) == "ValueError"


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
