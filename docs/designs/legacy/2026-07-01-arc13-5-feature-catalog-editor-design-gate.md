# Arc 13.5 - Feature Catalog Editor Design Gate

## Purpose

Define the Arc 13.5 direction for managing the ML Feature Catalog through the
Train/Admin surface before moving to the real dataset readiness audit in Arc 14.

## Background

- Arc 13 closed the feature catalog contract. `config/ml/features.csv` is now
  the ML feature contract, and `ml_name` is the raw training header and
  internal ML name.
- Practical use shows that direct CSV editing is not the safest default user
  workflow. A table editor inside `app_train.py` gives the project a better
  place for validation, review, and save boundaries.
- Opening UTF-8 CSV files in Excel or Numbers can display Korean labels
  incorrectly when the application does not automatically detect UTF-8.

## Decisions

- Treat the Feature Catalog as a Train/Admin workflow in `app_train.py`,
  presented as a top-level `Feature Catalog` tab in `TrainShell`.
- Keep `config/ml/features.csv` as the storage and contract file.
- Support CSV export for storage, sharing, and Excel/Numbers review, but keep
  export separate from canonical save.
- Split implementation into small product slices after this design gate:
  - read-only viewer and catalog validation;
  - Excel-safe export;
  - editable table and canonical save;
  - closeout, docs sync, final validation, and push.
- Use
  `docs/designs/2026-07-02-arc13-5-feature-catalog-editor-revised-slice-plan.md`
  as the detailed slice evidence for this revision.

## Architecture Direction

- The UI table is a thin view.
- Train UI actions pass through a controller and Feature Catalog application
  service boundary.
- Catalog loading and catalog validation reuse the existing `core/ml` loader
  and validator.
- CSV export and canonical save are owned by a service/file-adapter boundary,
  not by widget code.
- The UI must not own raw CSV parsing or writing directly.
- Project consistency validation is separate from catalog validation. It can be
  included only when the existing owner can be called without broad imports,
  dependency inversion, circular imports, or Train/Predict runtime side effects.
- Table implementation uses `QTableView` plus `QAbstractTableModel`; do not add
  `QTableWidget` or `setCellWidget`.

## Validation Scope

- Catalog validation covers `features.csv` header, row, value, projection, and
  zero-fill policy rules and is required in Slice 1.
- Project consistency validation covers registry/projection/reference
  consistency and is optional in Slice 1 unless it is clean to call through the
  existing owner.
- UI status must make the validation scope visible enough that users do not
  confuse catalog-only success with full project consistency success.

## Export And Save Policy

- Export CSV writes a user-selected file as UTF-8-SIG for Excel/Numbers review
  and never mutates the canonical catalog.
- Save writes only `config/ml/features.csv` as UTF-8 without BOM.
- Save preserves `REQUIRED_HEADERS` order, forbids unknown headers, forbids
  required-header removal, validates before writing, and should use temp file
  plus `os.replace` when possible.
- Save failure preserves the existing canonical file and keeps dirty state.
- Successful save reloads and validates the canonical catalog.

## Editable Scope

- Editable columns: `label`, `notes`, `active`, `zero_fill_policy`, `source`,
  `mapping_key`, `one_hot_group`.
- Locked columns: `order`, `feature_id`, `ml_name`, `role`, `ui_key`.
- Row add/delete is out of scope.
- Invalid values are not silently coerced. DTO-to-canonical-row conversion
  failures are surfaced as validation messages and block save.

## Expected Slices

- Slice 0: Feature Catalog Editor Design Gate.
- Slice 1: Read-only Feature Catalog Viewer / Validate.
- Slice 2: Excel-safe CSV Export.
- Slice 3: Editable Catalog Table / Save with validation.
- Slice 4: Closeout / Docs Sync / Final Push.

## Excluded Scope

- ML algorithm changes.
- Model artifact schema changes.
- Train runtime algorithm changes.
- Predictor schema contract changes.
- Calculator code changes.
- `config/ml/features.csv` schema changes.
- `ml_name`, `role`, `feature_id`, `ui_key`, `order` editing.
- Row add/delete.

## Stop Conditions

- Viewer implementation requires changing the `features.csv` schema.
- Save requires changing `core/ml` projection semantics.
- UI must directly parse or write raw CSV to complete the workflow.
- Locked column editing or row add/delete becomes necessary.
- Safe-write cannot preserve the canonical file on failure.
- `load_feature_catalog()` cannot load the current canonical file.
- Project consistency validation requires dependency direction violations.
- Train runtime, Predict schema/result behavior, or calculator files would need
  to change.

## Next Action

Implement Arc 13.5 Slice 1 read-only viewer and catalog validation.
