# 594 - Arc 10.5b Mock Bundle Smoke Verification

## Goal

Add an isolated DEV-only mock bundle and smoke runners so Arc10 Predict E2E and
Train shell/status smoke can be verified without real data or real model
artifacts.

## Why Arc 10.5b

Arc10 worker/progress/cancel is implemented, but real `model.pkl`, mapping, and
training data may be absent in local/cloud environments. Arc10.5b provides a
reproducible mock bundle for smoke verification before starting Arc11 Trainer
execution boundary design.

## Isolation And Commit Policy

- Default generated output remains outside the repo.
- Repo-local fallback is limited to ignored paths.
- Generated mock CSV/TSV/XLSX/JSON/PKL/log/output files are not committed.
- Local installs are explicit and protected by overwrite guards.
- Cleanup uses manifest sha256 checks and refuses mismatched files.

## Local Install / Cleanup Policy

- Bundle install targets are `model/model.pkl`, `data/mapping.json`, and
  `data/Practice_4.csv`.
- Existing local files are not overwritten without `--force`.
- Cleanup removes local installs only with explicit flags.
- Cleanup refuses sha mismatches and non-mock-looking paths.

## Predict E2E Smoke Result

- Command:
  `python3 -B tools/dev/mock_smoke/run_mock_predict_smoke.py --output-dir /tmp/predictor_v3_mock_smoke --rows 12 --predict-delay-ms 20 --with-cancel --cleanup --force`
- Result: OK.
- Verified paste/autofill, prediction completion for 12 rows, slow-model
  cooperative cancel, result/copy basics, and manifest cleanup.

## Train Shell / Status Smoke Result

- Command:
  `python3 -B tools/dev/mock_smoke/run_mock_train_shell_smoke.py --output-dir /tmp/predictor_v3_mock_smoke --cleanup --force`
- Result: OK.
- Verified tabs, embedded Predict workspace, model/train-data/mapping status
  visibility, and disabled Train/Data Mapping execution controls.
- Trainer execution remains deferred.

## App Train Execution Excluded

Arc11 Trainer execution is not implemented in this scope. This smoke only
claims shell/status/tab construction and disabled execution controls.

## Code Map Reuse Gate

```yaml
reuse_commonization: reused-existing-owner
```

- Checked code map keywords: `mock`, `smoke`, `mapping`, `manifest`,
  `cleanup`, `artifact`, `case input`, and `tsv`.
- Existing `tools/dev/mock_smoke` owner was reused and extended.
- Production Predict, Train, ML, mapping, and calculator code was not changed.

## Modified Files

- `.gitignore`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `project_brief.md`
- `project_log.md`
- `tools/dev/mock_smoke/README.md`
- `tools/dev/mock_smoke/cleanup_mock_smoke.py`
- `tools/dev/mock_smoke/generate_mock_case_input.py`
- `tools/dev/mock_smoke/generate_mock_mapping.py`
- `tools/dev/mock_smoke/generate_mock_prediction_artifact.py`
- `tools/dev/mock_smoke/generate_mock_smoke_bundle.py`
- `tools/dev/mock_smoke/generators.py`
- `tools/dev/mock_smoke/models.py`
- `tools/dev/mock_smoke/run_mock_predict_smoke.py`
- `tools/dev/mock_smoke/run_mock_train_shell_smoke.py`
- `tests/test_mock_smoke_generators.py`
- `result_reports/active/594_arc105b-mock-bundle-smoke-verification.md`

## Verification Results

- `python3 -B -m py_compile tools/dev/mock_smoke/*.py`: OK.
- `python3 -B -m pytest tests -k "mock_smoke or mock or artifact"`: OK,
  15 passed and 1342 deselected.
- `python3 -B tools/dev/mock_smoke/generate_mock_smoke_bundle.py --output-dir /tmp/predictor_v3_mock_smoke --rows 12 --predict-delay-ms 20 --manifest`: OK.
- `python3 -B tools/dev/mock_smoke/run_mock_predict_smoke.py --output-dir /tmp/predictor_v3_mock_smoke --rows 12 --predict-delay-ms 20 --with-cancel --cleanup --force`: OK.
- `python3 -B tools/dev/mock_smoke/run_mock_train_shell_smoke.py --output-dir /tmp/predictor_v3_mock_smoke --cleanup --force`: OK.
- `python3 -B tools/code_checker/build_reference_map.py`: OK, regenerated
  after new tools source files.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK, status
  `FRESH`.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings only.
- `git diff --check`: OK.

## Generated Output Path

- `/tmp/predictor_v3_mock_smoke/mock_smoke_model.pkl`
- `/tmp/predictor_v3_mock_smoke/mock_smoke_mapping.json`
- `/tmp/predictor_v3_mock_smoke/mock_smoke_case_input.tsv`
- `/tmp/predictor_v3_mock_smoke/mock_smoke_training_data.csv`
- `/tmp/predictor_v3_mock_smoke/mock_smoke_manifest.json`

These were generated for validation and removed by smoke runner cleanup.

## Cleanup Result

- Predict smoke cleanup removed generated bundle files plus local mock
  `model/model.pkl` and `data/mapping.json`.
- Train shell smoke cleanup removed generated bundle files plus local mock
  `model/model.pkl`, `data/mapping.json`, and `data/Practice_4.csv`.
- Final check found no generated files remaining under
  `/tmp/predictor_v3_mock_smoke`.

## Excluded Scope

- No production app behavior changes.
- No `apps/predict/` production UI, worker, controller, or service changes.
- No `apps/train/` Trainer execution implementation.
- No Train button enabling.
- No `core/ml` algorithm, training pipeline, preprocessing, or feature schema
  changes.
- No `core/mapping` production schema changes.
- No calculator changes.
- No generated data, mapping, model, or output committed.

## Read Ledger

- User prompt attachment: full file, reason: task owner prompt.
- `AGENTS.md`, `AGENT_TASK_ROUTER.md`, `DIFF_READ_BUDGET.md`,
  `ML_PREDICTOR_WORKFLOW.md`: required workflow/gate sections.
- `tools/dev/mock_smoke/`: relevant files, reason: existing owner extension.
- `core/predictor_schema/columns.py`: `INPUT_COLS` and table schema.
- `core/mapping/autofill.py`, `core/mapping/paths.py`: mapping/autofill and
  install target contract.
- `core/ml/artifacts.py`, `core/ml/inference.py`: model/train artifact and
  inference contract.
- `apps/predict/ui/workspace.py`,
  `apps/predict/controllers/prediction_controller.py`,
  `apps/predict/workers/prediction_worker.py`: smoke runner public behavior.
- `apps/train/ui/shell.py`, `apps/train/ui/train_model_panel.py`,
  `apps/train/ui/data_mapping_panel.py`: Train shell/status smoke boundary.
- `tests/test_mock_smoke_generators.py`: focused test owner.
- `docs/WORK_PLAN.md`, `project_brief.md`: current state sync.
- broad read: none beyond user-required prompt attachment.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

- `hotspot_delta: accepted-for-slice` because `generators.py` is the existing
  DEV-only mock smoke owner and this slice needed shared manifest/install/
  cleanup helpers across bundle and runner scripts. A later tooling cleanup can
  split manifest/install/cleanup helpers if mock smoke grows again.

## Next Action

- Arc11 Trainer execution boundary design using the same mock bundle.
