# 087 — Spreadsheet Table Component + Test Harness (First Slice)

## Goal

Stand up the first concrete piece of the global PyQt table UI contract
(`docs/ui/SPREADSHEET_TABLE_CONTRACT.md`) as a reusable component:

1. A view-agnostic `QAbstractTableModel` subclass plus pure-Python TSV
   helpers, so every future table surface (calculator AHRI / EN14825,
   train UI, helpers) can attach to the same model code instead of
   re-implementing copy / paste / clear / undo per tab.
2. A regression-style test harness that pins the contract's
   spreadsheet behaviors (TSV copy / paste, multi-cell paste, Delete
   clear, Ctrl+Z undo, numeric invalid display, point-dict conversion)
   so they cannot silently regress in a follow-up slice.

AHRI / EN14825 / ISO16358 UI wiring is **deferred** to follow-up
slices. This task only ships the model + helpers + tests.

## Scope

- `ui/spreadsheet_table.py` (new): pure-Python helpers
  (`parse_tsv`, `format_tsv`, `coerce_numeric`, `points_from_grid`) and
  `SpreadsheetTableModel(QAbstractTableModel)`. PyQt5 import-guarded
  so the module also imports cleanly in non-GUI environments.
- `tests/test_spreadsheet_table_model.py` (new): 27 tests covering
  shape, set/get, paste, copy, clear, undo, invalid numeric, point
  dict conversion, and pure-Python helper edge cases.
- `docs/WORK_PLAN.md`: mark the harness as the first completed step in
  the next-action sequence; update the queued slice order to
  AHRI SEER2 → AHRI HSPF2 → EN14825 SCOP → EN14825 SEER.
- `result_reports/active/087_spreadsheet-table-component-harness.md`:
  this report.

## Non-goals

- No `ui/calc_window.py` wiring; no replacement of
  `input_widgets_ahri`, `input_widgets_hspf2`, or `input_widgets_en`.
- No AHRI / EN14825 / ISO16358 UI integration.
- No `app_calculator.py` redesign.
- No calculator engine, region config, ML feature schema, calculator
  result schema, or adapter change.
- No ISO16358-2 HSPF mismatch audit; no xfail change.
- No `QTableWidget` or `setCellWidget` use.
- No keybinding wiring (Tab / Enter navigation, Ctrl+C / Ctrl+V /
  Ctrl+Z) — those live at the view / controller layer in a follow-up
  slice. The model already exposes every method the controller needs.

## Verification

- `python3 -B -m py_compile ui/spreadsheet_table.py` → OK.
- `python3 -B -m pytest tests/test_spreadsheet_table_model.py -q`
  → `27 passed`.
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → `3 passed` (boundary unaffected; `ui/spreadsheet_table.py` is
  outside `core/calculator_*.py` and is not part of the scan).
- `python3 -B -m pytest -q` → `434 passed, 34 xfailed`. Baseline before
  this task was `407 passed, 34 xfailed`; the +27 delta is exactly the
  new spreadsheet model tests. xfail counts unchanged.

## Task Results

### Task 1 — `ui/spreadsheet_table.py` first slice

Files changed: `ui/spreadsheet_table.py` (new).

Public API:

- `parse_tsv(text) -> List[List[str]]` — normalizes CRLF / CR to LF,
  drops a single trailing blank row, rejects non-string input.
- `format_tsv(grid) -> str` — emits `\t`-separated columns,
  `\n`-separated rows, trailing `\n`, `None` → `""`.
- `coerce_numeric(value) -> Optional[float]` — returns `None` for
  empty / unparseable values; tolerates whitespace.
- `points_from_grid(column_labels, grid, capacity_row=0, power_row=1)
  -> Dict[str, Tuple[float, float]]` — converts a column-shaped grid
  into `{col: (capacity, power)}`; fails fast on row width mismatch
  or non-numeric capacity / power.
