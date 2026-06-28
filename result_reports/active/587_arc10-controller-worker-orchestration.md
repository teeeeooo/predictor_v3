# 587 - Arc 10 Controller Worker Orchestration

## Goal

Move prediction run orchestration behind `PredictionController.start_*()` so
the controller owns request preparation, worker thread lifecycle, row-result
session updates, and cancellation requests.

## Scope

- Added `start_all()`, `start_case_ids()`, `cancel()`, async callbacks, and
  QThread/worker lifecycle ownership to
  `apps/predict/controllers/prediction_controller.py`.
- Kept service/adapters as the prediction and result-mapping boundaries.
- Updated `PredictWorkspace._run_prediction()` to use `start_all()` and finish
  via callback with minimal UI changes.
- Added focused controller-worker orchestration tests.
- Advanced `docs/WORK_PLAN.md` to Slice 5.

## Non-goals

- No command-bar cancel/progress UI.
- No broad workspace rewrite.
- No ML behavior, mapping schema, calculator, model artifact, or unified table
  UX changes.

## Verification

- `python3 -B -m py_compile apps/predict/controllers/*.py apps/predict/workers/*.py apps/predict/ui/workspace.py`: OK.
- `python3 -B -m pytest tests -k "predict and (controller or worker or progress)"`: OK, 20 passed and 1314 deselected after fixes.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings and code-map freshness reminder; no changed/new source warning.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked;
  stale by metadata from prior commits and not regenerated in this slice.
- `python3 -B tools/check_agent_change_gate.py --cached`: OK.
- `git diff --check`: OK.
- `git status --short`: checked before commit.

## Task Results

- task 1: OK - controller exposes async `start_all()`, `start_case_ids()`,
  `cancel()`, and `is_running`; invalid rows are applied without worker calls,
  valid rows are marked running before worker start, and double-start is
  rejected while running.
- task 2: OK - controller creates the QThread/worker pair, wires
  row/progress/finish/cancel/failure signals, quits the thread on terminal
  worker signals, and clears references after the thread finishes.
- task 3: OK - tests cover session row updates, double-start rejection,
  invalid-row skip, cancellation, mixed error/complete summary, and worker
  no-session mutation.

## Notable Fixes During Validation

- Initial controller test fake service returned only one target, which correctly
  produced `partial` rows. The fake service now returns all `TARGETS` for
  complete rows.
- A `QThread.deleteLater()` cleanup path segfaulted during pytest. Cleanup now
  clears controller references on the next event-loop tick after `finished`
  instead of deleting the thread wrapper during its own signal handling.

## Read Ledger

- `apps/predict/controllers/prediction_controller.py`: full file, reason:
  orchestration owner under active edit.
- `apps/predict/workers/prediction_worker.py`: full file, reason: worker signal
  contract used by controller.
- `apps/predict/ui/workspace.py`: lines 200-340, reason: minimal run-path
  integration.
- `tests/test_apps_predict_prediction_worker.py`: full file, reason: worker
  signal test patterns reused for controller tests.
- `tests/test_apps_predict_prediction_service_status.py`: full file, reason:
  controller construction and model-status fixture pattern.
- broad read: none.
- repeated read: none.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

- `new_source: small` because the new controller test module is focused.
- `hotspot_delta: accepted-for-slice` because this slice explicitly assigns
  worker lifecycle orchestration to `PredictionController`; if Slice 5 adds
  more controller responsibility, split pressure should be reassessed before
  continuing.
- `reuse_commonization: reused-existing-owner` because controller uses existing
  row adapter, result adapter, service, and worker owners instead of creating a
  generic worker framework.

## Structure Warnings

- No changed/new source file emitted structure guard LOC/class warnings.
- `PredictionController` grew for the explicit orchestration slice; further
  lifecycle or UI-state accumulation should trigger a split audit.

## Known Risks

- Workspace progress/cancel controls are still minimal and move to Slice 5.
- Row-level cancelled presentation remains a later result/status handling
  decision.
- Real-model success smoke remains blocked until `model/model.pkl` is present.

## Commit / Push

- Commit: this report is included in the Slice 4 commit.
- Push: deferred until Slice 7 per user request.

## Project Memory Delta

- none
