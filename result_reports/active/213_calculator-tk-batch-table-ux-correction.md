# 213 — calculator_tk Batch Table UX Correction

## Goal

Correct the Hong Kong CSPF batch dialog table UX using the 212 Option D decision: keep the batch model/spec/handler boundary, but replace the Entry/Label-grid interaction surface with a reusable Tk batch table adapter/controller aligned with the Excel-like table contract.

## Preflight

- Branch: `main`.
- Prior decision: 212 recommended a batch-oriented reusable Tk table adapter/controller instead of patching the old `BatchCaseTable` or forcing the matrix-shaped `MetricInputTable`.
- Preserved boundary: `BatchProfileSpec`, `BatchColumnSpec`, `BatchTableModel`, and `HongKongCspfBatchHandler` remain toolkit/profile boundary owners.
- Single-case CSPF/HSPF tables remain on `MetricInputTable` and `ExcelLikeTableController`; this task did not modify those owners.

## Modified Files

- `ui_tk/batch_table.py`
- `ui_tk/batch_table_controller.py`
- `ui_tk/batch_case_table.py`
- `ui_tk/batch_controller.py`
- `ui_tk/sections/hong_kong_cspf_batch_spec.py`
- `ui_tk/sections/hong_kong_cspf_batch_section.py`
- `tests/test_ui_tk_batch_table_controller.py`
- `tests/test_ui_tk_hong_kong_cspf_batch_spec.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/WORK_PLAN.md`

## Implementation

- Added `ui_tk/batch_table.py` for batch table helper contracts: grid addresses, role-aware paste/clear target resolution, copy selection bounds, and navigation helpers.
- Added `ui_tk/batch_table_controller.py` for Tk interaction behavior:
  - rectangular selection
  - Ctrl/Cmd+C TSV copy
  - Ctrl/Cmd+V TSV paste into editable cells only
  - Delete/Backspace clear on editable cells only
  - Ctrl/Cmd+Z undo for grouped clear/paste/edit snapshots
  - Tab/Shift+Tab/Enter/Shift+Enter navigation
  - click then type replace-on-type for input cells
  - result cells are selectable/copyable but not directly editable
- Reworked `BatchCaseTable` into a table surface with cell frames, cell roles, text-row snapshot/restore, editable batch updates, and result read-only cells.
- Updated `BatchCalculationController` from explicit-run orchestration to recalculation summary orchestration.

## Hong Kong CSPF Policy

- Removed the visible `Status` column from the Hong Kong CSPF batch spec.
- Default rows are now 5 rows: the first row remains a sample case for verification, rows 2-5 are blank starter cases.
- `Run Batch` and `Clear Results` were removed from the dialog.
- Input changes, paste, clear, row add, and row remove now schedule debounced auto-calculation.
- Blank and partial rows leave `CSPF` / `CSEC` blank.
- Invalid rows leave `CSPF` / `CSEC` blank and do not stop other rows from calculating.
- Valid rows still use the existing single-case Hong Kong CSPF core path through profile resolver, dispatcher, and `build_cspf_input`.

## Preserved Flow

- Hong Kong CSPF batch remains a dialog opened from the CSPF page, not a metric notebook tab.
- Existing single-case Hong Kong CSPF immediate calculation flow is unchanged.
- Hong Kong HSPF and the 207 load-line correction were not modified.

## Verification

- `python -m pytest -q tests/test_ui_tk_batch_models.py` — passed.
- `python -m pytest -q tests/test_ui_tk_hong_kong_cspf_batch_spec.py` — passed.
- `python -m pytest -q tests/test_ui_tk_batch_table_controller.py` — passed.
- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py` — passed with Tk-dependent skips in the headless environment.
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py` — passed with Tk-dependent skips in the headless environment.
- `python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py` — passed.
- `python3 -B tools/check_code_structure.py` — passed with the pre-existing `ui_tk/sections/bin_detail_panel.py` LOC soft warning.
- `git diff --check` — passed.

## Manual Smoke Needed

Windows GUI smoke is still needed for actual interaction feel:

- Open Hong Kong CSPF, click `Multi 입력`.
- Confirm no `Run Batch`, no `Clear Results`, no visible `Status` column.
- Confirm 5 default rows and the first sample row auto-calculates.
- Paste Excel TSV into input columns.
- Copy a rectangle including `CSPF` / `CSEC`.
- Delete/Backspace clears only input cells.
- Ctrl/Cmd+Z restores grouped paste/clear/edit.
- Tab/Shift+Tab/Enter/Shift+Enter navigation feels table-like.
- Click then type replaces the active input cell.
- Result cells remain selectable/copyable but not user-editable.
- Main calculator window size is unaffected before the dialog opens.

## Excluded

- No calculator core formula changes.
- No region config, golden expected, or fixture changes.
- No HSPF, EN/AHRI/KS batch implementation.
- No detail/bin schema, graph/export, formula trace, or C# WPF work.
- No `docs/designs` changes.

## Next Action

Close out Windows GUI smoke for the corrected Hong Kong CSPF batch table UX, then proceed to common detail/bin result schema foundation.
