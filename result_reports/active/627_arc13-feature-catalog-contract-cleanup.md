# 627 Arc 13 Feature Catalog Contract Cleanup

## Goal

Clarify the feature catalog contract after Slice 2, split catalog module
responsibilities, and add non-runtime training header guard helpers/tests.

## Changed Files

- `core/ml/feature_catalog.py`
- `core/ml/feature_catalog_validation.py`
- `core/ml/feature_catalog_projection.py`
- `core/ml/features.py`
- `tests/test_ml_feature_catalog.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `docs/designs/2026-06-30-arc13-ml-feature-manifest-design-gate.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/active/627_arc13-feature-catalog-contract-cleanup.md`

## Training Header Contract

- `ml_name` is the raw training data header and the internal ML
  feature/target name.
- Training CSV/Excel headers must match catalog `ml_name` values.
- No `train_header`, alias, or header mapping column is added.
- Feature addition flow is catalog row -> role metadata -> training header
  aligned to `ml_name` -> validator/tests -> training.

## Module Split

- `core/ml/feature_catalog.py`: data model, CSV loader, existing public
  re-exports.
- `core/ml/feature_catalog_validation.py`: catalog validation and registry
  reference validation.
- `core/ml/feature_catalog_projection.py`: feature/target/projection helpers
  and training header contract helpers.

Existing imports such as
`from core.ml.feature_catalog import validate_feature_catalog` are preserved by
re-export.

## Order Semantics

`BASE_FEATURES` and `TARGETS` remain deterministic export lists for current ML
runtime compatibility, but they are not UI order contracts. Predictor UI order
is reserved for Slice 3 schema projection: group order `input` -> `auto` ->
`result`, then catalog `order` inside each group.

`BASE_FEATURE_RESULT_EXPORT_ORDER` remains only as a legacy deterministic export
policy because current `BASE_FEATURES` places `Ref Qty` before power/frequency
target-like names while `TARGETS` has a different stable order.

## Training Header Helpers

- `FeatureCatalog.training_headers()`
- `FeatureCatalog.validate_training_headers(headers)`
- `validate_training_headers(headers, catalog)`

Tests cover accepted catalog headers, missing required headers, unknown headers,
and derived features not being required as raw training headers.

## Import-Time Catalog Hardening

- Missing catalog file errors include the missing path.
- Invalid catalog row parse errors and validation errors are wrapped with clear
  `RuntimeError` messages from `core.ml.features`.
- A guard test checks that `DEFAULT_CATALOG_PATH` exists for runtime import.

## Runtime Behavior

No predictor schema projection, inference zero-fill behavior, preprocessing
formula, registry behavior, train/predict UI behavior, ML algorithm, or artifact
behavior changed. The only runtime-facing behavior remains the Slice 2
`core.ml.features` catalog-backed export surface.

## Read Ledger

- `config/ml/features.csv`: full small file, reason: catalog contract and role
  semantics.
- `core/ml/feature_catalog.py`: full file, reason: split loader/data model from
  validation and projection.
- `core/ml/features.py`: full small file, reason: import-time error hardening.
- `tests/test_ml_feature_catalog.py`: full focused test file, reason: order
  semantics and training header tests.
- `result_reports/active/626_arc13-ml-features-projection-from-catalog.md`:
  targeted order/risk sections, reason: cleanup of Slice 2 semantic issue.
- `docs/designs/2026-06-30-arc13-ml-feature-manifest-design-gate.md`: targeted
  schema, projection, and migration sections, reason: contract wording cleanup.
- broad read: none.
- repeated read: none.

## change_gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

`new_source` is small: the new validation and projection modules split existing
catalog responsibilities without adding a new runtime surface.

## Known Risks / Open Questions

- Training header validation is not yet wired into training runtime.
- Predictor schema remains hard-coded until Slice 3.
- Packaging must continue to include `config/ml/features.csv`.

## Next Action

Arc 13 Slice 3 - Predictor Schema Projection from Catalog.

## Verification

- `python3 -B -m compileall -q core/ml core/predictor_schema apps/predict apps/train tests`:
  OK.
- `python3 -B -m pytest tests -k "feature_catalog"`: OK, 21 passed and
  1415 deselected.
- `python3 -B -m pytest tests -k "predict_schema or prediction_adapter or prediction_usecase or apps_predict"`:
  OK, 129 passed and 1307 deselected.
- `python3 -B tools/code_checker/build_reference_map.py --check`: initially
  stale after module split.
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
  topic: Arc 13 feature catalog contract
  content: `ml_name` is the raw training header and internal ML name; no
    training-header alias/mapping is introduced. Catalog responsibilities are
    split into loader/data model, validation, and projection helpers.
  keywords: arc13, feature-catalog, ml-name, training-header, validation,
    projection
