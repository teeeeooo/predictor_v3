"""Train Data Mapping service foundation tests."""

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
    assert actions["save_mapping_json"].enabled
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
