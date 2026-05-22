# 104 — ISO Table Excel-like Behavior Patch

- Mode: implementation (UI input table + tests + WORK_PLAN).
- Branch: work/iso-separation-plan.
- Predecessor: 094 audit identified four gaps in `ProfileInputGridModel` /
  `ProfileInputGridView` relative to `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`
  (copy, clear, invalid display, Enter/Shift+Enter direction).
- Scope: align the ISO16358 CSPF input table (ISO T1, India ISEER, Hong
  Kong, SASO T3 — they all share `ProfileInputGridModel` /
  `ProfileInputGridView`) with the global Excel-like table contract.
  ISO calculation logic, fixtures, expected values, xfail set, profile
  registry, Hong Kong HSPF, and result-table copy are intentionally **not**
  touched.

## Task 1 — Ctrl+C TSV copy

- File: `ui/calculators_2point.py`.
- `ProfileInputGridModel.selected_to_tsv(selection)` added. Reuses the
  existing `format_tsv` helper from `ui/spreadsheet_table.py` so the
  serialization stays bit-identical to AHRI / EN tables (contract §7).
  Non-rectangular selections are expanded to their bounding rectangle
  (contract §7 mandate). Out-of-range cells return `""`.
- `ProfileInputGridView.copy_selection_tsv()` / `copy_selection_to_clipboard()`
  added. `_selected_cells()` helper returns `{(row, col)}` deduplicated and
  sorted. Empty selection falls back to the current index so a single-cell
  copy works.
- `keyPressEvent` intercepts `QKeySequence.Copy` (Ctrl+C on Linux/Win,
  Cmd+C on macOS) and writes TSV to `QApplication.clipboard()`. Existing
  paste / edit / auto-recalculate paths are untouched.

## Task 2 — Delete / Backspace clear

- `ProfileInputGridModel.clear_cells(selection)` added. Builds a
  deduplicated list of in-bounds `(row, col)` pairs, then writes `""`
  into each non-empty cell while `_bulk_updating=True` so per-cell
  `values_changed` emissions do not fire. All cleared cells land in a
  **single undo entry** (one list pushed onto `_undo_stack`) — that
  matches contract §8 ("clearing emits a single undo group") and reuses
  the model's existing `(row, col, old_value)` undo entry format, so
  `undo()` rolls them back as one Ctrl+Z step.
- `dataChanged` is emitted once over the bounding rectangle of the
  cleared cells, and `values_changed` is emitted once at the end so the
  ISO recalculation path runs exactly once (and degrades to
  "입력값 부족" until the user types again).
- `ProfileInputGridView.clear_selection()` + `Delete` / `Backspace`
  handling in `keyPressEvent` were added. Empty selection falls back to
  the current index (same convention as copy).

## Task 3 — Invalid cell visualization

- `ProfileInputGridModel.is_cell_invalid(row, col)` added. ISO retains
  its existing "positive numeric required" rule via the model's
  `_parse_cell()` (non-numeric **or** ≤ 0 → invalid). Empty cells are
  **never** invalid — they continue to mean "user has not filled this
  yet" so the result panel still says "입력값 부족" rather than
  flagging blanks red.
- `data(..., BackgroundRole)` previously returned hard-coded white. Now
  returns `QBrush(QColor(*INVALID_CELL_BACKGROUND_RGB))` when invalid
  and the original `QColor("#FFFFFF")` otherwise — so the rest of the
  styling (gridlines, selection color, etc.) is unchanged for valid /
  empty cells.
- `data(..., ToolTipRole)` now exposes `INVALID_CELL_TOOLTIP` for
  invalid cells. Both constants are imported from `ui/spreadsheet_table.py`,
  matching the AHRI / EN invalid indicator so the visual is consistent
  across calculator tabs.
- `core/calculator_iso16358.py` validation, `parsed_points()` semantics,
  and the calculate button flow are all untouched.

## Task 4 — Excel-like navigation

- `ProfileInputGridView.next_navigation_index(row, col, direction)` is
  a pure (state-mutation-free) helper that returns the contract §10
  next index for `"right" | "left" | "down" | "up"` with wrap-around
  within the grid and clamping at the table boundary (no focus loss).
  Mirrors the helper that already lives on `SpreadsheetTableView` so
  ISO and AHRI/EN obey the same wrap rules.
- `move_active_cell(direction)` replaces the old `move_to_next_cell()`,
  which moved unconditionally right. `move_to_next_cell()` is kept as a
  backwards-compatible alias for `move_active_cell("down")` (some
  delegate/test code references it; contract §3 says Enter = down).
- `ProfileInputGridDelegate.eventFilter` now branches on `Qt.Key_Return`
  / `Qt.Key_Enter` (down, Shift = up), `Qt.Key_Tab` (right, Shift =
  left), and `Qt.Key_Backtab` (left, since Qt collapses `Shift+Tab`
  into `Backtab`). Each branch commits + closes the editor and then
  calls `view.move_active_cell(direction)` — that avoids the view's
  `keyPressEvent` firing twice while the delegate is editing.
