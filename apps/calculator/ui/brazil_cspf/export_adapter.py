"""Tk clipboard, file-dialog, and CSV adapters for Brazil exports."""

from __future__ import annotations

import csv
from pathlib import Path
from tkinter import filedialog

from .export_document import BrazilCspfExportDocument


def copy_brazil_cspf_export(widget, document: BrazilCspfExportDocument) -> bool:
    contents = document.as_tsv()
    if not contents:
        return False
    widget.clipboard_clear()
    widget.clipboard_append(contents)
    return True


def write_brazil_cspf_sectioned_csv(
    path: str | Path,
    document: BrazilCspfExportDocument,
    *,
    encoding: str = "utf-8-sig",
) -> None:
    with Path(path).open("w", newline="", encoding=encoding) as handle:
        writer = csv.writer(handle)
        for section in document.sections:
            writer.writerow((f"[{section.label}]",))
            if section.headers:
                writer.writerow(section.headers)
            writer.writerows(section.rows)


def export_brazil_cspf_sectioned_csv(
    parent, default_filename: str, document: BrazilCspfExportDocument
) -> bool:
    path = filedialog.asksaveasfilename(
        parent=parent,
        initialfile=default_filename,
        defaultextension=".csv",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
    )
    if not path:
        return False
    write_brazil_cspf_sectioned_csv(path, document)
    return True


__all__ = [
    "copy_brazil_cspf_export",
    "export_brazil_cspf_sectioned_csv",
    "write_brazil_cspf_sectioned_csv",
]
