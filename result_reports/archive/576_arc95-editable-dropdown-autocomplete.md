# 576 Arc 9.5 Editable Dropdown Autocomplete

## Goal

- Correct Predict dropdown cells so they support direct typing, autocomplete,
  typed-value commit, and spreadsheet-style first-click selection behavior.

## Scope

- Updated `DropdownDelegate` to create editable `QComboBox` editors with
  case-insensitive popup completers.
- Removed delegate-level whole-cell click-to-popup behavior.
- Updated `CaseTableView` so first click selects and a later same-cell click
  enters edit mode.
- Added focused tests for editable dropdown editor construction, typed ODU
  commit/autofill side effects, and mouse-driven edit lifecycle.

## Non-goals

- Mapping option lookup still lives in `PredictWorkspace`; that boundary is
  corrected in the next slice.
- No ML, calculator, schema, or result-surface changes.

## Verification

- `PYTHONPATH=. QT_QPA_PLATFORM=offscreen pytest -q tests/test_apps_predict_mapping_backed_dropdown.py tests/test_apps_predict_spreadsheet_ux.py` - OK, 15 passed.
- `python3 -B tools/check_code_structure.py` - OK with pre-existing unrelated soft warnings and code-map freshness reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` - STALE; not regenerated in this focused interaction slice.
- `git diff --check` - OK.

## Task Results

- Dropdown editor is editable, accepts custom typed text, and keeps mapping
  options available through an attached completer.
- Typed dropdown values now commit through `CaseTableModel.setData()`, so the
  existing `InputEditController.handle_cell_edited()` autofill path runs.
- The table no longer uses `SelectedClicked`; first click remains selection
  mode and same-cell click enters edit mode.

## Reference Parity / Change Gate

- Existing delegate and table view owners were reused.
- Reuse/commonization decision: this is local Predict table interaction
  behavior with no sibling PySide6 dropdown table yet. The path remains inside
  `apps/predict/ui/tables/` until another owner needs the same policy.
- `code_map_check`: checked; stale before this slice, not regenerated because
  the source change is focused and local.

## Structure Warnings

- No changed/new source file emitted a LOC/class warning.
- Existing unrelated calculator and code-map freshness warnings remain.

## Changed Files

- `apps/predict/ui/tables/delegates.py`
- `apps/predict/ui/tables/case_table_view.py`
- `tests/test_apps_predict_mapping_backed_dropdown.py`
- `tests/test_apps_predict_spreadsheet_ux.py`

## Known Risks

- Dropdown arrow-specific popup affordance is not separately implemented in
  this slice; typing/autocomplete and same-cell edit entry are covered.
- Broader table state-machine edge cases remain covered by later adequacy work.

## Commit / Push

- Commit: pending for this slice.
- Push: deferred per user request until all slices complete.

## Project Memory Delta

- none
