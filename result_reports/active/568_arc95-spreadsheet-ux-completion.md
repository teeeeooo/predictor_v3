# 568 - Arc 9.5 Spreadsheet UX Completion

## Goal

Complete the unified case table spreadsheet baseline that was previously
deferred: grouped undo, Tab/Enter navigation, click/type replace-on-type,
selected-range paste fill, and read-only mutation prevention.

## Scope

- Add grouped undo helper for edit/paste/clear actions.
- Extend `CaseTableView` copy/paste/clear/key handling.
- Implement Tab / Shift+Tab / Enter / Shift+Enter navigation.
- Implement printable-key whole-cell replacement for the active editable cell.
- Add focused spreadsheet UX tests.
- Update Work Plan next action to Slice 7.

## Non-goals

- No mapping-backed option provider changes.
- No visual parity polish.
- No ML, mapping schema, calculator, worker/progress, or Trainer execution
  changes.
- No push before Slice 11.

## Boundary Decision

Owner boundary: `apps/predict/ui/tables/`.

The view owns interaction behavior. The undo helper stores UI edit groups only;
it does not own business logic. The model remains the mutation guard through
its editability flags.

Navigation decision:

- Tab/Enter traverse selectable cells, including read-only result/status cells.
- Mutation paths still skip read-only cells.

change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  code_map_check: skipped
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included

Change gate notes:

- `hotspot_delta`: accepted for this slice because Slice 6 explicitly completes
  the table interaction baseline in the existing unified view owner.
- `code_map_check`: skipped because the prompt limits Slice 6 modifications to
  table interaction files/tests/report; code-map regeneration is deferred to
  final closeout if still needed.
- `reuse_commonization`: reused existing clipboard helpers and table model
  editability flags.

Read Ledger:

- `apps/predict/ui/tables/case_table_view.py`: lines 1-114, reason: extend
  unified table interaction behavior.
- `apps/predict/ui/tables/clipboard.py`: lines 1-31, reason: preserve TSV
  parsing/formatting helpers.
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`: lines 60-235, reason:
  confirm baseline paste, clear, navigation, undo, and edit/replace behavior.
- broad read: none.
- repeated read: none.

## Verification

- `python3 -B -m py_compile apps/predict/ui/tables/*.py`: passed.
- `python3 -B -m pytest tests/test_apps_predict_spreadsheet_ux.py tests/test_apps_predict_workspace_unified_table.py`: passed, 12 tests.
- `python3 -B tools/check_code_structure.py`: passed with pre-existing
  calculator soft warnings plus code-map freshness reminder; no changed/new
  source file warning.
- `git diff --check`: passed.
- `git status --short`: checked; Slice 6 view/undo/tests, Work Plan, and this
  report were dirty before commit.

Structure Warnings:

- none from `tools/check_code_structure.py` for changed/new source files.

Warning Triage:

- `apps/predict/ui/tables/case_table_view.py` is 239 LOC after completing the
  interaction baseline. Accepted for this slice because selection, clipboard,
  clear, undo, navigation, and type-replace are one cohesive table interaction
  owner. Slice 7 should keep mapping option-provider logic in
  delegate/workspace/controller boundaries rather than adding mapping
  responsibility to this view.

## Known Risks

- Partial-edit undo through native Qt editors is not separately asserted here;
  whole-cell replacement, paste, and clear are covered by focused tests.
- Redo remains optional and is not implemented in this slice.

## Commit / Push

- Commit: pending.
- Push: not run; Slice 11 only.

## Next

Slice 7 - Mapping-backed Dropdown / Per-row Option Update.
