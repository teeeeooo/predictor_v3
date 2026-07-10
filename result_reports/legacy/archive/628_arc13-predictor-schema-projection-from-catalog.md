# 628 Arc 13 Predictor Schema Projection From Catalog

## Goal

Move predictor schema ML-visible columns to feature catalog projection while
preserving the existing `COLUMNS`, `INPUT_COLS`, `AUTO_COLS`, and `RESULT_COLS`
contracts used by Predict UI and adapters.

## Changed Files

- `core/ml/feature_catalog_projection.py`
- `core/predictor_schema/columns.py`
- `tests/test_ml_feature_catalog.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/active/628_arc13-predictor-schema-projection-from-catalog.md`

## Current Schema Parity

The projected schema preserves current keys, headers, widths, colors,
`ml_feature`, `ml_target`, `source`, and `mapping_key` values for the existing
schema. Focused tests assert:

- `INPUT_COLS`: `cooling_capa`, `heating_capa`, dropdown-only input columns.
- `AUTO_COLS`: `id_volume` through `comp_cc`.
- `RESULT_COLS`: ML result columns plus rule-only `EER`, `CSPF`, `COP`,
  `HSPF2` columns.

## Projection Result

- `core.ml.feature_catalog_projection.predictor_columns_projection()` projects
  active catalog rows with role `input`, `auto`, or `result`.
- Projection order is role group `input` -> `auto` -> `result`, then catalog
  `order` inside each group.
- `one_hot`, `derived`, and `hidden` rows do not directly create UI columns.
- Input/auto rows receive `ml_feature`; result rows receive `ml_target`; auto
  rows receive `source` and `mapping_key`.

## Width / Color Strategy

Width and color remain code-derived. `ROLE_PRESENTATION_DEFAULTS` owns role
colors and base widths:

- `input`: width `90`, `#FFFFFF`
- `auto`: width `90`, `#F2F2F2`
- `result`: width `100`, `#E6F3E6`

Narrow `WIDTH_OVERRIDES` preserve existing widths for `comp_eer`, `comp_cc`,
and `ref_qty`. Existing dropdown-only input widths and rule-only result widths
remain code-owned compatibility metadata because those columns are not catalog
ML feature rows.

## Runtime Behavior

Runtime-facing source owner changed for `core/predictor_schema/columns.py`.
The exported schema values are preserved. Predict adapters and UI still import
the same schema exports and do not read raw CSV directly.

No inference zero-fill behavior, preprocessing formula, registry behavior,
prediction result dict contract, train/predict UI behavior, ML algorithm, or
artifact behavior changed.

## Read Ledger

- `config/ml/features.csv`: full small file, reason: catalog role/order source.
- `core/ml/feature_catalog_projection.py`: full file, reason: projection helper
  addition.
- `core/predictor_schema/columns.py`: full file, reason: schema owner
  conversion.
- `apps/predict/adapters/row_to_ml_input_adapter.py`: lines 1-120, reason:
  adapter schema usage check.
- `apps/predict/adapters/prediction_result_adapter.py`: lines 1-100, reason:
  result mapping check.
- `apps/predict/schema/column_schema_adapter.py`: lines 1-120, reason: adapter
  contract check.
- `tests/test_ml_feature_catalog.py`: full focused test file, reason: schema
  projection and parity tests.
- `result_reports/active/627_arc13-feature-catalog-contract-cleanup.md`:
  targeted contract/order sections, reason: Slice 3 boundary.
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

`hotspot_delta` is wiring-only: `columns.py` remains the predictor schema
export owner and delegates ML-visible column construction to catalog projection
without changing downstream adapters.

## Known Risks / Open Questions

- Dropdown-only input columns and rule-only result columns are still code-owned
  compatibility inserts because they are not catalog ML feature rows.
- Role-based width defaults require narrow compatibility overrides to preserve
  the current schema exactly.
- One-hot adapter tuples are still hard-coded until a later slice.

## Next Action

Arc 13 Slice 4 - One-hot Adapter Projection from Catalog or Training Header
Runtime Guard.

## Verification

- `python3 -B -m compileall -q core/ml core/predictor_schema apps/predict apps/train tests`:
  OK.
- `python3 -B -m pytest tests -k "feature_catalog"`: OK, 25 passed and
  1415 deselected.
- `python3 -B -m pytest tests -k "predict_schema or prediction_adapter or prediction_usecase or apps_predict"`:
  OK, 129 passed and 1311 deselected.
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
  topic: Arc 13 predictor schema projection
  content: Predictor schema ML-visible columns now project from the feature
    catalog by role group and catalog order, while dropdown-only input and
    rule-only result columns remain code-owned compatibility inserts.
  keywords: arc13, predictor-schema, feature-catalog, columns, ui-order,
    role-defaults
