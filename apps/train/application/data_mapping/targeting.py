"""Qt-free stable row-occurrence resolution for mapping targets."""

from __future__ import annotations

from collections.abc import Sequence


def row_identity_at_index(
    row_keys: Sequence[str],
    row_index: int | None,
) -> tuple[str, int] | None:
    """Return stable row key and occurrence for one valid local index."""
    if row_index is None or not 0 <= row_index < len(row_keys):
        return None
    row_key = row_keys[row_index]
    occurrence = sum(1 for key in row_keys[:row_index] if key == row_key)
    return row_key, occurrence


def row_index_for_identity(
    row_keys: Sequence[str],
    row_key: str,
    row_occurrence: int | None,
) -> int | None:
    """Resolve one exact stable occurrence without falling back to another row."""
    if row_occurrence is None or row_occurrence < 0:
        return None
    matches = tuple(index for index, key in enumerate(row_keys) if key == row_key)
    return matches[row_occurrence] if row_occurrence < len(matches) else None


def unique_row_identity(row_keys: Sequence[str], row_key: str) -> tuple[str, int] | None:
    """Resolve an index-less key only when it identifies exactly one row."""
    matches = tuple(index for index, key in enumerate(row_keys) if key == row_key)
    if len(matches) != 1:
        return None
    return row_key, 0
