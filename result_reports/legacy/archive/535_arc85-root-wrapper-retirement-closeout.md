# 535 - Arc 8.5 Root Wrapper Retirement Closeout

## Goal

Close Arc 8.5 after retiring root compatibility wrappers and migrating active
production code/tests to package owner paths before Arc 9.

## Deleted Root Wrappers

ML/schema/mapping/constants:

- `core/predictor.py`
- `core/data_pipeline.py`
- `core/models.py`
- `core/trainer.py`
- `core/constants.py`

Calculator wrappers:

- `core/calculator_dispatcher.py`
- `core/calculator_profiles.py`
- `core/calculator_input_adapter.py`
- `core/calculator_prediction_adapter.py`
- `core/calculator_unit_adapter.py`
- `core/calculator_iso16358.py`
- `core/calculator_ks_c9306.py`
- `core/calculator_en14825.py`
- `core/calculator_ahri_seer2.py`
- `core/calculator_ahri_hspf2.py`
- `core/calculator_asnzs_hspf_excel.py`

Flat calculator-adjacent adapters moved and root files deleted:

- `core/calculator_result_adapter.py`
- `core/calculator_ranking_adapter.py`

## Final Owner Paths

- ML inference/training/preprocessing/registry/features/artifacts:
  `core/ml/`.
- Predictor table schema:
  `core/predictor_schema/`.
- Mapping paths/repository/update/autofill:
  `core/mapping/`.
- Common paths:
  `core/common/`.
- Calculator profiles/dispatcher/adapters/standards:
  `core/calculators/`.
- Calculator result/ranking adapters:
  `core/calculators/adapters/result_adapter.py` and
  `core/calculators/adapters/ranking_adapter.py`.

## Migrated Active Callers

- `apps/predict/services/prediction_service.py` now imports ML artifact and
  inference owners directly.
- Legacy/reference-only `ui/` Train/Predict files now import schema/artifact/
  training/mapping owners directly so they remain importable without wrappers.
- `apps/calculator/ui/**` now imports calculator owner paths directly.
- Tests now import owner paths directly.
- Current architecture and work-plan docs now describe wrapper retirement as
  complete.
- Archive/history references were left untouched.

## Verification

- Focused calculator tests:
  - Result: 120 passed for dispatcher/input/prediction/result/ranking/envelope
    chain and selected Tk calculator UI guard tests.
- Arc 8 focused calculator set:
  - Result: 99 passed.
- Final py_compile:
  - `python3 -B -m py_compile core/*.py core/ml/*.py core/predictor_schema/*.py core/mapping/*.py core/common/*.py core/calculators/*.py core/calculators/adapters/*.py core/calculators/standards/*.py scripts/update_mapping.py app_calculator.py app_predict.py app_train.py`
  - Result: passed.
- App import smoke:
  - `python3 -B -c "import app_calculator; import app_predict; import app_train"`
  - Result: passed.
- Owner import smoke:
  - `python3 -B -c "from core.ml.inference import predict_row; from core.ml.training import train_all_models; from core.predictor_schema.columns import COLUMNS; from core.mapping.repository import load_mapping_data; from core.calculators.dispatcher import create_calculator_for_profile"`
  - Result: passed.
- Active wrapper absence guard with `docs/archive/**` excluded:
  - Result: no hits for ML/root wrappers, calculator wrappers, or result/ranking
    root adapters.
- Root file absence guard:
  - Result: passed for all deleted files.
- `python3 -B tools/check_code_structure.py`
  - Result: passed with existing soft warnings for large calculator/UI files and
    code-map freshness reminder.
- `python3 -B tools/code_checker/build_reference_map.py`
  - Result: regenerated.
- `python3 -B tools/code_checker/build_reference_map.py --check`
  - Result: fresh against current commit before closeout commit; warning notes
    the expected dirty working tree / generated-map metadata behavior.
- `git diff --check`
  - Result: passed.
- `git status --short`
  - Result: expected closeout docs/report before commit.

## Excluded

- No ML algorithm, feature list, target list, preprocessing calculation, model
  artifact, mapping JSON schema, calculator formula, calculator config,
  fixture, golden, public result key, PySide6 schema/mapping recovery,
  worker/progress, or Trainer app implementation changes.

## Active Report Count

- 19 active reports after this closeout report is added.

## Next

Arc 9 - PySide6 Predictor Schema / Mapping Recovery.
