"""Read-only Data Mapping service foundation for Train/Admin."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.mapping.entity_model import (
    MappingAttributeDefinition,
    MappingEntityCatalog,
    MappingEntityDefinition,
    MappingEntityRow,
    MappingValidationError,
)
from core.mapping.entity_runtime_adapter import (
    load_runtime_mapping_catalog,
    runtime_mapping_source_label,
)
from core.mapping.entity_validation import validate_mapping_entity_catalog


@dataclass(frozen=True)
class DataMappingAction:
    """Read-only action metadata for future Data Mapping workflows."""

    key: str
    label: str
    enabled: bool
    reason: str


@dataclass(frozen=True)
class DataMappingSnapshot:
    """Service snapshot for the read-only Data Mapping foundation."""

    catalog: MappingEntityCatalog
    validation_errors: tuple[MappingValidationError, ...]
    source_label: str
    actions: tuple[DataMappingAction, ...]

    @property
    def is_valid(self) -> bool:
        """Return whether the mapping entity catalog has no validation errors."""
        return not self.validation_errors


class MappingCatalogProvider(Protocol):
    """Read-only provider interface for future mapping data adapters."""

    def load_catalog(self) -> MappingEntityCatalog:
        """Return a mapping entity catalog."""
        ...

    @property
    def source_label(self) -> str:
        """Return a display label describing the provider source."""
        ...


class FoundationMappingCatalogProvider:
    """Small sample provider for UI wiring tests only.

    It is not a production data source and does not read or write mapping.json.
    """

    source_label = "Foundation sample provider for UI wiring tests only"

    def load_catalog(self) -> MappingEntityCatalog:
        """Return a small valid catalog used by the read-only foundation UI."""
        return MappingEntityCatalog(
            entities=(
                MappingEntityDefinition(
                    entity_key="fan_motor",
                    label="Fan Motor",
                    key_attribute="motor_code",
                    attributes=(
                        MappingAttributeDefinition("motor_code", "Motor Code"),
                        MappingAttributeDefinition(
                            "motor_efficiency",
                            "Motor Efficiency",
                            data_type="number",
                            required=True,
                        ),
                        MappingAttributeDefinition(
                            "enabled",
                            "Enabled",
                            data_type="boolean",
                        ),
                    ),
                    notes="Generic future entity example.",
                ),
                MappingEntityDefinition(
                    entity_key="evap_index",
                    label="Evap Index",
                    key_attribute="evap_index",
                    attributes=(
                        MappingAttributeDefinition("evap_index", "Evap Index"),
                        MappingAttributeDefinition("Size", "Size", data_type="number"),
                        MappingAttributeDefinition(
                            "Inner Surface Area",
                            "Inner Surface Area",
                            data_type="number",
                            active=False,
                            notes="Inactive example attribute.",
                        ),
                    ),
                    notes="Existing mapping entity with future attribute example.",
                ),
            ),
            rows=(
                MappingEntityRow(
                    "fan_motor",
                    "FM-A",
                    {"motor_efficiency": 0.82, "enabled": True},
                ),
                MappingEntityRow(
                    "fan_motor",
                    "FM-B",
                    {"motor_efficiency": 0.86, "enabled": False},
                    active=False,
                    notes="Inactive row example.",
                ),
                MappingEntityRow(
                    "evap_index",
                    "S1-2",
                    {"Size": 1, "Inner Surface Area": 8.2},
                ),
            ),
            notes="Read-only UI foundation catalog.",
        )


class RuntimeMappingCatalogProvider:
    """Read-only provider backed by the existing runtime mapping repository."""

    def __init__(self, mapping_file: str | None = None) -> None:
        self._mapping_file = mapping_file

    @property
    def source_label(self) -> str:
        """Return the runtime mapping source displayed by the UI."""
        return runtime_mapping_source_label(self._mapping_file)

    def load_catalog(self) -> MappingEntityCatalog:
        """Return the current runtime mapping data as a read-only catalog."""
        return load_runtime_mapping_catalog(self._mapping_file)


class DataMappingService:
    """Provide read-only Mapping Entity catalog snapshots for Train/Admin UI."""

    def __init__(self, provider: MappingCatalogProvider | None = None) -> None:
        self._provider = provider or RuntimeMappingCatalogProvider()

    @property
    def source_label(self) -> str:
        """Return the configured provider source label before loading."""
        return self._provider.source_label

    def load_snapshot(self) -> DataMappingSnapshot:
        """Return catalog data, validation result, and disabled future actions."""
        catalog = self._provider.load_catalog()
        return DataMappingSnapshot(
            catalog=catalog,
            validation_errors=validate_mapping_entity_catalog(catalog),
            source_label=self.source_label,
            actions=_future_actions(),
        )


def _future_actions() -> tuple[DataMappingAction, ...]:
    disabled_reason = "Read-only mode."
    return (
        DataMappingAction("import_csv_v2", "Import", False, disabled_reason),
        DataMappingAction("export_csv_v2", "Export", False, disabled_reason),
        DataMappingAction("save_mapping_json", "Save", False, disabled_reason),
        DataMappingAction("reload_runtime", "Reload", False, disabled_reason),
    )
