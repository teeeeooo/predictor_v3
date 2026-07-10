# Arc 15A Data Definition Core Projection Validator

## Goal

Implement the Qt-free Arc 15A Data Definition foundation: project
`schema.csv` plus explicit derived feature policy into Feature
Catalog-compatible rows, validate parity against current `features.csv`, extract
mapping requirements, validate one-hot relationships, and expose a read-only
readiness report object.

## Modified Files

- `core/data_definition/__init__.py`
- `core/data_definition/derived_policy.py`
- `core/data_definition/model.py`
- `core/data_definition/projection.py`
- `core/data_definition/readiness.py`
- `core/data_definition/report_model.py`
- `core/data_definition/validation.py`
- `tests/test_data_definition_core_projection.py`
- `result_reports/active/713_arc15a-data-definition-core-projection-validator.md`

## Implementation Summary

- Added a new `core.data_definition` package with read-only dataclasses,
  projection helpers, validation helpers, and passive readiness slots.
- Reused existing `core.predictor_schema.catalog_v2` and
  `core.ml.feature_catalog` loaders instead of creating new file parsers.
- Kept projection and validation in memory only; no save, auto-fix, UI,
  runtime adapter, config, or mapping value behavior was changed.
- Split report/issue dataclasses into `report_model.py` to avoid a new-source
  class-count structure warning.

## Projection / Validator Contract

- Projection order matches current `features.csv`: input, auto, emitted
  one-hot features, ML target result rows, then derived policy rows.
- `notes` is intentionally excluded from parity because Arc 15A validates
  behavior/compatibility fields only: order, `ml_name`, role, `ui_key`, label,
  source, `mapping_key`, `one_hot_group`, zero-fill policy, and active state.
- Current active derived rows are owned by
  `load_current_derived_feature_policy()` and are not treated as orphans.
- `cond_area` and `cond_volume` preserve semantic mapping requirements against
  `cond_specs`, while Feature Catalog compatibility comparison uses current
  source `odu`.
- One-hot validation distinguishes selector rows from emitted hidden ML feature
  rows and compares emitted groups with current Feature Catalog groups.
- Readiness checks are passive: training headers are header-only if
  `data/Practice_4.csv` exists; model activation and restart impact are marked
  not evaluated in Arc 15A.

## Current Parity Result

- Projected feature rows: 28.
- Feature Catalog parity issues: 0.
- Mapping requirements: 8.
- One-hot relationships: `refrigerant -> R410A, R32, R290`;
  `expansion_device -> EEV, Capi`.
- Readiness slots: training headers unavailable, model activation not
  evaluated, restart impact not evaluated. These are info-level report entries,
  not parity failures.

## Validation Result

- `python3 -m py_compile $(find core/data_definition -name '*.py' -print)`:
  OK.
- `python3 -m pytest tests/test_data_definition_core_projection.py tests/test_predict_schema_catalog_v2_projection.py`:
  OK, 18 passed.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  hotspot warnings and stale code-map reminder; no changed source warning.
- `python3 -B tools/code_checker/build_reference_map.py --check`: STALE;
  recorded as code-map check evidence, no unrelated code map regeneration.
- `git diff --check`: OK.
- `git status --short`: OK; only expected new `core/data_definition/`, focused
  test, and report files are present.
- `git diff --name-only`: OK; empty before staging because the current changes
  are new untracked files.
- `git diff --stat`: OK; empty before staging for the same untracked-file
  reason. Staged scope is limited to allowed files before commit.
- `git diff --cached --check`: OK after staging allowed files.
- `git diff --cached --name-only` / `--stat`: OK; staged scope is the seven
  `core/data_definition` files, one focused test, and this report.

## Manual Check

Manual GUI/training/model checks are not required for this core-only read-only
foundation.

## Excluded Scope

- No UI changes.
- No save/write behavior.
- No runtime behavior changes.
- No `config/predict/schema.csv` or `config/ml/features.csv` changes.
- No `data/mapping.json` creation or modification.
- No Feature Catalog direct-edit removal.
- No Data Mapping Manager value edit/save logic changes.
- No Predict runtime adapter changes.
- No generic one-hot owner switch.
- No training/model readiness UI.
- No model retrain, training smoke, Predict GUI smoke, legacy wide CSV import,
  broad refactor, main merge, or main push.

## Structure / Change Gate

change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: checked

Read Ledger:
- `AGENT_TASK_ROUTER.md`: implementation/source and ML/Predictor route
  sections, reason: task routing and report gate.
- `docs/designs/2026-07-06-arc15-unified-data-definition-manager-foundation.md`:
  full Arc 15A boundary, reason: implementation contract.
- `docs/designs/2026-07-03-arc13-5r-predict-schema-v2-field-spec-confirmation.md`:
  field/spec and one-hot relationship ranges, reason: schema contract.
- `docs/designs/2026-07-03-arc13-5r-projection-owner-switch.md`: owner switch
  result and remaining runtime-owned paths, reason: no runtime owner switch.
- `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md`: ML/Predictor hard boundary
  and flow, reason: feature schema boundary.
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`: dependency and
  pre-write boundary ranges, reason: new core package boundary.
- `docs/architecture/project_architecture.md`: ML feature and schema owner
  ranges, reason: owner reuse decision.
- `docs/agent_workflows/DIFF_READ_BUDGET.md` and
  `docs/agent_workflows/AGENT_CHANGE_GATES.md`: code map and structured
  change gate ranges, reason: source change report metadata.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`: narrow keyword hits, reason:
  reuse/commonization check.
- `config/predict/schema.csv` and `config/ml/features.csv`: full small files,
  reason: current contract rows are the projection/parity input.
- `core/predictor_schema/catalog_v2.py`,
  `core/predictor_schema/catalog_v2_projection.py`,
  `core/ml/feature_catalog.py`, `core/ml/feature_catalog_projection.py`:
  loader/projection owner ranges, reason: reuse existing owners.
- `tests/test_predict_schema_catalog_v2_projection.py` and
  `tests/test_ml_feature_catalog.py`: focused test ranges, reason: preserve
  existing parity style.
- broad read: small CSV files and Arc 15 design record only; both are direct
  task inputs.
- repeated read: none.

## Next Action

Arc 15B — Data Definition Read-only UI.
