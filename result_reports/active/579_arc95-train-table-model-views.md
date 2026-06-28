# 579 Arc 9.5 Trainer Table Model Views

## Goal

- Remove forbidden `QTableWidget` usage from Trainer visual panels.

## Scope

- Added a small read-only `StaticTableModel` under `apps/train/ui/models/`.
- Replaced Trainer summary/status tables with `QTableView` model/view surfaces.
- Updated tests to assert model/view usage, model data, disabled execution
  controls, and source guard behavior.

## Non-goals

- Trainer execution remains deferred.
- No Train service/controller/worker implementation was added.
- No mapping schema, ML, calculator, or Predict workflow changes.

## Verification

- `PYTHONPATH=. QT_QPA_PLATFORM=offscreen pytest -q tests/test_apps_train_shell.py` - OK, 7 passed.
- `rg -n "QTableWidget|QTableWidgetItem" apps/train/ui tests/test_apps_train_shell.py || true` - production source clean; only test source-guard strings remain.
- `python3 -B tools/check_code_structure.py` - OK with pre-existing unrelated soft warnings and code-map freshness reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` - STALE; not regenerated in this focused Trainer UI slice.
- `git diff --check` - OK.

## Task Results

- `TrainModelPanel` summary table now uses `QTableView` with
  `StaticTableModel`.
- `DataMappingPanel` mapping status table now uses `QTableView` with
  `StaticTableModel`.
- Tests no longer assert the forbidden widget pattern.

## Reference Parity / Change Gate

- Existing Trainer panel structure was retained; only table implementation
  changed.
- Reuse/commonization decision: a tiny UI-local static model is shared by both
  Trainer placeholder/status tables because they have the same read-only
  header/row tuple shape.
- `code_map_check`: checked; stale before this slice, not regenerated because
  the change is focused and local.

## Structure Warnings

- No changed/new source file emitted a LOC/class warning.
- Existing unrelated calculator and code-map freshness warnings remain.

## Changed Files

- `apps/train/ui/models/__init__.py`
- `apps/train/ui/models/static_table_model.py`
- `apps/train/ui/train_model_panel.py`
- `apps/train/ui/data_mapping_panel.py`
- `tests/test_apps_train_shell.py`

## Known Risks

- These Trainer tables remain placeholder/status surfaces until Arc 11
  execution work defines live data updates.

## Commit / Push

- Commit: pending for this slice.
- Push: deferred per user request until all slices complete.

## Project Memory Delta

- none
