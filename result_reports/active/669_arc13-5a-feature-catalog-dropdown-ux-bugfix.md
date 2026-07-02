# Arc 13.5A Feature Catalog Dropdown UX Bugfix

## Goal

Fix Feature Catalog table dropdown cells so current values are visible, role is editable through a dropdown, dropdown choices commit to the model, and one-click dropdown entry works reliably.

## Scope

- Feature Catalog application DTO editability metadata.
- Feature Catalog Qt dropdown delegate paint/editor/commit lifecycle.
- Feature Catalog table view one-click dropdown edit entry.
- Focused Qt tests for dropdown options, editability, editor creation, commit, and click-to-edit.

## Non-goals

- Fingerprint Scope Fix.
- Model artifact compatibility, schema refresh/live apply, add/delete/duplicate expansion.
- Feature Catalog schema changes.
- Calculator raw hex literal cleanup.
- Report lifecycle cleanup or unrelated refactor.
- External GUI library changes.

## User-Reported Symptoms

- Dropdown cells appeared blank.
- `Feature 유형(role)` dropdown did not open.
- `source`, `mapping_key`, `one_hot_group`, `zero_fill_policy`, and `active` dropdown selections did not update the table cell.
- Dropdown click behavior required multiple clicks and could feel like an unintended value was selected.

## Cause

- `role` had dropdown options but remained in the locked header set, so the table model refused edit entry.
- The delegate created `QComboBox` editors but did not explicitly commit and close on user activation.
- Custom paint drew a full combo control over the cell rectangle, which could obscure DisplayRole text.
- Table edit triggers only opened an editor after selected-click/double-click paths, not the first completed click on a dropdown cell.

## Changed Files

- `apps/train/application/feature_catalog/models.py`: moved `role` into editable headers and kept `order`, `ml_name`, `ui_key` locked.
- `apps/train/ui/feature_catalog/delegates.py`: preserved default text paint, drew only a small arrow affordance, and connected combo activation to `commitData` / `closeEditor`.
- `apps/train/ui/feature_catalog/table_view.py`: added single-click dropdown edit entry on mouse release for editable dropdown cells only.
- `tests/test_apps_train_feature_catalog.py`: added focused Qt coverage for role editability, dropdown option exposure, combo editor creation/commit, and single-click edit entry.

## Verification

- `python3 -m compileall apps tests`: OK.
- `python3 -m pytest tests/test_apps_train_feature_catalog.py`: OK, 21 passed.
- `git diff --check`: OK.
- `python3 -B tools/check_code_structure.py`: NG, existing unrelated `apps/calculator/ui/calculator_app.py` raw hex literal guard failure only.
- `python3 -B tools/check_code_structure.py --verbose`: changed Feature Catalog files are not structure warning targets; warnings are existing calculator/core/code-map freshness warnings.

## Local GUI Smoke

- `python3 app_train.py`: process launched and remained running; startup printed the existing missing `data/mapping.json` warning.
- Computer Use manual visual smoke: blocked. The running `Python` app was listed, but `get_app_state("Python")` and `get_app_state("org.python.python")` returned `cgWindowNotFound`, so direct screen click verification could not be completed in this environment.
- Supplemental local Qt GUI smoke: OK. A visible `TrainShell` session opened the Feature Catalog tab, verified dropdown cell display values/options for `role`, `source`, `mapping_key`, `one_hot_group`, `zero_fill_policy`, and `active`, verified single-click role editor entry, and verified combo activation commits to the table model.

## Table Parity Evidence

- QTableView / QAbstractTableModel / QStyledItemDelegate pattern preserved.
- No `QTableWidget` or `setCellWidget()` introduced.
- Dropdown editor opens via Qt event-loop scheduling; no sleep-based timing introduced.
- Edit path remains model `setData`; paste/clear/undo paths in `FeatureCatalogTableView` were not mixed into delegate commit logic.
- DisplayRole text remains the primary cell paint source; validation BackgroundRole remains model-owned.

## Reuse / Commonization

- `reuse_commonization`: local-with-reason.
- Existing Feature Catalog table model/view/delegate owners already contained the relevant behavior, so the fix extends those owners instead of adding a new table helper or reusable UI surface.
- No repeated cross-surface policy was introduced.

## Structure / Code Map

- `code_map_check`: no-change.
- Reason: no new files, no new reusable surface/helper/adapter, no owner boundary move, and no commonization path change. Private lifecycle helpers were added inside the existing owner files only.
- Structure warnings: none for changed Feature Catalog files.

## Known Failures / Risks

- Computer Use visual manual smoke could not inspect the Python window due `cgWindowNotFound`; supplemental Qt GUI smoke and focused Qt tests cover the dropdown lifecycle but are not a human visual click-through.
- `tools/check_code_structure.py` still reports the pre-existing calculator raw hex literal failure outside this task scope.

## Next Suggested Action

- Arc 13.5A Fingerprint Scope Fix.

## Scope Compliance

- Stayed within allowed source/test/report files.
- Did not change Feature Catalog schema, ML artifacts, calculator literals, or unrelated UI flows.

## Commit / Push

- commit: final hash reported in terminal output after push
- push: final status reported in terminal output after push
- local_head: final SHA reported in terminal output after push
- remote_main: final SHA reported in terminal output after push
- match: final match status reported in terminal output after push

## Project Memory Delta

- none
