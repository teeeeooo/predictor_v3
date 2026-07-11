"""Pure Brazil sectioned result export document and schema."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

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


__all__ = [
    "BRAZIL_CSPF_RESULT_COLUMNS",
    "BRAZIL_CSPF_RULE_COLUMNS",
    "BrazilCspfExportDocument",
    "BrazilExportSection",
    "build_brazil_cspf_export_document",
]