- `SpreadsheetTableModel(row_labels, column_labels, parent=None)`:
  - Qt overrides: `rowCount`, `columnCount`, `data`, `setData`,
    `flags`, `headerData`. `setData` returns `True` and emits
    `dataChanged` after pushing an undo snapshot.
  - Helpers: `row_labels`, `column_labels`, `set_cell`, `get_cell`,
    `to_grid`, `is_cell_invalid`, `selected_to_tsv`, `paste_tsv`,
    `clear_cells`, `can_undo`, `undo`, `reset_undo`, `as_point_dict`.
  - `paste_tsv(top_row, top_col, tsv)` writes the TSV grid starting
    at `(top_row, top_col)`; cells outside the model bounds are
    silently dropped; returns the number of cells written.
  - `selected_to_tsv(selection)` expands the selection to its
    bounding rectangle and emits TSV ending in `\n`.
  - `clear_cells(selection)` empties every editable cell in the
    selection and returns the count of actually-cleared cells.
  - `set_cell` / `paste_tsv` / `clear_cells` each push a single
    snapshot onto the undo stack; `undo()` pops the most recent one
    and restores the grid via `beginResetModel` / `endResetModel`.
    `paste_tsv` / `clear_cells` discard the snapshot when no cell
    actually changed.
  - `as_point_dict(capacity_row=0, power_row=1)` delegates to
    `points_from_grid` for the AHRI / EN14825 / ISO16358 column-shape
    layout.

PyQt5 import guard: the module starts with
`try: from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
... except ImportError: _PYQT_AVAILABLE = False`. When PyQt5 is
missing the pure-Python helpers still import and `SpreadsheetTableModel`
is exposed as `None`.

Contract coverage (this slice):

| Contract section | Item | Slice status |
| --- | --- | --- |
| §3 UX baseline | TSV `Ctrl+C` copy | model helper: `selected_to_tsv` |
| §3 UX baseline | TSV `Ctrl+V` paste, multi-cell | model helper: `paste_tsv` |
| §3 UX baseline | `Delete` / `Backspace` clear | model helper: `clear_cells` |
| §3 UX baseline | `Ctrl+Z` undo | model helper: `undo` / `can_undo` / `reset_undo` |
| §3 UX baseline | Invalid numeric marking | model helper: `is_cell_invalid` (read-only flag for delegates) |
| §3 UX baseline | Read-only / auto-cell visual marking | **deferred** (no read-only flagging yet) |
| §4 implementation | `QTableView` + `QAbstractTableModel` | model side done; view wiring deferred |
| §4 implementation | `QStyledItemDelegate` editor pattern | **deferred** to controller slice |
| §5 editor lifecycle | 1-click dropdown via `QTimer.singleShot` | **deferred** |
| §6 path isolation | Edit vs paste vs cascade | model exposes them as separate methods; controller wiring deferred |
| §7 copy/paste | TSV format, bounding-rect copy, top-left-anchored paste, out-of-bounds drop | done |
| §7 copy/paste | Single-value repeat-to-selection paste | **deferred** (model does not yet repeat) |
| §8 clear | Editable cells cleared in selection | done (every cell editable in this slice) |
| §9 undo | Per-action undo group; reset on data-context change | done |
| §9 undo | Redo (`Ctrl+Y` / `Ctrl+Shift+Z`) | **deferred** |
| §10 navigation | Tab / Enter wrap-around | **deferred** to view |
| §11 numeric validation | Invalid-cell read-only flag | done |
| §11 numeric validation | Visual error indicator paint | **deferred** to delegate |
| §12 `blockSignals` | `try/finally` discipline | not directly relevant: model emits `dataChanged`; callers wrap their batch mutations |
| §13 checklist | Helper / test-harness checklist gate | satisfied for this slice (see task 2) |

### Task 2 — `tests/test_spreadsheet_table_model.py`

Files changed: `tests/test_spreadsheet_table_model.py` (new).

Test categories and results:

