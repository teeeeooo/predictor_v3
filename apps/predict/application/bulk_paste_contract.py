"""Immutable contracts for the Predict bulk-paste application boundary."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BulkPasteDestination:
    """Stable input identity and selected-range shape for one paste."""

    start_row: int
    start_feature_identity: str
    selected_rows: int = 1
    selected_columns: int = 1


@dataclass(frozen=True)
class BulkPasteIssue:
    """One precise canonical input issue produced from the final row state."""

    case_id: str
    column_key: str
    code: str
    message: str


@dataclass(frozen=True)
class BulkPasteOutcome:
    """Aggregate result for one attempted bulk paste or compound undo."""

    applied: bool
    pasted_cells: int = 0
    derived_cells: int = 0
    expanded_rows: int = 0
    affected_case_ids: tuple[str, ...] = ()
    issues: tuple[BulkPasteIssue, ...] = ()
    undo_id: str = ""
    truncated_cells: int = 0
    message: str = ""


@dataclass(frozen=True)
class StagedBulkPasteIssue:
    """Row-indexed issue before canonical case identities are committed."""

    row_index: int
    column_key: str
    code: str
    message: str


__all__ = [
    "BulkPasteDestination",
    "BulkPasteIssue",
    "BulkPasteOutcome",
    "StagedBulkPasteIssue",
]
