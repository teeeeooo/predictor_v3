"""Windows Excel acquisition for DRM-sensitive legacy Mapping bootstrap CSVs."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from apps.train.adapters.mapping._legacy_validation import LegacyMappingBootstrapError
from apps.train.adapters.mapping.legacy_bootstrap import parse_legacy_mapping_rows
from core.mapping.editor_model import MappingEditorDraft

_XL_DELIMITED = 1
_XL_TEXT_QUALIFIER_NONE = -4142
_XL_TEXT_FORMAT = 2
_UTF8_CODE_PAGE = 65001


def parse_legacy_mapping_csv_with_excel(source: str | Path) -> MappingEditorDraft:
    """Acquire raw CSV lines through dedicated Excel, then parse the strict contract."""
    return parse_legacy_mapping_rows(_read_rows_with_excel(Path(source)))


def _read_rows_with_excel(source: Path) -> list[list[str]]:
    try:
        import xlwings as xw
    except ImportError as exc:
        raise LegacyMappingBootstrapError(
            "Excel automation is unavailable because xlwings is not installed.",
            block="layout",
        ) from exc

    app = None
    book = None
    rows: list[list[str]] | None = None
    cleanup_errors: list[str] = []
    try:
        app = xw.App(visible=False, add_book=False)
        app.api.Workbooks.OpenText(
            str(source.resolve()),
            _UTF8_CODE_PAGE,
            1,
            _XL_DELIMITED,
            _XL_TEXT_QUALIFIER_NONE,
            False,
            False,
            False,
            False,
            False,
            False,
            None,
            [(1, _XL_TEXT_FORMAT)],
        )
        book = app.books.active
        if book is None:
            raise RuntimeError("Excel did not expose the opened legacy CSV workbook")
        sheet = book.sheets[0]
        used = sheet.used_range
        last_row = int(used.last_cell.row)
        last_column = int(used.last_cell.column)
        if last_column != 1:
            raise RuntimeError(
                "Excel split the legacy CSV instead of preserving raw text lines"
            )
        values = sheet.range((1, 1), (last_row, 1)).value
        rows = _parse_raw_lines(values, last_row)
    except LegacyMappingBootstrapError:
        raise
    except Exception as exc:
        raise LegacyMappingBootstrapError(
            f"Excel automation could not read the legacy Mapping CSV: {exc}",
            block="layout",
        ) from exc
    finally:
        if book is not None:
            try:
                book.close()
            except Exception as exc:
                cleanup_errors.append(f"workbook close failed: {exc}")
        if app is not None:
            try:
                app.quit()
            except Exception as exc:
                cleanup_errors.append(f"Excel application quit failed: {exc}")

    if cleanup_errors:
        raise LegacyMappingBootstrapError(
            "Excel automation cleanup failed: " + "; ".join(cleanup_errors),
            block="layout",
        )
    if rows is None:
        raise LegacyMappingBootstrapError(
            "Excel automation returned no legacy Mapping rows.",
            block="layout",
        )
    return rows


def _parse_raw_lines(values: Any, row_count: int) -> list[list[str]]:
    lines = _raw_text_lines(values, row_count)
    try:
        return list(csv.reader(lines))
    except csv.Error as exc:
        raise LegacyMappingBootstrapError(str(exc), block="layout") from exc


def _raw_text_lines(values: Any, row_count: int) -> list[str]:
    raw_values = [values] if row_count == 1 else values
    if not isinstance(raw_values, list):
        raise LegacyMappingBootstrapError(
            "Excel automation returned an invalid raw-text table shape.",
            block="layout",
        )
    lines: list[str] = []
    for raw_value in raw_values:
        value = raw_value
        if isinstance(raw_value, list):
            if len(raw_value) != 1:
                raise LegacyMappingBootstrapError(
                    "Excel automation split one legacy CSV line into multiple cells.",
                    block="layout",
                )
            value = raw_value[0]
        if value is None:
            lines.append("")
        elif isinstance(value, str):
            lines.append(value)
        else:
            raise LegacyMappingBootstrapError(
                "Excel automation changed a raw legacy CSV line from text; "
                "the strict bootstrap contract was not preserved.",
                block="layout",
            )
    return lines
