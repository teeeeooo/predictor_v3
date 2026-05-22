# 105 — ISO Result / Read-only Table Ctrl+C TSV Copy

- Mode: implementation (UI read-only result tables + tests + WORK_PLAN).
- Branch: work/iso-separation-plan.
- Predecessor: 104 aligned the ISO input table
  (`ProfileInputGridModel` / `ProfileInputGridView`) with the Excel-like
  table contract but explicitly deferred read-only result tables. 094
  audit's Known Risk on read-only result table copy lands here.
- Scope: extend Ctrl+C TSV copy to the ISO16358 read-only result /
  trace tables — `TwoPointTableModel` (BatchTwoPointDialog),
  `RegionResultTableModel` (IsoCspfSingleWidget.result_table),
  `TraceTableModel` (TraceDetailPanel iso / iseer tables and
  RegionDetailTab.table). Calculation, fixtures, expected values, the
  ISO input table behavior from 104, profile registry, Hong Kong HSPF,
  and result-report lifecycle maintenance are intentionally **not**
  touched.

## Task 1 — TSV helper

- File: `ui/calculators_2point.py`.
- `selected_cells_to_tsv(model, cells)` added as a module-level helper.
  Reuses `format_tsv` from `ui/spreadsheet_table.py` so the
  serialization stays bit-identical to AHRI / EN / ISO input tables
  (contract §7).
- Drives the TSV grid from `model.data(index, Qt.DisplayRole)` — what
  the user sees on screen is what lands on the clipboard (formatted
  floats, fixed precision, EER strings, etc.).
- Non-rectangular / disjoint selections are expanded to their bounding
  rectangle (contract §7 mandate).
- Out-of-range `(row, col)` cells inside the bounding rectangle resolve
  to `""` so a partial selection still produces a well-formed N×M TSV.
- Empty `cells` returns `""`.

## Task 2 — Ctrl+C wiring on read-only result tables

- File: `ui/calculators_2point.py`.
- `_ReadOnlyCopyMixin` + `ReadOnlyCopyTableView(QTableView)` subclass
  added. The mixin provides `_selected_cell_set()`,
  `copy_selection_tsv()`, and `copy_selection_to_clipboard()`. The
  subclass overrides `keyPressEvent` to intercept `QKeySequence.Copy`
  (Ctrl+C on Linux/Windows, Cmd+C on macOS) and write TSV to
  `QApplication.clipboard()`.
- Empty selection falls back to `currentIndex()` so a single focused
  cell still copies.
- The `__init__` of `ReadOnlyCopyTableView` sets
  `SelectionBehavior=SelectItems` and `SelectionMode=ExtendedSelection`
  so contiguous and Ctrl-click range selection both work — the minimum
  needed for the copy contract.
- Read-only tables intentionally do **not** support Delete / Backspace
  clear, Ctrl+V paste, or Ctrl+Z undo. Those operations are no-ops by
  design (these tables hold computed results / bin traces and are not
  user-editable).
- Existing `QTableView()` instantiations were replaced by
  `ReadOnlyCopyTableView()`:
  - `TraceDetailPanel.iso_table_view` (ISO 16358 T1 bin detail).
  - `TraceDetailPanel.iseer_table_view` (India ISEER bin detail).
  - `RegionDetailTab.table` (per-region detail tab).
  - `IsoCspfSingleWidget.result_table` (region/profile result table).
- `TwoPointTableView` already had a `keyPressEvent` handling Ctrl+V
  paste into editable input columns. It now also mixes in
  `_ReadOnlyCopyMixin` and handles `QKeySequence.Copy` before the
  paste branch — TSV from the bounding rectangle of the selection
  lands on the clipboard via the same helper. The existing paste /
  edit / debounced recalculate paths are untouched.
- Refresh, tab switching, summary updates, and graph repaint paths are
  unchanged.

## Task 3 — Tests

- New file: `tests/test_iso16358_result_table_copy_tsv.py`.
- Coverage (each gated by `pytest.importorskip("PyQt5")`):
  - `TwoPointTableModel` copy: edit two rows of input cells via
    `setData`, select the 2×2 rectangle, copy, assert clipboard text.
  - `RegionResultTableModel` copy: seed two rows via `set_schema`,
    select the full grid, assert clipboard text matches what
    DisplayRole returned.
  - `TraceTableModel` copy: seed two bin rows via `set_data`, select
    the first two columns, assert the formatted DisplayRole values
    (e.g. `-8.00`) appear on the clipboard.
  - `RegionDetailTab.table` is a `ReadOnlyCopyTableView` and its
    `copy_selection_to_clipboard()` produces the expected TSV — proves
    the per-region detail tab gets the same copy connection.
  - Non-rectangular selection (two disjoint corner cells) expands to
    the bounding rectangle — full 3×3 grid lands on the clipboard.
  - Empty-selection fallback: clearing the selection model and setting
    only `currentIndex` still copies that one cell.
  - `selected_cells_to_tsv` out-of-range cells in the bounding
    rectangle resolve to empty strings.
