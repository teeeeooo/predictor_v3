"""Dropdown option provider boundary for Predict table editors."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from apps.predict.mapping.mapping_repository import PredictMappingRepository
from apps.predict.schema.case_table_schema_adapter import UnifiedCaseColumn


FALLBACK_DROPDOWN_OPTIONS = {
    "ref_type": ("R410A", "R32", "R290"),
    "exp_type": ("EEV", "Capi"),
}


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
    ) -> None:
        self._mapping_repository = mapping_repository
        self._columns_by_key = {column.key: column for column in columns}

    def options_for_key(
        self,
        key: str,
        row_options: tuple[str, ...] = (),
    ) -> tuple[str, ...]:
        """Return row-specific options when present, otherwise base options."""
        if row_options:
            return row_options
        return self.base_options_for_key(key)

    def base_options_for_key(self, key: str) -> tuple[str, ...]:
        """Return fallback or mapping-backed base options for a dropdown key."""
        if key in FALLBACK_DROPDOWN_OPTIONS:
            return FALLBACK_DROPDOWN_OPTIONS[key]
        column = self._columns_by_key.get(key)
        if column is None:
            return ()
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
        if getattr(self._mapping_repository, "_mapping_data", None) is not None:
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
