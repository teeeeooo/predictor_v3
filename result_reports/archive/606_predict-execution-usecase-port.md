# Predict Execution UseCase Port

## Goal

Implement `Arc 11 Reopen - Slice 2: Predict Execution UseCase / Execution Port
Correction`.

## Scope

- Added a Qt-free `PredictionUseCase` for request preparation, invalid/running
  row state, service-result application, cancellation rows, and summary
  conversion.
- Added prediction execution port payloads and protocol under
  `apps/predict/ports/`.
- Added `PySidePredictionRunner` as the QThread/PredictionWorker adapter.
- Rewired `PredictionController` to use the usecase and runner adapter instead
  of owning QThread/PredictionWorker lifecycle directly.
- Added non-PySide usecase tests and updated controller/smoke cleanup checks.

## Non-goals

- No core ML behavior changes.
- No mapping schema changes.
- No calculator changes.
- No visual redesign.
- No generated files committed.

## Task Results

- task 1: OK - prediction usecase added without PySide imports.
- task 2: OK - execution port payload/protocol added.
- task 3: OK - PySide/QThread worker lifecycle moved to runner adapter.
- task 4: OK - usecase/controller/worker/smoke tests pass.

## Changed Files

- `apps/predict/application/prediction_usecase.py`
- `apps/predict/ports/prediction_execution_port.py`
- `apps/predict/adapters/pyside_prediction_runner.py`
- `apps/predict/controllers/prediction_controller.py`
- `apps/predict/workers/prediction_worker.py`
- `tools/dev/mock_smoke/run_mock_predict_smoke.py`
- `tests/test_apps_predict_prediction_controller_worker.py`
- `tests/test_apps_predict_prediction_usecase.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `docs/WORK_PLAN.md`

## Verification

- `python3 -B -m py_compile apps/predict/*.py apps/predict/**/*.py tools/dev/mock_smoke/*.py app_predict.py`: OK.
- `python3 -B -m pytest tests -k "predict or mock_smoke or execution or usecase or worker or progress" -q`: OK, 162 passed.
- `python3 -B tools/dev/mock_smoke/run_mock_predict_smoke.py --output-dir /tmp/predictor_v3_mock_smoke --rows 12 --predict-delay-ms 20 --with-cancel --cleanup --force`: OK.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK after regeneration.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator/UI soft warnings only.
- `git diff --check`: OK.

## Structure Warnings

No changed/new source file emits a structure soft warning. Remaining warnings are
pre-existing calculator/UI files outside this slice.

## Read Ledger

- `apps/predict/controllers/prediction_controller.py`: lines 1-340, reason:
  remove controller-owned QThread/worker lifecycle.
- `apps/predict/workers/prediction_worker.py`: lines 1-120, reason: move
  payload contracts to port module while preserving worker behavior.
- `apps/predict/services/prediction_service.py`: lines 1-107, reason: confirm
  service remains Qt-free prediction boundary.
- `apps/predict/adapters/row_to_ml_input_adapter.py`: lines 1-113, reason:
  reuse request preparation adapter in usecase.
- `apps/predict/adapters/prediction_result_adapter.py`: lines 1-85, reason:
  reuse result conversion policy in usecase.
- broad read: none.
- repeated read: `apps/predict/adapters/pyside_prediction_runner.py`, reason:
  ensure terminal signals emit after QThread cleanup.

```yaml
change_gate:
  new_source: small
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

reuse_commonization: reused existing prediction service, row input adapter,
result adapter, and PredictionWorker; new usecase/runner files only separate
application orchestration from PySide execution.

## Known Risks

- Prediction cancellation remains cooperative between rows; this slice does not
  change prediction cancellation semantics.
- Controller still serves the PySide UI surface, but QThread ownership is now
  inside the PySide runner adapter.

## Next Action

Arc 11 Slice 3 - Re-closeout / Train-Predict Manual Smoke Gate.

## Project Memory Delta

- type: decision
  topic: Predict execution usecase port
  content: Predict request preparation/result application now has a UI-neutral usecase and execution payload/port, with QThread lifecycle isolated in the PySide runner adapter.
  keywords: arc11, predict-usecase, prediction-port, pyside-runner, qthread-adapter

## Commit / Push

- Commit: pending.
- Push: deferred until all Arc 11 slices complete.
