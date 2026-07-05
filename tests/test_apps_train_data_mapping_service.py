"""Train Data Mapping service foundation tests."""

import json

from apps.train.services.data_mapping_service import (
    DataMappingService,
    FoundationMappingCatalogProvider,
    RuntimeMappingCatalogProvider,
)
from core.mapping.editor_projection import project_runtime_mapping_to_editor_draft


def test_data_mapping_service_returns_catalog_validation_and_disabled_actions():
    snapshot = DataMappingService(FoundationMappingCatalogProvider()).load_snapshot()

    assert snapshot.source_label == "Foundation sample provider for UI wiring tests only"
    assert snapshot.draft.group("idu") is not None
    assert snapshot.draft.group("odu_cond_specs") is not None
    assert snapshot.is_valid
    assert snapshot.validation_errors == ()
    assert snapshot.actions
    assert {action.key for action in snapshot.actions} == {
        "import_csv_v2",
        "export_csv_v2",
        "save_mapping_json",
        "reload_runtime",
    }
    assert [action.label for action in snapshot.actions] == [
        "Import",
        "Export",
        "Save",
        "Reload",
    ]
    actions = {action.key: action for action in snapshot.actions}
    assert not actions["save_mapping_json"].enabled
    assert actions["save_mapping_json"].reason == "No writable mapping file is configured."
    assert actions["import_csv_v2"].reason == "Read-only mode."


def test_data_mapping_service_disables_save_when_draft_has_issues():
    class InvalidDraftProvider:
        source_label = "invalid draft"

        def load_draft(self):
            return project_runtime_mapping_to_editor_draft(
                {
                    "idu": {"IDU-A": {"ID Volume": 1.25}},
                    "evap_index": {},
                    "odu": {},
                    "compressor": {},
                    "exp_type": {"EEV": {}},
                }
            )

    snapshot = DataMappingService(InvalidDraftProvider()).load_snapshot()
    actions = {action.key: action for action in snapshot.actions}

    assert not snapshot.is_valid
    assert [issue.code for issue in snapshot.validation_errors] == [
        "required_section_missing"
    ]
    assert not actions["save_mapping_json"].enabled


def test_data_mapping_service_edit_commands_set_dirty_and_rerun_validation():
    service = DataMappingService(FoundationMappingCatalogProvider())

    initial = service.load_snapshot()
    edited = service.edit_cell("idu", 0, "IDU", "")

    assert not initial.dirty
    assert edited.dirty
    assert not edited.is_valid
    assert [issue.code for issue in edited.validation_errors] == ["blank_key"]

    reloaded = service.reload_snapshot()
    assert not reloaded.dirty
    assert reloaded.is_valid


def test_data_mapping_service_saves_runtime_mapping_and_clears_dirty(tmp_path):
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
            },
            "vendor_notes": {"keep": true}
        }
        """,
        encoding="utf-8",
    )
    service = DataMappingService(RuntimeMappingCatalogProvider(str(mapping_file)))
    service.edit_cell("idu", 0, "ID Volume", "2.5")

    result, snapshot = service.save_mapping()

    saved = json.loads(mapping_file.read_text(encoding="utf-8"))
    assert result.success
    assert result.backup_path is not None
    assert saved["idu"]["IDU-A"]["ID Volume"] == 2.5
    assert saved["vendor_notes"] == {"keep": True}
    assert not snapshot.dirty


def test_data_mapping_service_add_duplicate_delete_rows():
    service = DataMappingService(FoundationMappingCatalogProvider())

    added = service.add_row("idu")
    assert added.dirty
    assert len(added.draft.group("idu").rows) == 2

    duplicated = service.duplicate_row("idu", 0)
    assert len(duplicated.draft.group("idu").rows) == 3
    assert "duplicate_key" in [issue.code for issue in duplicated.validation_errors]

    deleted = service.delete_row("idu", 1)
    assert len(deleted.draft.group("idu").rows) == 2


def test_data_mapping_service_default_uses_runtime_provider():
    service = DataMappingService()

    assert isinstance(service._provider, RuntimeMappingCatalogProvider)
    assert service.source_label.startswith("Runtime mapping repository:")


def test_runtime_mapping_provider_loads_temp_mapping_json(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text(
        """
        {
            "idu": {"IDU-A": {"ID Volume": 1.25}},
            "evap_index": {},
            "odu": {"ODU-A": {"OD Volume": 2.5}},
            "compressor": {},
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

    snapshot = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_file))
    ).load_snapshot()

    assert snapshot.is_valid
    assert "Runtime mapping repository:" in snapshot.source_label
    idu = snapshot.draft.group("idu")
    assert idu is not None
    assert idu.rows[0].value_for("ID Volume") == 1.25
