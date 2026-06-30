# 626 Arc 13 ML Features Projection From Catalog

## Goal

Convert `core/ml/features.py` exports to feature catalog projections while
preserving existing import surface, feature order, and downstream behavior.

## Changed Files

- `config/ml/features.csv`
- `core/ml/feature_catalog.py`
- `core/ml/features.py`
- `tests/test_ml_feature_catalog.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/active/626_arc13-ml-features-projection-from-catalog.md`

## Result Row Order Correction

`config/ml/features.csv` result rows now follow canonical `TARGETS` order:

1. `Cooling Power`
2. `Heating Power`
3. `Ref Qty`
4. `Cooling Hz`
5. `Heating Hz`

No result row role, `ui_key`, label, or `zero_fill_policy` semantics changed.

## TARGET_COMPAT_ORDER

Removed. `FeatureCatalog.targets()` now returns active `role=result` rows in
catalog order. Tests assert that result row order and exported `TARGETS` both
match the canonical target order.

Because legacy `BASE_FEATURES` order differs from canonical target order for
result-like names, `base_features()` keeps a separate
`BASE_FEATURE_RESULT_ORDER` projection to preserve current runtime order.

## Projection Result

`core/ml/features.py` now loads and validates the catalog, then exports:

- `BASE_FEATURES = catalog.base_features()`
- `DERIVED_FEATURES = catalog.derived_features()`
- `TARGETS = catalog.targets()`

If the catalog is invalid, import raises `RuntimeError` with the validator
messages joined into the exception text.

## Runtime Behavior

Runtime import surface is preserved:

- `core.ml.features.BASE_FEATURES`
- `core.ml.features.DERIVED_FEATURES`
- `core.ml.features.TARGETS`

The values and order are covered by parity tests. `core/ml/registry.py`,
`core/predictor_schema/columns.py`, `core/ml/inference.py`,
`core/ml/preprocessing.py`, predict/train adapters, inference zero-fill
behavior, ML algorithms, and artifacts were not changed.

## Read Ledger

- `docs/designs/2026-06-30-arc13-ml-feature-manifest-design-gate.md`: targeted
  projection and migration lines, reason: Slice 2 scope.
- `result_reports/active/625_arc13-feature-catalog-loader-validator.md`:
  targeted runtime unchanged and known risk sections, reason: Slice 1 context.
- `config/ml/features.csv`: full small file, reason: result row order and
  catalog row semantics.
- `core/ml/feature_catalog.py`: full 250 LOC file, reason: projection owner and
  removal of target compatibility ordering.
- `core/ml/features.py`: full small file, reason: runtime export conversion.
- `core/ml/registry.py`: lines 1-69, reason: confirm no registry behavior
  change and preserve reference tests.
- `core/ml/inference.py`: lines 1-90, reason: confirm zero-fill behavior is
  untouched.
- `core/ml/preprocessing.py`: lines 1-85, reason: confirm derived formula owner
  is untouched.
- `tests/test_ml_feature_catalog.py`: full focused test file, reason: parity
  test updates.
- broad read: none.
- repeated read: none.

## change_gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

`hotspot_delta` is wiring-only: `core/ml/features.py` is a small compatibility
export surface now sourcing values from the catalog projection. No additional
schema, registry, inference, preprocessing, or adapter responsibility was
added.

## Known Risks / Open Questions

- Importing `core.ml.features` now reads `config/ml/features.csv`. This is the
  intended Slice 2 source-owner change, but packaging must include the catalog.
- `BASE_FEATURES` and canonical `TARGETS` still have conflicting result-like
  ordering, so `BASE_FEATURE_RESULT_ORDER` remains a compatibility policy.
- Predictor schema projection is still hard-coded in
  `core/predictor_schema/columns.py` until Slice 3.

## Next Action

Arc 13 Slice 3 - Predictor Schema Projection from Catalog.

## Verification

- `python3 -B -m compileall -q core/ml core/predictor_schema apps/predict apps/train tests`
  OK.
- `python3 -B -m pytest tests -k "feature_catalog"`: OK, 13 passed and
  1415 deselected.
- `python3 -B -m pytest tests -k "predict_schema or prediction_adapter or prediction_usecase or apps_predict"`:
  OK, 129 passed and 1299 deselected.
- `python3 -B tools/code_checker/build_reference_map.py --check`: initially
  stale after source changes.
- `python3 -B tools/code_checker/build_reference_map.py`: regenerated
  `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK, fresh.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings outside this slice.
- `git diff --check`: OK.
- `python3 -B tools/check_agent_change_gate.py --cached`: OK.
- `git diff --cached --check`: OK.
- `git status --short`: staged task files only before commit.

## Commit / Push

- pending

## Project Memory Delta

- type: decision
  topic: Arc 13 ML features catalog projection
  content: `core/ml/features.py` now exports BASE_FEATURES, DERIVED_FEATURES,
    and TARGETS from the validated feature catalog. TARGETS order is owned by
    result row order; BASE_FEATURES preserves a separate legacy result-like
    ordering policy.
  keywords: arc13, feature-catalog, core-ml-features, targets-order,
    base-features-order
