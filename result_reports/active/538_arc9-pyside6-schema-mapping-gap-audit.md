# 538 Arc 9 PySide6 Schema Mapping Gap Audit

## Goal

Audit the current PySide6 Predict schema, mapping, row-to-ML, and result
adapter gaps before Arc 9 implementation slices.

## Current PySide6 Gaps

- `apps/predict/ui/tables/input_table_model.py` owns local `InputColumn` and
  `INPUT_COLUMNS` definitions instead of using
  `core.predictor_schema.columns.COLUMNS`.
- `apps/predict/ui/tables/result_table_model.py` owns local `ResultColumn` and
  `RESULT_COLUMNS` definitions instead of using the predictor result column
  schema.
- `apps/predict/adapters/row_to_ml_input_adapter.py` owns a local
  `_FIELD_TO_FEATURE` mapping and local one-hot option lists instead of deriving
  direct ML feature mapping from `COLUMNS[*].ml_feature` and core schema
  metadata.
- `apps/predict/adapters/prediction_result_adapter.py` owns a local
  `_TARGET_TO_RESULT_KEY` mapping instead of deriving result target mapping from
  `core.ml.features.TARGETS` and predictor result columns.
- `apps/predict` has no mapping/autofill boundary yet. Dropdown choices,
  IDU simple autofill, ODU cascade, and `cond_specs` recovery are absent from
  the PySide6 path.
- `core/mapping/autofill.py` is currently an owner placeholder only; it has no
  pure autofill/cascade implementation.

## Legacy Reference Behavior

- Legacy `ui/base_model.py` reads `COLUMNS` and `DROPDOWN_TARGET` from
  `core.predictor_schema.columns`.
- Legacy row/column headers, editability, and background role are driven by
  the `COLUMNS` group metadata.
- Legacy dropdown autofill uses `DROPDOWN_TARGET`, selected mapping sections,
  auto column `source`, and auto column `mapping_key`.
- Legacy `get_row_as_ml_dict()` maps every column with `ml_feature` to a numeric
  ML input feature and one-hot encodes `ref_type` as `R410A`, `R32`, `R290` and
  `exp_type` as `EEV`, `Capi`.
- Legacy `ui/predict_window.py` handles ODU cascade dropdown choices and
  `cond_specs` lookup for `Cond Area` / `Cond Volume`.
- Legacy result writes map ML targets to result columns for cooling/heating
  power, refrigerant quantity, and cooling/heating Hz while seasonal metrics
  remain outside current ML prediction.

## Core Owner Contracts

- Predictor table schema owner:
  `core/predictor_schema/columns.py`
  (`COLUMNS`, `INPUT_COLS`, `AUTO_COLS`, `RESULT_COLS`, `DROPDOWN_COLS`,
  `DROPDOWN_TARGET`).
- Mapping owner:
  `core/mapping/paths.py`, `core/mapping/repository.py`,
  `core/mapping/autofill.py`.
- ML runtime owner:
  `core/ml/artifacts.py`, `core/ml/features.py`, `core/ml/inference.py`.
- Root compatibility wrappers are retired; Arc 9 must import package owner
  paths directly.

## Arc 9 Slice Targets

- Slice 2: add a Qt-free Predict schema adapter derived from
  `core.predictor_schema.columns`.
- Slice 3: move input/result table models onto schema adapter descriptors and
  remove mock-only columns.
- Slice 4: implement Qt-free core mapping/autofill logic plus app-side
  controller/repository wiring.
- Slice 5: recover row-to-ML and prediction-result adapters against
  `COLUMNS[*].ml_feature`, one-hot options, and `core.ml.features.TARGETS`.
- Slice 6: run integration smoke, update closeout docs, and push Arc 9.

## Excluded Scope

- No ML algorithm, model artifact, feature list, target list, preprocessing
  formula, mapping JSON schema, calculator formula/config/fixture/golden, or
  public result contract changes.
- No root compatibility wrapper recreation.
- No worker/progress/cancel implementation.
- No Trainer foundation implementation.
- No legacy PyQt behavior refactor.

## UI/UX Contract Check

- Table-shaped PySide6 surfaces are governed by
  `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`.
- Input/result surface shaping is governed by
  `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`.
- PySide6 table adapter is still a gap; toolkit-neutral table acceptance
  remains the active contract for this arc.

## Verification

- `git diff --check`: pending for slice closeout.
- `git status --short`: pending for slice closeout.

## Next Action

Arc 9 Slice 2 - Predict schema adapter from `core.predictor_schema`.
