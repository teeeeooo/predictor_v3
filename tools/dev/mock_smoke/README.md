# DEV-only Mock Smoke Foundation

This folder provides local/cloud smoke-test helpers for environments that do
not have real training data or a real `model/model.pkl`.

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

Do not commit generated CSV, XLSX, PKL, logs, or smoke outputs.

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

## Reproducibility Manifest

Pass `--manifest` to either generator to create or update:

```text
mock_smoke_manifest.json
```

The manifest records generated output paths, seed, row count, and UTC
`created_at` timestamps. If both generators use the same output directory, the
manifest keeps both `prediction_artifact` and `training_data` entries.

The manifest is a generated smoke output and must not be committed.

## Manual Smoke Guide

1. Generate the mock prediction artifact.
2. Install it with `--install-local-model` only when an app smoke needs
   `model/model.pkl`.
3. Run `python3 -B app_predict.py`.
4. Add or paste a few rows and run prediction.
5. Check model-present status, row-level prediction results, progress updates,
   and cooperative cancel behavior.
6. Run `python3 -B app_train.py` and confirm the Predict tab still embeds the
   Predict workspace; Trainer execution remains deferred.

## Cleanup

Remove generated outputs:

```bash
rm -rf /tmp/predictor_v3_mock_smoke ../predictor_v3_mock_smoke .dev_artifacts/mock_smoke .mock_smoke predictor_v3_mock_smoke
```

If you installed a local mock model, remove it or restore your backup:

```bash
rm -f model/model.pkl
```

Only do this when `model/model.pkl` is a generated DEV smoke artifact.

## What This Can Verify

- model-present app state;
- `app_predict` prediction workflow smoke;
- worker/progress/cancel smoke;
- `app_train` Predict-tab construction;
- future training-flow data availability smoke.

## What This Cannot Verify

- real prediction accuracy;
- real physical trends;
- trustworthy feature importance;
- real HVAC design decisions;
- production model quality.
