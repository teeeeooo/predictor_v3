from __future__ import annotations

import csv
import io
import shutil
import sys
import types
from pathlib import Path

import pytest

from apps.train.adapters.mapping import (
    LegacyMappingBootstrapError,
    parse_legacy_mapping_csv,
    parse_legacy_mapping_csv_with_excel,
)
from apps.train.adapters.mapping.legacy_bootstrap import parse_legacy_mapping_rows
from apps.train.composition.runtime import _legacy_bootstrap_parser_for_platform
from apps.train.services.data_mapping_service import (
    DataMappingService,
    RuntimeMappingCatalogProvider,
)

LEGACY_FIXTURE = Path("tests/fixtures/mapping/mapping_tables_legacy_wide.csv")
RUNTIME_FIXTURE = Path("tests/fixtures/mapping/mapping_runtime_equivalent.json")


def _fixture_rows() -> list[list[str]]:
    with LEGACY_FIXTURE.open(newline="", encoding="utf-8") as source:
        return list(csv.reader(source))


def _fixture_lines() -> list[str]:
    return LEGACY_FIXTURE.read_text(encoding="utf-8-sig").splitlines()


def _rows_to_lines(rows: list[list[str]]) -> list[str]:
    lines = []
    for row in rows:
        target = io.StringIO(newline="")
        csv.writer(target, lineterminator="").writerow(row)
        lines.append(target.getvalue())
    return lines


class _LastCell:
    def __init__(self, row: int, column: int) -> None:
        self.row = row
        self.column = column


class _UsedRange:
    def __init__(self, row_count: int, column_count: int) -> None:
        self.last_cell = _LastCell(row_count, column_count)


class _Sheet:
    def __init__(
        self,
        raw_lines: list[object],
        *,
        fail_read: bool = False,
        used_column: int = 1,
    ) -> None:
        self._raw_lines = raw_lines
        self._fail_read = fail_read
        self.used_range = _UsedRange(len(raw_lines), used_column)
        self.requested_range = None

    def range(self, start, end):  # noqa: ANN001, ANN201
        self.requested_range = (start, end)
        if self._fail_read:
            raise PermissionError("DRM read denied")
        values = [[line] for line in self._raw_lines]
        return types.SimpleNamespace(value=values if len(values) != 1 else values[0][0])


class _Book:
    def __init__(self, sheet: _Sheet) -> None:
        self.sheets = [sheet]
        self.closed = False

    def close(self) -> None:
        self.closed = True


class _Books:
    def __init__(self) -> None:
        self.active = None


class _WorkbooksApi:
    def __init__(self, app: "_FakeApp", *, fail_open: bool = False) -> None:
        self._app = app
        self._fail_open = fail_open
        self.open_text_args = None

    def OpenText(self, *args) -> None:  # noqa: N802
        self.open_text_args = args
        if self._fail_open:
            raise PermissionError("Excel could not open protected source")
        self._app.books.active = self._app.book


class _FakeApp:
    def __init__(
        self,
        raw_lines: list[object],
        *,
        fail_open: bool = False,
        fail_read: bool = False,
        used_column: int = 1,
    ) -> None:
        self.sheet = _Sheet(raw_lines, fail_read=fail_read, used_column=used_column)
        self.book = _Book(self.sheet)
        self.books = _Books()
        self.workbooks_api = _WorkbooksApi(self, fail_open=fail_open)
        self.api = types.SimpleNamespace(Workbooks=self.workbooks_api)
        self.quit_called = False

    def quit(self) -> None:
        self.quit_called = True


def _install_fake_xlwings(
    monkeypatch,
    raw_lines: list[object],
    *,
    fail_open: bool = False,
    fail_read: bool = False,
    used_column: int = 1,
):  # noqa: ANN001, ANN201
    created = []

    def app_factory(*, visible: bool, add_book: bool):  # noqa: ANN202
        assert visible is False
        assert add_book is False
        app = _FakeApp(
            raw_lines,
            fail_open=fail_open,
            fail_read=fail_read,
            used_column=used_column,
        )
        created.append(app)
        return app

    monkeypatch.setitem(sys.modules, "xlwings", types.SimpleNamespace(App=app_factory))
    return created


def _error_signature(error: LegacyMappingBootstrapError) -> tuple[object, ...]:
    return (error.reason, error.legacy_row, error.block, error.field, error.key)


def test_production_platform_selects_excel_only_for_windows():
    assert _legacy_bootstrap_parser_for_platform("win32") is parse_legacy_mapping_csv_with_excel
    assert _legacy_bootstrap_parser_for_platform("darwin") is parse_legacy_mapping_csv
    assert _legacy_bootstrap_parser_for_platform("linux") is parse_legacy_mapping_csv


