# 586 - Arc 10 Prediction Worker Implementation

## Goal

Implement the focused PredictionWorker foundation that can process validated
prediction requests, emit row/progress/final signals, and support cooperative
cancellation between rows.

## Scope

- Added `PredictionWorker(QObject)` to
  `apps/predict/workers/prediction_worker.py`.
- Exported the worker from `apps/predict/workers/__init__.py`.
- Added `tests/test_apps_predict_prediction_worker.py`.
- Updated the worker contract tests for the new low-Qt worker boundary.
- Advanced `docs/WORK_PLAN.md` to Slice 4.

## Non-goals

- No controller QThread orchestration.
- No workspace or command-bar integration.
- No ML behavior, model artifact, mapping schema, calculator, or unified table
  UX changes.

## Verification

- `python3 -B -m py_compile apps/predict/workers/*.py`: OK.
- `python3 -B -m pytest tests/test_apps_predict_prediction_worker.py tests/test_apps_predict_worker_contracts.py`: OK, 10 passed.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings and code-map freshness reminder; no changed/new source warning.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked;
  stale by metadata from prior commits and not regenerated in this slice.
- `python3 -B tools/check_agent_change_gate.py --cached`: OK.
- `git diff --check`: OK.
- `git status --short`: checked before commit.

## Task Results

- task 1: OK - worker accepts a `PredictionJob`, calls
  `PredictionService.predict_one()` per request, emits `row_result`,
  `progress`, and final `finished` summary signals.
- task 2: OK - `cancel()` sets a cooperative flag checked before the next row
  and after each processed row; no thread termination pattern is used.
- task 3: OK - headless tests cover complete path, row error continuation,
  cancel-before-run, cancel-after-first-row, no widget/session imports, and no
  session mutation.

## Read Ledger

- `apps/predict/workers/prediction_worker.py`: full file, reason: worker owner
  implementation is under 120 LOC.
- `apps/predict/workers/__init__.py`: full file, reason: export surface.
- `tests/test_apps_predict_worker_contracts.py`: full file, reason: contract
  test update target is small.
- `apps/predict/services/prediction_service.py`: lines 1-120, reason: worker
  service call contract.
- broad read: none.
- repeated read: none.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

- `new_source: small` because the new test module is focused and the worker
  implementation stays inside the existing approved worker owner.
- `reuse_commonization: reused-existing-owner` because the worker delegates
  prediction to `PredictionService` and keeps result presentation/session
  mutation outside the worker.

## Structure Warnings

- No changed/new source file emitted LOC/class warnings.
- Worker imports `PySide6.QtCore` only; it does not import widgets or
  `PredictSession`.

## Known Risks

- Worker is callable and signal-based, but QThread lifecycle ownership starts in
  Slice 4.
- Cancelled not-yet-run rows are summarized by the worker; row-level cancelled
  presentation is still a controller/result-adapter decision in later slices.
- Real-model success smoke remains blocked until `model/model.pkl` is present.

## Commit / Push

- Commit: this report is included in the Slice 3 commit.
- Push: deferred until Slice 7 per user request.

## Project Memory Delta

- none