| # | Test | Result |
| --- | --- | --- |
| 1 | `parse_tsv` handles CRLF + trailing newline | pass |
| 2 | `parse_tsv` returns `[]` for empty string | pass |
| 3 | `parse_tsv` rejects non-string input | pass |
| 4 | `format_tsv` emits trailing newline | pass |
| 5 | `format_tsv` empty grid → `""` | pass |
| 6 | `points_from_grid` rejects row-width mismatch | pass |
| 7 | Shape uses row_labels and column_labels (incl. `headerData`) | pass |
| 8 | Constructor rejects empty labels | pass |
| 9 | `set_cell` / `get_cell` round-trip + Qt `data()` | pass |
| 10 | `set_cell(None)` stores empty string | pass |
| 11 | `set_cell` rejects out-of-bounds indices | pass |
| 12 | 2×3 TSV paste at origin writes the rectangle | pass |
| 13 | Paste at offset anchors at top-left | pass |
| 14 | Paste silently drops out-of-bounds cells | pass |
| 15 | Rectangle selection copy returns TSV | pass |
| 16 | Non-rectangular selection expands to bounding rect | pass |
| 17 | Clear helper empties only selected cells | pass |
| 18 | Clear helper returns 0 when selection already empty | pass |
| 19 | Undo restores state before paste | pass |
| 20 | Undo restores state before clear | pass |
| 21 | Undo returns False when stack is empty | pass |
| 22 | `reset_undo` clears the stack | pass |
| 23 | Invalid numeric value stored as-is | pass |
| 24 | Invalid numeric value flagged (`is_cell_invalid`) | pass |
| 25 | `as_point_dict` converts capacity / power rows | pass |
| 26 | `as_point_dict` rejects non-numeric capacity | pass |
| 27 | `as_point_dict` rejects empty power | pass |

PyQt optional skip: the test file uses
`pytest.importorskip("PyQt5")` at module top after setting
`QT_QPA_PLATFORM=offscreen`. In a PyQt5-less environment the entire
file is skipped at collection time without errors. This matches the
existing pattern in `tests/test_app_calculator_ui_smoke.py`.

No test depends on the OS clipboard or a real GUI launch. The model
is exercised in-process via helper methods only.

### Task 3 — `docs/WORK_PLAN.md` next-action sequence

Files changed: `docs/WORK_PLAN.md`.

- Added a `Current milestone focus` bullet pointing to the new
  spreadsheet table component (`ui/spreadsheet_table.py`) and harness
  (`tests/test_spreadsheet_table_model.py`), explicitly stating that
  AHRI/EN/ISO UI wiring is not yet connected.
- Reworked the `Repo 다음 순서` block:
  1. spreadsheet table component harness (this slice) — completed.
  2. AHRI SEER2 horizontal table-input first slice (Slice A of the
     calculator design doc).
  3. AHRI HSPF2 horizontal table-input slice (Slice B).
  4. EN14825 table-input slice (Slice C → SCOP, Slice D → SEER).
- Removed `unit normalization adapter` and `envelope chain
  end-to-end smoke` from the queued-next-action list because both are
  done; they are now listed as completed prerequisites in the
  trailing paragraph.
- `ISO16358-2 HSPF mismatch` continues to be marked as a user-side
  external audit and is **not** added back into the repo immediate
  next-action list.
- Unit adapter expansion to ISO / KS / EN profiles and ML /
  inverse-search resumption stay below the table-input UI slices.

## Test Results

- `python3 -B -m py_compile ui/spreadsheet_table.py` → exit 0.
- `python3 -B -m pytest tests/test_spreadsheet_table_model.py -q`
  → `27 passed`.
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → `3 passed`.
- `python3 -B -m pytest -q` → `434 passed, 34 xfailed`.

## Changed Files

- `ui/spreadsheet_table.py` — new. Reusable spreadsheet model +
  pure-Python TSV / point-dict helpers; PyQt5 import-guarded.
