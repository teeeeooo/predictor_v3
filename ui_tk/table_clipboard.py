"""Clipboard helpers for table-shaped Tkinter surfaces."""

from __future__ import annotations

from collections.abc import Sequence


def encode_table_tsv(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """Return header-included TSV suitable for spreadsheet paste."""
    lines = [_tsv_row(headers)]
    lines.extend(_tsv_row(row) for row in rows)
    return "\n".join(lines)


def copy_table_to_clipboard(
    widget,
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
) -> bool:
    contents = encode_table_tsv(headers, rows)
    if not contents:
        return False
    widget.clipboard_clear()
    widget.clipboard_append(contents)
    return True


def _tsv_row(values: Sequence[str]) -> str:
    return "\t".join(_safe_cell(value) for value in values)


def _safe_cell(value: object) -> str:
    if value is None:
        return ""
    return str(value)
