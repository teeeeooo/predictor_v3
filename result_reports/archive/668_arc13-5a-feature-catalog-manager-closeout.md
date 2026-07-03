# Arc 13.5A Feature Catalog Manager Closeout

## Goal

Close out Arc 13.5A remaining Feature Catalog Manager slices after Slice 0.

## Completed

- Slice 1: UX foundation with user-friendly headers, dropdown options, Help, current-state export, and baseline dirty state.
- Slice 2: Add, Duplicate, and Delete draft row workflows with generated `order` and `ui_key`.
- Slice 3: Post-save schema apply behavior via restart-required messaging.
- Slice 4: Model artifact Feature Catalog fingerprint guard.
- Slice 5: Common table clipboard/undo helper cleanup.
- Arc 13.5A correction: Dropdown UX bugfix completed in
  `result_reports/archive/669_arc13-5a-feature-catalog-dropdown-ux-bugfix.md`.
- Arc 13.5A correction: Feature Catalog fingerprint scope narrowed to the ML
  model contract in
  `result_reports/archive/670_arc13-5a-feature-catalog-fingerprint-scope.md`.
- Arc 13.5A correction: redundant `active` row payload field removed; active
  state now affects fingerprint by row inclusion/exclusion, recorded in
  `result_reports/archive/671_arc13-5a-fingerprint-active-field-dedup.md`.
- Workflow/design docs synced to current behavior.

## Validation

- `python3 -m compileall core apps tools tests` - OK
- `python3 -m pytest tests/test_ml_feature_catalog.py tests/test_apps_train_feature_catalog.py tests/test_apps_train_shell.py tests/test_apps_train_training_service.py tests/test_mock_smoke_generators.py tests/test_apps_predict_prediction_service_status.py tests/test_apps_predict_table_interactions.py tests/test_apps_predict_table_models.py tests/test_apps_predict_workspace_unified_table.py` - OK, 126 passed
- `git diff --check` - OK
- `python3 -B tools/check_code_structure.py --verbose` - NG, pre-existing unrelated raw hex literal:
  - `apps/calculator/ui/calculator_app.py:105`
  - Existing unrelated soft warnings remained outside changed files.

## Manual Smoke

Computer Use visual smoke was blocked in the remote environment because the Mac
session was at the display/login boundary. Supplemental local Qt GUI smoke
passed during the dropdown bugfix, and the user later confirmed direct GUI smoke
OK for the dropdown UX in the local desktop session. Automated offscreen Qt
coverage exercised Feature Catalog panel load, edit, export, add/delete draft
state, shell tab presence, Predict table interactions, DEV training artifact
load, and Train shell smoke script.

## Changed Files

- `docs/workflows/ml_feature_catalog_workflow.md`
- `docs/designs/2026-07-02-arc13-5a-feature-catalog-manager-correction-design.md`
- `apps/train/application/feature_catalog/models.py`
- `apps/train/ui/feature_catalog/delegates.py`
- `apps/train/ui/feature_catalog/table_view.py`
- `core/ml/catalog_fingerprint.py`
- `tests/test_apps_train_feature_catalog.py`
- `tests/test_ml_feature_catalog.py`

## Lifecycle

Active report count exceeds lifecycle threshold; cleanup is pending as a separate user-approved maintenance task. No report lifecycle movement was performed in this closeout.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  ui_literal_exemption: none
  reuse_commonization: not_required
  report_exemption: none
  read_ledger: included
```

## Commit / Push

Closeout docs and this report are committed after validation. Push is performed after this final closeout commit.

## Next

No Arc 13.5A blocker remains. Next action is active report lifecycle cleanup.
