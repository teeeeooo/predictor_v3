# 581 Arc 9.5 Second Correction Closeout

## Goal

- Close the Arc 9.5 second correction implementation slices with automated
  regression coverage and accurate project-state docs.

## Scope

- Updated `docs/WORK_PLAN.md`, `project_brief.md`, and `project_log.md` to
  record automated correction complete with user manual smoke still pending.
- Verified the focused correction suites and production source guards covering
  the manual-smoke failure classes.

## Non-goals

- Arc 10 was not reactivated because user manual smoke acceptance is still
  pending.
- No source behavior changed in this closeout docs slice.

## Verification

- `PYTHONPATH=. QT_QPA_PLATFORM=offscreen pytest -q tests/test_apps_predict_workspace_unified_table.py tests/test_apps_predict_mapping_backed_dropdown.py tests/test_apps_predict_spreadsheet_ux.py tests/test_apps_predict_unified_result_status.py tests/test_apps_train_shell.py` - OK, 40 passed.
- `rg -n "ColumnGroupBand|\\.mapping_repository\\.load\\(\\)|QTableWidget|QTableWidgetItem" apps/predict/ui/workspace.py apps/predict/ui/tables apps/train/ui || true` - OK, no production matches.
- `python3 -B tools/check_code_structure.py` - OK with pre-existing unrelated calculator soft warnings and code-map freshness reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` - STALE; not regenerated in this closeout docs slice.
- `git diff --check` - OK.

## Task Results

- Slice A recorded manual-smoke rejection and reset project state.
- Slice B replaced the detached group band with a table-linked grouped header.
- Slice C made dropdown editors editable with autocomplete and corrected
  first-click selection behavior.
- Slice D moved base dropdown option lookup behind an app-side adapter.
- Slice E removed duplicated embedded Predict title/top status in Trainer.
- Slice F replaced Trainer `QTableWidget` surfaces with model/view tables.
- Slice G moved Predict row lifecycle mutations behind a controller and cleared
  undo history on reset.
- Slice H keeps Arc 10 on hold pending user manual smoke.

## Reference Parity / Change Gate

- Existing Predict/Train package owners were reused throughout the correction.
- New files were placed under feature owner packages:
  `apps/predict/ui/tables/`, `apps/predict/adapters/`,
  `apps/predict/controllers/`, and `apps/train/ui/models/`.
- `code_map_check`: checked; stale before and during this correction, not
  regenerated because the reference map was already stale and correction slices
  were focused local owner changes.

## Structure Warnings

- Changed/new source files did not emit LOC/class warnings.
- Existing unrelated calculator soft warnings and code-map freshness warning
  remain.

## Changed Files

- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/active/581_arc95-second-correction-closeout.md`

## Known Failures / Risks

- User manual smoke is still required before Arc 9.5 can be accepted and Arc 10
  can resume.
- Real-model prediction success smoke remains blocked by absent `model/model.pkl`.
- Active report count exceeds lifecycle threshold; cleanup should be handled as
  a separate follow-up.

## Commit / Push

- Commit: pending for this slice.
- Push: deferred until after this slice commit, then required by user request.

## Project Memory Delta

- type: decision
- topic: Arc 9.5 second correction
- content: Arc 9.5 automated correction is complete, but Arc 10 remains on hold until user manual smoke accepts the corrected surface.
- keywords: arc95, manual-smoke, arc10-hold, predict-train-ui