- `tests/test_spreadsheet_table_model.py` — new. 27 tests across
  helpers + model behavior; `pytest.importorskip("PyQt5")` gate.
- `docs/WORK_PLAN.md` — current milestone focus and near-term
  execution order updated.
- `result_reports/active/087_spreadsheet-table-component-harness.md`
  — this report.

## Known Failures / Risks

- Read-only / auto-cell flagging is not yet implemented in the
  model. The first AHRI SEER2 slice will need either a row-level or
  column-level read-only marker, or a `cell_is_editable(row, col)`
  predicate, before background colors and edit-guards can attach.
- Redo (`Ctrl+Y` / `Ctrl+Shift+Z`) is intentionally deferred. The
  current `undo()` discards the redo information; this matches the
  contract's "redo is recommended but optional" stance for now.
- `paste_tsv` does not yet implement the
  "single-value repeat-to-selection" rule (Excel behavior for a
  1×1 source pasted into an N×M selection). The current behavior is
  to write the single value into the top-left cell only. The first
  view slice can add this when the selection model is wired.
- The model has no notion of a "max undo depth wiped on context
  switch" beyond `reset_undo()`. Callers must call `reset_undo()`
  themselves on profile / file change.
- `set_cell` pushes one snapshot per call, so a programmatic loop
  that sets N cells creates N undo entries. The first view slice
  should expose a `batch_edit` or accept a list-of-cells variant if
  the AHRI SEER2 wiring needs grouped edits beyond paste / clear.
- `ui/spreadsheet_table.py` is currently unused by any view. If it
  drifts from the contract before the first AHRI SEER2 slice lands,
  the regression risk is invisible in production but the
  `test_spreadsheet_table_model.py` harness will catch it.

## Next Suggested Action

1. **AHRI SEER2 horizontal table-input first slice** (Slice A of
   `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`):
   - Construct a `SpreadsheetTableModel` with
     `row_labels=["능력 [Btu/h]", "전력 [W]"]`,
     `column_labels=["A_Full", "B_Full", "B_Low", "E_Int", "F_Low"]`.
   - Replace only the AHRI SEER2 portion of `input_widgets_ahri`
     with a `QTableView` bound to the model.
   - Keep `input_widgets_ahri["A_Full_cap"]` / `A_Full_pow"]` / …
     populated from the model (read via `as_point_dict` or
     `to_grid`) so `calculate_ahri()` keeps working unchanged.
   - Add an offscreen PyQt smoke test that exercises the model →
     calculator path end-to-end through the new view.
2. Add a `cell_is_editable(row, col)` predicate (or row-level
   read-only flag) to `SpreadsheetTableModel` only when Slice A
   actually needs it, with new tests in
   `test_spreadsheet_table_model.py`. Do not pre-add fields the
   first view slice does not consume.

## Scope Compliance

- `ui/calc_window.py` — not modified.
- `app_calculator.py` — not modified.
- No AHRI / EN14825 / ISO16358 UI integration; no
  `input_widgets_*` dict touched.
- No calculator engine, region config, expected / golden, fixture,
  adapter, unit conversion, or ML caller change.
- No `QTableWidget` introduced.
- No `setCellWidget` introduced.
- No xfail relaxation; ISO16358-2 HSPF mismatch list unchanged.
- `tests/test_calculator_schema_boundaries.py` not modified;
  `core/calculator_*.py` boundary scan is unaffected because
  `ui/spreadsheet_table.py` is outside that scope.
- New file lives under `ui/` so the existing schema boundary that
  forbids importing `ui` from `core/calculator_*.py` is preserved.

## Commit / Push

- Source + tests + docs commit: a single commit covering
  `ui/spreadsheet_table.py`, `tests/test_spreadsheet_table_model.py`,
  `docs/WORK_PLAN.md`.
- Report commit: this report as a separate commit (`report: ...`
  style).
- Both commits pushed to `origin/work/iso-separation-plan`.
