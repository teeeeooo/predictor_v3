# 575 Arc 9.5 Table-linked Group Header

## Goal

- Correct the Arc 9.5 fake unified-table group header so group labels follow the
  real `QTableView` header geometry during horizontal scroll and column resize.

## Scope

- Added a Predict table View helper: `apps/predict/ui/tables/group_header.py`.
- Replaced the detached `ColumnGroupBand` construction in `PredictWorkspace`
  with `TableLinkedGroupHeader`.
- Added focused offscreen regression coverage for scroll, resize, and source
  guard behavior.

## Non-goals

- No schema, ML, mapping, calculator, or prediction execution changes.
- Dropdown editor, mapping option boundary, Train embedding, Trainer table MVC,
  and workspace command/state cleanup remain later slices.

## Verification

- `PYTHONPATH=. QT_QPA_PLATFORM=offscreen pytest -q tests/test_apps_predict_workspace_unified_table.py` - OK, 7 passed.
- `python3 -B tools/check_code_structure.py` - OK with pre-existing soft warnings outside this slice and code-map freshness reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` - STALE; not regenerated in this focused UI slice.
- `git diff --check` - OK.

## Task Results

- `TableLinkedGroupHeader` computes group rectangles from
  `horizontalHeader().sectionViewportPosition()` and `sectionSize()`.
- Header labels update on horizontal scroll, section resize/move, header
  geometry changes, and model column/reset signals.
- Visible label geometry is clipped to the table viewport, while full
  section-derived geometry remains testable through `group_column_rects()`.

## Reference Parity / Change Gate

- Existing Predict table view/model/delegate boundaries were reused; no core or
  schema owner was changed.
- The new file is owned by the Predict table View package because the behavior
  is table-header presentation and depends on Qt header geometry.
- Reuse/commonization decision: no broader project helper was reused because
  this is the first PySide6 grouped-header helper and the behavior depends on
  unified case-table column groups. A future repeated grouped-header surface can
  promote it after another owner appears.
- `code_map_check`: checked; stale before this slice, not regenerated because
  the slice adds a small local View helper and the map was already stale.

## Structure Warnings

- No changed/new source file emitted a LOC/class warning.
- Existing unrelated warnings remain in calculator files and code-map freshness.

## Changed Files

- `apps/predict/ui/tables/group_header.py`
- `apps/predict/ui/workspace.py`
- `tests/test_apps_predict_workspace_unified_table.py`

## Known Risks

- Offscreen tests validate geometry linkage, not final human visual polish.
- Later dropdown/state-machine work may add more table interaction coverage.

## Commit / Push

- Commit: pending for this slice.
- Push: deferred per user request until all slices complete.

## Project Memory Delta

- none
