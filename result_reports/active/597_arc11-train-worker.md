# Arc 11 Train Worker

## Goal

Add the Train worker boundary so training can run outside the UI thread in the
next controller/UI slices.

## Scope

- Added `apps/train/workers/train_worker.py`.
- Added worker package exports.
- Added cooperative cancel forwarding to `TrainingService`.
- Added focused TrainWorker tests.
- Updated `docs/WORK_PLAN.md` next action.

## Non-goals

- No Train UI button wiring.
- No broad controller implementation.
- No core ML/training changes.
- No Data Mapping update execution.

## Task Results

- task 1: OK - `TrainWorker` receives immutable `TrainingRequest`, calls
  `TrainingService.train(...)`, and emits log/progress/finished/failed/cancelled
  signals.
- task 2: OK - cancellation is cooperative only; worker forwards cancel to the
  service/backend and never terminates a thread.
- task 3: OK - tests cover success, service error, pre-run cancel, DEV backend
  cooperative cancel, and no widget/panel imports.

## change_gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

Reasons:

- `new_source: small` - new worker file is scoped to the existing
  `apps/train/workers` owner package.
- `code_map_check: checked` - code map remains stale after Arc11 source
  additions; regeneration is still deferred until the source surfaces stabilize.
- `reuse_commonization: checked` - Predict worker lifecycle was used as the
  reference pattern, but TrainWorker stays local because it emits training-level
  result/log/progress semantics instead of row-level prediction results.

## Read Ledger

- `apps/predict/workers/prediction_worker.py`: lines 1-150, reason: signal,
  cancellation, and no-session-mutation reference.
- `apps/predict/controllers/prediction_controller.py`: lines 225-390, reason:
  upcoming thread cleanup reference.
- `apps/train/services/training_service.py`: current file, reason: cancel
  forwarding integration point.
- `tests/test_apps_predict_prediction_worker.py`: lines 1-230, reason: worker
  signal test pattern.
- broad read: none.
- repeated read: none.

## Verification

- `python3 -B -m py_compile apps/train/workers/*.py apps/train/services/*.py`: PASS
- `python3 -B -m pytest tests -k "train and worker"`: PASS, 5 selected
- `python3 -B tools/check_code_structure.py`: PASS with pre-existing hotspot
  warnings only; no changed/new source warning
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked,
  stale after Arc11 source additions; regeneration deferred
- `git diff --check`: PASS
- `git status --short`: PASS, only intended Slice 3 files changed

## Changed Files

- `apps/train/workers/__init__.py`
- `apps/train/workers/train_worker.py`
- `apps/train/services/training_service.py`
- `tests/test_apps_train_worker.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/597_arc11-train-worker.md`

## Known Failures / Risks

- Production `train_all_models()` still cannot be interrupted mid-call; worker
  records the cooperative cancel limitation and waits for backend return.
- Code map regeneration is deferred until later Arc11 source slices complete.

## Next Suggested Action

Arc 11 Slice 4 — Train Controller.

## Project Memory Delta

- none

## Commit / Push

- Commit: included in Slice 3 commit
- Push: not pushed
