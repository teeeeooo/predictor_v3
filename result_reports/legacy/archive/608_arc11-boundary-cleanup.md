# Arc 11 Boundary Cleanup

## Goal

Finalize remaining Train/Predict execution boundary cleanup before moving to
Arc 12.

## Scope

- Removed `PredictionController`'s direct dependency on the concrete
  `PySidePredictionRunner`.
- Moved PySide runner creation to `PredictWorkspace` composition wiring.
- Deleted the legacy cooperative `TrainWorker` direct execution path and its
  focused tests.
- Disabled default direct `TrainingService.train()` production execution; only
  explicitly injected test/dev backends can use it.
- Routed optional real-core Train smoke through `QProcessTrainingRunner`.
- Kept Train/Predict mock E2E and Predict cancel smoke passing.

## Non-goals

- No core ML algorithm, preprocessing, feature list, or target registry changes.
- No mapping schema changes.
- No calculator changes.
- No UI visual redesign.
- No generated mock files committed.
- No broad report lifecycle cleanup.

## Task Results

- task 1: OK - `PredictionController` concrete PySide dependency removed.
- task 2: OK - PySide runner wiring moved to `PredictWorkspace`.
- task 3: OK - legacy `TrainWorker` path deleted.
- task 4: OK - `TrainingService.train()` default direct production execution
  disabled; optional real-core smoke uses QProcess runner path.
- task 5: OK - tests and smokes pass.

## Changed Files

- `apps/predict/controllers/prediction_controller.py`
- `apps/predict/ui/workspace.py`
- `apps/train/services/training_service.py`
- `apps/train/workers/__init__.py`
- `apps/train/workers/train_worker.py`
- `tools/dev/mock_smoke/run_mock_predict_smoke.py`
- `tools/dev/mock_smoke/run_mock_train_execution_smoke.py`
- `tests/test_apps_predict_prediction_controller_worker.py`
- `tests/test_apps_train_training_service.py`
- `tests/test_apps_train_worker.py`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`

## Verification

- `python3 -B -m py_compile apps/train/**/*.py apps/predict/**/*.py tools/dev/mock_smoke/*.py app_train.py app_predict.py`: OK.
- `python3 -B -m pytest tests -k "train or predict or mock_smoke or execution or usecase or process or qprocess" -q`: OK, 172 passed.
- `python3 -B tools/dev/mock_smoke/run_mock_train_execution_smoke.py --output-dir /tmp/predictor_v3_mock_smoke --rows 12 --cleanup --force`: OK.
- `python3 -B tools/dev/mock_smoke/run_mock_predict_smoke.py --output-dir /tmp/predictor_v3_mock_smoke --rows 12 --predict-delay-ms 20 --with-cancel --cleanup --force`: OK.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK after regeneration.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator/UI soft warnings only.
- `git diff --check`: OK.

## Boundary Checks

- `PredictionController` imports no `PySidePredictionRunner` concrete: OK.
- `PySidePredictionRunner` remains under `apps/predict/adapters/`: OK.
- Production Train UI execution owner remains `QProcessTrainingRunner` ->
  `train_job.py`: OK.
- Train cancel retains terminate/kill hard-stop path: OK.
- Generated mock files were cleaned up: OK.

## Structure Warnings

No changed/new source file emits a structure soft warning. Remaining warnings are
pre-existing calculator/UI files outside this slice.

## Read Ledger

- `apps/predict/controllers/prediction_controller.py`: focused full file,
  reason: remove concrete PySide runner dependency.
- `apps/predict/ui/workspace.py`: focused constructor range, reason: move
  runner composition into PySide workspace.
- `apps/train/services/training_service.py`: focused full file, reason: remove
  default direct production execution path.
- `apps/train/workers/train_worker.py`: focused full file, reason: evaluate and
  delete legacy direct worker path.
- `tools/dev/mock_smoke/run_mock_train_execution_smoke.py`: focused smoke path,
  reason: route optional real-core smoke through QProcess runner.
- broad read: none.
- repeated read: none.

```yaml
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

reuse_commonization: reused existing QProcess train runner, train job,
PredictionUseCase, and PySide runner adapter; no new runner abstraction was
introduced beyond the existing factory/port boundary.

## Known Risks

- Real model quality and physical trend validation remain outside mock smoke.
- Calculator usecase boundary debt is intentionally deferred to Arc 12.

## Next Action

Arc 12 Slice 0 - Calculator UI/Application Boundary Audit.

## Project Memory Delta

- type: decision
  topic: Arc 11 final Train/Predict boundary cleanup
  content: PredictionController no longer owns concrete PySide runner creation; legacy direct TrainWorker was deleted; TrainingService default direct production execution was disabled in favor of QProcess train job ownership.
  keywords: arc11, boundary-cleanup, prediction-controller, train-worker, qprocess

## Commit / Push

- Commit: pending.
- Push: pending.