- `ProfileInputGridView.keyPressEvent` mirrors the same branching for
  non-edit mode. Existing paste / undo / Delete handlers remain.

## Task 5 — Tests

- New file: `tests/test_iso16358_table_excel_like_behavior.py`.
- Coverage (each gated by `pytest.importorskip("PyQt5")`):
  - `selected_to_tsv` bounding-rectangle TSV.
  - `copy_selection_to_clipboard` ↔ `QApplication.clipboard()`.
  - `clear_selection` blanks N cells and `undo()` restores them
    (single Ctrl+Z group → all original values come back).
  - `clear_selection` with no selection falls back to the current
    index.
  - Empty cells: `is_cell_invalid → False`, BackgroundRole is **not**
    the invalid `QBrush`.
  - Non-numeric, `"0"`, `"-5"`, `"0.0"`: `is_cell_invalid → True`,
    BackgroundRole returns invalid `QBrush(INVALID_CELL_BACKGROUND_RGB)`,
    ToolTipRole exposes `INVALID_CELL_TOOLTIP`.
  - Positive numeric cell is not invalid.
  - `next_navigation_index` parametrized for all four directions
    including wrap-around and corner clamping.
  - `move_active_cell` end-to-end through the view: down → right → up →
    left walks the 2×2 grid as expected.
- PyQt5 optional skip: yes — same pattern as
  `tests/test_app_calculator_ui_smoke.py` /
  `tests/test_spreadsheet_table_model.py`. Headless CI without PyQt5
  reports `1 skipped` for this file. No OS-clipboard / Excel /
  Sheets dependency is taken — copy verification reads
  `QApplication.clipboard().text()` directly.

## Task 6 — WORK_PLAN

- `docs/WORK_PLAN.md`: moved "ISO table Excel-like behavior patch" out
  of the "Near-term execution order" sequence and into the
  immediately-following "completed" annotation referencing this report
  (104). New sequence:
  1. ISO result/read-only table copy TSV
     (`TwoPointTableModel` / `RegionResultTableModel` /
     `TraceTableModel` / `RegionDetailTab.table`)
  2. unit adapter 확장 — ISO / KS / EN profile in
     `core/calculator_unit_adapter.py`
  3. ML / inverse-search 복귀 준비
- Hong Kong HSPF status unchanged (core/config/test + profile/dispatcher
  smoke complete; UI surface still absent, per 103). Not touched here.
- Result-report lifecycle maintenance (active → archive/summaries
  reconciliation): out of scope per the task brief; noted in Known
  Risks.

## Verification

```
python3 -B -m py_compile ui/calculators_2point.py tests/test_app_calculator_ui_smoke.py
→ ok

python3 -B -m pytest \
    tests/test_app_calculator_ui_smoke.py \
    tests/test_spreadsheet_table_model.py \
    tests/test_spreadsheet_table_view.py \
    tests/test_calculator_schema_boundaries.py \
    tests/test_iso16358_table_excel_like_behavior.py -q
→ 3 passed (calculator_schema_boundaries), 4 skipped (PyQt5 unavailable
  in this sandbox; all PyQt5-gated UI tests including the new ISO
  Excel-like behavior tests skip via importorskip)

python3 -B -m pytest -q
→ 430 passed, 5 skipped, 23 xfailed
```

Sandbox note: PyQt5 is not installed in this environment, so the
PyQt5-gated UI smoke / spreadsheet-table / new ISO Excel-like tests
collect-skip via `pytest.importorskip("PyQt5")`. The non-UI suite
(425+ tests) remains green and the new test file parses / imports
under static analysis. On a PyQt5-equipped environment the new test
file is the active guard.

## Known Risks

- PyQt5 not installed in this sandbox; new test file is design-correct
  but its assertions can only be exercised on a PyQt5-equipped machine
  (same constraint as the existing `tests/test_app_calculator_ui_smoke.py`
  and `tests/test_spreadsheet_table_view.py`).
- ISO read-only result tables (`TwoPointTableModel`,
  `RegionResultTableModel`, `TraceTableModel`,
  `RegionDetailTab.table`) still lack `Ctrl+C` TSV copy — contract §3
  applies to read-only tables for the copy rule. That is the next
  sequence item, not in this slice.
- ISO HSPF UI input surface still does not exist; Hong Kong HSPF
  reachability remains profile-only (103).
- Result-report lifecycle maintenance (active → archive/summaries
  reconciliation) pending — intentionally not performed this turn.

## Files Modified

- `ui/calculators_2point.py` (model: `is_cell_invalid`, `selected_to_tsv`,
  `clear_cells`, `BackgroundRole`/`ToolTipRole`; delegate: Enter / Tab /
  Backtab branching; view: `copy_selection_tsv`,
  `copy_selection_to_clipboard`, `clear_selection`,
  `next_navigation_index`, `move_active_cell`, updated `keyPressEvent`).
- `tests/test_iso16358_table_excel_like_behavior.py` (new file).
- `docs/WORK_PLAN.md` (Near-term execution order updated; ISO table
  Excel-like patch moved to completed annotation).
- `result_reports/active/104_iso-table-excel-like-behavior-patch.md`
  (this report).
