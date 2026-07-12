"""Small CSV export helpers for Tkinter table-shaped surfaces."""

from __future__ import annotations

import csv
from collections.abc import Sequence
from pathlib import Path
from tkinter import filedialog


def write_csv(
    path: str | Path,
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    *,
    encoding: str = "utf-8-sig",
) -> None:
    """Write table headers and rows to CSV using an Excel-friendly default."""
    with Path(path).open("w", newline="", encoding=encoding) as handle:
        writer = csv.writer(handle)
        writer.writerow(tuple(headers))
        writer.writerows(tuple(row) for row in rows)


def write_rows_csv(
    path: str | Path,
    rows: Sequence[Sequence[str]],
    *,
    encoding: str = "utf-8-sig",
) -> None:
    """Write already-sectioned rows without imposing a table header."""
    with Path(path).open("w", newline="", encoding=encoding) as handle:
        csv.writer(handle).writerows(tuple(row) for row in rows)


def export_table_to_csv(
    parent,
    default_filename: str,
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
) -> bool:
    """Ask for a destination path and export table data; cancel is a no-op."""
    path = filedialog.asksaveasfilename(
        parent=parent,
        initialfile=default_filename,
        defaultextension=".csv",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
    )
    if not path:
        return False
    write_csv(path, headers, rows)
    return True


def export_rows_to_csv(
    parent,
    default_filename: str,
    rows: Sequence[Sequence[str]],
) -> bool:
    """Ask for a destination and export sectioned rows; cancel is a no-op."""
    path = filedialog.asksaveasfilename(
        parent=parent,
        initialfile=default_filename,
        defaultextension=".csv",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
    )
    if not path:
        return False
    write_rows_csv(path, rows)
    return True
