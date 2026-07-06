# Arc 15 Unified Data Definition Manager Design Record

## Goal

Create the Arc 15 design record for Unified Data Definition Manager Foundation,
register it in the design index, and preserve the current codebase evidence for
the Arc 15A starting boundary.

## Modified Files

- `docs/designs/2026-07-06-arc15-unified-data-definition-manager-foundation.md`
- `docs/designs/README.md`
- `result_reports/active/712_arc15-unified-data-definition-manager-design-record.md`

## Summary of Decisions

- Arc 15 proceeds as Unified Data Definition Manager Foundation.
- `config/predict/schema.csv` is promoted to the primary Data Definition
  source.
- `config/ml/features.csv` remains the compatibility contract through Arc
  15A/B and becomes an ML projection/compatibility output only after staged
  parity and save contracts are stable.
- A separate derived feature policy is required because current `features.csv`
  has `derived` rows that `schema.csv` alone does not represent.
- `data/mapping.json` remains the mapping value SSOT.
- Data Definition Manager owns definition, requirement, projection, validation,
  and readiness. Data Mapping Manager owns actual mapping value edits.
- Generic one-hot owner switch is deferred to Arc 15E; Arc 15A validates parity
  only.

## Current Codebase Evidence Checked

- `docs/designs/README.md` had no Arc 15-specific design record entry.
- Arc 13.5R records establish Predict Schema Catalog v2, schema field rules,
  and the projection owner switch.
- Arc 14 records establish Data Mapping Manager as a mapping value surface and
  reject legacy wide CSV import restoration as the primary path.
- `config/predict/schema.csv` contains Predict column metadata, mapping
  entity/attribute fields, rule references, model input metadata, `ml_name`, and
  one-hot grouping.
- `core.predictor_schema.columns` now builds `COLUMNS` through
  `load_projected_columns_v2()`.
- `config/ml/features.csv` still contains ML feature, target, one-hot, and
  active derived rows.
- `core.ml.feature_catalog_projection` still owns derived features, training
  headers, zero-fill, target, and one-hot projections.
- `apps.train.ui.shell` still exposes both Data Mapping and Feature Catalog
  tabs.
- `apps.train.services.data_mapping_service` edits/saves/exports mapping
  drafts backed by runtime mapping data.
- `apps.predict.adapters.row_to_ml_input_adapter` still contains hard-coded
  one-hot input group ownership for current runtime behavior.

## Validation Result

- `git diff --check`: OK.
- `git status --short`: OK; only the README modification and two expected
  untracked created files are present.
- `git diff --name-only`: OK; tracked diff lists `docs/designs/README.md`.
- `git diff --stat`: OK; tracked diff stat is one README insertion. Created
  untracked files are listed by `git status --short` until staged.
- Pytest, py_compile, training/model smoke, and Predict GUI smoke are skipped
  because this is a docs-only design record task.

## Manual Check

Manual check not required for this docs-only design record.

## Excluded Scope

- No code changes.
- No CSV changes.
- No `mapping.json` creation or modification.
- No Feature Catalog, Data Mapping, or Predict runtime behavior changes.
- No fixture/golden changes.
- No Arc 15A implementation.
- No model retrain, training smoke, or Predict GUI smoke.
- No legacy wide CSV import restoration design.
- No merge.

## Commit / Push

- Docs commit: `df6cc58f69b2af8e73a154c7902fd936ae1692d5`
- Report commit: recorded in terminal output because it would require editing
  this report after committing itself.
- Push status: recorded in terminal output after remote verification.

## Next Action

Arc 15A — Data Definition Core Projection and Cross-contract Validator.
