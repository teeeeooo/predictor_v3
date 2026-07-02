# Project-wide Architecture Audit / Restructuring Plan

## Role and scope

This document records the project-wide architecture audit result and restructuring plan for `predictor_v3`.

It is intended to be used as the source input for the next Architecture SSOT update. It does not implement the migration by itself, and it does not authorize behavior changes to calculator formulas, ML algorithms, model artifacts, fixtures, golden data, or public result contracts.

The key decision is:

- `core/` flat root is a current compatibility/public surface, not the final target structure.
- The final target is real package-boundary separation for ML, calculators, mapping, common utilities, and predictor schema.
- Compatibility wrappers may be used during migration, but they are transition safety devices, not the final architecture.
- PySide6 Predictor recovery should resume only after the project-wide package boundary decision is reflected in architecture docs.

## 1. Current diagnosis

Current `core/` mixes several responsibilities in one flat root:

- ML pipeline
- Calculator engines
- Shared utilities
- Constants, schema, paths, feature names, and target names
- Calculator input/result adapters
- Dispatcher/profile registry

Current representative files include:

- `core/constants.py`
- `core/predictor.py`
- `core/trainer.py`
- `core/models.py`
- `core/data_pipeline.py`
- `core/utils.py`
- `core/calculators/standards/iso16358.py`
- `core/calculators/standards/ks_c9306.py`
- `core/calculators/standards/ahri_hspf2.py`
- `core/calculators/standards/ahri_seer2.py`
- `core/calculators/standards/en14825.py`
- `core/calculators/standards/asnzs_hspf_excel.py`
- `core/calculators/dispatcher.py`
- `core/calculators/profiles.py`
- `core/calculators/adapters/input_adapter.py`
- `core/calculators/adapters/prediction_adapter.py`
- `core/calculators/adapters/unit_adapter.py`

This structure worked while the project was smaller, but it is no longer a good final structure. Continuing PySide6 Predictor work on top of the flat `core/` root would harden the wrong boundary into new code.

## 2. Audit findings

### 2.1 Existing Predictor / PyQt reference behavior

The legacy PyQt Predict path already has useful behavior contracts that must be preserved or adapterized.

Existing Predict flow:

1. Load mapping data from `core.utils.load_mapping_data(MAPPING_JSON_FILE)`.
2. Load model artifact through `core.predictor.load_model(MODEL_FILE)`.
3. Use table columns defined in `core.constants.COLUMNS`.
4. Use mapping/autofill behavior for IDU, ODU, evaporator, compressor, and condenser specs.
5. Convert each row to ML input through column metadata.
6. Call `core.predictor.predict_row()`.
7. Write prediction outputs back to result columns.

Key legacy owners:

- `ui/predict_window.py`: legacy controller/reference behavior for model load, mapping load, prediction execution, ODU cascade, and result writeback.
- `ui/base_model.py`: legacy table model that uses `core.constants.COLUMNS` as column SSOT and converts UI row data to ML feature dict.
- `ui/base_view.py`: legacy table view/delegate behavior for dropdown UX.
- `ui/train_window.py`: legacy Train/Admin reference for training worker, mapping update, log/progress behavior.

Legacy PyQt code is not a production import target for new PySide6 code. It is reference-only. Reusable behavior must be moved or adapterized into non-UI owners.

### 2.2 Existing ML owners

Current ML ownership is mostly clear but flat.

| Responsibility | Current owner | Target direction |
|---|---|---|
| Model artifact path | `core.constants.MODEL_FILE` | `core/ml/artifacts.py` |
| Train data path | `core.constants.TRAIN_DATA_FILE` | `core/ml/artifacts.py` |
| ML features | `core.constants.BASE_FEATURES`, `DERIVED_FEATURES` | `core/ml/features.py` |
| ML targets | `core.constants.TARGETS` | `core/ml/features.py` or `core/ml/targets.py` |
| Inference route | `core.predictor.load_model`, `build_input_df`, `predict_row` | `core/ml/inference.py` |
| Preprocessing / derived features | `core.data_pipeline.calculate_derived_features`, `prepare_pipeline` | `core/ml/preprocessing.py` |
| Model registry | `core.models.MODEL_REGISTRY` | `core/ml/registry.py` |
| Training route | `core.trainer.train_all_models` | `core/ml/training.py` |
| Training log helper | `core.utils.save_train_log_to_excel` | `core/ml/logging.py` or `core/common/io.py` |

### 2.3 Existing predictor schema owners

