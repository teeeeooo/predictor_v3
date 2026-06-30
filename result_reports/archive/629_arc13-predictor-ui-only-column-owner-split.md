# 629 Arc 13 Predictor UI-only Column Owner Split

## Goal

Split predictor UI-only compatibility columns out of
`core/predictor_schema/columns.py` while preserving the existing predictor
schema export contract.

## Changed Files

- `core/predictor_schema/ui_columns.py`
- `core/predictor_schema/columns.py`
- `tests/test_ml_feature_catalog.py`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/active/629_arc13-predictor-ui-only-column-owner-split.md`

## UI-only Column Inventory

`core/predictor_schema/columns.py` previously mixed catalog-based ML columns
with UI-only compatibility columns:

- Catalog-based ML columns: projected from `config/ml/features.csv` for roles
  `input`, `auto`, and `result`.
- Dropdown-only input columns: `idu`, `evap_index`, `odu`, `fin_type`, `pi`,
  `row`, `compressor`, `ref_type`, and `exp_type`.
- Rule-only result columns: `eer`, `cspf`, `cop`, and `hspf2`.

The dropdown-only and rule-only columns are not ML feature catalog rows, so
they now live in `core/predictor_schema/ui_columns.py`.

## Owner Split Result

- `DROPDOWN_INPUT_COLUMNS` owns dropdown-only input metadata.
- `RULE_RESULT_COLUMNS` owns rule-only result metadata.
- `INPUT_INSERT_AFTER` and `RESULT_INSERT_AFTER` own compatibility insertion
  points.
- `insert_columns_after()` owns the small insertion helper.

`ui_columns.py` does not read `config/ml/features.csv` and does not import the
feature catalog loader.

## columns.py Responsibility

`core/predictor_schema/columns.py` now keeps the final predictor schema assembly
role:

- load and validate the feature catalog;
- call `predictor_columns_projection()`;
- split projected columns by `input`, `auto`, and `result`;
- insert UI-only compatibility columns;
- export `COLUMNS`, `INPUT_COLS`, `AUTO_COLS`, `RESULT_COLS`,
  `DROPDOWN_COLS`, and existing column index constants.

The old `LEGACY_*` names were removed from `columns.py` because they described
owner history rather than current responsibility.

## Same-slice Risk Cleanup

Handled in this slice:

- UI-only literal dicts no longer remain in `columns.py`.
- The insertion helper is not duplicated between modules.
- Tests assert the UI-only owner module directly, not just the final key order.

Not handled in this slice:

- One-hot adapter projection remains separate.
- Training header runtime guards remain separate.
- Prediction result dict contract remains unchanged.

## Runtime Behavior

Runtime schema values are preserved. The source owner changed for UI-only
metadata, but the final `COLUMNS`, `INPUT_COLS`, `AUTO_COLS`, `RESULT_COLS`,
dropdown column keys, result keys, widths, colors, and insertion order remain
the same.

No `features.csv`, inference zero-fill behavior, preprocessing formula,
registry behavior, predict/train UI behavior, prediction result dict contract,
ML algorithm, model artifact, mapping schema, or calculator code changed.

## Read Ledger

- `core/predictor_schema/columns.py`: full file, reason: UI-only inventory and
  assembly owner split.
- `core/ml/feature_catalog_projection.py`: full file, reason: confirm catalog
  projection boundary.
- `tests/test_ml_feature_catalog.py`: focused full file, reason: existing
  catalog/schema parity tests.
- `result_reports/active/628_arc13-predictor-schema-projection-from-catalog.md`:
  focused file, reason: prior Slice 3 risk and boundary.
- `docs/WORK_PLAN.md`: current slice and next action sections.
- `project_brief.md`: Arc 13 status section.
- `project_log.md`: recent Arc 13 entries.
- broad read: none.
- repeated read: none.

## change_gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

`new_source` is small and limited to predictor schema UI-only metadata.
`hotspot_delta` is wiring-only because downstream schema exports are preserved.

## Known Risks / Open Questions

- One-hot adapter tuples are still hard-coded until Arc 13 Slice 4.
- Rule-only result columns remain UI-only compatibility metadata, not feature
  catalog rows.
- Narrow width overrides for catalog-projected columns remain necessary to
  preserve exact existing schema widths.

## Next Action

Arc 13 Slice 4 - One-hot Adapter Projection from Catalog.

## Verification

- `python3 -B -m compileall -q core/predictor_schema tests/test_ml_feature_catalog.py`:
  OK.
- `python3 -B -m pytest tests/test_ml_feature_catalog.py -q`: OK, 28
  passed.
- `python3 -B -m compileall -q core/ml core/predictor_schema apps/predict apps/train tests`:
  OK.
- `python3 -B -m pytest tests -k "feature_catalog"`: OK, 28 passed and
  1415 deselected.
- `python3 -B -m pytest tests -k "predict_schema or prediction_adapter or prediction_usecase or apps_predict"`:
  OK, 129 passed and 1314 deselected.
- `python3 -B tools/code_checker/build_reference_map.py --check`: initially
  stale after source changes.
- `python3 -B tools/code_checker/build_reference_map.py`: regenerated
  `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK, fresh.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings outside this slice.
- `git diff --check`: OK.
- `git status --short`: task files only before staging.

## Commit / Push

- pending

## Project Memory Delta

- type: decision
  topic: Arc 13 predictor UI-only column owner split
  content: Predictor dropdown-only input and rule-only result columns are owned
    by `core/predictor_schema/ui_columns.py`; `columns.py` assembles catalog
    projection plus UI-only inserts and preserves final schema exports.
  keywords: arc13, predictor-schema, ui-columns, feature-catalog, columns
