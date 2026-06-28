# 570 - Arc 9.5 Unified Result Status Integration

## Goal

Ensure prediction results, row status, and warning/error messages are displayed
inside the unified case table and summarized consistently in the Predict
workspace.

## Scope

- Extend unified table refresh roles for display/background/tooltip updates.
- Include partial/warning result rows in workspace summary counts and badge
  state.
- Add focused result/status integration tests.
- Update Work Plan next action to Slice 9.

## Non-goals

- No ML target list changes.
- No model artifact or prediction service behavior changes.
- No calculator integration.
- No worker/progress implementation.
- No push before Slice 11.

## Boundary Decision

Owner boundary: session summary, unified table model presentation, and workspace
status display.

The table model reads `ResultRow` state and emits presentation-role refreshes;
it still does not call prediction services, mapping repositories, training, or
calculator APIs.

change_gate:
  new_source: none
  hotspot_delta: wiring-only
  code_map_check: skipped
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included

Change gate notes:

- `hotspot_delta`: workspace changes are status summary wiring only.
- `code_map_check`: skipped because no new source file was added in this slice
  and code-map regeneration is deferred to final closeout if still needed.
- `reuse_commonization`: reused existing `ResultRow`, `PredictSession`, and
  `CaseTableModel` boundaries.

Read Ledger:

- `apps/predict/state/predict_session.py`: lines 1-67, reason: add warning
  summary count.
- `apps/predict/ui/tables/case_table_model.py`: lines 1-214, reason: confirm
  result/status display, tooltip, and refresh roles.
- `apps/predict/ui/workspace.py`: lines 260-340, reason: align bottom summary
  and badge with unified status state.
- `apps/predict/adapters/prediction_result_adapter.py`: lines 1-86, reason:
  confirm partial result status source.
- broad read: none.
- repeated read: none.

## Verification

- `python3 -B -m py_compile apps/predict/**/*.py`: passed.
- `python3 -B -m pytest tests -k "predict and (result or status or case_table or workspace)"`: passed, 34 selected.
- `python3 -B tools/check_code_structure.py`: passed with pre-existing
  calculator soft warnings plus code-map freshness reminder; no changed/new
  source file warning.
- `git diff --check`: passed.
- `git status --short`: checked; Slice 8 session/model/workspace/tests, Work
  Plan, and this report were dirty before commit.

Structure Warnings:

- none from `tools/check_code_structure.py` for changed/new source files.

## Known Risks

- Status display strings remain compact raw status labels in this slice; visual
  label polish belongs to Slice 9.

## Commit / Push

- Commit: pending.
- Push: not run; Slice 11 only.

## Next

Slice 9 - Predict Visual Asset Parity Correction.