`core/constants.py` currently owns both ML-facing and UI/table-facing schema. This is too broad.

Current responsibilities mixed into `core/constants.py` include:

- `COLUMNS`
- `INPUT_COLS`
- `AUTO_COLS`
- `RESULT_COLS`
- dropdown metadata
- UI headers
- UI widths/colors
- `ml_feature`
- `BASE_FEATURES`
- `DERIVED_FEATURES`
- `TARGETS`
- file paths such as `MODEL_FILE`, `TRAIN_DATA_FILE`, `MAPPING_JSON_FILE`

Target direction:

| Responsibility | Target owner |
|---|---|
| Predict table columns | `core/predictor_schema/columns.py` |
| input/auto/result grouping | `core/predictor_schema/columns.py` |
| dropdown metadata | `core/predictor_schema/dropdowns.py` or `core/predictor_schema/columns.py` |
| result column contract | `core/predictor_schema/result_columns.py` |
| ML feature list | `core/ml/features.py` |
| artifact/path constants | `core/ml/artifacts.py` and `core/mapping/paths.py` |
| UI-specific widths/colors | toolkit-specific UI layer or design-token binding, not ML core |

### 2.4 Existing mapping/update owners

Current mapping responsibilities are split but not cleanly packaged.

| Responsibility | Current owner | Target direction |
|---|---|---|
| mapping JSON path | `core.constants.MAPPING_JSON_FILE` | `core/mapping/paths.py` |
| mapping JSON load | `core.utils.load_mapping_data` | `core/mapping/repository.py` |
| IDU/Evap/Compressor simple autofill | legacy `ui/base_model.py` | `core/mapping/autofill.py` plus UI controller adapter |
| ODU cascade | legacy `ui/predict_window.py` | `core/mapping/autofill.py` |
| `cond_specs` lookup | legacy `ui/predict_window.py` | `core/mapping/autofill.py` |
| Excel/CSV to mapping JSON conversion | `scripts/update_mapping.py` | `core/mapping/update.py` |
| PyQt file dialog | `scripts/update_mapping.py` | remain in script/UI wrapper only, not core |

Important split:

- `update_mapping_to_json()` conversion logic should move toward `core/mapping/update.py`.
- `select_excel_file()` is UI/toolkit-specific and must not move into `core/mapping`.

### 2.5 Existing calculator owners

Calculator code is currently stable enough to preserve behavior, but not structurally final.

Current owners:

| Responsibility | Current owner | Target direction |
|---|---|---|
| calculator profile registry | `core/calculators/profiles.py` | migrated |
| calculator dispatcher | `core/calculators/dispatcher.py` | migrated |
| ISO 16358 engine | `core/calculators/standards/iso16358.py` | migrated |
| KS C 9306 engine | `core/calculators/standards/ks_c9306.py` | migrated |
| AHRI SEER2 engine | `core/calculators/standards/ahri_seer2.py` | migrated |
| AHRI HSPF2 engine | `core/calculators/standards/ahri_hspf2.py` | migrated |
| EN 14825 engine | `core/calculators/standards/en14825.py` | migrated |
| AS/NZS Excel compatibility | `core/calculators/standards/asnzs_hspf_excel.py` | migrated |
| calculator input adapter | `core/calculators/adapters/input_adapter.py` | migrated |
| calculator prediction adapter | `core/calculators/adapters/prediction_adapter.py` | migrated |
| calculator unit adapter | `core/calculators/adapters/unit_adapter.py` | migrated |

The dispatcher and profile registry are good migration anchors because they already centralize the standard/profile-to-calculator mapping.

## 3. Final target package structure

The long-term target structure is:

    core/
      common/
        numeric.py
        units.py
        paths.py
        errors.py

      predictor_schema/
        columns.py
        dropdowns.py
        result_columns.py

      mapping/
        paths.py
        repository.py
        autofill.py
        update.py

      ml/
        artifacts.py
        features.py
        registry.py
        preprocessing.py
        inference.py
        training.py
        logging.py

      calculators/
        profiles.py
        dispatcher.py
        adapters/
          input_adapter.py
          prediction_adapter.py
          unit_adapter.py
        standards/
          iso16358.py
          ks_c9306.py
          en14825.py
          ahri_seer2.py
          ahri_hspf2.py
          asnzs_hspf_excel.py

## 4. Migration principles

### Principle 1 — Final structure, not temporary patching

The goal is not to stop at wrappers. The final target is real implementation ownership under package boundaries.