- PyQt5 optional skip: yes — same pattern as the existing UI tests.
  Headless CI without PyQt5 collect-skips this file via
  `pytest.importorskip("PyQt5")`. Clipboard verification stays at
  `QApplication.clipboard().text()`; no OS-level / Excel / Sheets
  dependency.

## Task 4 — Existing-behavior preservation

- `tests/test_iso16358_table_excel_like_behavior.py` (104) continues
  to gate on PyQt5; no change required. In this sandbox it collect-
  skips alongside the new file, same as 104.
- `tests/test_app_calculator_ui_smoke.py` is collected and its
  `pytest.importorskip("PyQt5")` skip behavior is unchanged.
- `ProfileInputGridModel` / `ProfileInputGridView` (the ISO input
  table from 104) were **not** modified — none of the helpers added in
  this slice touch the input-table model, view, or delegate. Edit /
  Paste / Clear / Undo / Enter-Tab navigation on the input table is
  preserved bit-for-bit.
- No common `SpreadsheetTableModel` migration was performed; ISO input
  table keeps its own `ProfileInputGridModel` as 104 left it.

## Task 5 — WORK_PLAN

- `docs/WORK_PLAN.md`: removed "ISO result/read-only table copy TSV"
  from the Near-term execution order sequence and moved it to the
  immediately-following "completed" annotation referencing this
  report (105). New sequence:
  1. unit adapter 확장 — ISO / KS / EN profile in
     `core/calculator_unit_adapter.py`
  2. ML / inverse-search 복귀 준비
- Hong Kong HSPF status unchanged: core/config/test +
  profile/dispatcher smoke complete; UI surface still absent (per 103).
- Result-report lifecycle maintenance (active → archive / summaries
  reconciliation) was explicitly out of scope per the task brief.
  It is **not** performed here and is recorded under Known Risks.

## Verification

```
python3 -B -m py_compile ui/calculators_2point.py tests/test_app_calculator_ui_smoke.py tests/test_iso16358_result_table_copy_tsv.py
→ ok

python3 -B -m pytest \
    tests/test_iso16358_table_excel_like_behavior.py \
    tests/test_app_calculator_ui_smoke.py \
    tests/test_spreadsheet_table_model.py \
    tests/test_spreadsheet_table_view.py \
    tests/test_calculator_schema_boundaries.py \
    tests/test_iso16358_result_table_copy_tsv.py -q
→ 3 passed, 5 skipped
(5 PyQt5-gated UI test files collect-skip — calculator_schema_boundaries
 has 3 non-UI tests that pass.)

python3 -B -m pytest -q
→ 430 passed, 6 skipped, 23 xfailed
```

Sandbox note: PyQt5 is not installed in this environment, so the new
PyQt5-gated UI test file collect-skips via
`pytest.importorskip("PyQt5")` — same constraint as 104. The non-UI
suite stays green and the new test file parses / imports under static
analysis (`py_compile`). On a PyQt5-equipped environment the new test
file is the active guard.

## Known Risks

- PyQt5 not installed in this sandbox; new test file is design-correct
  but its assertions can only be exercised on a PyQt5-equipped machine
  (same constraint as `tests/test_app_calculator_ui_smoke.py`,
  `tests/test_spreadsheet_table_view.py`, and the 104 test file).
- ISO HSPF UI input surface still does not exist; Hong Kong HSPF
  reachability remains profile-only (103).
- Result-report lifecycle maintenance (active → archive / summaries
  reconciliation) pending — intentionally not performed this turn per
  task brief.

## Files Modified

- `ui/calculators_2point.py` (module-level `selected_cells_to_tsv`,
  `_ReadOnlyCopyMixin`, `ReadOnlyCopyTableView` subclass;
  `TwoPointTableView` now mixes in the copy mixin and handles
  Ctrl+C; `TraceDetailPanel.iso_table_view` / `iseer_table_view`,
  `RegionDetailTab.table`, `IsoCspfSingleWidget.result_table` switched
  to `ReadOnlyCopyTableView`).
- `tests/test_iso16358_result_table_copy_tsv.py` (new file).
- `docs/WORK_PLAN.md` (Near-term execution order updated; ISO
  result/read-only table copy TSV moved to completed annotation).
- `result_reports/active/105_iso-result-table-copy-tsv.md`
  (this report).
