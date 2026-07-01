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
  presented as a viewer/editor table.
- Keep `config/ml/features.csv` as the storage and contract file.
- Support CSV export for storage, sharing, and Excel/Numbers review.
- Implement in two product slices after this design gate:
  - read-only viewer, validate, and export;
  - editable table and save.

## Architecture Direction

- The UI table is a thin view.
- Train UI actions should pass through a controller/service/usecase boundary.
- Catalog loading, validation, and writing should reuse the existing catalog
  loader/validator where possible, with a focused writer added only if needed.
- The UI must not own raw CSV parsing or writing directly.
- Export encoding policy belongs in the service/usecase or writer boundary, not
  in widget code.

## Expected Slices

- Slice 0: Feature Catalog Editor Design Gate.
- Slice 1: Feature Catalog Viewer / Validate / Export.
- Slice 2: Editable Catalog Table / Save.

## Excluded Scope

- ML algorithm changes.
- Model artifact schema changes.
- Train runtime algorithm changes.
- Predictor schema contract changes.
- Calculator code changes.

## Open Questions

- Should the editor be a new top-level tab, or a panel inside the existing
  Train / Model area?
- What CSV export encoding policy should be used for Excel/Numbers review,
  including whether UTF-8-SIG should be the default?
- How should validation results be displayed in the Train/Admin UI?
- Should save be blocked on validation failure, and what failure severity
  levels are needed?

## Next Action

Run the Calculator Sub-Arc - KOREA Notebook Entry first, then start Arc 13.5
Slice 0 with this design gate as the current direction.
