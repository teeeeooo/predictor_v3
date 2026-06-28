# Arc 11 Train E2E Smoke With Mock Bundle

## Goal

Add DEV-only Train execution E2E smoke using the Arc 10.5b mock bundle, then
run Predict smoke against the Train-produced model artifact.

## Scope

- Added `run_mock_train_execution_smoke.py`.
- Updated DEV mock smoke README and focused mock smoke tests.
- Tightened TrainController signal delivery by making it a `QObject` receiver,
  so UI callbacks run on the controller/UI thread.
- Regenerated the code map after Arc11 source surfaces landed.
- Updated `docs/WORK_PLAN.md` next action.

## Non-goals

- No production core training algorithm changes.
- No generated data/model/mapping/output committed.
- No Data Mapping execution.

## Task Results

- task 1: OK - Train execution smoke runner generates the mock bundle, installs
  mapping/train data, starts training through Train UI/controller, verifies
  log/progress/summary/model artifact, runs Predict after Train output, and
  cleans generated outputs.
- task 2: OK - optional real core training smoke is available behind
  `--with-real-core-training` and skipped by default.
- task 3: OK - focused tests cover the new runner and cleanup behavior.

## change_gate

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

Reasons:

- `new_source: small` - new runner stays under existing DEV mock smoke owner.
- `hotspot_delta: wiring-only` - TrainController changed only to make worker
  signal callbacks route through a `QObject` receiver.
- `code_map_check: regenerated` - `docs/code_map/CODEBASE_REFERENCE_MAP.md`
  regenerated and now passes freshness check.
- `reuse_commonization: reused-existing-owner` - runner reuses mock bundle
  generation, DEV fast backend, Train shell/panel/controller boundary, and
  existing Predict smoke workspace helper.

## Read Ledger

- `tools/dev/mock_smoke/run_mock_predict_smoke.py`: full focused runner, reason:
  Predict smoke helper reuse.
- `tools/dev/mock_smoke/run_mock_train_shell_smoke.py`: focused current runner,
  reason: Train shell smoke state parity.
- `tools/dev/mock_smoke/generators.py`: lines 220-520, reason: bundle,
  manifest, install, and cleanup contract.
- `apps/train/controllers/train_controller.py`: focused current file, reason:
  UI-thread callback delivery fix.
- `apps/train/ui/train_model_panel.py`: focused current file, reason: E2E UI
  assertions and button path.
- `tests/test_mock_smoke_generators.py`: focused current file, reason: runner
  test coverage.
- broad read: none.
- repeated read: none.

## Verification

- `python3 -B -m py_compile tools/dev/mock_smoke/*.py apps/train/**/*.py`: PASS
- `python3 -B -m pytest tests -k "mock_smoke or train_execution or train and e2e"`: PASS, 16 selected
- `python3 -B tools/dev/mock_smoke/run_mock_train_execution_smoke.py --output-dir /tmp/predictor_v3_mock_smoke --rows 12 --cleanup --force`: PASS
- `python3 -B tools/dev/mock_smoke/run_mock_predict_smoke.py --output-dir /tmp/predictor_v3_mock_smoke --rows 12 --predict-delay-ms 20 --with-cancel --cleanup --force`: PASS
- `python3 -B tools/code_checker/build_reference_map.py --check`: PASS, fresh
- `python3 -B tools/check_code_structure.py`: PASS with pre-existing hotspot
  warnings only
- `git diff --check`: PASS
- `git status --short`: PASS, only intended Slice 6 files changed

## Changed Files

- `apps/train/controllers/train_controller.py`
- `tools/dev/mock_smoke/run_mock_train_execution_smoke.py`
- `tools/dev/mock_smoke/README.md`
- `tests/test_mock_smoke_generators.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/600_arc11-train-e2e-smoke.md`

## Known Failures / Risks

- Real core training smoke remains optional and was not run.
- Offscreen Qt prints a font alias warning; it does not fail the smoke.

## Next Suggested Action

Arc 11 Slice 7 — Closeout.

## Project Memory Delta

- none

## Commit / Push

- Commit: included in Slice 6 commit
- Push: not pushed
