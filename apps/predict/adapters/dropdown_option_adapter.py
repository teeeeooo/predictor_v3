"""Dropdown option provider boundary for Predict table editors."""

from __future__ import annotations

from collections.abc import Sequence

from apps.predict.mapping.mapping_repository import PredictMappingRepository
from apps.predict.schema.case_table_schema_adapter import UnifiedCaseColumn


FALLBACK_DROPDOWN_OPTIONS = {
    "ref_type": ("R410A", "R32", "R290"),
    "exp_type": ("EEV", "Capi"),
}


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

    def _mapping_section(self, section_name: str) -> object:
        mapping_data = self._mapping_repository.load()
        if not isinstance(mapping_data, dict):
            return {}
        return mapping_data.get(section_name, {})
