# 573 - Arc 9.5 Final Acceptance Closeout

## Goal

Close Arc 9.5 Reopen after verifying unified case table visual/table parity,
spreadsheet UX baseline completion, mapping-backed dropdown behavior, and
Trainer visual parity.

## Scope

- Confirm Slice 1-10 commits are present.
- Confirm the local B-option `docs/designs/assets/predict_ref_img.png`
  reference remains the Predict acceptance reference.
- Record Arc 9.5 acceptance checklist.
- Run final focused validation.
- Update closeout docs so Arc 10 Prediction Worker / Progress is next.
- Commit final docs/report changes and push accumulated Slice 1-11 commits.

## Slice Commits

- Slice 1: `0fff2aa docs(predict): reopen arc95 unified case table criteria`
- Slice 2: `455e37e docs(predict): define unified case table contract`
- Slice 3: `e33303c feat(predict): add unified case table schema adapter`
- Slice 4: `59dbd06 feat(predict): add unified case table model`
- Slice 5: `62def20 feat(predict): switch workspace to unified case table`
- Slice 6: `de6899f feat(predict): complete unified table spreadsheet interactions`
- Slice 7: `9ee986e feat(predict): add mapping backed dropdown options`
- Slice 8: `bb7d6d3 feat(predict): integrate unified table result statuses`
- Slice 9: `515a211 style(predict): correct unified table visual parity`
- Slice 10: `0e605ce style(train): correct trainer visual parity`
- Slice 11: final docs/report commit recorded in the final user-facing
  closeout response to avoid a self-referential report hash update loop.

## Modified Files By Category

- Predict unified table contract/model/view/workspace:
  `apps/predict/schema/case_table_schema_adapter.py`,
  `apps/predict/ui/tables/case_table_model.py`,
  `apps/predict/ui/tables/case_table_view.py`,
  `apps/predict/ui/workspace.py`.
- Spreadsheet UX and mapping presentation:
  `apps/predict/ui/tables/undo.py`,
  `apps/predict/controllers/input_edit_controller.py`,
  `apps/predict/ui/tables/delegates.py`.
- Result/status/session presentation:
  `apps/predict/state/predict_session.py`,
  `apps/predict/ui/status_widgets.py`.
- Shared/Trainer visual surfaces:
  `ui_common/visual_tokens.py`,
  `apps/common/ui/style.py`,
  `apps/train/ui/shell.py`,
  `apps/train/ui/train_model_panel.py`,
  `apps/train/ui/data_mapping_panel.py`.
- Tests:
  focused predict/train/table/mapping/style tests under `tests/`.
- Docs/reports:
  `project_brief.md`, `docs/WORK_PLAN.md`, `project_log.md`,
  `docs/architecture/pyside6_train_predict_architecture.md`,
  `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`,
  active reports `563` through `573`.

## Acceptance Checklist

Unified case table:

- OK - one visible row represents one prediction case.
- OK - input, auto-fill/calculated, prediction result, and status/warning
  columns are grouped in one table.
- OK - internal `case_id` remains hidden identity, not a visible column.
- OK - result/status columns are read-only, selectable, and copyable.

Spreadsheet UX:

- OK - rectangular selection.
- OK - copy TSV.
- OK - paste TSV.
- OK - selected-range fill.
- OK - Delete/Backspace clear.
- OK - grouped undo.
- OK - Tab/Shift+Tab/Enter/Shift+Enter navigation.
- OK - click/type replace-on-type.
- OK - read-only mutation prevention.

Mapping:

- OK - mapping-backed per-row dropdown option updates.
- OK - ODU cascade stale value clear.
- OK - missing mapping controlled status.

Visual:

- OK - local B-option `predict_ref_img.png` reference reflected without
  reverting to split table history.
- OK - color intensity is reduced and not excessive.
- OK - command/status grouping is coherent.

Trainer:

- OK - Predict tab reuses unified `PredictWorkspace`.
- OK - Trainer visual hierarchy is corrected.
- OK - Trainer execution remains intentionally deferred.

## Validation

- `python3 -B -m py_compile apps/predict/**/*.py apps/train/**/*.py apps/common/**/*.py ui_common/*.py app_predict.py app_train.py app_calculator.py`: passed.
- `python3 -B -m pytest tests -k "predict or train or visual or table or mapping or schema"`: passed, 475 selected.
- `python3 -B tools/check_code_structure.py`: passed with pre-existing
  calculator soft warnings plus code-map freshness reminder; no changed/new
  source file warning.
- `git diff --check`: passed.
- `git status --short`: checked; closeout docs and this report were dirty
  before final commit.

## Manual Smoke Needed

- Real-model prediction success smoke is not claimed because this checkout does
  not include a valid `model/model.pkl` artifact.
- Worker/progress/cancel behavior is not implemented in Arc 9.5 and moves to
  Arc 10.
- Trainer execution foundation is not implemented in Arc 9.5 and remains Arc
  11 scope.

## Excluded Scope

- No ML algorithm, feature list, preprocessing calculation, model artifact, or
  public result contract changes.
- No mapping JSON schema changes.
- No calculator formula/config/fixture/golden/public result changes.
- No Arc 10 worker/progress implementation.
- No Trainer execution implementation.
- No legacy `ui/` restoration, PyQt5 production dependency, root compatibility
  wrappers, or flat root `core/` owner additions.

## Docs Closeout

- `project_brief.md`: Arc 9.5 marked complete and current phase moved to Arc
  10.
- `docs/WORK_PLAN.md`: next action moved to Arc 10 - Prediction Worker /
  Progress.
- `project_log.md`: compact Arc 9.5 closeout milestone entry added.

## Push Result

- Final publication status is recorded in the final user-facing closeout
  response per the report workflow, avoiding a self-referential report update
  loop.

## Next

Arc 10 - Prediction Worker / Progress.
