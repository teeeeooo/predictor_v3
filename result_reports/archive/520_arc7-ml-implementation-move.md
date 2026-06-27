# 520 Arc 7 ML Implementation Move

## Goal

Move ML implementation ownership under `core/ml/` while preserving existing root
imports as compatibility wrappers.

## Moved Owners

- `core.ml.inference`: actual owner for `load_model`, `build_input_df`, and
  `predict_row`.
- `core.ml.preprocessing`: actual owner for `calculate_derived_features`,
  `prepare_pipeline`, and `load_and_preprocess`.
- `core.ml.registry`: actual owner for `MODEL_REGISTRY` and
  `get_model_config`.
- `core.ml.training`: actual owner for `optimize_and_train` and
  `train_all_models`.
- `core.ml.features`: actual owner for `BASE_FEATURES`, `DERIVED_FEATURES`, and
  `TARGETS`.
- `core.ml.artifacts`: actual owner for `BASE_DIR`, `DATA_DIR`, `MODEL_DIR`,
  `MODEL_FILE`, and `TRAIN_DATA_FILE`.

## Compatibility

- `core/predictor.py` re-exports from `core.ml.inference`.
- `core/data_pipeline.py` re-exports from `core.ml.preprocessing`.
- `core/models.py` re-exports from `core.ml.registry`.
- `core/trainer.py` re-exports from `core.ml.training`.
- `core/constants.py` re-exports ML feature and artifact constants.

## Excluded

- No ML algorithm changes.
- No feature name, target name, preprocessing formula, model artifact structure,
  training behavior, mapping schema, data/model artifact, calculator, PySide6
  recovery, worker/progress, or Trainer app changes.

## Verification

- `python3 -B -m py_compile core/ml/*.py core/predictor.py core/trainer.py core/models.py core/data_pipeline.py core/constants.py`: passed.
- Root/new inference identity smoke: passed.
- Root/new preprocessing identity smoke: passed.
- Root/new registry identity smoke: passed.
- Root/new training identity smoke: passed.
- Root/new feature/artifact equality smoke: passed.
- `git diff --check`: passed.
- `git status --short`: checked.

## Known Risks

- Existing compatibility callers still import root modules; caller migration is
  handled by later policy/closeout checks.
- Predictor schema and mapping ownership remain for later Arc 7 slices.

## Next Action

Slice 4 - Predictor schema move.
