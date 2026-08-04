# HVAC ML Feature Engineering

Purpose: define project-specific feature engineering guidance for HVAC ML models.

Boundary: these notes guide ML feature design and interpretation only. They must not be used to modify calculator formulas, fixtures, region configs, or golden expected values.

## ML / Calculator Boundary

The ML layer predicts point performance, not seasonal efficiency.

ML models may predict condition-point values such as capacity, input power, operating frequency, or refrigerant quantity. Seasonal metrics such as CSPF and HSPF are calculator outputs and must remain in the deterministic calculator path.

Feature engineering must therefore preserve this separation:
- use measured test-point performance and hardware specifications as ML feature sources;
- keep CSPF, HSPF, CSEC, HSEC, golden/reference results, and calculator outputs out of the ML feature pool;
- do not treat ML feature choices as calculator schema, fixture, golden, or region-config authority.

## Current Feature Sources

The current compatibility exports `BASE_FEATURES`, `DERIVED_FEATURES`, and
`TARGETS` live in `core/ml/features.py` and are projected from the validated ML
feature catalog. Generation-specific Feature/Target authority and target policy
belong to canonical Data Definition plus the immutable
`ModelRegistrySnapshot`; `core/ml/registry.py::MODEL_REGISTRY` remains a generated
compatibility facade rather than a writable owner.

The base candidate pool includes:
- point performance columns: cooling/heating capacity, power, and frequency;
- hardware dimensions: indoor/outdoor volume, evaporator/condenser area and volume;
- compressor and refrigerant information: compressor EER, compressor cc, refrigerant one-hot columns, expansion-device one-hot columns, and refrigerant quantity.

This is a candidate pool, not a global mandatory feature list. Production training applies the generation-bound `ModelRegistrySnapshot` Target policy to the ordered input pool for each target; compatibility `MODEL_REGISTRY` output is not the policy owner.

## Cooling / Heating Separation

Cooling and heating target predictions must keep independent feature boundaries.

Do not use MultiOutput training to combine cooling and heating targets. The same registry entry may orchestrate both mode targets, but each target still needs its own target-specific feature boundary. Mode-specific rules may exclude the opposite mode's measured performance and derived features where they would leak target context or represent an invalid operating mode.

## Target Leakage Rules

The measured value of the same condition point being predicted must not be used as an input feature.

Examples:
- when predicting `Cooling Power`, measured `Cooling Power` is a target, not a feature;
- when predicting `Heating Power`, measured `Heating Power` is a target, not a feature;
- power-derived features are leakage for power target prediction if they use the power value being predicted;
- measured capacity or power from other existing test points can be a feature source only when it does not include the target point's measured answer.

The current `prepare_pipeline()` path uses the generation-bound registry snapshot when provided to remove active Targets and construct the ordered input pool. Production training then applies the selected runtime Target policy through the canonical target-registry owner before fitting. Compatibility `TARGETS`/`MODEL_REGISTRY` remain bootstrap/import facades, not an independent source of target policy.

## XGBoost RFE Feature Selection Pattern

XGBoost training and RFECV/RFE feature selection must preserve pandas DataFrame column names.

Rules:
- pass a DataFrame into `model.fit()` and selector `.fit()`; do not convert `X` to `.values`;
- build candidate features only after removing the active target, global excluded target columns, target-specific excluded columns, leakage columns, and mandatory columns;
- run RFE/RFECV only on the remaining candidate pool;
- append mandatory features back to the final selected list after candidate selection;
- keep target-specific feature boundaries independent for Cooling, Heating, frequency, power, and refrigerant quantity targets.

Rationale:
- `.values` removes feature names and can break `feature_names_in_` based train/predict alignment;
- V2 used `OptimalModel.features` as a workaround after feature names were lost, but the current preferred pattern is DataFrame-native training;
- RandomForest to XGBoost migrations must remove leftover `.values` habits before model fitting.

Snapshot expectations:
- keep a candidate-pool snapshot, such as `features_<target>_candidates.json`, to detect RFE input drift;
- keep a selected-feature snapshot, such as `features_<target>_selected.json`, to detect selection-result drift;
- do not rely on the candidate snapshot alone because RFE output can change while the input pool is unchanged.

## Validated Derived Feature Families

The current `DERIVED_FEATURES` are validated ratio-based families and should be preserved unless a dedicated ML feature review changes them.

Current families:
- cooling capacity normalized by compressor EER, condenser area, evaporator area, and compressor cc;
- heating capacity normalized by compressor EER, condenser area, evaporator area, and compressor cc.

These features encode capacity relative to hardware or compressor scale. The implementation uses vectorized zero-division guards and writes `0` when the denominator is `0`. That behavior is implementation reality, but data review should still treat impossible or missing core hardware values separately from legitimate unsupported-mode zeros.

## Adding Derived Features

Any new derived feature must document:
- source columns;
- physical meaning;
- unit basis or ratio basis;
- leakage risk by target;
- zero-division and missing-value handling;
- cooling/heating applicability;
- whether it belongs in the common candidate pool or behind a target-specific rule.

Do not add derived features by only naming a formula. The review must explain what physical relationship the feature represents and why it does not leak the target.

## Future Base Feature Candidates

Future hardware base features under consideration:
- evaporator inner area;
- condenser inner area.

These should be treated as hardware specification inputs, not derived performance outputs. Adding them requires a schema implementation decision and target-specific leakage review; this document alone does not implement the schema.

## Grill-me Confirmed Notes

- ML predicts point performance; calculator computes seasonal efficiency.
- Main feature sources are existing test-point performance data and hardware specifications.
- Cooling and heating remain separate.
- The target condition point's measured capacity/power must be excluded from features.
- Existing ratio-based `DERIVED_FEATURES` are validated and retained.
- Power target models must not use power-derived features that contain the answer.
