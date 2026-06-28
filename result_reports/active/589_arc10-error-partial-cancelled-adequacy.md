# 589 - Arc 10 Error / Partial / Cancelled Handling Adequacy

## Goal

Strengthen Arc 10 worker/progress behavior for model-missing, invalid rows,
partial success/error, cancellation, and running-state mutation protection.

## Scope

- Added worker cancelled case-id payloads.
- Updated controller cancellation handling to record not-yet-run rows as
  row-level `cancelled` results.
- Added cancelled counts/status rendering in session summary, workspace summary,
  and table background handling.
- Added focused tests for model-missing row errors, cancelled row state, and row
  mutation guard while prediction is running.
- Advanced `docs/WORK_PLAN.md` to Slice 7.

## Non-goals

- No core ML behavior changes.
- No feature/preprocess/model artifact changes.
- No calculator changes.
- No visual redesign.

## Verification

- `python3 -B -m py_compile apps/predict/**/*.py apps/train/**/*.py app_predict.py app_train.py`: OK.
- `python3 -B -m pytest tests -k "predict and (worker or progress or controller or result or status or table or workspace)"`: OK, 82 passed and 1259 deselected.
- `python3 -B -m pytest tests/test_apps_train_shell.py`: OK, 7 passed.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings and code-map freshness reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked;
  stale by metadata from prior commits and not regenerated in this slice.
- `python3 -B tools/check_agent_change_gate.py --cached`: OK.
- `git diff --check`: OK.
- `git status --short`: checked before commit.

## Task Results

- task 1: OK - model-missing service outcomes are controlled row-level errors.
- task 2: OK - invalid rows are applied before worker execution and are not
  sent to the worker.
- task 3: OK - mixed complete/error rows preserve per-row state and summary
  counts.
- task 4: OK - cancellation stops future row processing; completed/error rows
  remain, and not-yet-run rows are marked `cancelled`.
- task 5: OK - focused tests cover model missing, invalid skip, mixed results,
  cancellation, double start, row mutation guard, result/status read-only
  behavior, and Train shell construction.

## Read Ledger

- `apps/predict/workers/prediction_worker.py`: relevant summary/cancel ranges,
  reason: cancelled payload.
- `apps/predict/controllers/prediction_controller.py`: relevant cancel handler
  range, reason: row-level cancelled result mutation.
- `apps/predict/state/predict_session.py`: full file, reason: status counts
  owner is small.
- `apps/predict/ui/tables/case_table_model.py`: relevant status/background
  range, reason: cancelled rendering.
- `apps/predict/ui/workspace.py`: relevant summary/badge/running guard range,
  reason: cancelled/running display.
- relevant tests under `tests/test_apps_predict_*`: focused assertion updates.
- broad read: none.
- repeated read: none.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

- `reuse_commonization: reused-existing-owner` because cancelled handling uses
  existing worker/controller/session/result/table owners.

## Structure Warnings

- No changed/new source file emitted structure guard warnings.
- Remaining warnings are pre-existing calculator soft warnings plus code-map
  freshness reminder.

## Known Risks

- Real-model success smoke remains blocked until `model/model.pkl` is present.
- Full manual GUI smoke remains required after Slice 7.

## Commit / Push

- Commit: this report is included in the Slice 6 commit.
- Push: deferred until Slice 7 per user request.

## Project Memory Delta

- none
