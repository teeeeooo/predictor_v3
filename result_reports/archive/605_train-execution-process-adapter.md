# Train Execution Process Adapter

## Goal

Implement `Arc 11 Reopen - Slice 1: Train Execution Port + QProcess Hard Stop`.

## Scope

- Added a UI/runtime-neutral training execution port.
- Added a PySide `QProcess` runner adapter for killable Train execution.
- Added a child process job entrypoint that runs production core training or
  DEV-fast smoke training and emits structured stdout events.
- Added temp artifact write/promote behavior for production training output.
- Rewired `TrainController` from direct QThread worker ownership to the
  process runner boundary.
- Updated mock Train/Predict smokes and focused tests.

## Non-goals

- No ML algorithm, preprocessing, registry, feature, mapping, or calculator
  behavior changes.
- No Data Mapping execution implementation.
- No generated model/data/mapping artifacts committed.

## Task Results

- task 1: OK - `TrainingExecutionPort` added under `apps/train/ports/`.
- task 2: OK - `QProcessTrainingRunner` added under `apps/train/adapters/`.
- task 3: OK - `apps/train/jobs/train_job.py` process entrypoint added.
- task 4: OK - training can write temp artifact and promote with `os.replace`.
- task 5: OK - `TrainController` uses runner hard cancel; UI cancel path still
  calls controller.
- task 6: OK - process runner, controller, mock smoke, and train tests pass.

## Changed Files

- `apps/train/ports/training_execution_port.py`
- `apps/train/adapters/qprocess_training_runner.py`
- `apps/train/adapters/training_process_events.py`
- `apps/train/jobs/train_job.py`
- `apps/train/controllers/train_controller.py`
- `core/ml/training.py`
- `tools/dev/mock_smoke/run_mock_train_execution_smoke.py`
- `tools/dev/mock_smoke/run_mock_predict_smoke.py`
- `tests/test_apps_train_controller.py`
- `tests/test_apps_train_qprocess_runner.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `docs/WORK_PLAN.md`

## Verification

- `python3 -B -m py_compile apps/train/*.py apps/train/**/*.py tools/dev/mock_smoke/*.py core/ml/training.py app_train.py`: OK.
- `python3 -B -m pytest tests -k "train or mock_smoke or process or qprocess or execution" -q`: OK, 42 passed.
- `python3 -B tools/dev/mock_smoke/run_mock_train_execution_smoke.py --output-dir /tmp/predictor_v3_mock_smoke --rows 12 --cleanup --force`: OK.
- `python3 -B tools/dev/mock_smoke/run_mock_predict_smoke.py --output-dir /tmp/predictor_v3_mock_smoke --rows 12 --predict-delay-ms 20 --with-cancel --cleanup --force`: OK.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK after regeneration.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator/UI soft warnings only.
- `git diff --check`: OK.

## Structure Warnings

No changed/new source file emits a structure soft warning. Remaining warnings are
pre-existing calculator/UI files outside this slice.

## Read Ledger

- `apps/train/services/training_service.py`: lines 1-151, reason: existing Train
  service validation/direct training boundary.
- `apps/train/controllers/train_controller.py`: lines 1-192, reason: replace
  QThread orchestration with runner boundary.
- `apps/train/workers/train_worker.py`: lines 1-95, reason: legacy worker
  compatibility and cancellation comparison.
- `core/ml/training.py`: lines 1-163, reason: add output path without changing
  model algorithm/schema.
- `tools/dev/mock_smoke/run_mock_train_execution_smoke.py`: lines 1-163,
  reason: route mock Train E2E through process runner.
- `tests/test_apps_train_controller.py`: lines 1-180, reason: update controller
  assertions to runner boundary.
- broad read: none.
- repeated read: `apps/train/adapters/qprocess_training_runner.py`, reason:
  split event parsing below source soft limit.

```yaml
change_gate:
  new_source: small
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

reuse_commonization: checked existing Train service/controller/worker and mock
backend paths; no reusable process runner existed, so the new adapter stays
feature-local under `apps/train/adapters/`.

## Known Risks

- Production real-core training remains expensive and was not run.
- `TrainWorker` remains as a legacy compatibility implementation for existing
  tests, but production controller execution now uses the process runner.

## Next Action

Arc 11 Slice 2 - Predict Execution UseCase / Execution Port Correction.

## Project Memory Delta

- type: decision
  topic: Train execution process adapter
  content: Production Train UI execution now flows through a QProcess runner adapter and child process job so cancel can terminate/kill the training process and avoid partial final artifacts.
  keywords: arc11, train-execution, qprocess, hard-cancel, process-adapter

## Commit / Push

- Commit: pending.
- Push: deferred until all Arc 11 slices complete.
