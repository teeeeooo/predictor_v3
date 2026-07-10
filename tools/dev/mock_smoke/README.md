# DEV-only Mock Smoke Foundation

This folder provides local/cloud smoke-test helpers for environments that do
not have real training data, real mapping data, or a real `model/model.pkl`.

The generated files are for workflow smoke only. They must not be used to judge
real prediction accuracy, physical trends, feature importance, HVAC design
quality, or production model performance.

## Isolation

Default output is outside the repo:

```bash
python3 -B tools/dev/mock_smoke/generate_mock_prediction_artifact.py
python3 -B tools/dev/mock_smoke/generate_mock_training_data.py
```

Default directory:

```text
../predictor_v3_mock_smoke/
```

Repo-local fallback is allowed only under an ignored directory:

```bash
python3 -B tools/dev/mock_smoke/generate_mock_prediction_artifact.py --output-dir .dev_artifacts/mock_smoke
python3 -B tools/dev/mock_smoke/generate_mock_training_data.py --output-dir .dev_artifacts/mock_smoke
```

Do not commit generated CSV, TSV, XLSX, JSON, PKL, logs, or smoke outputs.

## Mock Bundle

Generate the full smoke bundle:

```bash
python3 -B tools/dev/mock_smoke/generate_mock_smoke_bundle.py \
  --output-dir /tmp/predictor_v3_mock_smoke \
  --rows 12 \
  --predict-delay-ms 20 \
  --manifest
```

The bundle includes:

- `mock_smoke_model.pkl`
- `mock_smoke_mapping.json`
- `mock_smoke_case_input.tsv`
- `mock_smoke_training_data.csv`
- `mock_smoke_manifest.json`

Local install is explicit and protected:

```bash
python3 -B tools/dev/mock_smoke/generate_mock_smoke_bundle.py \
  --output-dir /tmp/predictor_v3_mock_smoke \
  --rows 12 \
  --predict-delay-ms 20 \
  --manifest \
  --install-local-model \
  --install-local-mapping \
  --install-local-train-data
```

Use `--force` only for deliberate DEV smoke replacement of existing local
files.

## Mock Prediction Artifact

Generate a smoke artifact:

```bash
python3 -B tools/dev/mock_smoke/generate_mock_prediction_artifact.py \
  --output-dir /tmp/predictor_v3_mock_smoke \
  --manifest
```

For an app smoke that needs `model/model.pkl`, install explicitly:

```bash
python3 -B tools/dev/mock_smoke/generate_mock_prediction_artifact.py \
  --output-dir /tmp/predictor_v3_mock_smoke \
  --install-local-model
```

The install command does not overwrite an existing `model/model.pkl`. To replace
an existing local DEV smoke artifact, use `--force` deliberately:

```bash
python3 -B tools/dev/mock_smoke/generate_mock_prediction_artifact.py \
  --output-dir /tmp/predictor_v3_mock_smoke \
  --install-local-model \
  --force
```

## Mock Training Data

Generate synthetic CSV data:

```bash
python3 -B tools/dev/mock_smoke/generate_mock_training_data.py \
  --output-dir /tmp/predictor_v3_mock_smoke \
  --manifest
```

The CSV includes the current ML base features and targets. It is useful for
future training-flow smoke preparation only; its metrics are meaningless.

## Mock Mapping And Case Input

Generate mapping JSON:

```bash
python3 -B tools/dev/mock_smoke/generate_mock_mapping.py \
  --output-dir /tmp/predictor_v3_mock_smoke \
  --manifest
```

Generate paste-ready TSV:

```bash
python3 -B tools/dev/mock_smoke/generate_mock_case_input.py \
  --output-dir /tmp/predictor_v3_mock_smoke \
  --rows 12 \
  --manifest
```

Paste `mock_smoke_case_input.tsv` starting at the first input cell of the
unified Predict table (`cooling_capa`). The TSV has no header row and follows
`INPUT_COLS` order.

## Reproducibility Manifest

Pass `--manifest` to either generator to create or update:

```text
mock_smoke_manifest.json
```

The manifest records generated output paths, sha256, seed, row count, optional
prediction delay, local install paths, and UTC `created_at` timestamps. If
generators use the same output directory, the manifest keeps
`prediction_artifact`, `mapping`, `case_input`, and `training_data` entries.

The manifest is a generated smoke output and must not be committed.

## Smoke Runners

Predict E2E smoke:

```bash
python3 -B tools/dev/mock_smoke/run_mock_predict_smoke.py \
  --output-dir /tmp/predictor_v3_mock_smoke \
  --rows 12 \
  --predict-delay-ms 20 \
  --with-cancel \
  --cleanup \
  --force
```

Train shell/status smoke:

```bash
python3 -B tools/dev/mock_smoke/run_mock_train_shell_smoke.py \
  --output-dir /tmp/predictor_v3_mock_smoke \
  --cleanup \
  --force
```

The shell/status runner checks the four current tabs, resource badges, active
Train/Data Mapping controls, removed placeholders, and production execution
adapter composition. Use the Train execution runner below for E2E execution.

Train execution E2E smoke:

```bash
python3 -B tools/dev/mock_smoke/run_mock_train_execution_smoke.py \
  --output-dir /tmp/predictor_v3_mock_smoke \
  --rows 12 \
  --cleanup \
  --force
```

This runner injects the DEV-only fast training backend behind the production
process adapter and Train controller port, writes a local inference-compatible
`model/model.pkl`, and then runs Predict smoke against that trained output. The
optional `--with-real-core-training` flag exercises the real child-process
training job, but remains off by default because it is expensive and its
metrics are meaningless for mock data.

## Manual Smoke Guide

1. Generate the mock bundle.
2. Install model/mapping/train data explicitly only when an app smoke needs
   local files.
3. Run `python3 -B app_predict.py`.
4. Paste `mock_smoke_case_input.tsv` from the first input cell and run
   prediction.
5. Check model-present status, row-level prediction results, progress updates,
   and cooperative cancel behavior.
6. Run `python3 -B app_train.py` and confirm the exact top-level flow is
   `Predict`, `Train / Model`, `Data Definition`, and `Data Mapping`.
7. Start a bounded Train run and confirm log/progress/finish state; use `중지`
   to verify process cancellation when a disposable test artifact is available.

## Cleanup

Manifest-based cleanup:

```bash
python3 -B tools/dev/mock_smoke/cleanup_mock_smoke.py \
  --output-dir /tmp/predictor_v3_mock_smoke \
  --remove-local-model \
  --remove-local-mapping \
  --remove-local-train-data
```

Fallback manual cleanup for generated output directories:

```bash
rm -rf /tmp/predictor_v3_mock_smoke ../predictor_v3_mock_smoke .dev_artifacts/mock_smoke .mock_smoke predictor_v3_mock_smoke
```

If you installed a local mock model, remove it or restore your backup:

```bash
rm -f model/model.pkl
rm -f data/mapping.json
rm -f data/Practice_4.csv
```

Only do this when the files are generated DEV smoke artifacts.

## What This Can Verify

- model-present app state;
- `app_predict` prediction workflow smoke;
- worker/progress/cancel smoke;
- `app_train` Predict-tab construction;
- `app_train` shell/status/tab construction smoke;
- Train / Model controls and production process-adapter composition;
- DEV-only Train execution E2E through execution port/controller/UI;
- Predict smoke after DEV Train output;
- active Data Definition and Data Mapping manager surfaces.

## What This Cannot Verify

- real prediction accuracy;
- real physical trends;
- trustworthy feature importance;
- real HVAC design decisions;
- production model quality.
- Data Mapping Excel update execution.