Compatibility wrappers may exist during transition, but they are not the end state.

### Principle 2 — No behavior change during package-boundary migration

Package boundary migration must not change:

- calculator formulas
- seasonal metric results
- ML algorithms
- model artifact structure
- feature lists
- target names
- mapping JSON behavior
- fixtures
- golden data
- public result contracts

### Principle 3 — Compatibility wrappers are migration safety devices

Existing root import paths may remain temporarily as wrappers to avoid breaking callers.

Example transition:

    final owner:
    core/calculators/standards/iso16358.py

Temporary compatibility wrappers should be retired only after callers migrate.

### Principle 4 — New production code must use the new package boundary

Once the package boundary foundation is created, new code should import from the target owner path, not from flat root compatibility paths.

Example:

    preferred after boundary foundation:
    from core.ml.inference import predict_row
    from core.predictor_schema.columns import COLUMNS
    from core.calculators.dispatcher import create_calculator_for_profile

    not preferred for new code:
    from core.ml.inference import predict_row
    from core.predictor_schema.columns import COLUMNS
    from core.calculators.dispatcher import create_calculator_for_profile

### Principle 5 — Move implementation in focused slices

Do not move all implementation files in one large refactor. Move by domain and verify after each slice.

Recommended grouping:

1. Architecture SSOT update
2. Core package boundary foundation
3. ML implementation move
4. Predictor schema and mapping move
5. Calculator implementation move
6. PySide6 Predictor schema/mapping recovery
7. Worker/progress and Trainer foundation

## 5. Proposed migration arcs

### Arc A — Architecture SSOT Update

Goal:

- Convert this plan into repository-owned architecture contracts.

Target docs:

- `docs/architecture/project_architecture.md`
- `docs/architecture/pyside6_train_predict_architecture.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`, only if phase/arc map needs adjustment

Must record:

- target package tree
- current compatibility surface
- wrapper lifetime rule
- new code import rule
- migration order
- verification rule
- explicit statement that compatibility wrappers are not final structure

No production code changes in this arc.

### Arc B — Core Package Boundary Foundation

Goal:

- Create package directories and public package paths with no behavior change.

Target additions:

- `core/common/`
- `core/predictor_schema/`
- `core/mapping/`
- `core/ml/`
- `core/calculators/`

Initial files may re-export existing flat-root owners to establish import paths.

This arc is transitional but required to create stable target import paths before deeper recovery work.

Validation:

- py_compile
- import smoke for old and new paths
- focused calculator dispatcher/profile smoke
- ML import smoke
- mapping import smoke

### Arc C — ML Implementation Move

Goal:

- Move actual ML implementation ownership under `core/ml/`.

Target moves:

- `core/predictor.py` to `core/ml/inference.py`
- `core/trainer.py` to `core/ml/training.py`
- `core/models.py` to `core/ml/registry.py`
- `core/data_pipeline.py` to `core/ml/preprocessing.py`

Root files remain as compatibility wrappers during caller migration.

Validation:

- `build_input_df` import smoke
- `predict_row` import smoke
- `train_all_models` import smoke
- feature/target import smoke
- model artifact absent graceful-failure smoke
- focused ML tests when available

### Arc D — Predictor Schema and Mapping Move

Goal:

- Separate schema/mapping responsibility from `core/constants.py`, `core/utils.py`, and `scripts/update_mapping.py`.

Target moves/extractions:

- `COLUMNS`, `INPUT_COLS`, `AUTO_COLS`, `RESULT_COLS` to `core/predictor_schema/columns.py`
- dropdown metadata to `core/predictor_schema/dropdowns.py` or `columns.py`
- result schema helpers to `core/predictor_schema/result_columns.py`
- `BASE_FEATURES`, `DERIVED_FEATURES`, `TARGETS` to `core/ml/features.py`
- `MODEL_FILE`, `TRAIN_DATA_FILE` to `core/ml/artifacts.py`
- `MAPPING_JSON_FILE` to `core/mapping/paths.py`
- `load_mapping_data` to `core/mapping/repository.py`
- pure mapping conversion logic from `scripts/update_mapping.py` to `core/mapping/update.py`
- autofill/cascade/cond_specs logic to `core/mapping/autofill.py`

Constraints:

- PyQt/PySide/Tk file dialogs must not move into core mapping logic.
- `scripts/update_mapping.py` may remain as CLI/UI wrapper.

Validation:

- mapping load smoke
- mapping conversion smoke, if fixture exists
- no PyQt import inside `core/mapping`
- predictor schema import smoke
- legacy compatibility import smoke

