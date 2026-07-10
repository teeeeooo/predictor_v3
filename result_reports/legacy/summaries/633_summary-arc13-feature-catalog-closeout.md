# 633 Summary - Arc 13 Feature Catalog Closeout

## Goal

Close Arc 13 by summarizing the ML Feature Catalog migration from design gate
through runtime guards, workflow hardening, and report lifecycle cleanup.

Covered reports:

- `624_arc13-ml-feature-manifest-design-gate.md`
- `625_arc13-feature-catalog-loader-validator.md`
- `626_arc13-ml-features-projection-from-catalog.md`
- `627_arc13-feature-catalog-contract-cleanup.md`
- `628_arc13-predictor-schema-projection-from-catalog.md`
- `629_arc13-predictor-ui-only-column-owner-split.md`
- `630_arc13-one-hot-adapter-projection-from-catalog.md`
- `631_arc13-training-input-contract-runtime-guard.md`
- `632_arc13-catalog-guard-packaging-workflow-hardening.md`

## Major Decisions

- `config/ml/features.csv` is the ML feature contract.
- `ml_name` is the raw training data header and internal ML feature or target
  name.
- No training header alias or mapping layer exists.
- User-managed catalog fields are limited to the feature contract. UI
  presentation, model policy, derived formulas, and artifact schema remain
  code-owned.
- `core/ml/features.py` exports `BASE_FEATURES`, `DERIVED_FEATURES`, and
  `TARGETS` from catalog projection while preserving import names.
- Predictor schema ML-visible input, auto, and result columns project from the
  catalog. UI order is role group `input -> auto -> result`, then catalog
  `order`.
- Dropdown-only input columns and rule-only result columns are owned by
  `core/predictor_schema/ui_columns.py`.
- One-hot feature lists are catalog-owned through one-hot group projection.
- `MODEL_REGISTRY` remains developer-managed, but registry target and rule
  names are guarded against catalog drift.
- Training fails before fitting when raw data headers do not match catalog
  `ml_name` values.
- Inference missing-feature `0.0` fill is limited to catalog
  `zero_fill_policy=mode_missing_allowed`, currently only Cooling/Heating
  Capa/Power.

## Owner Changes

- `config/ml/features.csv`: user-managed ML feature/target/one-hot contract.
- `core/ml/feature_catalog.py`: CSV loader and data model.
- `core/ml/feature_catalog_validation.py`: catalog and registry reference
  validation.
- `core/ml/feature_catalog_projection.py`: feature, target, predictor column,
  one-hot, zero-fill, and training-header projections.
- `core/ml/features.py`: stable import surface projected from catalog.
- `core/predictor_schema/columns.py`: final predictor schema assembly/export.
- `core/predictor_schema/ui_columns.py`: UI-only compatibility columns.
- `apps/predict/adapters/row_to_ml_input_adapter.py`: consumes catalog one-hot
  groups through projection.
- `core/ml/training.py`: training header runtime guard.
- `core/ml/inference.py`: inference zero-fill policy guard.

## Runtime Behavior Changes

- Training data with unknown headers fails before model fitting.
- Training data missing required catalog training headers fails before model
  fitting.
- Derived feature headers are not required in raw training data.
- Prediction input no longer silently fills non-allowed missing base features
  with `0.0`.
- Prediction still allows mode-missing `0.0` fill for the four catalog-approved
  Cooling/Heating capacity/power names.
- Predict UI schema exports and prediction result dict contracts were
  preserved.
- ML algorithm, Optuna/RFE/XGBoost parameters, model artifact schema, mapping
  schema, calculator code, and train/predict UI layout were not changed.

## User Workflow

User feature edits now follow `docs/workflows/ml_feature_catalog_workflow.md`:

1. Edit `config/ml/features.csv`.
2. Add or update the feature row and stable `feature_id`.
3. Set role-specific fields.
4. Align training CSV/Excel headers to `ml_name`.
5. Save as UTF-8 comma-delimited CSV.
6. Run focused guard tests.
7. Train only after guards pass.

## Resolved Risks

- Feature constants, predictor schema ML columns, one-hot lists, training
  header validation, and inference zero-fill policy now share the same catalog
  contract.
- Registry targets and target-rule keys must be active catalog result rows.
- Target leakage rules are guarded after catalog projection.
- `config/ml/features.csv` runtime presence is guarded by focused tests.
- UI-only predictor compatibility metadata is separated from ML feature
  contract rows.

## Remaining Risks

- Production training data outside the repository must be manually aligned to
  catalog `ml_name` headers before training.
- Future packaging work must explicitly include `config/ml/features.csv` if a
  packaging system is added.
- Real-model prediction success smoke remains blocked in this checkout because
  `model/model.pkl` is absent.
- DEV/mock smoke verifies workflow readiness but not production model quality,
  prediction accuracy, or physical trend validity.

## Excluded Scope

- No model retraining.
- No generated model/data artifact commits.
- No ML algorithm, parameter, artifact schema, mapping schema, calculator, or
  Train/Predict UI layout changes.
- No broad packaging framework.

## Validation

- Slice 0: documentation/design gate only.
- Slice 1-6 focused validation repeatedly covered catalog, training/inference,
  and predict selectors.
- Final Slice 7 validation:
  - `python3 -B -m compileall -q core/ml core/predictor_schema apps/predict apps/train tests`:
    OK.
  - `python3 -B -m pytest tests -k "feature_catalog"`: OK, 40 passed and
    1418 deselected.
  - `python3 -B -m pytest tests -k "training or train or inference or ml"`:
    OK, 85 passed and 1373 deselected.
  - `python3 -B -m pytest tests -k "predict_schema or prediction_adapter or prediction_usecase or apps_predict"`:
    OK, 132 passed and 1326 deselected.
  - `python3 -B tools/code_checker/build_reference_map.py --check`: OK, fresh.
  - `python3 -B tools/check_code_structure.py`: OK with pre-existing
    calculator soft warnings outside Arc 13.
  - `git diff --check`: OK.

## Lifecycle

- Arc 13 active reports 624 through 632 are covered by this summary.
- Covered reports are archived under `result_reports/archive/`.
- `result_reports/memory/project_memory_seed.md` is updated with compact
  durable Arc 13 decisions.

## Next Action

Arc 14 - ML Catalog-Aligned Real Dataset Readiness Audit.
