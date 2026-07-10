# 625 Arc 13 Feature Catalog Loader Validator

## Goal

Add the Arc 13 Slice 1 non-runtime ML feature catalog draft, loader/validator,
and parity tests as the foundation for a later `core/ml/features.py` projection
slice.

## Changed Files

- `config/ml/features.csv`
- `core/ml/feature_catalog.py`
- `tests/test_ml_feature_catalog.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/active/625_arc13-feature-catalog-loader-validator.md`

## Catalog Policy Summary

- CSV columns follow the Slice 0 schema: `order`, `feature_id`, `ml_name`,
  `role`, `ui_key`, `label`, `source`, `mapping_key`, `one_hot_group`,
  `zero_fill_policy`, `active`, and `notes`.
- CSV excludes width, color, delegate/editor behavior, model policy, RFE,
  target-specific leakage rules, derived formulas, and artifact schema.
- `mode_missing_allowed` is limited to `Cooling Capa`, `Cooling Power`,
  `Heating Capa`, and `Heating Power`.
- `MODEL_REGISTRY` remains developer-managed code. Tests validate its target,
  `exclude`, and `allowed` references against the catalog.

## Validation / Parity Result

- Catalog projections match current `BASE_FEATURES`, `DERIVED_FEATURES`, and
  `TARGETS`.
- Predictor input/auto and result mappings match current predictor schema.
- One-hot groups match `RowToMlInputAdapter` tuples.
- Registry references are present in the catalog.
- Inactive rows are excluded from runtime-style projections.
- Invalid catalog samples fail validator checks.
- Train panel local `TARGETS` tuple matches catalog targets.

## Runtime Unchanged

No existing runtime module imports `core.ml.feature_catalog` in this slice.
`core/ml/features.py`, `core/ml/registry.py`,
`core/predictor_schema/columns.py`, `core/ml/inference.py`,
`core/ml/preprocessing.py`, `apps/predict`, and `apps/train` runtime behavior
were not changed.

## Read Ledger

- `docs/designs/2026-06-30-arc13-ml-feature-manifest-design-gate.md`: targeted
  headings for schema, validation, projection, and migration policy.
- `core/ml/features.py`: lines 1-17, reason: current feature/target constants.
- `core/ml/registry.py`: lines 1-69, reason: registry target/rule references.
- `core/predictor_schema/columns.py`: lines 1-140, reason: predictor schema
  feature/result mapping parity.
- `apps/predict/adapters/row_to_ml_input_adapter.py`: lines 1-120, reason:
  one-hot tuple parity.
- `apps/predict/adapters/prediction_result_adapter.py`: lines 1-100, reason:
  target/result mapping behavior.
- `apps/predict/schema/column_schema_adapter.py`: lines 1-120, reason:
  schema adapter metadata surface.
- `apps/train/ui/train_model_panel.py`: symbol search and lines 1-60, reason:
  local target tuple check.
- broad read: none.
- repeated read: none.

## change_gate

```yaml
change_gate:
  new_source: justified
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

`new_source` is justified because the 247 LOC catalog module is cohesive but
near the soft limit. If Slice 2 expands it materially, split validation or
projection helpers before adding more responsibility.

`reuse_commonization` is checked: code-map search found no existing
feature-catalog loader/helper owner; `core/ml` is the existing ML owner package.

## Known Risks / Open Questions

- Current `BASE_FEATURES` and `TARGETS` order differ for result-like names.
  Slice 1 keeps explicit target compatibility order in the catalog projection
  to satisfy parity without runtime changes.
- The catalog is not yet a production runtime source.
- Broad `build_input_df()` zero-fill behavior remains unchanged.
- Real model prediction quality is not validated by this foundation slice.

## Next Action

Arc 13 Slice 2 - ML Features Projection from Catalog.

## Verification

- `python3 -B -m pytest tests --collect-only -q -k "feature_catalog or predict_schema or prediction_adapter or prediction_usecase or apps_predict"`:
  OK, 140 collected and 1286 deselected.
- `python3 -B -m compileall -q core/ml core/predictor_schema apps/predict apps/train tests`:
  OK.
- `python3 -B -m pytest tests -k "feature_catalog"`: OK, 11 passed and
  1415 deselected.
- `python3 -B -m pytest tests -k "predict_schema or prediction_adapter or prediction_usecase or apps_predict"`:
  OK, 129 passed and 1297 deselected.
- `python3 -B tools/code_checker/build_reference_map.py --check`: initially
  stale after adding source.
- `python3 -B tools/code_checker/build_reference_map.py`: regenerated
  `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK, fresh.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings outside this slice.
- `git diff --check`: OK.
- `python3 -B tools/check_agent_change_gate.py --cached`: OK.
- `git diff --check` / `git diff --cached --check`: OK.
- `git status --short`: staged task files only before commit.

## Commit / Push

- pending

## Project Memory Delta

- type: decision
  topic: Arc 13 feature catalog loader foundation
  content: A non-runtime ML feature catalog CSV and stdlib loader/validator now
    exist with focused parity tests against current constants, predictor schema,
    one-hot tuples, registry references, zero-fill policy, and Train panel
    target tuple. Runtime imports remain unchanged.
  keywords: arc13, feature-catalog, ml-feature-manifest, validator, parity,
    zero-fill-policy
