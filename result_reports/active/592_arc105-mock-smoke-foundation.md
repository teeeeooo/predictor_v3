# 592 - Arc 10.5 Mock Smoke Foundation

## Goal

Add DEV-only mock smoke generators so local/cloud workflows can smoke
`app_predict` and `app_train` readiness without real training data or a real
`model/model.pkl`.

## Isolation Principle

- Default generated output is outside the repo at `../predictor_v3_mock_smoke/`
  or a user-provided `--output-dir`.
- Repo-local fallback is documented only under ignored paths such as
  `.dev_artifacts/mock_smoke/`.
- `model/model.pkl` is never written by default. Installing a mock model
  requires `--install-local-model`; replacing an existing local model also
  requires `--force`.

## Generated Artifact Commit Policy

- Generated mock CSV, XLSX, PKL, log, and output files must not be committed.
- `.gitignore` now ignores DEV mock output directories and `mock_smoke_*`
  generated output patterns.
- The validation-generated files were written to `/tmp/predictor_v3_mock_smoke`
  and are intentionally outside the repository.

## Scope

- Added `tools/dev/mock_smoke/` with README, CLI wrappers, and shared generator
  logic.
- Added an inference-compatible mock prediction artifact generator using the
  existing `core.ml` feature, registry, preprocessing, and inference contracts.
- Added a deterministic synthetic training CSV generator for future training
  flow smoke preparation.
- Added focused tests for artifact load/predict, default production-model
  isolation, install overwrite safety, CSV columns, and `.gitignore` coverage.
- Updated project state docs and regenerated the code map because new tools
  source files were added.

## Modified Files

- `.gitignore`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `project_brief.md`
- `project_log.md`
- `tools/dev/mock_smoke/README.md`
- `tools/dev/mock_smoke/__init__.py`
- `tools/dev/mock_smoke/generate_mock_prediction_artifact.py`
- `tools/dev/mock_smoke/generate_mock_training_data.py`
- `tools/dev/mock_smoke/generators.py`
- `tests/test_mock_smoke_generators.py`
- `result_reports/active/592_arc105-mock-smoke-foundation.md`

## Code Map Reuse Gate

```yaml
reuse_commonization: local-with-reason
```

- Checked code map keywords: `mock`, `artifact`, `model`, `training`,
  `smoke`, `data`, and `prediction`.
- Existing reusable production owners were found for ML features, registry,
  preprocessing, inference loading/prediction, and artifact paths.
- The generator itself remains local to `tools/dev/mock_smoke/` because it is
  DEV-only smoke tooling with strict generated-output isolation, not production
  ML behavior.

## Verification Results

- `python3 -B -m py_compile tools/dev/mock_smoke/*.py`: OK.
- `python3 -B -m pytest tests -k "mock_smoke or mock or artifact"`: OK,
  5 passed and 1342 deselected.
- `python3 -B tools/dev/mock_smoke/generate_mock_prediction_artifact.py --output-dir /tmp/predictor_v3_mock_smoke`:
  OK, generated `/tmp/predictor_v3_mock_smoke/mock_smoke_model.pkl`.
- `python3 -B tools/dev/mock_smoke/generate_mock_training_data.py --output-dir /tmp/predictor_v3_mock_smoke`:
  OK, generated `/tmp/predictor_v3_mock_smoke/mock_smoke_training_data.csv`.
- `python3 -B tools/code_checker/build_reference_map.py`: OK, regenerated
  after new tools files were added.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK, status
  `FRESH` by source fingerprint.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings only.
- `git diff --check`: OK.
- `git status --short`: checked before commit.

## Manual Smoke Guide

1. Generate a mock artifact:
   `python3 -B tools/dev/mock_smoke/generate_mock_prediction_artifact.py --output-dir /tmp/predictor_v3_mock_smoke`
2. Install it only for DEV smoke when needed:
   `python3 -B tools/dev/mock_smoke/generate_mock_prediction_artifact.py --output-dir /tmp/predictor_v3_mock_smoke --install-local-model`
3. Run `python3 -B app_predict.py`.
4. Add or paste rows, run prediction, and check row results, progress, and
   cancel behavior.
5. Run `python3 -B app_train.py` and confirm Predict tab reuse plus Train/Data
   Mapping tab construction. Trainer execution remains deferred.
6. Cleanup generated outputs and any installed DEV mock `model/model.pkl`.

## Excluded Scope

- No production app behavior changes.
- No `apps/predict/` UI, worker, controller, or service changes.
- No `apps/train/` Trainer execution implementation.
- No `core/ml` algorithm, training pipeline, preprocessing, or feature schema
  changes.
- No calculator or mapping schema changes.
- No real data, real model artifact, mock model install, or generated smoke
  output committed.
- No broad report lifecycle cleanup.

## Next Action

- Arc10 manual smoke with mock artifact, then Arc11 decision.

## Read Ledger

- User prompt attachment: full file, reason: task owner prompt.
- `AGENTS.md`: full lite entrypoint, reason: project contract.
- `AGENT_TASK_ROUTER.md`: Coding, Smoke, ML/Predictor sections, reason:
  required routing.
- `docs/agent_workflows/DIFF_READ_BUDGET.md`: Reference Evidence / Code Map
  Reuse Gate, reason: new DEV helper/tooling.
- `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md`: full relevant route,
  reason: ML boundary.
- `core/ml/features.py`: full file, reason: `BASE_FEATURES` and `TARGETS`.
- `core/ml/inference.py`: full file, reason: artifact contract.
- `core/ml/training.py`: relevant model artifact construction flow, reason:
  artifact structure.
- `core/ml/artifacts.py`: full file, reason: model path install safety.
- `core/ml/preprocessing.py`: full file, reason: feature preparation reuse.
- `core/ml/registry.py`: full file, reason: target-specific feature rules.
- `apps/predict/services/prediction_service.py`: full file, reason: model
  status/predict service boundary.
- `apps/predict/workers/prediction_worker.py`: full file, reason: Arc10 smoke
  target boundary.
- `docs/WORK_PLAN.md`, `project_brief.md`, `project_log.md`: relevant current
  state sections.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`: narrow keyword search only.
- broad read: none beyond the user-required prompt attachment and small owner
  files.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
  report_exemption: none
  read_ledger: included
```

- `new_source: small` because the new DEV-only tools package stays below source
  soft limits and separates CLI wrappers from generation logic.
- `code_map_check: regenerated` because new tools source files were added and
  `docs/code_map/CODEBASE_REFERENCE_MAP.md` changed.
- `reuse_commonization: local-with-reason` because production ML owners are
  reused for contracts, while generated-output isolation belongs in DEV-only
  tooling.
