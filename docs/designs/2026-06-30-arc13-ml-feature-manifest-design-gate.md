# Arc 13 Slice 0 - ML Feature Manifest Design Gate

## Goal

Define the minimal design gate for moving ML feature ownership toward a
user-managed CSV manifest without changing production runtime behavior in this
slice.

Arc 13 keeps the broader ML Pipeline Stabilization direction, but its first
entry point is narrowed to ML Feature Manifest SSOT Foundation.

## Non-goals

- Do not change production Python behavior.
- Do not connect a manifest to runtime imports.
- Do not convert `core/ml/features.py`, `core/ml/registry.py`, or
  `core/predictor_schema/columns.py` to manifest projections in Slice 0.
- Do not create `config/ml/features.csv` as a runtime-looking source in this
  slice.
- Do not change model algorithms, Optuna/RFE/XGBoost parameters, fixtures,
  golden expected values, mapping schema, or model artifact schema.
- Do not revisit Arc 12.

## Current Owner Inventory

| Owner | Current responsibility | Manifest impact |
| --- | --- | --- |
| `core/ml/features.py` | Defines `BASE_FEATURES`, `DERIVED_FEATURES`, and `TARGETS` as runtime constants. | Long-term projection target. Slice 1 must validate parity before this file reads catalog projections. |
| `core/ml/registry.py` | Defines `MODEL_REGISTRY`, model targets, `use_rfe`, and target-specific `exclude` / `allowed` rules. | Keep developer-managed initially. Catalog validator should verify all registry target/exclude/allowed names exist in the catalog. |
| `core/predictor_schema/columns.py` | Defines `COLUMNS`, `INPUT_COLS`, `AUTO_COLS`, `RESULT_COLS`, `ml_feature`, `ml_target`, `source`, `mapping_key`, `width`, and `bg_color`. | Split user-managed feature contract from code-derived UI presentation. Width/color stay code-derived by role. |
| `apps/predict/adapters/row_to_ml_input_adapter.py` | Uses schema `ml_feature` metadata and hard-codes one-hot tuples `R410A` / `R32` / `R290` and `EEV` / `Capi`. | One-hot group ownership can move to catalog projection after parity tests. |
| `apps/predict/adapters/prediction_result_adapter.py` | Uses `TARGETS` plus result-column `ml_target` mapping to detect missing target predictions and fill `ResultRow`. | Result target projection can simplify this mapping, but behavior must remain identical. |
| `apps/predict/schema/column_schema_adapter.py` | Adapts `COLUMNS` into Qt-free `PredictColumn`, including width, color, `ml_feature`, `ml_target`, `source`, and `mapping_key`. | Should keep consuming predictor schema projection, not load manifest directly. |
| `core/ml/inference.py` | `build_input_df()` fills every missing `BASE_FEATURES` member with `0.0`, then calls `calculate_derived_features()`. | Current compatibility behavior conflicts with target policy for most features. Tightening is deferred until catalog policy is tested. |
| `core/ml/preprocessing.py` | Owns `calculate_derived_features()`, `prepare_pipeline()` target/global leakage drops, and base-feature NaN filtering in `load_and_preprocess()`. | Derived formulas remain code-owned. Manifest marks derived feature names and role only. |
| `core/ml/training.py` | Iterates `MODEL_REGISTRY`, applies target rules, uses RFE/Optuna, stores selected feature lists in artifact data. | No Slice 0 or Slice 1 runtime change. Registry validator should protect feature references before training. |
| `core/ml/artifacts.py` | Owns `MODEL_FILE`, `TRAIN_DATA_FILE`, and single-artifact path contract. | Out of manifest scope. Artifact schema remains code-owned. |

## User-Managed CSV Boundary

The CSV should contain only fields a user must know to add, remove, or rename
an ML feature. It should not contain presentation settings, model policy, or
implementation formulas.

User-managed fields:

| Column | Purpose | Required policy |
| --- | --- | --- |
| `order` | Stable ordering for projections and review. | Required for active rows. |
| `feature_id` | Stable identifier that survives label/name edits. | Unique. Required. |
| `ml_name` | Training data header name and internal ML feature or target name. | Unique among active rows. Required for ML-visible roles. No train-header alias/mapping column is planned. |
| `role` | Feature classification. | Enum: `input`, `auto`, `result`, `derived`, `one_hot`, `hidden`. |
| `ui_key` | Predictor schema key when UI-visible. | Required for `input`, `auto`, `result`; unique among UI-visible active rows. |
| `label` | User-facing header/label. | Required for `input`, `auto`, `result`. |
| `source` | Auto-fill source key. | Required for `auto`; empty otherwise unless explicitly justified. |
| `mapping_key` | Mapping payload key for auto-fill. | Required for `auto`. |
| `one_hot_group` | Stable group name for one-hot features. | Required for `one_hot`; examples: `refrigerant`, `expansion_device`. |
| `zero_fill_policy` | Whether prediction may synthesize missing values as `0.0`. | Enum: `disallow`, `mode_missing_allowed`. |
| `active` | Projection participation. | `true` rows project; `false` rows are deprecated inventory only. |
| `notes` | Human review notes. | Optional. |

