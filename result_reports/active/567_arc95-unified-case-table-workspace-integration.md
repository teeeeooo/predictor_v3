# 567 - Arc 9.5 Unified Case Table Workspace Integration

## Goal

Switch the Predict workspace from split input/result tables to one unified case
table surface where one visible row represents one prediction case.

## Scope

- Add `CaseTableView`.
- Wire `PredictWorkspace` to `CaseTableModel` and `CaseTableView`.
- Remove active workspace dependency on `QSplitter` and
  `TableSelectionScrollSync`.
- Keep result/status cells selectable and copyable but read-only.
- Add workspace integration tests and update the existing workspace smoke.
- Update Work Plan next action to Slice 6.

## Non-goals

- No grouped undo, full navigation override, or type-replace state machine.
- No mapping-backed dropdown provider update.
- No split table file deletion.
- No ML, mapping schema, calculator, worker/progress, or Trainer execution
  changes.
- No push before Slice 11.

## Boundary Decision

Owner boundary: `apps/predict/ui/`.

The workspace owns widget composition and command wiring only. The unified
table model owns presentation data roles. Mapping/autofill remains controller
owned, and prediction execution remains controller/service owned.

change_gate:
  new_source: small
  hotspot_delta: wiring-only
  code_map_check: skipped
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included

Change gate notes:

- `hotspot_delta`: workspace edit is wiring-only replacement of split table
  composition with the unified table.
- `code_map_check`: skipped because the prompt limits Slice 5 modifications to
  workspace/view/tests/report; code-map regeneration is deferred to final
  closeout if still needed.
- `reuse_commonization`: reused existing table view clipboard patterns,
  command bar wiring, row lifecycle, and controller boundaries.

Read Ledger:

- `apps/predict/ui/workspace.py`: lines 1-366, reason: replace split table
  composition and row lifecycle wiring.
- `apps/predict/ui/tables/input_table_view.py`: lines 1-105, reason: reuse
  clipboard/paste/clear interaction baseline for unified view.
- `apps/predict/ui/tables/result_table_view.py`: lines 1-44, reason: preserve
  read-only copy behavior.
- `apps/predict/ui/tables/clipboard.py`: lines 1-31, reason: reuse TSV helper.
- `apps/predict/ui/tables/delegates.py`: lines 1-66, reason: preserve dropdown
  delegate wiring.
- `apps/predict/ui/command_bar.py`: lines 1-43, reason: adjust copy action
  label/behavior.
- broad read: `apps/predict/ui/workspace.py` full file, blocker: workspace
  split-table composition methods were distributed through constructor,
  configuration, row lifecycle, refresh, and command handlers.
- repeated read: none.

## Verification

- `python3 -B -m py_compile apps/predict/**/*.py apps/common/**/*.py app_predict.py`: passed.
- `python3 -B -m pytest tests -k "predict and (workspace or case_table or table or schema)"`: passed, 37 selected.
- `python3 -B -c "from PySide6.QtWidgets import QApplication; import os; os.environ.setdefault('QT_QPA_PLATFORM','offscreen'); app=QApplication.instance() or QApplication([]); from apps.predict.ui.workspace import PredictWorkspace; w=PredictWorkspace(); assert w is not None"`: passed; emitted a Qt font alias performance warning only.
- `python3 -B tools/check_code_structure.py`: passed with pre-existing
  calculator soft warnings plus code-map freshness reminder; no changed/new
  source file warning.
- `git diff --check`: passed.
- `git status --short`: checked; Slice 5 workspace/view/tests, Work Plan, and
  this report were dirty before commit.

Structure Warnings:

- none for changed/new source files.

## Known Risks

- Group band is a lightweight visual affordance in this slice; detailed visual
  parity belongs to Slice 9.
- Spreadsheet undo/navigation/type-replace completion belongs to Slice 6.

## Commit / Push

- Commit: pending.
- Push: not run; Slice 11 only.

## Next

Slice 6 - Spreadsheet UX Completion.