### Arc E — Calculator Implementation Move

Goal:

- Move calculator engines under `core/calculators/`.

Target moves:

- calculator profiles are migrated to `core/calculators/profiles.py`
- calculator dispatcher is migrated to `core/calculators/dispatcher.py`
- ISO 16358 engine is migrated to `core/calculators/standards/iso16358.py`
- KS C 9306 engine is migrated to `core/calculators/standards/ks_c9306.py`
- AHRI HSPF2 engine is migrated to `core/calculators/standards/ahri_hspf2.py`
- AHRI SEER2 engine is migrated to `core/calculators/standards/ahri_seer2.py`
- EN 14825 engine is migrated to `core/calculators/standards/en14825.py`
- AS/NZS Excel compatibility is migrated to `core/calculators/standards/asnzs_hspf_excel.py`
- calculator adapters are migrated to `core/calculators/adapters/`

Root files remain as wrappers until callers migrate.

Validation:

- calculator import smoke old/new paths
- dispatcher smoke
- profile resolution smoke
- focused calculator tests
- golden result preservation

### Arc F — PySide6 Predictor Schema/Mapping Recovery

Goal:

- Make PySide6 Predict use the approved package boundaries.

Recovery targets:

- remove local schema ownership from `InputTableModel`
- remove local schema ownership from `ResultTableModel`
- remove hard-coded feature mapping from `RowToMlInputAdapter`
- remove hard-coded result mapping from `PredictionResultAdapter`
- use `core/predictor_schema`, `core/mapping`, and `core/ml` owners
- preserve `case_id` internal identity and row-header user identity
- keep ML behavior unchanged

Validation:

- PySide6 import smoke
- offscreen PredictWorkspace smoke
- input/result schema alignment smoke
- mapping/autofill smoke
- prediction route smoke with graceful model-missing handling

### Arc G — Prediction Worker/Progress and Trainer Foundation

Goal:

- Resume UI/runtime work only after schema/mapping recovery.

Targets:

- prediction worker/progress/cancel boundary
- real-model smoke readiness
- Trainer Admin App foundation
- Train/Model panel using `core/ml/training.py`
- Data Mapping panel using `core/mapping/update.py`

## 6. Verification policy

Every migration slice must include focused verification.

Minimum:

    python3 -B -m py_compile <changed modules>
    python3 -B -c "import <old path>; import <new path>"
    git diff --check
    git status --short

Calculator moves require:

- dispatcher smoke
- profile resolution smoke
- focused calculator tests
- golden preservation check

ML moves require:

- feature/target import smoke
- `build_input_df` smoke
- `predict_row` route smoke
- model artifact missing graceful-failure check
- training import smoke

Mapping moves require:

- mapping repository import smoke
- conversion smoke when fixture is available
- search check that `core/mapping` does not import PyQt/PySide/Tk UI toolkits

UI recovery requires:

- PySide6 offscreen smoke
- table/input/result contract check
- no legacy `ui.*` production imports
- no new flat-root dependency when new package owner exists

## 7. Decisions

1. `core/` flat root is current compatibility/public surface, not final structure.
2. Final structure separates `core/common`, `core/predictor_schema`, `core/mapping`, `core/ml`, and `core/calculators`.
3. Compatibility wrappers are transition safety devices, not final architecture.
4. New production code must use approved package owner paths after boundary foundation exists.
5. Calculator engines move toward `core/calculators/standards`.
6. ML pipeline moves toward `core/ml`.
7. Predictor table/schema/mapping responsibility moves out of flat `core/constants.py`.
8. Pure mapping conversion moves out of `scripts/update_mapping.py`; file dialog behavior remains outside core.
9. PySide6 Predictor schema/mapping recovery waits until project-wide architecture reset is reflected in architecture docs.
10. Worker/progress and Trainer foundation wait until schema/mapping recovery is stable.

## 8. Out of scope for this plan

This plan does not authorize:

- calculator formula changes
- ML algorithm changes
- feature engineering changes
- model artifact format changes
- fixture/golden changes
- public API/result key changes
- immediate deletion of root compatibility files
- immediate retirement of legacy PyQt reference files
- large mixed refactors combining package movement with behavior changes

## 9. Next action

Next action:

1. Update architecture SSOT documents with this plan.
2. Then implement core package boundary foundation.
3. Then begin actual implementation moves in focused slices.
4. Then resume PySide6 Predictor schema/mapping recovery.
