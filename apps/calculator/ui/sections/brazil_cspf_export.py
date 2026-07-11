"""Brazil-local sectioned result export contract and adapters."""

from __future__ import annotations

import csv
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog

from apps.calculator.application.brazil_cspf.models import BrazilRuleDisplay
from apps.calculator.ui.table_clipboard import encode_table_tsv


BRAZIL_CSPF_RESULT_COLUMNS: tuple[str, ...] = (
    "Scenario",
    "CSPF",
    "CSTL [kWh]",
    "CSEC [kWh]",
)

BRAZIL_CSPF_RULE_COLUMNS: tuple[str, ...] = (
    "Rule",
    "조건",
    "대상값",
    "기준값",
    "판정",
)


@dataclass(frozen=True)
class BrazilExportSection:
    """One independently shaped section in a Brazil result export."""

    label: str
    headers: tuple[str, ...] = ()
    rows: tuple[tuple[str, ...], ...] = ()

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("Brazil export section label must not be empty")
        if self.headers and any(len(row) != len(self.headers) for row in self.rows):
            raise ValueError("Brazil export rows must match their section header")

    def tsv_lines(self) -> tuple[str, ...]:
        lines = [f"[{self.label}]"]
        if self.headers:
            lines.extend(encode_table_tsv(self.headers, self.rows).splitlines())
        else:
            lines.extend("\t".join(row) for row in self.rows)
        return tuple(lines)


@dataclass(frozen=True)
class BrazilCspfExportDocument:
    """Shared source of truth for valid Brazil Copy/CSV/as_text output."""

    sections: tuple[BrazilExportSection, ...]

    def as_tsv(self) -> str:
        lines: list[str] = []
        for section in self.sections:
            lines.extend(section.tsv_lines())
        return "\n".join(lines)


def build_brazil_cspf_export_document(
    rows: Sequence[Sequence[str]],
    rules: Sequence[BrazilRuleDisplay],
    final_status: str,
) -> BrazilCspfExportDocument:
    rule_rows = tuple(
        (
            rule.label,
            rule.condition_text or rule.comparison,
            rule.left_value_text,
            rule.right_value_text,
            rule.status_text,
        )
        for rule in rules
    )
    return BrazilCspfExportDocument(
        sections=(
            BrazilExportSection(
                label="Result",
                headers=BRAZIL_CSPF_RESULT_COLUMNS,
                rows=tuple(tuple(value) for value in rows),
            ),
            BrazilExportSection(
                label="Rule",
                headers=BRAZIL_CSPF_RULE_COLUMNS,
                rows=rule_rows,
            ),
            BrazilExportSection(
                label="Final",
                rows=(("Final", final_status),),
            ),
        )
    )


def copy_brazil_cspf_export(widget, document: BrazilCspfExportDocument) -> bool:
    """Copy a sectioned Brazil document without flattening its schemas."""
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
    """Write section labels and each section's own header/rows to CSV."""
    with Path(path).open("w", newline="", encoding=encoding) as handle:
        writer = csv.writer(handle)
        for section in document.sections:
            writer.writerow((f"[{section.label}]",))
            if section.headers:
                writer.writerow(section.headers)
            writer.writerows(section.rows)


def export_brazil_cspf_sectioned_csv(
    parent,
    default_filename: str,
    document: BrazilCspfExportDocument,
) -> bool:
    """Choose a destination and write the sectioned Brazil CSV document."""
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
    "BRAZIL_CSPF_RESULT_COLUMNS",
    "BRAZIL_CSPF_RULE_COLUMNS",
    "BrazilCspfExportDocument",
    "BrazilExportSection",
    "build_brazil_cspf_export_document",
    "copy_brazil_cspf_export",
    "export_brazil_cspf_sectioned_csv",
    "write_brazil_cspf_sectioned_csv",
]