def test_excel_acquisition_matches_direct_contract_without_source_write(monkeypatch):
    lines = _fixture_lines()
    created = _install_fake_xlwings(monkeypatch, lines)
    original = LEGACY_FIXTURE.read_bytes()

    acquired = parse_legacy_mapping_csv_with_excel(LEGACY_FIXTURE)

    assert acquired == parse_legacy_mapping_csv(LEGACY_FIXTURE)
    assert LEGACY_FIXTURE.read_bytes() == original
    app = created[0]
    assert app.book.closed and app.quit_called
    assert app.sheet.requested_range == ((1, 1), (len(lines), 1))
    args = app.workbooks_api.open_text_args
    assert args is not None
    assert args[0] == str(LEGACY_FIXTURE.resolve())
    assert args[1:5] == (65001, 1, 1, -4142)
    assert args[5:11] == (False, False, False, False, False, False)
    assert args[12] == [(1, 2)]


@pytest.mark.parametrize("failure_kind", ["header", "row_width", "duplicate", "numeric"])
def test_excel_acquisition_preserves_strict_legacy_failures(monkeypatch, failure_kind):
    rows = _fixture_rows()
    lines = _rows_to_lines(rows)
    if failure_kind == "header":
        rows[0][0] = "Wrong Header"
        lines = _rows_to_lines(rows)
    elif failure_kind == "row_width":
        lines[3] = lines[3].rstrip(",")
        rows = list(csv.reader(lines))
    elif failure_kind == "duplicate":
        duplicate = [""] * len(rows[0])
        duplicate[0] = rows[1][0]
        rows.append(duplicate)
        lines = _rows_to_lines(rows)
    else:
        rows[1][1] = "not-a-number"
        lines = _rows_to_lines(rows)

    with pytest.raises(LegacyMappingBootstrapError) as direct:
        parse_legacy_mapping_rows(rows)
    created = _install_fake_xlwings(monkeypatch, lines)
    with pytest.raises(LegacyMappingBootstrapError) as acquired:
        parse_legacy_mapping_csv_with_excel(LEGACY_FIXTURE)

    assert _error_signature(acquired.value) == _error_signature(direct.value)
    assert created[0].book.closed and created[0].quit_called


def test_excel_acquisition_rejects_coercion_or_split_range_and_releases(monkeypatch):
    values: list[object] = _fixture_lines()
    values[1] = 3.5
    created = _install_fake_xlwings(monkeypatch, values)
    with pytest.raises(LegacyMappingBootstrapError, match="raw legacy CSV line from text"):
        parse_legacy_mapping_csv_with_excel(LEGACY_FIXTURE)
    assert created[0].book.closed and created[0].quit_called

    created = _install_fake_xlwings(monkeypatch, _fixture_lines(), used_column=2)
    with pytest.raises(LegacyMappingBootstrapError, match="split the legacy CSV"):
        parse_legacy_mapping_csv_with_excel(LEGACY_FIXTURE)
    assert created[0].book.closed and created[0].quit_called


def test_excel_read_failure_preserves_existing_unsaved_session(monkeypatch, tmp_path):
    mapping_file = tmp_path / "mapping.json"
    shutil.copy2(RUNTIME_FIXTURE, mapping_file)
    service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_file)),
        legacy_bootstrap_parser=parse_legacy_mapping_csv_with_excel,
    )
    service.load_snapshot()
    service.edit_cell("idu", 0, "ID Volume", "99.5")
    mapping_file.unlink()
    before_token = service._session.state_token()
    before_revision = service.draft_revision
    created = _install_fake_xlwings(monkeypatch, _fixture_lines(), fail_read=True)

    preview = service.preview_legacy_bootstrap(tmp_path / "protected.csv")

    assert not preview.can_apply
    assert preview.blockers[0].code == "legacy_bootstrap_invalid_source"
    assert service._session.state_token() == before_token
    assert service.draft_revision == before_revision
    assert not mapping_file.exists()
    assert created[0].book.closed and created[0].quit_called


def test_excel_open_failure_is_fail_closed_without_direct_parser_fallback(monkeypatch):
    assert parse_legacy_mapping_csv(LEGACY_FIXTURE) is not None
    created = _install_fake_xlwings(monkeypatch, _fixture_lines(), fail_open=True)

    with pytest.raises(LegacyMappingBootstrapError, match="Excel automation could not read"):
        parse_legacy_mapping_csv_with_excel(LEGACY_FIXTURE)

    assert not created[0].book.closed
    assert created[0].quit_called
