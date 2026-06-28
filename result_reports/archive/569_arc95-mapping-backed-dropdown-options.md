# 569 - Arc 9.5 Mapping-backed Dropdown Options

## Goal

Move Predict table dropdowns beyond fallback-only behavior by wiring
mapping-backed base options and row-specific ODU cascade options through
controller/workspace/delegate boundaries.

## Scope

- Store row-specific dependent dropdown options in `InputEditController`.
- Inject a row-aware option provider into `DropdownDelegate`.
- Provide base mapping options from `PredictWorkspace` while preserving
  fallback refrigerant and expansion options.
- Add focused dropdown/mapping tests.
- Add Qt widget cleanup to workspace-facing tests after diagnosing offscreen
  teardown segfaults.
- Update Work Plan next action to Slice 8.

## Non-goals

- No mapping JSON schema changes.
- No table model/view mapping repository imports.
- No ML, calculator, worker/progress, visual polish, or Trainer execution
  changes.
- No push before Slice 11.

## Boundary Decision

Owner boundary: controller/workspace/delegate.

`InputEditController` owns mapping/autofill side effects and row-specific option
state. `PredictWorkspace` owns repository-backed option lookup and injects a
provider. `DropdownDelegate` owns editor construction only and does not know the
repository.

change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  code_map_check: skipped
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included

Change gate notes:

- `hotspot_delta`: accepted for this slice because workspace additions are
  provider wiring. `case_table_view.py` only gained a visible-view guard for
  type-replace editor opening to prevent offscreen teardown failures.
- `code_map_check`: skipped because no new source file was added in this slice
  and code-map regeneration is deferred to final closeout if still needed.
- `reuse_commonization`: reused `core.mapping.autofill`, existing
  `InputEditController`, and `DropdownDelegate`.

Read Ledger:

- `apps/predict/controllers/input_edit_controller.py`: lines 1-44, reason:
  extend existing mapping/autofill controller option state.
- `apps/predict/ui/tables/delegates.py`: lines 1-66, reason: inject provider
  while preserving delegate responsibility.
- `apps/predict/ui/workspace.py`: lines 130-190, reason: configure dropdown
  delegate and provider.
- `core/mapping/autofill.py`: lines 1-139, reason: confirm ODU cascade and stale
  value clear behavior.
- `tests/test_apps_predict_mapping_controller.py`: lines 1-74, reason: mirror
  existing controller mapping tests.
- broad read: none.
- repeated read: none.

## Verification

- `python3 -B -m py_compile apps/predict/**/*.py core/mapping/*.py`: passed.
- `python3 -B -m pytest tests -k "predict and (mapping or dropdown or cascade or table)"`: passed, 39 selected.
- `python3 -B tools/check_code_structure.py`: passed with pre-existing
  calculator soft warnings plus code-map freshness reminder; no changed/new
  source file warning.
- `git diff --check`: passed.
- `git status --short`: checked; Slice 7 controller/delegate/workspace/view
  guard/tests, Work Plan, and this report were dirty before commit.

Validation note:

- The broad focused pytest initially exited 139 after all selected tests passed
  because offscreen Qt widgets were left for process teardown. Added explicit
  cleanup to workspace-facing tests and reran the exact selector successfully.

Structure Warnings:

- none from `tools/check_code_structure.py` for changed/new source files.

Warning Triage:

- `apps/predict/ui/tables/case_table_view.py` is 240 LOC and remains under the
  250 LOC soft split threshold. Accepted because this slice did not add mapping
  responsibility to the view.

## Known Risks

- Per-row options are updated after controller-handled edits; future import
  flows must route edits through the same controller boundary to keep option
  state current.

## Commit / Push

- Commit: pending.
- Push: not run; Slice 11 only.

## Next

Slice 8 - Unified Result / Status Integration.
