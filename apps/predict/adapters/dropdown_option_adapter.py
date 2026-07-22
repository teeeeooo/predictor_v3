"""Dropdown option provider boundary for Predict table editors."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from apps.predict.mapping.mapping_repository import PredictMappingRepository
from apps.predict.schema.case_table_schema_adapter import UnifiedCaseColumn
from core.data_definition.one_hot import OneHotRuntimeSnapshot


@dataclass(frozen=True)
class MappingResourceStatus:
    """Qt-free mapping resource status for Predict UI display."""

    mapping_path: str
    status: str
    message: str = ""


class DropdownOptionAdapter:
    """Resolve base and row-specific dropdown options outside QWidget code."""

    def __init__(
        self,
        mapping_repository: PredictMappingRepository,
        columns: Sequence[UnifiedCaseColumn],
        one_hot_snapshot: OneHotRuntimeSnapshot | None = None,
    ) -> None:
        self._mapping_repository = mapping_repository
        self._columns_by_key = {column.key: column for column in columns}
        self._one_hot_groups_by_selector = {
            group.selector_column_key: group
            for group in (one_hot_snapshot.groups if one_hot_snapshot else ())
        }
        self._one_hot_mapping_bindings = tuple(
            group.source_binding
            for group in self._one_hot_groups_by_selector.values()
            if group.source_mode == "mapping_backed"
        )

    def options_for_key(
        self,
        key: str,
        row_options: tuple[str, ...] | None = None,
    ) -> tuple[str, ...]:
        """Return row-specific options when present, otherwise base options."""
        if row_options is not None:
            return row_options
        return self.base_options_for_key(key)

    def base_options_for_key(self, key: str) -> tuple[str, ...]:
        """Return mapping-backed base options for a dropdown key."""
        column = self._columns_by_key.get(key)
        if column is None:
            return ()
        one_hot_group = self._one_hot_groups_by_selector.get(key)
        if one_hot_group is not None:
            if one_hot_group.source_mode in {"static", "external"}:
                return tuple(item.source_value for item in one_hot_group.categories)
            if one_hot_group.source_mode == "mapping_backed":
                section_name = one_hot_group.source_binding
            else:
                return ()
        else:
            section_name = column.dropdown_target or column.mapping
        if not section_name:
            return ()
        section = self._mapping_section(section_name)
        if not isinstance(section, dict):
            return ()
        return tuple(sorted(str(option) for option in section.keys()))

    def mapping_status(self) -> MappingResourceStatus:
        """Return mapping file/cache status without exposing raw checks to widgets."""
        mapping_path = getattr(self._mapping_repository, "mapping_file", "")
        if mapping_path and not Path(mapping_path).exists():
            return MappingResourceStatus(
                mapping_path=str(mapping_path),
                status="missing",
                message="Mapping file is missing.",
            )
        cached_mapping = getattr(self._mapping_repository, "_mapping_data", None)
        if cached_mapping is not None and not isinstance(cached_mapping, dict):
            return MappingResourceStatus(
                mapping_path=str(mapping_path),
                status="invalid",
                message="Mapping data shape is invalid.",
            )
        if cached_mapping is not None:
            missing_bindings = tuple(
                binding for binding in self._one_hot_mapping_bindings
                if not isinstance(cached_mapping.get(binding), dict)
            )
            if missing_bindings:
                return MappingResourceStatus(
                    mapping_path=str(mapping_path),
                    status="invalid",
                    message=(
                        "One-hot Mapping source section is missing: "
                        + ", ".join(missing_bindings)
                        + ". Refresh or restore mapping.json before Predict input."
                    ),
                )
            return MappingResourceStatus(
                mapping_path=str(mapping_path),
                status="loaded",
                message="Mapping data is loaded.",
            )
        if mapping_path and Path(mapping_path).exists():
            return MappingResourceStatus(
                mapping_path=str(mapping_path),
                status="exists",
                message="Mapping file exists.",
            )
        return MappingResourceStatus(mapping_path="", status="missing", message="")

    def _mapping_section(self, section_name: str) -> object:
        mapping_data = self._mapping_repository.load()
        if not isinstance(mapping_data, dict):
            return {}
        return mapping_data.get(section_name, {})
