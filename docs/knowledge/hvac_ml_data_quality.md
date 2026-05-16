# HVAC ML Data Quality

Purpose: define data quality, leakage review, and fail-fast guidance for HVAC ML datasets.

Boundary: this document supports ML data review only. It must not be used to modify calculator formulas, fixtures, region configs, or golden expected values.

## Leakage Boundaries

The following values are forbidden as ML input features:
- CSPF, HSPF, CSEC, HSEC;
- golden/reference results;
- calculator outputs;
- the measured capacity or power of the same condition point being predicted.

Existing test-point performance data can be a valid feature source, but only when it does not include the measured answer for the target point. Review feature construction at the row and target level, not only by column name.

`MODEL_REGISTRY.target_rules` is the current source for target-specific feature boundaries:
- `exclude` rules remove mode-opposite or target-risk columns from power and frequency models;
- `allowed` rules restrict the refrigerant quantity model to its approved hardware/refrigerant feature subset.

Do not infer a global mandatory feature list from `BASE_FEATURES`.

## Fail-fast vs Review Flags

Separate physically impossible core hardware data from mode-specific missing data.

Fail-fast candidates:
- `Cond Area`, `Evap Area`, or `Comp cc` is `0`, missing, or physically impossible for a model that depends on those hardware specifications;
- required hardware specification columns are absent after schema alignment;
- mandatory model features configured for a pipeline are missing.

Review or fail-fast candidates, depending on source and target:
- capacity exists but matching input power is `0`;
- heat exchanger area is `0` or abnormally small;
- refrigerant type, expansion-device type, or refrigerant quantity is missing;
- compressor-on rows look like fan-only rows;
- heating-only or cooling-only records are mixed into the opposite mode without explicit mode handling.

Do not automatically delete every abnormal row. Use the issue type to decide whether to fail fast, label the row, exclude it after review, or keep it with metadata.

## Unsupported Mode Zeros

A zero caused by an unsupported mode is different from a zero in a core hardware specification.

Examples:
- a cooling-only model may have no meaningful heating-mode performance value;
- a heating-only model may have no meaningful cooling-mode performance value;
- such unsupported-mode zeros should be handled through mode-specific feature rules and target exclusions.

By contrast, core hardware values such as condenser area, evaporator area, compressor cc, refrigerant type, and expansion-device type describe the unit itself. Missing or zero values there usually indicate a schema, extraction, or data-quality problem.

## Derived Feature Data Checks

Current derived features divide capacity by compressor EER, heat exchanger area, or compressor cc. The calculation protects against zero division, but the resulting `0` is not automatically valid training evidence.

When a denominator is `0` or missing, review whether the row represents:
- an unsupported mode;
- missing hardware extraction;
- an invalid hardware value;
- a real but unusual system configuration.

Document the decision before changing feature logic or training filters.

## Transformation Review

Prefer vectorized transformations for ML preprocessing and derived feature calculation. Avoid row-wise `apply` for routine feature generation unless there is a clear reason and the performance/consistency tradeoff has been reviewed.

Training and prediction must preserve DataFrame column names. Do not convert training inputs to `.values` before `model.fit()` because feature names such as `feature_names_in_` are part of the train/predict alignment contract.

Train/predict alignment checks should verify:
- expected feature columns are present;
- extra calculator output or target columns are not passed as features;
- one-hot refrigerant and expansion-device columns use the same names in training and prediction;
- target-specific `exclude` or `allowed` rules were applied before model input.

## ML Safety Gates

Use fail-fast gates before training or prediction reaches model `.fit()` / `.predict()`.

Safety checks:
- **Preprocess version**: saved model metadata, such as `preprocess_version`, must match the current preprocessing contract. Store this on the project model wrapper, not by mutating a third-party XGBoost object directly.
- **Feature freeze**: compare required model features, preferably from `model.feature_names_in_` or the wrapper's recorded feature list, against the current DataFrame columns before prediction.
- **Data leakage hard gate**: target-specific leakage features must be blocked before training starts. If leakage rules fail, do not enter `fit()`.

V2 lessons:
- attaching metadata directly to XGBoost objects is fragile across serialization and version updates;
- CSPF/HSPF are rule-based calculator outputs and should not enter the ML feature pool or leakage rule target set as ordinary model inputs;
- refrigerant quantity leakage is easy to miss because it may be a target for one model and a tempting candidate feature for another.

## Test Harness Strategy

Use layered test gates so routine edits do not accidentally weaken ML or UI contracts.

1. **Feature harness**: run frequently and keep it fast. Check `MODEL_REGISTRY` against the current feature pool, verify leakage exclusions, and compare candidate/selected feature snapshots.
2. **UI logic harness**: run when UI state logic changes. Check AUTO_COLS editable/read-only transitions, signal blocking, and master-dropdown driven reset behavior.
3. **ML sanity harness**: run when model behavior changes. Check broad physical sanity, monotonicity review flags, and prediction repeatability for identical inputs.
4. **Optimization harness**: run only when explicitly requested, such as with a `--run-optuna` flag. Do not refresh Optuna results as part of ordinary fast validation.

Execution rules:
- UI, data, or feature code changes should run the current fast non-slow test gate before completion reporting;
- ML model or parameter changes should run the broader model-relevant test gate;
- completion reports should name the verifier that actually ran, and skipped preferred verifiers are weaker evidence rather than pass signals.

Snapshot management:
- candidate snapshots watch the RFE input pool;
- selected snapshots watch the RFE output;
- both are required;
- update snapshots only for intentional feature contract changes, not automatically after every training run.

## Physical Sanity Checks

`physical_constraints_for_ml.md` provides sanity-check guidance for HVAC tendencies, monotonicity caveats, and review flags. Treat it as a review aid, not as a strict deletion rule and not as calculator authority.

Physical sanity concerns should produce a clear action:
- fail fast for impossible core schema or hardware values;
- flag rows for review when measurement, chamber state, or operating mode may explain the value;
- keep valid exceptions when control logic or test conditions justify them.