Code-derived or developer-managed fields excluded from CSV:

| Excluded field | Owner |
| --- | --- |
| `width`, `bg_color`, delegate/editor behavior, table widget settings | UI/schema projection code, derived from role and toolkit rules. |
| RFE usage, `model_key`, target-specific `exclude` / `allowed` rules | `MODEL_REGISTRY` developer policy. |
| Derived feature formulas | `core/ml/preprocessing.py`. |
| Artifact schema, model wrapper metadata, selected-feature snapshots | ML artifact/training owners. |
| Calculator seasonal outputs such as CSPF/HSPF as model inputs | Forbidden by ML/calculator boundary; result-only classification needs explicit review. |

Feature addition flow:

1. Add a feature row to `config/ml/features.csv`.
2. Set role and required metadata such as `source`, `mapping_key`, or
   `one_hot_group`.
3. Align the raw training CSV/Excel header to the row's `ml_name`.
4. Run catalog validator and parity tests before training.

`BASE_FEATURES` and `TARGETS` are ML feature/target name exports, not UI column
order contracts. Predictor UI order is owned by predictor schema projection:
group order is `input` -> `auto` -> `result`, and rows inside each group follow
catalog `order`. Width and color remain role-based code-derived defaults.

## Minimal Manifest Schema Proposal

Initial target path for implementation is `config/ml/features.csv`, but Slice 0
does not create or load that file.

```csv
order,feature_id,ml_name,role,ui_key,label,source,mapping_key,one_hot_group,zero_fill_policy,active,notes
10,cooling_capa,Cooling Capa,input,cooling_capa,냉방능력,,,,mode_missing_allowed,true,mode-specific missing allowed only for compatible prediction modes
20,heating_capa,Heating Capa,input,heating_capa,난방능력,,,,mode_missing_allowed,true,mode-specific missing allowed only for compatible prediction modes
30,id_volume,ID Volume,auto,id_volume,ID Volume,idu,ID Volume,,disallow,true,
40,r32,R32,one_hot,,R32,,,refrigerant,disallow,true,
50,cooling_power,Cooling Power,result,cooling_power,냉방 소비전력,,,,mode_missing_allowed,true,target and result projection
60,cool_capa_per_eer,Cool_Capa_per_EER,derived,,,,,,disallow,true,formula remains code-owned
```

Role decisions:

- `input`: user-entered numeric or dropdown-backed data that may expose an ML
  feature.
- `auto`: auto-filled hardware/spec data sourced from mapping.
- `result`: model target displayed in prediction results.
- `derived`: code-calculated feature, not user-editable and no UI column.
- `one_hot`: encoded feature generated from a grouped categorical UI value.
- `hidden`: active internal feature inventory with no UI column.

Result target expression:

- Result targets are rows with `role=result`.
- Their `ml_name` values define the `TARGETS` projection.
- Their `ui_key` values define the result UI projection.

Hidden/internal expression:

- Use `role=hidden` for active catalog entries that must be known to validators
  but should not appear in UI projections.
- Use `active=false` only for deprecated inventory. In projections, inactive
  rows are excluded by default.

## Zero Fill Policy

Current behavior:

- `core/ml/inference.py::build_input_df()` adds every missing member of
  `BASE_FEATURES` to the input frame as `0.0`.
- This is compatibility behavior and is not changed in Slice 0.

Target policy:

- `zero_fill_policy=mode_missing_allowed` is allowed only for:
  `Cooling Capa`, `Cooling Power`, `Heating Capa`, `Heating Power`.
- All other features default to `disallow`.
- The intended reason is mode-specific absence: cooling-only or heating-only
  workflows may legitimately omit the opposite mode capacity/power.
- Missing hardware, one-hot, mapping, or data-quality features should not be
  silently synthesized as `0.0`.

Gap:

- Current `build_input_df()` is broader than the target policy.
- Tightening it requires explicit behavior tests and user confirmation in a
  later implementation slice because existing prediction compatibility may
  depend on broad zero fill.

## Role-Based UI Presentation Defaults

The user-managed CSV does not own presentation details.

| Role | UI projection | Default presentation owner |
| --- | --- | --- |
| `input` | Visible input column if `ui_key` exists. | White/default input width from schema projection. |
| `auto` | Visible auto-fill column if `ui_key` exists. | Gray/default auto width from schema projection. |
| `result` | Visible result column if `ui_key` exists. | Green/default result width from schema projection. |
| `derived` | No UI column. | None. |
| `one_hot` | Usually no direct UI column; generated from categorical input. | One-hot group projection. |
| `hidden` | No UI column. | None. |

## Projection Strategy

Target shape for implementation:

