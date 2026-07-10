# 673 Summary - Arc 13.5 / 13.5A Feature Catalog Manager Closeout

## Goal

Summarize the Arc 13.5 and Arc 13.5A Feature Catalog Manager workstream and
archive the completed active reports.

Covered reports:

- `635_planning-doc-sync-arc13-5-feature-catalog-editor.md`
- `655_active-report-lifecycle-cleanup-pre-arc13-5.md`
- `656_arc13-5-feature-catalog-design-gate.md`
- `657_arc13-5-feature-catalog-viewer.md`
- `658_arc13-5-feature-catalog-export.md`
- `659_arc13-5-feature-catalog-edit-save.md`
- `660_arc13-5-feature-catalog-closeout.md`
- `661_arc13-5a-feature-catalog-identity.md`
- `662_arc13-5a-feature-catalog-identity-followup.md`
- `663_arc13-5a-slice1-feature-catalog-ux-foundation.md`
- `664_arc13-5a-slice2-feature-catalog-row-actions.md`
- `665_arc13-5a-slice3-feature-catalog-schema-apply.md`
- `666_arc13-5a-slice4-model-catalog-fingerprint.md`
- `667_arc13-5a-slice5-common-table-helpers.md`
- `668_arc13-5a-feature-catalog-manager-closeout.md`
- `669_arc13-5a-feature-catalog-dropdown-ux-bugfix.md`
- `670_arc13-5a-feature-catalog-fingerprint-scope.md`
- `671_arc13-5a-fingerprint-active-field-dedup.md`
- `672_arc13-5a-final-closeout-update.md`

## Major Decisions

- `app_train.py` is the default Feature Catalog Manager entrypoint for normal
  validation, Excel-safe export, whitelisted edits, draft row actions, help,
  validation-gated save, and restart-required schema apply messaging.
- Direct `config/ml/features.csv` editing remains an advanced/developer
  fallback, not the default user workflow.
- `ml_name` is the catalog row identity after `feature_id` removal. It remains
  the raw training data header and internal ML feature/target name.
- GUI display names are user-friendly while canonical CSV headers remain
  stable English/internal keys.
- `order`, `ml_name`, and `ui_key` are locked in the table. `role`, `label`,
  `notes`, `active`, `zero_fill_policy`, `source`, `mapping_key`, and
  `one_hot_group` are editable where validation allows.
- Add, Duplicate, and Delete operate on draft table state first. File mutation
  happens only through validation-gated Save.
- Save writes canonical UTF-8 without BOM and reports that already-open
  schema-dependent UI surfaces require restart.
- Model artifacts store a Feature Catalog compatibility fingerprint. Prediction
  model load rejects missing or mismatched fingerprints.

## Arc 13.5A Corrections

- Dropdown UX bugfix:
  - dropdown cell values remain visible;
  - `Feature 유형(role)` is editable by dropdown;
  - combo activation commits through the Qt delegate lifecycle;
  - single-click dropdown edit entry is covered by focused Qt tests;
  - Computer Use visual smoke was blocked by remote display/login state, but
    user direct GUI smoke later confirmed the dropdown UX OK.
- Fingerprint scope fix:
  - model compatibility fingerprint uses active rows only;
  - payload fields are `ml_name`, `role`, `one_hot_group`, and
    `zero_fill_policy`;
  - `active` changes compatibility by row inclusion/exclusion, not by being
    stored redundantly inside each payload row;
  - `label`, `notes`, `order`, `ui_key`, `source`, and `mapping_key` are
    excluded from model artifact compatibility.

## Runtime Behavior

- Feature Catalog Manager loads and validates catalog/project consistency in
  the Train/Admin shell.
- CSV export uses UTF-8-SIG for Excel/Numbers review and includes current
  unsaved table edits.
- Canonical save remains validation-gated and preserves UTF-8 without BOM.
- Save success surfaces a restart-required schema apply message; live schema
  refresh is intentionally not implemented in this workstream.
- Inference blocks model artifacts with missing/mismatched catalog
  fingerprints; existing old-scope artifacts are expected to require retraining.

## Excluded Scope

- No model retraining.
- No Feature Catalog schema refresh/live apply runtime wiring.
- No broad training logic refactor.
- No calculator raw hex literal cleanup.
- No report lifecycle movement beyond this summary/archive cleanup.

## Validation

- Arc 13.5/13.5A slices repeatedly ran focused compile, Qt, ML catalog, Train
  shell/service, Predict service/table, and smoke tests recorded in the source
  reports.
- Lifecycle cleanup validation:
  - `git diff --check`: OK.
  - `python3 -B tools/check_code_structure.py`: NG only for the existing
    unrelated `apps/calculator/ui/calculator_app.py` raw hex literal guard
    failure.
  - Active report count is below lifecycle threshold after archive movement.
  - Memory seed summary registration and compact durable decision entry were
    updated.

## Lifecycle

- Covered active reports are archived under `result_reports/archive/`.
- This summary is registered in `result_reports/memory/project_memory_seed.md`.
- Memory seed gained one compact durable Arc 13.5A decision entry.

## Next Action

Arc 14 - ML Catalog-Aligned Real Dataset Readiness Audit.
