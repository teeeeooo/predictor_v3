# 523 Arc 7 Core ML / Schema / Mapping Closeout

## Goal

Close Arc 7 as a no-behavior-change package restructure and prepare for Arc 8 -
Calculator Engine Package Restructure.

## Moved Owners

- `core/ml/inference.py`: `load_model`, `build_input_df`, `predict_row`.
- `core/ml/training.py`: `optimize_and_train`, `train_all_models`.
- `core/ml/registry.py`: `MODEL_REGISTRY`, `get_model_config`.
- `core/ml/preprocessing.py`: `calculate_derived_features`,
  `prepare_pipeline`, `load_and_preprocess`.
- `core/ml/features.py`: `BASE_FEATURES`, `DERIVED_FEATURES`, `TARGETS`.
- `core/ml/artifacts.py`: `BASE_DIR`, `DATA_DIR`, `MODEL_DIR`, `MODEL_FILE`,
  `TRAIN_DATA_FILE`.
- `core/predictor_schema/columns.py`: predictor columns, indexes, groups,
  dropdown target, and row count constants.
- `core/mapping/paths.py`: `MAPPING_JSON_FILE`.
- `core/mapping/repository.py`: `load_mapping_data`.
- `core/mapping/update.py`: `update_mapping_to_json`.
- `core/mapping/autofill.py`: target owner shell for ODU cascade, cond_specs,
  and dropdown-to-auto-fill extraction.

## Preserved Compatibility Wrappers

- `core/predictor.py`
- `core/trainer.py`
- `core/models.py`
- `core/data_pipeline.py`
- `core/constants.py`
- `core/utils.py`
- `scripts/update_mapping.py`

## Remaining Compatibility Callers

Expected compatibility callers:

- Legacy PyQt reference path: `ui/base_view.py`, `ui/base_model.py`,
  `ui/train_window.py`, `ui/predict_window.py`.
- Current PySide6 foundation path: `apps/predict/services/prediction_service.py`.
- Internal utility path: `core/utils.py` imports `LOG_DIR` from `core.constants`.

No new owner package under `core/ml`, `core/predictor_schema`, or `core/mapping`
imports root compatibility wrappers.

## Behavior Guard

- ML algorithms, training behavior, preprocessing calculations, feature list,
  target list, model artifact paths, mapping JSON schema, calculator code,
  data/model artifacts, fixtures, golden data, PySide6 Predictor recovery,
  worker/progress, and Trainer app behavior were not changed.
- Calculator engine files, dispatcher, profiles, and calculator adapters were
  not moved.

## Verification

- `python3 -B -m py_compile core/*.py core/ml/*.py core/predictor_schema/*.py core/mapping/*.py scripts/update_mapping.py app_predict.py app_train.py app_calculator.py`: passed.
- Root/new owner import smoke: passed.
- Root/new `predict_row` identity smoke: passed.
- Constants presence smoke: passed.
- Calculator dispatcher/profile smoke: passed.
- App import smoke: passed.
- Compatibility caller search: run and classified.
- New owner reverse-wrapper search: no matches.
- `python3 -B tools/check_code_structure.py`: passed with pre-existing
  calculator soft-limit warnings and stale code-map warning.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked;
  stale before/after this slice, not regenerated.
- `git diff --check`: run.
- `git status --short`: run.

Skipped:

- Full pytest: Arc prompt specified focused smoke.
- GUI smoke: no UI behavior implemented.
- Packaging check: no dependency/package artifact changes.

## Excluded Scope

- Calculator Engine Package Restructure.
- PySide6 Predictor schema/mapping recovery.
- Prediction worker/progress.
- Trainer Admin App foundation.
- Legacy `ui/` deletion/movement.
- Dependency, data, model artifact, fixture, golden, calculator behavior, ML
  algorithm, mapping schema, and public result contract changes.

## Next Action

Arc 8 - Calculator Engine Package Restructure.
