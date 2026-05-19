# 090 Spreadsheet Table View Controller

## Goal
- Add a QTableView-based view/controller slice for the existing SpreadsheetTableModel helpers.
- Connect the AHRI SEER2 and AHRI HSPF2 table surfaces to that controller.
- Protect copy/paste/clear/undo behavior and AHRI smoke behavior with tests.

## Scope
- In scope:
  - `ui/spreadsheet_table.py`
  - `ui/calc_window.py`
  - `tests/test_spreadsheet_table_view.py`
  - `tests/test_app_calculator_ui_smoke.py`
  - `docs/WORK_PLAN.md`
- Out of scope:
  - EN14825 table conversion
  - ISO16358 UI changes
  - calculator logic, adapter/unit conversion, golden expected changes
  - QTableWidget or setCellWidget usage

## Changed Files
- `ui/spreadsheet_table.py`
- `ui/calc_window.py`
- `tests/test_spreadsheet_table_view.py`
- `tests/test_app_calculator_ui_smoke.py`
- `docs/WORK_PLAN.md`

## Task 1 Result
- Modified file: `ui/spreadsheet_table.py`
- Added view/controller class: `SpreadsheetTableView`, a `QTableView` subclass that delegates to the existing model helper API.
- Supported methods:
  - `copy_selection_tsv()`
  - `paste_tsv_at_selection(tsv)`
  - `clear_selection()`
  - `undo_last()`
- Supported key/action paths:
  - `Ctrl+C`: copy selected cells as TSV to `QApplication.clipboard()`
  - `Ctrl+V`: paste clipboard TSV at the top-left selected cell
  - `Delete` / `Backspace`: clear selected cells
  - `Ctrl+Z`: undo the most recent model undo group
- Testability split:
  - TSV-returning and TSV-accepting methods do not depend on the OS clipboard.
  - `keyPressEvent()` only handles clipboard/key dispatch.
- Still unsupported spreadsheet contract items:
  - Tab / Shift+Tab / Enter / Shift+Enter navigation
  - Redo
  - Invalid-cell visual delegate
  - Read-only / auto-computed cell visual styling

## Task 2 Result
- Modified file: `ui/calc_window.py`
- AHRI SEER2 table creation now uses `SpreadsheetTableView()` instead of direct `QTableView()`.
- AHRI HSPF2 table creation now uses `SpreadsheetTableView()` instead of direct `QTableView()`.
- Existing factories were preserved:
  - `make_ahri_seer2_table_model()`
  - `make_ahri_hspf2_table_model()`
- Calculation logic was not changed.

## Task 3 Result
- Added/modified tests:
  - Added `tests/test_spreadsheet_table_view.py`
  - Updated `tests/test_app_calculator_ui_smoke.py`
- Covered behavior:
  - `copy_selection_tsv()` returns selected rectangle TSV.
  - `paste_tsv_at_selection()` writes TSV into the model from the selection anchor.
  - `clear_selection()` clears selected cells.
  - `undo_last()` reverts paste and clear groups.
  - Delete key smoke clears selection without clipboard dependency.
  - AHRI SEER2/HSPF2 UI smoke asserts both views are `SpreadsheetTableView`.
- PyQt optional skip:
  - PyQt-dependent tests continue to use `pytest.importorskip("PyQt5")`.

## Task 4 Result
- Modified file: `docs/WORK_PLAN.md`
- Updated the spreadsheet table status to include the common `SpreadsheetTableView` slice.
- Marked AHRI SEER2 and AHRI HSPF2 table slices as completed with `SpreadsheetTableView`.
- Kept ISO16358-2 HSPF mismatch as external user audit pending.
- Next order is:
  - EN14825 horizontal table-input slice
  - invalid-cell visual delegate
  - Tab/Enter navigation strengthening

## Verification
- `python3 -B -m py_compile ui/spreadsheet_table.py ui/calc_window.py tests/test_app_calculator_ui_smoke.py` — passed
- `python3 -B -m pytest tests/test_spreadsheet_table_model.py -q` — 32 passed
- `python3 -B -m pytest tests/test_spreadsheet_table_view.py -q` — 5 passed
- `python3 -B -m pytest tests/test_app_calculator_ui_smoke.py -q` — 13 passed
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` — 3 passed
- `python3 -B -m pytest -q` — 447 passed, 34 xfailed
- Guard check: `rg -n "QTableWidget|setCellWidget" ui/spreadsheet_table.py ui/calc_window.py tests/test_spreadsheet_table_view.py tests/test_app_calculator_ui_smoke.py` returned no matches.

## Known Risks
- `SpreadsheetTableView` currently uses the model's existing snapshot-based undo implementation; redo remains deferred.
- Paste behavior currently follows the existing model helper behavior. Single-value repeat-to-selection and invalid-cell painting remain future slices.
- Keyboard smoke covers Delete only; clipboard dispatch is intentionally kept thin and not tested through the real OS clipboard path.

## Commit / Push
- Source/docs/tests commit: `9e5035b` (`feat: add spreadsheet table view controller`)
- Report commit: separate `report: spreadsheet table view controller` commit.
- Push target: `origin/work/iso-separation-plan`.
