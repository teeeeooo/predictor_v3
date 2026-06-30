# 630 Arc 13 One-hot Adapter Projection From Catalog

## Goal

Move Predict one-hot feature list ownership from
`RowToMlInputAdapter` hard-coded tuples to the ML feature catalog projection
while preserving the existing prediction input dict contract.

## Changed Files

- `core/ml/feature_catalog_projection.py`
- `apps/predict/adapters/row_to_ml_input_adapter.py`
- `tests/test_ml_feature_catalog.py`
- `tests/test_apps_predict_prediction_adapters.py`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/active/630_arc13-one-hot-adapter-projection-from-catalog.md`

## Current One-hot Ownership Check

Before this slice, `RowToMlInputAdapter` owned:

- `_REFRIGERANT_FEATURES = ("R410A", "R32", "R290")`
- `_EXPANSION_FEATURES = ("EEV", "Capi")`

The adapter used `ref_type` and `exp_type` selections to initialize all
one-hot output keys to `0.0`, then set the selected feature to `1.0`. Unknown
nonblank selections produced the existing `Unsupported option ignored: ...`
warning and left the group at `0.0`.

## Projection Result

- `core.ml.feature_catalog_projection.one_hot_group()` now returns one named
  one-hot group with a clear missing-group error.
- `RowToMlInputAdapter` loads and validates the feature catalog through
  catalog/projection surfaces, not by reading raw CSV directly.
- `RowToMlInputAdapter` accepts injected `one_hot_groups` for focused tests.
- The adapter no longer exposes `_REFRIGERANT_FEATURES` or
  `_EXPANSION_FEATURES`.

The adapter still owns the UI input key to catalog group mapping:

- `ref_type` -> `refrigerant`
- `exp_type` -> `expansion_device`

That mapping belongs to adapter input semantics, not to the feature list owner.

## Behavior Parity

Preserved behavior:

- output keys: `R410A`, `R32`, `R290`, `EEV`, `Capi`;
- selected one-hot feature value: `1.0`;
- unselected one-hot feature value: `0.0`;
- missing selections leave all features in the group at `0.0`;
- unsupported selections keep the existing warning text;
- group output order follows catalog one-hot row order.

## Runtime Behavior

The prediction input dict contract is preserved. The runtime source owner for
one-hot feature lists changed to the validated feature catalog projection.

No `features.csv` semantics, predictor schema column contract, prediction
result dict contract, inference zero-fill behavior, training runtime guard,
ML algorithm, training/artifact behavior, mapping schema, or calculator code
changed.

## Read Ledger

- `AGENT_TASK_ROUTER.md`: ML/Predictor and report workflow sections.
- `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md`: focused ML/Predictor
  workflow boundary.
- `config/ml/features.csv`: one-hot row lines only via search output.
- `core/ml/feature_catalog.py`: loader/projection import surface.
- `core/ml/feature_catalog_projection.py`: full file, reason: one-hot helper.
- `apps/predict/adapters/row_to_ml_input_adapter.py`: full file, reason:
  current one-hot path and conversion.
- `tests/test_ml_feature_catalog.py`: focused file, reason: catalog one-hot
  parity tests.
- `tests/test_apps_predict_prediction_adapters.py`: focused file, reason:
  adapter one-hot behavior tests.
- `result_reports/active/629_arc13-predictor-ui-only-column-owner-split.md`:
  focused file, reason: prior remaining risk.
- `docs/WORK_PLAN.md`, `project_brief.md`, `project_log.md`: targeted Arc 13
  status sections.
- broad read: none.

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

The adapter behavior is unchanged at the prediction input dict boundary; only
the one-hot feature list source owner changed. The code map was regenerated
after structural source changes, and existing catalog projection ownership was
reused instead of creating a new feature-list owner.

## Known Risks / Open Questions

- Training header runtime guard remains for Arc 13 Slice 5.
- Dropdown option lists in `apps/predict/adapters/dropdown_option_adapter.py`
  still own UI dropdown base options and were not changed in this slice.

## Next Action

Arc 13 Slice 5 - Training Header Runtime Guard.

## Verification

- `python3 -B -m compileall -q core/ml apps/predict/adapters tests/test_ml_feature_catalog.py tests/test_apps_predict_prediction_adapters.py`:
  OK.
- `python3 -B -m pytest tests/test_ml_feature_catalog.py tests/test_apps_predict_prediction_adapters.py -q`:
  OK, 38 passed.
- `python3 -B -m compileall -q core/ml core/predictor_schema apps/predict apps/train tests`:
  OK.
- `python3 -B -m pytest tests -k "feature_catalog"`: OK, 29 passed and
  1418 deselected.
- `python3 -B -m pytest tests -k "predict_schema or prediction_adapter or prediction_usecase or apps_predict"`:
  OK, 132 passed and 1315 deselected.
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
  topic: Arc 13 one-hot adapter projection
  content: Predict one-hot feature lists are now sourced from the ML feature
    catalog projection; `RowToMlInputAdapter` keeps only UI input key to one-hot
    group mapping and preserves existing output dict behavior.
  keywords: arc13, one-hot, feature-catalog, predict-adapter, row-to-ml
