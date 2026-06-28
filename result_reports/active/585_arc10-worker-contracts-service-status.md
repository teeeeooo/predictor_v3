# 585 - Arc 10 Worker Contracts / Service Status Foundation

## Goal

Add the pre-worker contract payloads and Qt-free model status foundation needed
before implementing the PredictionWorker QObject and QThread lifecycle.

## Scope

- Added `apps/predict/workers/` with contract dataclasses only.
- Added `PredictionService.model_status()` and `PredictionModelStatus`.
- Added controller model-status delegation and an `is_running` contract
  property.
- Added `PredictionResultAdapter.cancelled_result()`.
- Added focused worker-contract and service-status tests.
- Advanced `docs/WORK_PLAN.md` to Slice 3.

## Non-goals

- No QThread lifecycle integration.
- No workspace UI integration or command-bar changes.
- No ML algorithm, feature, preprocessing, model artifact, mapping JSON, or
  calculator behavior changes.

## Verification

- `python3 -B -m py_compile apps/predict/workers/*.py apps/predict/services/*.py apps/predict/controllers/*.py apps/predict/adapters/*.py`: OK.
- `python3 -B -m pytest tests/test_apps_predict_worker_contracts.py tests/test_apps_predict_prediction_service_status.py`: OK.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings and code-map freshness reminder; no changed/new source warning.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked; stale because the map metadata predates current commits. Not regenerated in this slice because the prompt-specific modified-file scope did not include code-map artifacts.
- `python3 -B tools/check_agent_change_gate.py --cached`: OK.
- `git diff --check`: OK.
- `git status --short`: checked before commit.

## Task Results

- task 1: OK - `PredictionJob`, `PredictionProgress`, and
  `PredictionWorkerSummary` are frozen dataclass payloads in the Predict worker
  owner package.
- task 2: OK - `PredictionService.model_status()` reports missing, exists,
  load-error, or loaded state without importing Qt or eagerly loading the model.
- task 3: OK - result adapter now creates running, invalid, and cancelled
  status rows while preserving service result conversion.
- task 4: OK - focused tests cover contracts, missing path, no eager load,
  load-error state, session non-mutation, result factories, and no PySide
  imports in service/adapter/contract modules.

## Read Ledger

- `docs/architecture/project_architecture.md`: lines 1-180, reason: package
  owner and ML artifact boundary.
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`: lines 1-190,
  reason: source owner and responsibility split policy.
- `docs/agent_workflows/DIFF_READ_BUDGET.md`: lines 97-175, reason: reference
  evidence/code-map policy.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: lines 1-190 and 260-320,
  reason: structured source-change gate and staged report requirements.
- `apps/predict/controllers/prediction_controller.py`: full file, reason:
  current synchronous controller contract is under 100 LOC.
- `apps/predict/services/prediction_service.py`: full file, reason: Qt-free
  model load/status owner is under 100 LOC.
- `apps/predict/adapters/prediction_result_adapter.py`: full file, reason:
  result factory owner is under 100 LOC.
- `apps/predict/adapters/row_to_ml_input_adapter.py`: full file, reason:
  request dataclass imported by worker contracts is under 100 LOC.
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

- `new_source: small` because the new worker module is a focused contract-only
  owner under the approved `apps/predict/workers/` package.
- `reuse_commonization: reused-existing-owner` because status, result mapping,
  and request DTOs reuse existing Predict service/adapter/controller owners.

## Structure Warnings

- New source files are below LOC/class soft limits.
- No changed production source file adds PySide imports to service/adapter
  boundaries.

## Known Risks

- The actual `PredictionWorker(QObject)` and QThread lifecycle are not
  implemented until Slice 3/4.
- Code map remains stale by metadata after this slice and should be refreshed in
  an allowed closeout or structural-map slice before claiming final freshness.
- Real-model success smoke remains blocked until `model/model.pkl` is present.

## Commit / Push

- Commit: this report is included in the Slice 2 commit.
- Push: deferred until Slice 7 per user request.

## Project Memory Delta

- none
