"""Train Data Mapping service foundation tests."""

import json
from pathlib import Path

from openpyxl import load_workbook

from apps.train.services.data_mapping_service import (
    DataMappingService,
    FoundationMappingCatalogProvider,
    RuntimeMappingCatalogProvider,
)
from core.mapping.editor_projection import project_runtime_mapping_to_editor_draft


RUNTIME_FIXTURE = Path("tests/fixtures/mapping/mapping_runtime_equivalent.json")


def test_data_mapping_service_returns_catalog_validation_and_current_actions():
    snapshot = DataMappingService(FoundationMappingCatalogProvider()).load_snapshot()

    assert snapshot.source_label == "Foundation sample provider for UI wiring tests only"
    assert snapshot.draft.group("idu") is not None
    assert snapshot.draft.group("odu_cond_specs") is not None
    assert snapshot.is_valid
    assert snapshot.validation_errors == ()
    assert snapshot.actions
    assert {action.key for action in snapshot.actions} == {
        "export_csv_v2",
        "export_mapping_exchange",
        "save_mapping_json",
        "reload_runtime",
    }
    assert [action.label for action in snapshot.actions] == [
        "Export",
        "Mapping Exchange Package",
        "Save",
        "Reload",
    ]
    actions = {action.key: action for action in snapshot.actions}
    assert not actions["save_mapping_json"].enabled
    assert actions["save_mapping_json"].reason == "No writable mapping file is configured."
    assert "read-only review snapshot" in actions["export_csv_v2"].reason
    assert actions["export_mapping_exchange"].enabled


def test_runtime_fixture_loads_all_populated_mapping_groups():
    snapshot = DataMappingService(
        RuntimeMappingCatalogProvider(str(RUNTIME_FIXTURE))
    ).load_snapshot()

    assert snapshot.is_valid
    assert len(snapshot.draft.groups) == 7
    assert {group.group_key: len(group.rows) for group in snapshot.draft.groups} == {
        "idu": 9,
        "evap_index": 13,
        "odu": 5,
        "compressor": 3,
        "refrigerant": 2,
        "expansion": 2,
        "odu_cond_specs": 22,
    }
    assert all(not row.unresolved for group in snapshot.draft.groups for row in group.rows)


def test_data_mapping_service_reports_resource_status_without_view_path_checks(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    service = DataMappingService(RuntimeMappingCatalogProvider(str(mapping_file)))

    assert service.resource_status() == "missing"

    mapping_file.write_text("{}", encoding="utf-8")
    assert service.resource_status() == "exists"
    assert DataMappingService(FoundationMappingCatalogProvider()).resource_status() == "available"


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


def test_current_snapshot_returns_cached_draft_without_provider_reload():
    class CountingProvider(FoundationMappingCatalogProvider):
        def __init__(self):
            self.load_calls = 0

        def load_draft(self):
            self.load_calls += 1
            return super().load_draft()

    provider = CountingProvider()
    service = DataMappingService(provider)

    assert service.current_snapshot() is None
    loaded = service.load_snapshot()
    cached = service.current_snapshot()

    assert loaded.draft == cached.draft
    assert provider.load_calls == 1


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


def test_data_mapping_service_exports_dirty_draft_without_modifying_mapping_json(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text(
        """
        {
            "idu": {"IDU-A": {"ID Volume": 1.25}},
            "evap_index": {},
            "odu": {},
            "compressor": {},
            "ref_type": {"R32": {}},
            "exp_type": {"EEV": {}}
        }
        """,
        encoding="utf-8",
    )
    service = DataMappingService(RuntimeMappingCatalogProvider(str(mapping_file)))
    service.edit_cell("idu", 0, "IDU", "IDU-DRAFT")
    export_file = tmp_path / "snapshot.json"

    result, snapshot = service.export_snapshot(export_file)

    payload = json.loads(export_file.read_text(encoding="utf-8"))
    saved = json.loads(mapping_file.read_text(encoding="utf-8"))
    assert result.success
    assert snapshot.dirty
    assert payload["groups"][0]["rows"][0]["values"]["IDU"] == "IDU-DRAFT"
    assert saved["idu"] == {"IDU-A": {"ID Volume": 1.25}}


def test_data_mapping_service_exports_xlsx_dirty_draft_without_modifying_mapping_json(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text(
        """
        {
            "idu": {"IDU-A": {"ID Volume": 1.25}},
            "evap_index": {},
            "odu": {},
            "compressor": {},
            "ref_type": {"R32": {}},
            "exp_type": {"EEV": {}}
        }
        """,
        encoding="utf-8",
    )
    service = DataMappingService(RuntimeMappingCatalogProvider(str(mapping_file)))
    service.edit_cell("idu", 0, "IDU", "IDU-DRAFT")
    export_file = tmp_path / "snapshot.xlsx"

    result, snapshot = service.export_snapshot(export_file, "xlsx")

    workbook = load_workbook(export_file)
    saved = json.loads(mapping_file.read_text(encoding="utf-8"))
    assert result.success
    assert snapshot.dirty
    assert workbook["IDU"]["A2"].value == "IDU-DRAFT"
    assert saved["idu"] == {"IDU-A": {"ID Volume": 1.25}}


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