- Add `core/ml/feature_catalog.py` to load and validate the CSV and provide
  projection helpers.
- Keep existing import surfaces stable:
  - `core/ml/features.py` continues exporting `BASE_FEATURES`,
    `DERIVED_FEATURES`, and `TARGETS`.
  - `core/predictor_schema/columns.py` continues exporting `COLUMNS`,
    `INPUT_COLS`, `AUTO_COLS`, and `RESULT_COLS`.
  - Predict adapters continue consuming schema/helper projections, not raw CSV.
- Convert in stages with parity tests before replacing runtime constants.
- Keep `core/ml/registry.py` developer-managed at first. The catalog validator
  checks registry references but does not own leakage policy.

Candidate projection helpers:

| Helper | Projection |
| --- | --- |
| `base_features()` | Active `input`, `auto`, `one_hot`, and any model-input `hidden` rows, excluding `result` and `derived`. |
| `derived_features()` | Active `derived` rows. |
| `targets()` | Active `result` rows. |
| `predictor_columns()` | Active `input`, `auto`, and `result` rows with role-based width/color defaults. |
| `one_hot_groups()` | Mapping of stable group name to ordered `ml_name` tuple. |
| `zero_fill_policies()` | Mapping of `ml_name` to policy enum. |
| `training_headers()` | Active raw-training header names from `input`, `auto`, `one_hot`, and `result` rows; derived rows are excluded because formulas are code-owned. |

## Validation Requirements

Minimum validator requirements for implementation:

- `feature_id` is unique.
- `ml_name` is unique among active ML-visible features.
- `ui_key` is unique among UI-visible active features.
- `role` is an allowed enum value.
- `zero_fill_policy` is an allowed enum value.
- `mode_missing_allowed` is accepted only for `Cooling Capa`, `Cooling Power`,
  `Heating Capa`, and `Heating Power`.
- `role=input`, `role=auto`, and `role=result` require `ui_key` and `label`.
- `role=auto` requires `source` and `mapping_key`.
- `role=one_hot` requires a non-empty stable `one_hot_group`.
- `role=result` enters the `TARGETS` projection.
- Every registry target, `exclude`, and `allowed` name exists in the catalog.
- Every result target has a result UI projection.
- One-hot group names are non-empty and stable.
- CSPF/HSPF/CSEC/HSEC and other calculator seasonal outputs cannot enter the
  ML feature pool unless explicitly classified as result-only and excluded from
  model inputs.
- `active=false` rows are excluded from all runtime projections and retained
  only as deprecated inventory.

## Migration Plan

1. Slice 1: add the feature catalog CSV draft plus loader/validator with no
   runtime use. Include parity assertions against current constants and schema.
2. Slice 2: derive `core/ml/features.py` exports from catalog projections after
   parity tests cover `BASE_FEATURES`, `DERIVED_FEATURES`, and `TARGETS`.
3. Slice 2.5: split catalog loader, validation, and projection responsibilities;
   clarify that `ml_name` is the raw training header contract; add
   training-header validation helpers without connecting them to training
   runtime.
4. Slice 3: derive predictor schema columns from catalog projections with
   parity tests for order, keys, `ml_feature`, `ml_target`, and role-based
   width/color defaults.
5. Slice 4: move one-hot group ownership from hard-coded adapter tuples to a
   catalog projection while preserving current warnings and encoded output.
6. Slice 5: tighten `build_input_df()` zero-fill behavior from
   `zero_fill_policy` only after focused tests and user confirmation.
7. Slice 6: recheck ML pipeline leakage, artifact, and selected-feature guard
   behavior after catalog-backed projections are stable.

## Risks And Open Questions

- Current broad zero-fill behavior may be masking schema or mapping gaps; it
  should not be tightened without targeted compatibility tests.
- `BASE_FEATURES` currently includes target-like values such as `Ref Qty`,
  `Cooling Power`, `Heating Power`, `Cooling Hz`, and `Heating Hz`; model input
  eligibility must remain governed by registry target rules until catalog
  projections are proven.
- The existing Predict adapter requires `cooling_capa` even when future
  mode-specific behavior may require different validation.
- `apps/train/ui/train_model_panel.py` has a local target tuple; it should be
  checked in a later implementation slice before claiming target projection
  ownership is complete.
- `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md` still contains a historical
  owner sentence about `core/constants.py` / `core/models.py`; this design uses
  the current package owners from architecture docs and code.

## Next Slice Recommendation

Arc 13 Slice 1 - Feature Catalog Loader / Validator Foundation:

- Create `config/ml/features.csv` as the catalog draft.
- Add `core/ml/feature_catalog.py` loader/validator.
- Add tests that validate the catalog and assert parity with current
  `BASE_FEATURES`, `DERIVED_FEATURES`, `TARGETS`, `COLUMNS`, registry
  references, and one-hot groups.
- Keep runtime imports reading the existing modules until parity is accepted.
