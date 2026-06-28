# Arc 11 Training Service Contracts

## Goal

Add the Qt-free Train execution service contract and DEV-only fast backend
contract for later worker/controller/UI integration.

## Scope

- Added Train run contract dataclasses in `apps/train/state/`.
- Added `TrainingService` under `apps/train/services/`.
- Added DEV-only fast training backend under `tools/dev/mock_smoke/`.
- Added focused service/backend tests.
- Updated `docs/WORK_PLAN.md` next action.

## Non-goals

- No UI button wiring.
- No worker/controller integration.
- No core ML algorithm, registry, preprocessing, artifact schema, or Data
  Mapping update changes.

## Task Results

- task 1: OK - service dataclasses added as Qt-free Train run state contracts.
- task 2: OK - production service wraps `core.ml.training.train_all_models`
  through a dynamic service call boundary and returns structured results.
- task 3: OK - DEV fast backend creates inference-compatible mock artifacts by
  reusing existing mock generator logic.
- task 4: OK - focused tests cover missing data, valid mock CSV validation,
  PySide6 import boundary, DEV artifact creation, and production default
  separation.

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

- `new_source: small` - new source files are scoped to existing Train and mock
  smoke owner packages.
- `code_map_check: checked` - `build_reference_map.py --check` reports stale
  after new Arc11 source files; regeneration is deferred until all Arc11 source
  surfaces land to avoid per-slice map churn.
- `reuse_commonization: checked` - checked Predict service/worker/controller
  patterns and existing mock smoke generators; reused mock artifact generation,
  kept Train contracts local because result/progress/cancel semantics differ.

## Read Ledger

- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`: lines 1-230,
  reason: source owner boundary and new-file package policy.
- `docs/agent_workflows/DIFF_READ_BUDGET.md`: lines 97-214, reason: Code Map
  Reuse Gate and map regenerate policy.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`: matched controller/worker/training
  and mock smoke ranges, reason: reuse/commonization check.
- `apps/predict/services/prediction_service.py`: lines 1-140, reason: service
  contract reference.
- `apps/predict/workers/prediction_worker.py`: lines 1-150, reason: worker
  contract/lifecycle reference for upcoming slices.
- `tools/dev/mock_smoke/generators.py`: lines 220-520, reason: mock artifact
  reuse and cleanup behavior.
- broad read: none.
- repeated read: none.

## Verification

- `python3 -B -m py_compile apps/train/services/*.py apps/train/state/*.py tools/dev/mock_smoke/*.py`: PASS
- `python3 -B -m pytest tests -k "train and service or training_service or mock_smoke"`: PASS, 20 selected
- `python3 -B tools/check_code_structure.py`: PASS with pre-existing hotspot
  warnings only; no changed/new source warning remains
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked,
  reports stale after new source files; regeneration deferred until Arc11
  source surfaces stabilize
- `git diff --check`: PASS
- `git status --short`: PASS, only intended Slice 2 files changed

## Changed Files

- `apps/train/services/__init__.py`
- `apps/train/services/training_service.py`
- `apps/train/state/__init__.py`
- `apps/train/state/training_run_state.py`
- `tools/dev/mock_smoke/dev_training_backend.py`
- `tests/test_apps_train_training_service.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/596_arc11-training-service-contracts.md`

## Known Failures / Risks

- Production core training smoke is not run in this slice because it is
  expensive.
- Code map regeneration is intentionally deferred until later Arc11 source
  slices are complete.

## Next Suggested Action

Arc 11 Slice 3 — Train Worker.

## Project Memory Delta

- none

## Commit / Push

- Commit: included in Slice 2 commit
- Push: not pushed
