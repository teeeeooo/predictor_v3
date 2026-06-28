"""Clipboard helpers for Predict spreadsheet-like tables."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def parse_tsv(text: str) -> list[list[str]]:
    """Parse TSV text from spreadsheet clipboards."""
    if not isinstance(text, str):
        raise TypeError("TSV input must be a string")
    if text == "":
        return []
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    rows = normalized.split("\n")
    if rows and rows[-1] == "":
        rows = rows[:-1]
    return [row.split("\t") for row in rows]


def format_tsv(grid: Sequence[Sequence[Any]]) -> str:
    """Format a rectangular grid as TSV with a trailing newline."""
    rows = []
    for row in grid:
        rows.append("\t".join("" if cell is None else str(cell) for cell in row))
    return "" if not rows else "\n".join(rows) + "\n"


def rectangular_bounds(cells: Sequence[tuple[int, int]]) -> tuple[int, int, int, int] | None:
    """Return top/left/bottom/right bounds for selected cells."""
    if not cells:
        return None
    rows = [row for row, _col in cells]
    cols = [col for _row, col in cells]
    return min(rows), min(cols), max(rows), max(cols)
