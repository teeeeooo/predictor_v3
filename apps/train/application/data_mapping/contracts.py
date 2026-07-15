"""Stable Qt-free contracts for Data Mapping coverage and navigation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataMappingCellTarget:
    """Stable mapping-cell identity without a widget or table row index."""

    group_key: str
    row_key: str
    attribute_key: str
    row_occurrence: int = 0


@dataclass(frozen=True)
class DataMappingIssueTarget:
    """Issue target with stable identity plus presentation-local index hints."""

    group_key: str
    row_key: str = ""
    attribute_key: str = ""
    row_index: int | None = None
    column_index: int | None = None


@dataclass(frozen=True)
class DataMappingNavigationRequest:
    """One saved Data Definition requirement handoff to Data Mapping."""

    definition_identity: tuple[str, str]
    definition_column_key: str
    definition_label: str
    mapping_entity: str
    mapping_attribute: str
    resolved_group_key: str
    required: bool
    data_type: str
    prefer_unresolved: bool = True
    unresolved_row_key: str = ""
    unresolved_row_occurrence: int = 0
    saved: bool = True


@dataclass(frozen=True)
class DataMappingNavigationResult:
    """Deterministic result of opening one Data Mapping handoff."""

    status: str
    message: str
    request: DataMappingNavigationRequest
    target: DataMappingCellTarget | None = None

    @property
    def opened(self) -> bool:
        """Return whether the requested group and attribute were opened."""
        return self.status in {"opened", "opened_unresolved", "coverage_ready"}


@dataclass(frozen=True)
class DataMappingCoverageItem:
    """Coverage for one definition-owned mapping attribute."""

    definition_column_key: str
    mapping_group_key: str
    mapping_entity: str
    mapping_attribute: str
    required: bool
    data_type: str
    total_rows: int
    ready_rows: int
    missing_rows: int
    invalid_rows: int
    unresolved_targets: tuple[DataMappingCellTarget, ...]
    status: str
    summary: str

    @property
    def first_unresolved(self) -> DataMappingCellTarget | None:
        """Return the first canonical unresolved target, if any."""
        return self.unresolved_targets[0] if self.unresolved_targets else None
