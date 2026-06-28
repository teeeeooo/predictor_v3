# Arc 11 Train Controller

## Goal

Add TrainController orchestration for service, worker, and QThread lifecycle.

## Scope

- Added `apps/train/controllers/train_controller.py`.
- Added controller package exports.
- Added focused controller tests for start, double start, missing path, finish,
  cancel, and widget-import boundary.
- Updated `docs/WORK_PLAN.md` next action.

## Non-goals

- No TrainModelPanel visual integration.
- No core ML/training changes.
- No Data Mapping update execution.

## Task Results

- task 1: OK - controller exposes `start(...)`, `cancel()`, `is_running`,
  `resource_status(...)`, and `last_result`.
- task 2: OK - controller owns QThread/worker lifecycle and clears worker
  references on finish/fail/cancel without force termination.
- task 3: OK - focused tests cover start/service call, double-start rejection,
  missing data error, finish state, cancel forwarding, and no widget imports.

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

- `new_source: small` - new controller file is scoped to the existing
  `apps/train/controllers` owner package.
- `code_map_check: checked` - code map remains stale after Arc11 source
  additions; regeneration is still deferred until source surfaces stabilize.
- `reuse_commonization: checked` - Predict controller lifecycle was used as the
  QThread cleanup reference; no shared controller abstraction added because
  Train terminal events and validation semantics differ.

## Read Ledger

- `apps/predict/controllers/prediction_controller.py`: lines 1-390, reason:
  QThread worker lifecycle and callback cleanup reference.
- `apps/train/workers/train_worker.py`: full current file, reason: controller
  signal contract.
- `apps/train/services/training_service.py`: focused current ranges, reason:
  validation and resource status contract.
- `tests/test_apps_predict_prediction_controller_worker.py`: lines 1-230,
  reason: async controller test pattern.
- broad read: none.
- repeated read: none.

## Verification

- `python3 -B -m py_compile apps/train/controllers/*.py apps/train/workers/*.py apps/train/services/*.py`: PASS
- `python3 -B -m pytest tests -k "train and controller"`: PASS, 5 selected
- `python3 -B tools/check_code_structure.py`: PASS with pre-existing hotspot
  warnings only; no changed/new source warning
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked,
  stale after Arc11 source additions; regeneration deferred
- `git diff --check`: PASS
- `git status --short`: PASS, only intended Slice 4 files changed

## Changed Files

- `apps/train/controllers/__init__.py`
- `apps/train/controllers/train_controller.py`
- `tests/test_apps_train_controller.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/598_arc11-train-controller.md`

## Known Failures / Risks

- UI integration is not complete until Slice 5 wires panel controls and state.
- Code map regeneration is deferred until later Arc11 source slices complete.

## Next Suggested Action

Arc 11 Slice 5 — Train UI Integration.

## Project Memory Delta

- none

## Commit / Push

- Commit: included in Slice 4 commit
- Push: not pushed
