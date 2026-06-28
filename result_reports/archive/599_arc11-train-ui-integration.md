# Arc 11 Train UI Integration

## Goal

Connect the Train / Model tab execution controls to `TrainController`.

## Scope

- Wired `TrainModelPanel` buttons, path state, progress, log, summary table,
  and terminal result state to the controller callback boundary.
- Added Train shell model/status refresh wiring for Trainer and embedded
  Predict status badges.
- Updated focused UI tests and Train shell smoke expectation from deferred
  Train controls to controller-ready Train controls.
- Updated `docs/WORK_PLAN.md` next action.

## Non-goals

- No Data Mapping update execution.
- No Predict production behavior change.
- No core ML/training changes.

## Task Results

- task 1: OK - Train panel enables `학습 실행` when data exists and no run is
  active; `중지` is enabled while a run is active; log/progress/summary update
  through callbacks.
- task 2: OK - default data path remains `data/Practice_4.csv`; tests use
  `set_data_path()` and do not depend on file dialogs.
- task 3: OK - Train shell/panel refreshes model status after terminal result;
  embedded Predict model badge is refreshed when possible.
- task 4: OK - focused UI/shell/controller/worker/service tests pass; Data
  Mapping buttons remain disabled.

## change_gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

Reasons:

- `hotspot_delta: wiring-only` - `train_model_panel.py` gained controller
  wiring but stayed below the 400 LOC soft warning threshold after cleanup.
- `code_map_check: checked` - code map remains stale after Arc11 source/UI
  additions; regeneration is deferred until source surfaces stabilize.
- `reuse_commonization: checked` - reused existing Train shell/panel layout,
  Predict status badge helper, StaticTableModel, and controller callback
  pattern; no new shared UI abstraction added in this slice.

## Read Ledger

- `apps/train/ui/train_model_panel.py`: full focused owner file, reason:
  command/progress/log/summary wiring.
- `apps/train/ui/shell.py`: full focused owner file, reason: Train/Predict
  status refresh wiring.
- `apps/predict/ui/workspace.py`: lines 1-170, reason: embedded Predict badge
  status owner.
- `apps/predict/ui/status_widgets.py`: lines 1-130, reason: reusable status
  badge helper.
- `tests/test_apps_train_shell.py`: focused current file, reason: UI test
  expectations.
- `tools/dev/mock_smoke/run_mock_train_shell_smoke.py`: focused current file,
  reason: shell smoke expectation changed with Train controls.
- broad read: none.
- repeated read: none.

## Verification

- `python3 -B -m py_compile apps/train/**/*.py app_train.py tools/dev/mock_smoke/run_mock_train_shell_smoke.py`: PASS
- `python3 -B -m pytest tests -k "train and (ui or shell or controller or worker or service)"`: PASS, 26 selected
- `python3 -B tools/check_code_structure.py`: PASS with pre-existing hotspot
  warnings only; changed UI/source files have no soft warning
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked,
  stale after Arc11 source additions; regeneration deferred
- `git diff --check`: PASS
- `git status --short`: PASS, only intended Slice 5 files changed

## Changed Files

- `apps/train/ui/train_model_panel.py`
- `apps/train/ui/shell.py`
- `tests/test_apps_train_controller.py`
- `tests/test_apps_train_shell.py`
- `tests/test_apps_train_worker.py`
- `tools/dev/mock_smoke/run_mock_train_shell_smoke.py`
- `tests/test_mock_smoke_generators.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/599_arc11-train-ui-integration.md`

## Known Failures / Risks

- Train E2E execution through the smoke runner is still Slice 6.
- `모델 열기` and `로그 저장` remain disabled.
- Code map regeneration is deferred until later Arc11 source slices complete.

## Next Suggested Action

Arc 11 Slice 6 — Train E2E Smoke with Mock Bundle.

## Project Memory Delta

- none

## Commit / Push

- Commit: included in Slice 5 commit
- Push: not pushed
