"""Train Data Mapping service foundation tests."""

from core.mapping.entity_model import (
    MappingAttributeDefinition,
    MappingEntityCatalog,
    MappingEntityDefinition,
    MappingEntityRow,
)
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
                    (MappingAttributeDefinition("motor_code", "Motor Code"),),
                ),
            ),
            rows=(
                MappingEntityRow("fan_motor", "FM-A", {}),
                MappingEntityRow("fan_motor", "FM-A", {}),
            ),
        )


def test_data_mapping_service_returns_catalog_validation_and_disabled_actions():
    snapshot = DataMappingService(FoundationMappingCatalogProvider()).load_snapshot()

    assert snapshot.source_label == "Foundation sample provider for UI wiring tests only"
    assert snapshot.catalog.entity_definition("fan_motor") is not None
    assert snapshot.catalog.entity_definition("evap_index") is not None
    assert snapshot.is_valid
    assert snapshot.validation_errors == ()
    assert snapshot.actions
    assert all(not action.enabled for action in snapshot.actions)
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
    assert {action.reason for action in snapshot.actions} == {"Read-only mode."}


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
            "odu_cascade": {
                "ODU-A": {
                    "Available_Fins": ["F&T"],
                    "Available_Pis": ["7"],
                    "Available_Rows": ["1"]
                }
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
    assert snapshot.catalog.entity_definition("idu") is not None
    assert snapshot.catalog.value_for("idu", "IDU-A", "ID Volume") == 1.25


def test_data_mapping_service_returns_validation_errors_from_provider_catalog():
    snapshot = DataMappingService(InvalidProvider()).load_snapshot()

    assert not snapshot.is_valid
    assert [error.code for error in snapshot.validation_errors] == ["duplicate_row_key"]
