# 531 - Arc 8.5 ML and Constants Wrapper Retirement

## Goal

Remove root ML wrappers and the `core/constants.py` compatibility surface after
migrating active callers to package owner paths.

## Migrated Active Callers

- `apps/predict/services/prediction_service.py`
  - `core.constants.MODEL_FILE` -> `core.ml.artifacts.MODEL_FILE`.
  - `core.predictor.load_model/predict_row` -> `core.ml.inference`.
- Legacy/reference-only `ui/` files kept importable:
  - `ui/base_model.py` and `ui/base_view.py` now import predictor table schema
    from `core.predictor_schema.columns`.
  - `ui/predict_window.py` now imports ML artifact, inference, mapping path,
    and explicit column constants from package owners.
  - `ui/train_window.py` now imports training data path and training entrypoint
    from package owners.
- `core/utils.py`
  - `LOG_DIR` now resolves from `core.common.paths`.
- `docs/architecture/project_wide_architecture_restructuring_plan.md`
  - Updated current example import paths for ML inference and predictor schema.

## Added Owner

- `core/common/paths.py`
  - Owns `LOG_DIR` as a common project path that does not belong to one domain
    owner.

## Deleted Root Compatibility Files

- `core/predictor.py`
- `core/data_pipeline.py`
- `core/models.py`
- `core/trainer.py`
- `core/constants.py`

## Validation

- `python3 -B -m py_compile core/ml/*.py core/predictor_schema/*.py core/mapping/*.py core/common/*.py`
  - Result: passed.
- `python3 -B -c "from core.ml.inference import load_model, build_input_df, predict_row; from core.ml.preprocessing import calculate_derived_features, prepare_pipeline; from core.ml.registry import MODEL_REGISTRY; from core.ml.training import train_all_models; from core.ml.features import BASE_FEATURES, DERIVED_FEATURES, TARGETS; from core.ml.artifacts import MODEL_FILE, TRAIN_DATA_FILE; from core.predictor_schema.columns import COLUMNS; from core.mapping.paths import MAPPING_JSON_FILE; from core.common.paths import LOG_DIR"`
  - Result: passed.
- `python3 -B -c "import app_predict; import app_train"`
  - Result: passed.
- Active-tree wrapper import search with `docs/archive/**` excluded:
  - Result: no active hits.
- Prompt-pattern wrapper import search without excluding `docs/archive/**`:
  - Result: one historical hit in `docs/archive/skills_v2_patterns.md`; left
    untouched as archive/history context.
- Root ML/constants file absence guard:
  - Result: passed.
- `git diff --check`
  - Result: passed.
- `git status --short`
  - Result: expected Slice 2 changes before commit.

## Excluded

- No ML algorithm, feature list, target list, preprocessing calculation,
  mapping schema, model artifact, dependency, or PySide6 recovery behavior
  changes.
- No archive/history document edits.

## Next

Slice 3 - Calculator caller migration and root wrapper deletion.
