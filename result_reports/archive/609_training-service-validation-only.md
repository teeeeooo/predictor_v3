# TrainingService Validation Only Cleanup

## Goal

Reduce `TrainingService` to Train resource validation/status ownership and move
DEV/test backend execution into a separate helper.

## Scope

- Removed `TrainingService.train()` and backend/cancel ownership.
- Added `tools/dev/mock_smoke/dev_training_runner.py` for explicitly supplied
  DEV/test backends.
- Updated TrainingService tests to assert validation/status only.
- Updated project state docs to reflect the cleaner boundary.

## Non-goals

- No core ML algorithm, preprocessing, feature list, or target registry changes.
- No mapping schema changes.
- No calculator changes.
- No UI visual redesign.
- No generated mock files committed.

## Task Results

- task 1: OK - `TrainingService` has no `train()` method.
- task 2: OK - DEV/test backend execution lives in mock-smoke helper.
- task 3: OK - production Train UI execution remains QProcess runner -> train
  job.
- task 4: OK - focused tests and smokes pass.

## Changed Files

- `apps/train/services/training_service.py`
- `tools/dev/mock_smoke/dev_training_runner.py`
- `tests/test_apps_train_training_service.py`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`

## Verification

- `python3 -B -m py_compile apps/train/**/*.py apps/predict/**/*.py tools/dev/mock_smoke/*.py app_train.py app_predict.py`: OK.
- `python3 -B -m pytest tests -k "train or predict or mock_smoke or execution or usecase or process or qprocess"`: OK, 172 passed.
- `python3 -B tools/dev/mock_smoke/run_mock_train_execution_smoke.py --output-dir /tmp/predictor_v3_mock_smoke --rows 12 --cleanup --force`: OK.
- `python3 -B tools/dev/mock_smoke/run_mock_predict_smoke.py --output-dir /tmp/predictor_v3_mock_smoke --rows 12 --predict-delay-ms 20 --with-cancel --cleanup --force`: OK.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK after regeneration.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator/UI soft warnings only.
- `git diff --check`: OK.

## Boundary Checks

- `TrainingService.train`: removed.
- DEV/test backend execution: `tools/dev/mock_smoke/dev_training_runner.py`.
- Production UI execution: remains `QProcessTrainingRunner` -> `train_job.py`.

## Structure Warnings

No changed/new source file emits a structure soft warning. Remaining warnings are
pre-existing calculator/UI files outside this slice.

## Read Ledger

- `apps/train/services/training_service.py`: focused full file, reason: remove
  execution helper responsibility.
- `tests/test_apps_train_training_service.py`: focused full file, reason:
  update validation/status and dev helper tests.
- `tools/dev/mock_smoke/dev_training_backend.py`: focused full file, reason:
  identify backend/helper split.
- broad read: none.
- repeated read: none.

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

reuse_commonization: reused existing `DevFastTrainingBackend`,
`TrainingRequest`, and TrainingService validation instead of adding a production
execution path.

## Known Risks

- DEV/test backend helper is intentionally not a production UI execution owner.
- Real model quality and physical trend validation remain outside mock smoke.

## Next Action

Arc 12 Slice 0 - Calculator UI/Application Boundary Audit.

## Project Memory Delta

- type: decision
  topic: TrainingService validation-only boundary
  content: TrainingService is reduced to resource status/request validation; DEV/test backend execution moved to mock-smoke helper while production UI training remains QProcess runner -> train job.
  keywords: training-service, validation, dev-backend, qprocess, arc11

## Commit / Push

- Commit: requested after validation; final hash reported in terminal output.
- Push: requested after validation; final remote match reported in terminal
  output.
